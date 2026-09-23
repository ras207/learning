import { canonicalJson, keyFingerprint, sha256Hex } from "./canonical.js";

const REQUEST_KIND = "ideation_approval_request";
const APPROVAL_KIND = "ideation_approval";

const $ = (id) => document.getElementById(id);

function bytesToB64url(bytes) {
  let binary = "";
  for (const b of new Uint8Array(bytes)) binary += String.fromCharCode(b);
  return btoa(binary).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}

function b64urlToBytes(text) {
  const padded = text.replace(/-/g, "+").replace(/_/g, "/") + "=".repeat((4 - (text.length % 4)) % 4);
  return Uint8Array.from(atob(padded), (c) => c.charCodeAt(0));
}

function hexToBytes(hex) {
  return Uint8Array.from(hex.match(/../g), (h) => parseInt(h, 16));
}

function encodeResult(obj) {
  return bytesToB64url(new TextEncoder().encode(JSON.stringify(obj)));
}

// All request content comes from the agent, so it is only ever inserted as text.
function el(tag, text, className) {
  const node = document.createElement(tag);
  if (text !== undefined) node.textContent = text;
  if (className) node.className = className;
  return node;
}

function describeValue(value) {
  return typeof value === "string" ? value : canonicalJson(value);
}

function showError(message) {
  $("status").replaceChildren(el("p", message, "error"));
  $("status").hidden = false;
}

function showResult(sectionId, code) {
  const section = $(sectionId);
  section.querySelector("textarea").value = code;
  section.hidden = false;
}

async function copyFrom(sectionId) {
  const area = $(sectionId).querySelector("textarea");
  try {
    await navigator.clipboard.writeText(area.value);
  } catch {
    area.select();
    document.execCommand("copy");
  }
  $(sectionId).querySelector(".copied").hidden = false;
}

function renderAction(action) {
  const list = $("signed-fields");
  const project = action.project;
  list.replaceChildren(
    el("p", `${action.operation} ${action.section} record ${action.record_id ?? "(none)"}`, "headline"),
    el("p", `Project ${project.project_id} (iteration ${project.iteration}), transaction ${action.transaction_id}`),
  );
  const fields = el("dl");
  for (const key of Object.keys(action.patch).sort()) {
    fields.append(el("dt", key), el("dd", describeValue(action.patch[key])));
  }
  list.append(fields);
  if (action.dependencies.length) list.append(el("p", `Depends on: ${action.dependencies.join(", ")}`));
}

function renderUnsigned(context) {
  $("unsigned-fields").replaceChildren(
    el("dt", "Summary"), el("dd", context?.transaction_summary ?? ""),
    el("dt", "Rationale"), el("dd", context?.rationale ?? ""),
  );
}

async function startApproval(fragment) {
  let request;
  try {
    request = JSON.parse(new TextDecoder().decode(b64urlToBytes(fragment)));
  } catch {
    return showError("This approval link is damaged. Ask the agent for a new one.");
  }
  if (request?.kind !== REQUEST_KIND || request.schema_version !== 1 || typeof request.action !== "object") {
    return showError("This link is not an ideation approval request.");
  }

  let computed;
  try {
    computed = await sha256Hex(canonicalJson(request.action));
  } catch (err) {
    return showError(`This request cannot be checked: ${err.message}. Do not approve it.`);
  }
  if (computed !== request.action_hash) {
    return showError("The request's hash does not match its contents. Do not approve it; tell the agent.");
  }

  renderAction(request.action);
  renderUnsigned(request.unsigned_context);
  $("hash").textContent = computed;
  $("approve").hidden = false;

  $("approve-button").addEventListener("click", async () => {
    try {
      const assertion = await navigator.credentials.get({
        publicKey: { challenge: hexToBytes(computed), userVerification: "required", timeout: 120000 },
      });
      const response = assertion.response;
      showResult("approval-result", encodeResult({
        schema_version: 1,
        kind: APPROVAL_KIND,
        authorization_id: request.authorization_id,
        action_hash: computed,
        credential_id: assertion.id,
        authenticator_data: bytesToB64url(response.authenticatorData),
        client_data_json: bytesToB64url(response.clientDataJSON),
        signature: bytesToB64url(response.signature),
      }));
    } catch (err) {
      showError(`Approval was not completed: ${err.message}`);
    }
  });
}

async function register() {
  const name = $("approver-name").value.trim();
  if (!name) return showError("Enter your name first.");
  try {
    const credential = await navigator.credentials.create({
      publicKey: {
        rp: { name: "Ideation approvals" },
        user: { id: crypto.getRandomValues(new Uint8Array(16)), name, displayName: name },
        challenge: crypto.getRandomValues(new Uint8Array(32)),
        pubKeyCredParams: [{ type: "public-key", alg: -7 }],
        authenticatorSelection: { residentKey: "required", userVerification: "required" },
        attestation: "none",
      },
    });
    const spki = credential.response.getPublicKey();
    $("fingerprint").textContent = await keyFingerprint(spki);
    showResult("register-result", encodeResult({
      schema_version: 1,
      kind: "ideation_approver",
      approver: name,
      rp_id: location.hostname,
      credential_id: credential.id,
      public_key_spki: bytesToB64url(spki),
      algorithm: credential.response.getPublicKeyAlgorithm(),
    }));
  } catch (err) {
    showError(`Registration was not completed: ${err.message}`);
  }
}

$("register-button").addEventListener("click", register);
for (const section of ["approval-result", "register-result"]) {
  $(section).querySelector("button").addEventListener("click", () => copyFrom(section));
}

const fragment = location.hash.slice(1);
if (fragment) {
  startApproval(fragment);
} else {
  $("no-request").hidden = false;
}
