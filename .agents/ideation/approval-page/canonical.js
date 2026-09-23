// Mirrors ideation_tools.hashing.canonical_hash:
// json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False), UTF-8, SHA-256 hex.

function compareCodePoints(a, b) {
  // Python sorts str keys by code point; JavaScript's default sort uses UTF-16 units.
  const ca = Array.from(a, (c) => c.codePointAt(0));
  const cb = Array.from(b, (c) => c.codePointAt(0));
  for (let i = 0; i < Math.min(ca.length, cb.length); i++) {
    if (ca[i] !== cb[i]) return ca[i] - cb[i];
  }
  return ca.length - cb.length;
}

export function canonicalJson(value) {
  if (value === null || value === true || value === false) return JSON.stringify(value);
  if (typeof value === "number") {
    // Python and JavaScript print non-integers differently (1.0 vs 1), so refuse them.
    if (!Number.isSafeInteger(value)) throw new Error(`Unsupported number ${value}: only whole numbers can be checked`);
    return String(value);
  }
  if (typeof value === "string") return JSON.stringify(value);
  if (Array.isArray(value)) return `[${value.map(canonicalJson).join(",")}]`;
  if (typeof value === "object") {
    const keys = Object.keys(value).sort(compareCodePoints);
    return `{${keys.map((k) => `${JSON.stringify(k)}:${canonicalJson(value[k])}`).join(",")}}`;
  }
  throw new Error(`Unsupported value of type ${typeof value}`);
}

export async function sha256Hex(text) {
  const digest = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(text));
  return Array.from(new Uint8Array(digest), (b) => b.toString(16).padStart(2, "0")).join("");
}

// Mirrors ideation_tools.approvers.key_fingerprint: first 8 bytes of SHA-256(SPKI) as XXXX-XXXX-XXXX-XXXX.
export async function keyFingerprint(spkiBytes) {
  const digest = await crypto.subtle.digest("SHA-256", spkiBytes);
  const hex = Array.from(new Uint8Array(digest).slice(0, 8), (b) => b.toString(16).padStart(2, "0")).join("").toUpperCase();
  return hex.match(/.{4}/g).join("-");
}
