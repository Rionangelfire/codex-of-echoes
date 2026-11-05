"""Build immutable Codex v2: hash-chained, append-only SQLite.

Design (best judgment for a portfolio demo):
- Keep v1 files untouched. v2 is a new DB: codex_immutable.db
- Each row stores prev_hash + entry_hash where
  entry_hash = SHA256(canonical_json(fields) + prev_hash)
  Genesis prev_hash = "0"*64
- Triggers reject UPDATE and DELETE on codex table.
  This stops casual tampering. A determined attacker can DROP TRIGGER,
  so verification (verify_codex.py) is the real guarantee: any edit
  without recomputing the whole chain breaks verification.
- Also writes codex_immutable.manifest.json with SHA256 of the
  exported JSON + head hash, so you can publish the fingerprint separately.
"""
import hashlib
import json
import sqlite3
from pathlib import Path

HERE = Path(__file__).parent
SOURCE_JSON = HERE / "codex_of_echoes.json"
DB_PATH = HERE / "codex_immutable.db"
OUT_JSON = HERE / "codex_immutable.json"
MANIFEST = HERE / "codex_immutable.manifest.json"

GENESIS = "0" * 64

def canonical(fields: dict) -> str:
    return json.dumps(fields, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

def entry_hash(fields: dict, prev_hash: str) -> str:
    payload = canonical(fields) + prev_hash
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()

def main():
    with open(SOURCE_JSON) as f:
        echoes = json.load(f)
    assert len(echoes) == 3

    if DB_PATH.exists():
        DB_PATH.unlink()

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE codex (
        id INTEGER PRIMARY KEY,
        title TEXT,
        type TEXT,
        function TEXT,
        symbol TEXT,
        resonance TEXT,
        directive TEXT,
        description TEXT,
        prev_hash TEXT NOT NULL,
        entry_hash TEXT NOT NULL
    )
    """)
    # Append-only guardrails
    cur.execute("""
    CREATE TRIGGER no_update_codex BEFORE UPDATE ON codex
    BEGIN SELECT RAISE(ABORT, 'IMMUTABLE: UPDATE blocked on codex'); END
    """)
    cur.execute("""
    CREATE TRIGGER no_delete_codex BEFORE DELETE ON codex
    BEGIN SELECT RAISE(ABORT, 'IMMUTABLE: DELETE blocked on codex'); END
    """)

    prev = GENESIS
    exported = []
    for e in sorted(echoes, key=lambda x: x["id"]):
        fields = {k: e[k] for k in ["id", "title", "type", "function", "symbol", "resonance", "directive", "description"]}
        h = entry_hash(fields, prev)
        cur.execute(
            "INSERT INTO codex (id, title, type, function, symbol, resonance, directive, description, prev_hash, entry_hash) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (e["id"], e["title"], e["type"], e["function"], e["symbol"], e["resonance"], e["directive"], e["description"], prev, h),
        )
        exported.append({**fields, "prev_hash": prev, "entry_hash": h})
        prev = h

    conn.commit()
    conn.close()

    with open(OUT_JSON, "w") as f:
        json.dump(exported, f, indent=4)

    json_bytes = Path(OUT_JSON).read_bytes()
    manifest = {
        "entries": len(exported),
        "head_hash": exported[-1]["entry_hash"],
        "genesis_prev_hash": GENESIS,
        "json_sha256": hashlib.sha256(json_bytes).hexdigest(),
        "note": "Verify with: python3 verify_codex.py. Publish json_sha256 + head_hash separately.",
    }
    with open(MANIFEST, "w") as f:
        json.dump(manifest, f, indent=4)

    print(f"OK: {DB_PATH} — {len(exported)} hash-chained entries")
    print(f"OK: head_hash={manifest['head_hash']}")
    print(f"OK: json_sha256={manifest['json_sha256']}")

if __name__ == "__main__":
    main()
