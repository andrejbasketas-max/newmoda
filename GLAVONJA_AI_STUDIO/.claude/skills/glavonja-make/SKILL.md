---
name: glavonja-make
description: Start production of a chosen GLAVONJA idea (by idea id) or a free topic. Use for /glavonja-make.
---
`python glavonja.py make <idea_id or "topic text"> [--duration SECONDS] [--lang sr|en]`

Production stops whenever the user must decide (Gemini approval/key, voice lock, Google Flow clips,
fallback approval). Report the waiting reason and the options exactly as printed.
NEVER run `glavonja.py approve` yourself – approvals belong to the user. Never upload anything.
