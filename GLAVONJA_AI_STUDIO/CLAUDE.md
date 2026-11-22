# CLAUDE.md – GLAVONJA AI STUDIO (instructions for Claude Code)

Claude Code is only the DEVELOPMENT tool for this project. Everyday production runs without Claude
(`start.bat` → dashboard). Keep Claude usage minimal: never do with Claude what the Python code does.

## Run things
- Python: `.venv\Scripts\python.exe` on Windows (`python3` elsewhere). Entry point: `glavonja.py`.
- Tests: `python -m pytest tests -q` (pipeline test runs in an isolated temp copy; `GLAVONJA_TEST_FULLHD=1` for 1080p).
- Self-test: `python glavonja.py selftest`.

## Architecture (read only what you need)
- `studio/core.py` paths, settings (defaults + `config/settings.json`), SQLite, `Project` state/resume.
- `studio/production.py` the 10 stages, `Blocked` (waiting for the user), editor, QC, export gate.
- `studio/agents/` researcher, scriptwriter, visual_director, thumbnails, seo (real modules).
- `studio/google_ai.py` Gemini TTS, Flow bridge, estimates, approvals, asset_license.json.
- `studio/consistency.py` reference signatures, calibrated style check, `style learn`.
- `studio/render/` procedural character/props/backgrounds/scenes (fallback animation + previews).
- `studio/audio.py` local fallback TTS (piper/espeak/sapi), music + SFX synthesis, mixing.
- `studio/dashboard.py` + `dashboard/index.html` local UI (stdlib HTTP server).

## Non-negotiable rules (from the channel owner)
1. Visual identity of the GLAVONJA channel comes first. Never invent channel details; use `references/`.
2. Google Flow (animation) and Gemini TTS (voice) are mandatory. Local fallbacks only after the user
   explicitly approves them; never skip silently; always show a credit estimate and ask before Google use.
3. NEVER approve on the user's behalf (`glavonja approve ...` is the user's decision), never upload to YouTube.
4. Zero budget: no paid APIs by default. Never put API keys in logs, commits or code.
5. Never delete user projects, outputs, references or the database. `update.bat` must stay safe.
6. Do not claim something works unless it was tested; Windows `.bat` files must stay ASCII + CRLF.

## Typical Claude tasks (cheap)
- "Adjust config/style.json so the fallback character matches references/character" → edit JSON, run `glavonja.py style test`.
- "Write the script for project X" → write `projects/X/script/script.txt` (# Section + one sentence per line),
  then `glavonja.py script-edit X projects/X/script/script.txt`. (Uses Claude – only when the user asks.)
