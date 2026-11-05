"""Verify immutable Codex v2.

Checks:
1. DB rows exist, ordered by id, prev_hash links form a chain from genesis.
2. Each entry_hash == SHA256(canonical(fields) + prev_hash).
3. JSON export matches DB exactly (if JSON file present).
4. Manifest head_hash + json_sha256 match recomputed values.

Exit 0 = VERIFIED. Exit 1 = TAMPERED, with reason printed.
"""
import hashlib
import json
import sqlite3
import sys
from pathlib import Path

HERE = Path(__file__).parent
DB_PATH = HERE / "codex_immutable.db"
JSON_PATH = HERE / "codex_immutable.json"
MANIFEST_PATH = HERE / "codex_immutable.manifest.json"
GENESIS = "0" * 64

def canonical(fields: dict) -> str:
    return json.dumps(fields, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

def entry_hash(fields: dict, prev_hash: str) -> str:
    return hashlib.sha256((canonical(fields) + prev_hash).encode("utf-8")).hexdigest()

def fail(msg: str):
    print(f"TAMPERED: {msg}")
    sys.exit(1)

def main():
    if not DB_PATH.exists():
        fail(f"missing DB {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    # Check triggers exist (defense-in-depth, not the sole guarantee)
    triggers = {r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='trigger' AND tbl_name='codex'")}
    if "no_update_codex" not in triggers or "no_delete_codex" not in triggers:
        print("WARNING: append-only triggers missing — hash chain still checked below")

    rows = list(cur.execute(
        "SELECT id, title, type, function, symbol, resonance, directive, description, prev_hash, entry_hash FROM codex ORDER BY id"
    ))
    conn.close()
    if not rows:
        fail("no rows in codex")

    prev = GENESIS
    rebuilt = []
    for r in rows:
        fields = {"id": r[0], "title": r[1], "type": r[2], "function": r[3], "symbol": r[4], "resonance": r[5], "directive": r[6], "description": r[7]}
        stored_prev, stored_hash = r[8], r[9]
        if stored_prev != prev:
            fail(f"id={r[0]} prev_hash link broken (expected {prev[:12]}..., got {stored_prev[:12]}...)")
        expected = entry_hash(fields, prev)
        if expected != stored_hash:
            fail(f"id={r[0]} entry_hash mismatch — content was changed without recomputing chain")
        rebuilt.append({**fields, "prev_hash": stored_prev, "entry_hash": stored_hash})
        prev = stored_hash

    if JSON_PATH.exists():
        with open(JSON_PATH) as f:
            j = json.load(f)
        if j != rebuilt:
            fail("codex_immutable.json does not match DB")
        json_sha = hashlib.sha256(JSON_PATH.read_bytes()).hexdigest()
    else:
        json_sha = None

    if MANIFEST_PATH.exists():
        with open(MANIFEST_PATH) as f:
            m = json.load(f)
        if m.get("head_hash") != prev:
            fail("manifest head_hash does not match recomputed head")
        if json_sha and m.get("json_sha256") != json_sha:
            fail("manifest json_sha256 does not match current JSON file")

    print(f"VERIFIED: {len(rows)} entries, hash chain intact")
    print(f"head_hash={prev}")
    if json_sha:
        print(f"json_sha256={json_sha}")
    print("Triggers present:" , sorted(triggers) if triggers else "none")

if __name__ == "__main__":
    main()
