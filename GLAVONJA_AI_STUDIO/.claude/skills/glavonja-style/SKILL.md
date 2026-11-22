---
name: glavonja-style
description: Show or update the GLAVONJA channel style (reference frames, measured style, test scene, approval). Use for /glavonja-style.
---
- Show: `python glavonja.py style show`
- Measure from `references/frames` + `references/videos`: `python glavonja.py style learn`
- Test scene + side-by-side sheet: `python glavonja.py style test` → open `docs/style_comparison.png`
- If the user asks you to match the character: compare `references/character/*` with
  `assets/characters/character_sheet.png`, edit only `config/style.json → character`, rerun `style test`.
- `style approve` only when the USER says the comparison is approved.
