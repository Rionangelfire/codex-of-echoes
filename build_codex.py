"""Build Codex of Echoes DB + JSON from the verified source JSON.

Source of truth: the uploaded codex_of_echoes JSON (3 entries).
This script is idempotent: it recreates the table and uses INSERT OR REPLACE.
"""
import json
import sqlite3
from pathlib import Path

HERE = Path(__file__).parent
SOURCE_JSON = Path("/home/hatch/workspace/user/files/codex_of_echoes.sql_2_0z9d.json")
DB_PATH = HERE / "codex_of_echoes.db"
OUT_JSON = HERE / "codex_of_echoes.json"

# Load source
with open(SOURCE_JSON) as f:
    echoes = json.load(f)

assert len(echoes) == 3, f"Expected 3 echoes, got {len(echoes)}"

# Build DB
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
cursor.execute("DROP TABLE IF EXISTS codex")
cursor.execute("""
CREATE TABLE codex (
    id INTEGER PRIMARY KEY,
    title TEXT,
    type TEXT,
    function TEXT,
    symbol TEXT,
    resonance TEXT,
    directive TEXT,
    description TEXT
)
""")
for e in echoes:
    cursor.execute(
        "INSERT OR REPLACE INTO codex (id, title, type, function, symbol, resonance, directive, description) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (e["id"], e["title"], e["type"], e["function"], e["symbol"], e["resonance"], e["directive"], e["description"]),
    )
conn.commit()

# Read back and export as a plain list (matches uploaded JSON format)
cursor.execute("SELECT id, title, type, function, symbol, resonance, directive, description FROM codex ORDER BY id")
rows = cursor.fetchall()
conn.close()

exported = [
    {
        "id": r[0],
        "title": r[1],
        "type": r[2],
        "function": r[3],
        "symbol": r[4],
        "resonance": r[5],
        "directive": r[6],
        "description": r[7],
    }
    for r in rows
]

with open(OUT_JSON, "w") as f:
    json.dump(exported, f, indent=4)

# Verify round-trip matches source exactly
with open(SOURCE_JSON) as f:
    source = json.load(f)
assert exported == source, "Round-trip mismatch between DB export and source JSON"

print(f"OK: {DB_PATH} created with {len(exported)} entries")
print(f"OK: {OUT_JSON} matches uploaded source JSON exactly")
for e in exported:
    print(f" - {e['id']}: {e['title']}")
