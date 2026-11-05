# Codex v2 — Immutable Build

**My judgment call:** Keep v1 untouched. v2 is a separate, hardened copy. That way the portfolio shows both the original build *and* the hardening.

## Files
- `build_immutable.py` — builds `codex_immutable.db` + `codex_immutable.json` + manifest
- `verify_codex.py` — verifies chain, JSON, and manifest. Exit 0 = VERIFIED, 1 = TAMPERED.
- `codex_immutable.db` — SQLite, 3 entries, triggers block UPDATE/DELETE
- `codex_immutable.json` — same 3 entries + `prev_hash` + `entry_hash`
- `codex_immutable.manifest.json` — publishable fingerprint

## How immutability works here
- `entry_hash = SHA256(canonical_json(fields) + prev_hash)`, genesis `prev_hash = 0*64`
- Each row links to the previous. Editing any row breaks its hash and all later links.
- Triggers `no_update_codex` / `no_delete_codex` block casual UPDATE/DELETE.
- Triggers are *not* the guarantee — an attacker can DROP TRIGGER. The hash chain + published manifest is the guarantee: `verify_codex.py` detects the edit.

## Verified break tests (run in lab, clean build restored after)
1. Direct `UPDATE codex SET title='HACKED'` → **BLOCKED**: `IMMUTABLE: UPDATE blocked on codex`, then `VERIFIED`
2. Attacker drops triggers + edits → **DETECTED**: `TAMPERED: id=1 entry_hash mismatch`, exit 1

## Fingerprints (v2, 3 entries)
- `head_hash=6ffafbe83939cd0e186812b4aa9574a53fb2df0e3f1b5a8cded2df0d6d59a24d`
- `json_sha256=ab5435165dccdec1cb24897f4cba748a14982170316ba492893e124581fdb37c`

## Demo
```bash
python3 build_immutable.py
python3 verify_codex.py
```

## Honest limits
This is tamper-*evident*, not tamper-*proof*. True immutability needs an external anchor the attacker can't rewrite — e.g., publish the head hash in git, on a second system, or sign it. For a portfolio, tamper-evident + published fingerprint is the right claim.
