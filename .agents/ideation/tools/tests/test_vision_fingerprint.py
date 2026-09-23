from __future__ import annotations

import pytest

from ideation_tools.hashing import sha256_bytes, vision_content_fingerprint

CANDIDATE = b"---\nstatus: candidate\nversion: 0.1\n---\n# Vision\n\nHelp learners keep what they learn.\n"


def test_status_value_does_not_change_the_fingerprint():
    approved = CANDIDATE.replace(b"status: candidate", b"status: approved")
    assert vision_content_fingerprint(approved) == vision_content_fingerprint(CANDIDATE)


def test_fingerprint_is_hex_sha256():
    fingerprint = vision_content_fingerprint(CANDIDATE)
    assert len(fingerprint) == 64 and int(fingerprint, 16) >= 0
    assert fingerprint == sha256_bytes(CANDIDATE.replace(b"status: candidate", b"status:"))


@pytest.mark.parametrize("edited", [
    CANDIDATE.replace(b"keep", b"forget"),                         # body text
    CANDIDATE.replace(b"version: 0.1", b"version: 0.2"),           # other header field
    CANDIDATE + b"\n",                                             # trailing whitespace
    CANDIDATE.replace(b"\n", b"\r\n"),                             # line endings
    CANDIDATE.replace(b"status: candidate\nversion: 0.1", b"version: 0.1\nstatus: candidate"),  # status line moved
    CANDIDATE.replace(b"status: candidate\n", b""),                # status line removed
])
def test_any_other_edit_changes_the_fingerprint(edited):
    assert vision_content_fingerprint(edited) != vision_content_fingerprint(CANDIDATE)


def test_status_line_in_the_body_is_not_ignored():
    body = b"# Vision\n\nstatus: one\n"
    assert vision_content_fingerprint(body) != vision_content_fingerprint(body.replace(b"status: one", b"status: two"))


def test_only_the_first_header_status_line_is_blanked():
    twice = b"status: candidate\nstatus: extra\n# Vision\n"
    assert vision_content_fingerprint(twice) != vision_content_fingerprint(twice.replace(b"extra", b"other"))


def test_crlf_status_line_keeps_its_line_ending():
    crlf = CANDIDATE.replace(b"\n", b"\r\n")
    approved = crlf.replace(b"status: candidate", b"status: approved")
    assert vision_content_fingerprint(approved) == vision_content_fingerprint(crlf)
