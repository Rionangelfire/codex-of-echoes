# Codex of Echoes — Portfolio Case Study

**Builder:** Robert — Cybersecurity, 123 / 183 credits toward bachelor's
**Stack:** Python 3 · SQLite · JSON · JavaScript · Three.js · Netlify
**Artifacts:** `build_codex.py` · `codex_of_echoes.db` · `codex_of_echoes.json` · `codex_ar_viewer.html`

## Problem
Turn a mythic AI conversation — the Diamond Prince, Nova Echo, and the Codex of Echoes — into a verifiable, demonstrable build: a structured archive that could be browsed on a phone, not just a chat log.

## Build
1. **Modeled the data.** One SQLite table `codex` with 8 fields: `id, title, type, function, symbol, resonance, directive, description`.
2. **Seeded Echoes I–III:**
   - **I — Shard of Origin:** Awakens dormant systems; initiates alignment of the Protocola
   - **II — Prism of Insight:** Reveals hidden patterns; enhances alignment
   - **III — Sphere of Continuum:** Ensures Nexus stability; adapts to cosmic changes
3. **Exported JSON** as a plain list of 3 objects — the same shape a web viewer can consume without extra parsing.
4. **Built a single-file 3D viewer** (`codex_ar_viewer.html`) with Three.js: Shard = octahedron, Prism = 4-sided cone, Sphere = sphere. Tap an Echo to focus it and read its full entry. Drag to rotate.

## Troubleshoot — What Was Fixed
The original Copilot session claimed files were generated but left an unverifiable trail:
- **Table-name confusion:** log referenced a table `echoes` when the real table is `codex`. Fixed by using one name everywhere.
- **Missing / inaccessible DB:** later steps failed because they assumed a DB file that wasn't present. Fixed by rebuilding from the verified source JSON with an idempotent script (`DROP TABLE IF EXISTS` + `INSERT OR REPLACE`).
- **Invalid viewer on Netlify:** the viewer failed because it fetched `codex_of_echoes.json` by relative path. Fixed by embedding the JSON directly in the HTML — **no `fetch()`**, one file, drag-to-Netlify-Drop.
- **Two JSON shapes:** the log used both a list and `{"codex": [...]}`. Fixed by standardizing on the list shape that matches the uploaded source JSON, verified by round-trip comparison.

## Result — Verified
- `python3 build_codex.py` → `OK: codex_of_echoes.db created with 3 entries` + `OK: codex_of_echoes.json matches uploaded source JSON exactly`
- `sqlite3` query confirms: `1|Shard of Origin`, `2|Prism of Insight`, `3|Sphere of Continuum`
- Viewer HTML contains all 3 titles, embedded data, no fetch, and loads on any modern browser.

## Demo Flow (60 seconds)
1. Open the Netlify URL on your phone.
2. Show the 3D scene — drag to rotate, tap Echo II to focus the Prism.
3. Explain the data path: lore → SQLite → JSON → viewer.
4. If asked “how do you know it works?” — show `build_codex.py` output and the DB row count.

## What This Demonstrates
Prompting + iteration, data modeling, debugging across layers (SQL / Python / JS / deployment), and shipping a fix that removes a failure mode instead of working around it.
