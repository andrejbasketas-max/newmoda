# HEROJ U PRAVO VREME — 15s Vertical AI Short (9:16)

Photorealistic cinematic rescue short. A boy chases a football onto a wet city street as a car approaches. A man dives in and pulls him clear at the last second. It ends warmly and loops seamlessly.

- **Format:** 1080×1920, 9:16, 24 fps (export 30 fps for Shorts/Reels/TikTok)
- **Length:** 15.0 s
- **Pipeline:** stills (Midjourney v7 / Leonardo Phoenix / Flux) → image-to-video (Runway Gen-4 / Kling 2.x / Veo 3) → edit in CapCut / Premiere
- **Rating:** no gore, no blood, no impact. The car never touches anyone.

---

## 1. Character & world bible (paste into EVERY prompt)

Lock these so faces and wardrobe stay consistent. Generate one reference sheet per character first, then use it as the **character / omni reference** (MJ `--cref` + `--cw 100`, Runway/Kling "reference image", Leonardo "Character Reference") in every shot.

**BOY:** 8-year-old boy, short messy dark-brown hair, big brown eyes, light olive skin, small scar-free face. He wears an olive-khaki zip hoodie over a grey t-shirt, dark-blue jeans, worn white-and-grey sneakers, and a small dark-navy backpack.

**MAN:** a man in his late 30s with short dark tousled hair, light stubble, strong jaw and kind brown eyes. He wears a black hooded zip jacket over a dark charcoal t-shirt, dark jeans and black boots.

**CAR:** a dark-grey/black 2010s European sedan with bright LED headlights and wet reflective paint.

**PROP:** a classic black-and-white football (soccer ball), scuffed and wet.

**WORLD:** a narrow European old-town street at dusk in heavy rain. Wet cobblestone/asphalt mirrors the light. There are warm amber shop lights, cold blue ambient light and visible rain streaks, with mist and backlit raindrops.

**Reference sheet prompt (do once per character):**
```
character reference sheet, [BOY or MAN description], front view, 3/4 view, profile,
neutral expression and emotional expression, consistent face, photorealistic,
soft studio light, plain grey background, 85mm lens, ultra-detailed skin texture --ar 3:2 --style raw
```

---

## 2. Global style block (append to every image + video prompt)

```
photorealistic cinematic film still, shot on ARRI Alexa 35, anamorphic lens,
heavy rain at dusk, wet reflective street, dramatic car headlights with lens flare,
teal-and-amber color grade, volumetric mist, backlit raindrops, shallow depth of field,
film grain, ultra-detailed, 8k, realistic physics, vertical 9:16 composition,
subject framed in upper two-thirds, clean lower third for subtitles
```

**Negative prompt:**
```
gore, blood, injury, crash impact, deformed hands, extra fingers, warped face,
face morphing, changing clothes, inconsistent character, cartoon, CGI look, plastic skin,
text, watermark, logo, low resolution, flicker, jitter
```

Image params (Midjourney): `--ar 9:16 --style raw --cref <ref_url> --cw 100 --s 150`

---

## 3. Shot list (6 clips → 15.0 s)

Subtitle safe zone: keep faces and action **above y≈1300 px**. Text sits at y≈1350–1650. Keep the top 180 px and right 140 px clear of key action, because platform UI covers those areas.

### SHOT 1 — HOOK (0.0–2.0s)
**Text:** SVE JE IZGLEDALO **IZGUBLJENO…** **VO:** "Sve je izgledalo izgubljeno…"

**Image prompt:**
```
low ground-level shot on a rain-soaked city street at dusk, a black-and-white football
bounces toward camera in the foreground, BOY [desc] sprints after it into the road,
mouth open in fear, behind him a dark sedan [desc] speeds toward him with blinding
headlights, rain streaks lit by headlights, [GLOBAL STYLE]
```
**Video prompt (i2v, 2s):**
```
fast dolly-in at ground level, the football bounces past the lens with a water splash,
the boy runs toward camera chasing it, the car behind accelerates and its headlights flare
and fill the frame, realistic rain, motion blur, urgent energy
```
- **First-second hook:** the ball splash hits the lens at frame 1. Add a 2-frame white headlight flash at 0.0s.
- **SFX:** heartbeat ×2 (starts at 0.0), rain bed, ball bounce, rising engine rev.

### SHOT 2 — THE DIVE (2.0–3.6s) · slow motion
**Text:** ON JE **REAGOVAO** **VO:** "Ali onda… on je reagovao!"

**Image prompt:**
```
side tracking shot, MAN [desc] mid-air in a horizontal dive across the wet street,
arms wrapping around BOY [desc], both airborne, the football in the foreground,
the dark sedan's headlights one metre away, raindrops frozen in the air, water spraying
from the man's boots, [GLOBAL STYLE]
```
**Video prompt (i2v, 4s → speed-ramp):**
```
extreme slow motion 120fps look, camera tracks laterally with the dive, the man leaps
and catches the boy mid-run, both fly out of the car's path, raindrops hang in the air
and burst on contact, headlights sweep through the frame, realistic body physics,
no contact with the car
```
- **Edit:** play 0.4s at 100% → ramp to 25% → ramp back to 100% for the last 0.2s.
- **SFX:** tire screech, low "whoosh" + sub-drop, mute the music for 0.3s at peak, then a horn.

### SHOT 3 — LANDING / CAR PASSES (3.6–5.0s)
**Image prompt:**
```
low angle, MAN [desc] rolls on the wet pavement shielding BOY [desc] in his arms,
water spraying around them, the dark sedan skids past behind them in motion blur,
headlights streaking, [GLOBAL STYLE]
```
**Video prompt (i2v, 2s):**
```
handheld low-angle camera, the man and boy roll to a stop on the wet road, the car
skids past behind them in a blur with spray from its tires, the camera shakes slightly,
then settles
```
- **SFX:** body roll on wet ground (soft), skid, spray whoosh, car doppler fading.

### SHOT 4 — TURNING POINT (5.0–9.0s)
**Text:** PRAVI HEROJI **NE NOSE PLAŠT** **VO:** "Pravi heroji ne nose plašt…"

**Image prompt:**
```
medium close-up, MAN [desc] kneeling on the wet street holding BOY [desc] by the
shoulders, checking he is okay, the boy breathing hard and looking up in shock,
the stopped sedan's headlights glowing behind them through mist, rain on their faces,
[GLOBAL STYLE]
```
**Video prompt (i2v, 4s):**
```
slow push-in, the man helps the boy sit up and gently checks his face and arms,
the boy nods, rain falls softly, headlights behind them flicker through the mist,
emotional, calm after chaos
```
- **SFX:** music switches here from tension to emotional piano + strings. The rain gets softer and the heartbeat slows.

### SHOT 5 — EMOTION (9.0–12.0s)
**Text:** ONI **SAMO BRINU** **VO:** "…oni samo brinu."

**Image prompt:**
```
emotional two-shot close-up, BOY [desc] looks up at MAN [desc] with grateful wide
eyes, the man smiles warmly and reassuringly, raindrops on their faces and hair,
warm bokeh street lights behind them, [GLOBAL STYLE]
```
**Video prompt (i2v, 3s):**
```
slow orbit around both faces, the boy's fear melts into a small smile, the man smiles
back and ruffles the boy's wet hair, raindrops glisten, subtle rack focus from the boy
to the man
```
- Cut at 10.5s to a 0.5s insert (optional): the man's hand on the boy's shoulder.

### SHOT 6 — FINALE + LOOP (12.0–15.0s)
**Text:** PODELI AKO VERUJEŠ U **DOBROTU!** ❤️ **VO:** "Podeli ako veruješ u dobrotu!"

**Image prompt:**
```
wide shot from behind, MAN [desc] and BOY [desc] walk away hand in hand down the
wet glowing street toward a golden sunset break in the clouds, rain easing,
the boy carries the football under his arm, warm amber reflections, hopeful,
[GLOBAL STYLE]
```
**Video prompt (i2v, 3s):**
```
slow crane-up and pull-back as they walk away hand in hand, the rain lightens,
golden light breaks through, in the final second the football slips from the boy's
arm and rolls back toward the camera across the wet street
```
- **Seamless loop:** the last 0.5s is the ball rolling toward the lens at ground level. Match its size and position to the first frame of Shot 1, and cross-dissolve 4 frames into 0.0s. The rain audio bed and heartbeat should run continuously across the cut. Then end the music on a sustained note that the opening heartbeat masks.

---

## 4. Edit timeline (CapCut)

| Time | Clip | Text overlay (Montserrat ExtraBold, white + yellow #FFC531 key word, 6px black shadow) | Audio |
|---|---|---|---|
| 0.0–2.0 | S1 | SVE JE IZGLEDALO **IZGUBLJENO…** | heartbeat, rain, engine rising |
| 2.0–3.6 | S2 (slow-mo ramp) | ON JE **REAGOVAO** | screech, whoosh, music drop |
| 3.6–5.0 | S3 | — | skid, doppler |
| 5.0–9.0 | S4 | PRAVI HEROJI **NE NOSE PLAŠT** | piano + strings start |
| 9.0–12.0 | S5 | ONI **SAMO BRINU** | strings swell |
| 12.0–15.0 | S6 → loop | PODELI AKO VERUJEŠ U **DOBROTU!** ❤️ | music resolve, rain, heartbeat bridge |

- Text animation: a 6-frame pop-in (scale 110→100%) with word-by-word yellow highlight. Remove each line 4 frames before the cut.
- **Pacing:** no shot runs over 4s. Add a cut or punch-in (110% zoom) every ~1–1.5s within long shots.
- **Grade:** teal shadows and amber highlights, +10 contrast. Add a light vignette and 35mm grain at 15%. Finish shot 6 warmer (+400K).
- **Music:** cinematic emotional trailer track (royalty-free, e.g. "inspiring piano build"), with the tension section at 0–5s and the emotional section from 5s on.
- **VO:** an excited, warm male or female voice in Serbian. ElevenLabs works with stability 40 and style 60.

---

## 5. Consistency checklist

- [ ] Use the same `--cref` / reference image and seed family for all 6 stills.
- [ ] Wardrobe check per shot: boy = olive hoodie + navy backpack, man = black hooded jacket.
- [ ] Time of day and rain intensity stay consistent until shot 6, where the rain eases deliberately.
- [ ] The car is the same model and colour in shots 1–4.
- [ ] Generate 3–4 i2v variants per shot and keep the one with no face drift.
- [ ] The last frame of S6 matches the first frame of S1, so the loop works.
- [ ] No contact between the car and either character in any frame.
