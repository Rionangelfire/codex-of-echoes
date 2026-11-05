# Codex of Echoes 📖

A **tamper-evident narrative archive** — a worldbuilding and organizational framework for a multiverse story, built to be verifiable rather than merely stored.

Version 2 is **tamper-evident, not tamper-proof**: changes leave evidence. That distinction matters, and it's deliberate.

## What's here

- `codex_of_echoes.json` / `codex_of_echoes.db` — the Codex itself (JSON + SQLite)
- `codex_immutable.json` / `codex_immutable.db` / `codex_immutable.manifest.json` — the hardened v2 with manifest
- `build_codex.py` / `build_immutable.py` — build scripts
- `verify_codex.py` — verification script
- `codex_ar_viewer.html` — AR viewer
- `CODEX_Case_Study.md` — case study
- `IMMUTABLE_README.md` — notes on the immutable build

## Run it

```bash
python build_codex.py
python verify_codex.py
```

## Built by

Robert Bostick — CTU Online, B.S. Computer Science (cybersecurity focus), Hillsboro, Texas.
