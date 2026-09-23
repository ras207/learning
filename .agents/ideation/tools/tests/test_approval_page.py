from __future__ import annotations

import base64
import copy
import functools
import hashlib
import json
import os
import shutil
import subprocess
import threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest

from ideation_tools.approval import build_approval_requests, encode_request
from ideation_tools.approvers import add_approver, key_fingerprint
from ideation_tools.hashing import canonical_hash

from test_approval import decision_tx

PAGE_DIR = Path(__file__).resolve().parents[2] / "approval-page"


def require_tool(available: bool, name: str) -> None:
    # CI must run these tests; a developer machine without the tool may skip them.
    if not available:
        if os.environ.get("CI"):
            pytest.fail(f"{name} is required in CI")
        pytest.skip(f"{name} is not installed")


def b64url_decode(text: str) -> bytes:
    return base64.urlsafe_b64decode(text + "=" * (-len(text) % 4))


def js_hashes(values: list) -> list[str]:
    require_tool(shutil.which("node") is not None, "node")
    # Read the values from stdin, then print one hash (or ERROR) per value.
    script = (
        "import { readFileSync } from 'node:fs';"
        f"import {{ canonicalJson, sha256Hex }} from {json.dumps((PAGE_DIR / 'canonical.js').as_uri())};"
        "const values = JSON.parse(readFileSync(0, 'utf8'));"
        "for (const v of values) {"
        "  try { console.log(await sha256Hex(canonicalJson(v))); } catch (e) { console.log('ERROR'); }"
        "}"
    )
    out = subprocess.run(
        ["node", "--input-type=module", "-e", script],
        input=json.dumps(values), capture_output=True, text=True, check=True,
    )
    return out.stdout.split()


CANONICAL_CASES = [
    None, True, False, 0, -42, 2**53 - 1, "", "plain",
    "quotes \" and \\ backslash", "line\nbreak\ttab\r", "control \x01\x1f", "é ñ ü 中文 العربية", "emoji 😀 👍🏽",
    "\u2028\u2029", [], {}, [1, "a", None, [True]],
    {"b": 1, "a": {"d": [], "c": "x"}},
    {"\U0001F600": 1, "\uffff": 2, "z": 3, "Z": 4, "é": 5},
    decision_tx()["state_mutations"][1],
]


def test_js_canonical_hash_matches_python():
    assert js_hashes(CANONICAL_CASES) == [canonical_hash(v) for v in CANONICAL_CASES]


def test_js_refuses_non_integer_numbers():
    assert js_hashes([1.5, {"a": [0.1]}, 2**53]) == ["ERROR", "ERROR", "ERROR"]


def test_js_key_fingerprint_matches_python():
    require_tool(shutil.which("node") is not None, "node")
    samples = [b"", b"abc", bytes(range(256))]
    script = (
        "import { readFileSync } from 'node:fs';"
        f"import {{ keyFingerprint }} from {json.dumps((PAGE_DIR / 'canonical.js').as_uri())};"
        "for (const hex of JSON.parse(readFileSync(0, 'utf8'))) {"
        "  console.log(await keyFingerprint(Buffer.from(hex, 'hex')));"
        "}"
    )
    out = subprocess.run(
        ["node", "--input-type=module", "-e", script],
        input=json.dumps([s.hex() for s in samples]), capture_output=True, text=True, check=True,
    )
    assert out.stdout.split() == [key_fingerprint(s) for s in samples]


@pytest.fixture
def page_url():
    handler = functools.partial(SimpleHTTPRequestHandler, directory=str(PAGE_DIR))
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    # WebAuthn needs a secure context; http://localhost counts as one.
    yield f"http://localhost:{server.server_address[1]}/index.html"
    server.shutdown()


@pytest.fixture
def browser_page():
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        require_tool(False, "playwright")
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        cdp = page.context.new_cdp_session(page)
        cdp.send("WebAuthn.enable")
        cdp.send("WebAuthn.addVirtualAuthenticator", {"options": {
            "protocol": "ctap2", "transport": "internal", "hasResidentKey": True,
            "hasUserVerification": True, "isUserVerified": True, "automaticPresenceSimulation": True,
        }})
        yield page
        browser.close()


def register(page, page_url: str) -> str:
    page.goto(page_url)
    page.click("#register summary")
    page.fill("#approver-name", "tester")
    page.click("#register-button")
    page.wait_for_selector("#register-result:not([hidden])")
    return page.input_value("#register-result textarea")


def test_register_then_approve_produces_valid_signature(browser_page, page_url):
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import ec

    code = register(browser_page, page_url)
    approver = json.loads(b64url_decode(code))
    assert approver["kind"] == "ideation_approver"
    assert approver["rp_id"] == "localhost"
    assert approver["algorithm"] == -7

    request = build_approval_requests(decision_tx(), page_url=page_url)[0]
    browser_page.goto("about:blank")
    browser_page.goto(request["link"])
    browser_page.wait_for_selector("#approve:not([hidden])")
    assert "decision" in browser_page.inner_text("#signed-fields")
    assert "Human decided" in browser_page.inner_text("#unsigned-fields")
    assert browser_page.inner_text("#hash") == request["action_hash"]

    browser_page.click("#approve-button")
    browser_page.wait_for_selector("#approval-result:not([hidden])")
    approval = json.loads(b64url_decode(browser_page.input_value("#approval-result textarea")))
    assert approval["authorization_id"] == "auth-1"
    assert approval["action_hash"] == request["action_hash"]
    assert approval["credential_id"] == approver["credential_id"]

    client_data_bytes = b64url_decode(approval["client_data_json"])
    client_data = json.loads(client_data_bytes)
    assert client_data["type"] == "webauthn.get"
    assert b64url_decode(client_data["challenge"]) == bytes.fromhex(request["action_hash"])

    auth_data = b64url_decode(approval["authenticator_data"])
    assert auth_data[:32] == hashlib.sha256(b"localhost").digest()
    assert auth_data[32] & 0x04, "user verification flag must be set"

    public_key = serialization.load_der_public_key(b64url_decode(approver["public_key_spki"]))
    public_key.verify(
        b64url_decode(approval["signature"]),
        auth_data + hashlib.sha256(client_data_bytes).digest(),
        ec.ECDSA(hashes.SHA256()),
    )


def test_registration_code_is_accepted_by_add_approver(browser_page, page_url):
    code = register(browser_page, page_url)
    shown = browser_page.inner_text("#fingerprint")
    approvers = {
        "schema_version": 1, "rp_id": "localhost", "origin": page_url.split("/index.html")[0],
        "approval_page_url": page_url, "approvers": [],
    }
    _, entry = add_approver(approvers, code, added_at="2026-09-23")
    assert entry["approver"] == "tester"
    assert entry["fingerprint"] == shown
    assert entry["fingerprint"] == key_fingerprint(b64url_decode(entry["public_key_spki"]))


def test_tampered_request_is_refused(browser_page, page_url):
    request = build_approval_requests(decision_tx(), page_url=page_url)[0]
    payload = {k: request[k] for k in ("schema_version", "kind", "authorization_id", "action", "action_hash", "unsigned_context")}
    tampered = copy.deepcopy(payload)
    tampered["action"]["patch"]["decision"] = "No"
    browser_page.goto(f"{page_url}#{encode_request(tampered)}")
    browser_page.wait_for_selector("#status .error")
    assert "does not match" in browser_page.inner_text("#status")
    assert browser_page.is_hidden("#approve")


def test_damaged_link_is_refused(browser_page, page_url):
    browser_page.goto(f"{page_url}#not-a-real-request")
    browser_page.wait_for_selector("#status .error")
    assert browser_page.is_hidden("#approve")
