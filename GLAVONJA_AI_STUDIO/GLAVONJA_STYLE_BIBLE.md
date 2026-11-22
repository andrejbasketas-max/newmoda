# GLAVONJA STYLE BIBLE

> **Status: PROVISIONAL – the real channel has not been analysed yet.**
> During development the channel https://www.youtube.com/@Theglavonja could not be opened
> (YouTube was blocked from the build environment and the vidIQ connector had no credits).
> Nothing in this document describes the real channel from observation. The rules below are the
> **production rules** the studio enforces. The **visual values** come from `config/style.json`.
> Those values become real once you add channel frames and run *Style → Measure style*
> (`glavonja style learn`), then approve them (`glavonja style approve`).

## 0. What we know for sure (from the channel owner)

- Channel: **GLAVONJA** – 2D stickman videos.
- Animation is produced with **Google Flow**; narration with **Gemini TTS**. This stays the
  standard production method for every video (PART 3.1.1).

Everything else (exact character design, colours, line weight, backgrounds, editing rhythm,
typography, thumbnail layout) must be **measured from your real frames**. It is not guessed.

## 1. Reference library (the single source of truth)

| Folder | What goes there | Used for |
|---|---|---|
| `references/frames/` | 10–20 screenshots of real videos (different scenes: day, night, close-ups, wide shots) | colour / line / brightness signature, consistency check, Flow prompts |
| `references/videos/` | 1–2 of **your own** videos (mp4) | a frame is extracted every 4 s automatically |
| `references/character/` | clean crops of the GLAVONJA character (front, side, expressions) | attached to every Google Flow request as the character reference |
| `assets/characters/character_sheet.png` | studio-generated poses of the fallback character | fallback animation + storyboard previews |
| `assets/characters/expressions.png` | all facial expressions | same |
| `assets/backgrounds/library.png` | all procedural backgrounds | same |
| `assets/props/props_library.png` | 57 vector props | same |
| `docs/style_comparison.png` | **real channel frames (top) vs studio test scene (bottom)** | your visual approval |

## 2. Character rules (never broken)

1. There is exactly **one** GLAVONJA character. In Flow prompts he is always described as the same
   character and the `references/character/` images are attached. In fallback animation he is drawn
   from `config/style.json → character` and nothing else.
2. Never change his head size, line thickness, face design, clothing or colours between scenes or videos.
3. Secondary characters (`friend`, `villain`, `expert`) differ **only** by an accessory (cap, glasses).
4. Expressions come from the fixed set: neutral, happy, excited, shocked, scared, angry, sad, thinking,
   smirk, dead, determined, confused.
5. Poses come from the fixed set: idle, talk, walk, run, jump, point, shock, think, cheer, scared,
   fall, shrug, wave, lie, sit, facepalm, push, climb, swim.

## 3. Visual values (from `config/style.json`, filled by measurement)

| Property | Current value | Source |
|---|---|---|
| Outline thickness (px @1080p) | `character.line_width_px` | measured median dark-line run length after `style learn` |
| Background default | `palette.background_default` | most frequent light colour in references |
| Accent colours | `palette.accent / accent2 / accent3` | most saturated frequent colours in references |
| Head/body proportion | `character.head_ratio` | **set by eye** in the comparison sheet (cannot be measured automatically) |
| Subtitles | `subtitles.*` | adjust to match the channel's subtitle look |
| Thumbnail text | `thumbnail.*` | adjust after comparing with your thumbnails |

The measured numbers are written to `style.json → measured_from_references` (date, frame count, dominant
colours, accent candidates, median line thickness, mean brightness/saturation).

## 4. Scene & editing rules

- One shot = up to **8 s** (one Flow clip) and covers 1–3 narration sentences. Every visual must show
  what the narration says at that moment (VISUAL DIRECTOR maps every sentence; no random images).
- GLAVONJA is in almost every shot. His screen position stays consistent between consecutive shots.
- Transitions: mostly hard cuts; a whip/whoosh only at section changes; never the same effect three
  times in a row.
- Camera: slow zoom-in / zoom-out / pans; a punch-in + shake only on shocking moments.
- Numbers in the narration (e.g. "1600 km/h") appear as a big yellow caption.
- Subtitles: max 6 words per cue, synchronised to the narration timing, white with black outline.
- Music is ducked under the voice (sidechain). Sound effects: whoosh on transitions, pop on objects,
  boom on shocks.

## 5. Thumbnails

- 1280×720, max 4 words, thick outline, one clear focal point, readable at 168×94 (a small preview is
  saved next to every thumbnail).
- Concept A uses a real frame from the most dramatic **Google Flow** shot (closest to the channel look).
  B is a reaction plus arrow. C is a split / versus layout.
- Put your best existing thumbnails into `references/frames/` too, so the palette check learns them.

## 6. Consistency gate (PART 3.1.2 – mandatory)

1. Every imported Flow clip is sampled at 3 points and compared with the closest reference frame
   (palette, brightness, saturation, edge density, line thickness). Clips that fail are moved to
   `flow/rejected/` and **must be regenerated in Flow**. A new request is written automatically.
2. The threshold is **auto-calibrated** from how much your own reference frames differ from each other.
   There is also a hard palette limit.
3. Before export every final shot is checked again. A video is exported to `outputs/` **only if**:
   all shots pass, all shots come from Google Flow, the narration is Gemini TTS, and you approved the style.
   Otherwise it stays in the project's `final/` folder as a **draft**, and the report says why.

## 7. Voice

- One Gemini TTS voice, chosen once in *Voice → audition* and **locked**. It is used for every video.
- If Gemini is unavailable or the quota is used up, production stops and asks. A local voice (Piper / espeak-ng)
  is used only after you explicitly approve it for that video, and the report says so.

## 8. How to finish this Style Bible (5 minutes)

1. Dashboard → 🎨 Style → upload 10–20 screenshots (+ 1–2 own videos) and character crops.
2. Click **Measure style**, then **Test scene + comparison**. Look at `docs/style_comparison.png`.
3. If the fallback character differs (head size, eyes, clothing), change `config/style.json → character`
   (or ask Claude Code once: *"adjust style.json to match references/character"*), then repeat step 2.
4. Click **Approve visual identity**.
