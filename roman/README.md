# A Roman Soldier Gets Transported to 2026

60-second vertical (1080×1920, 30 fps) 3D animated comedy short. Output: `roman-soldier-2026.mp4`.

Everything is generated from code. The picture is Three.js rendered frame by frame in headless Chromium, the soundtrack is synthesized with NumPy/SciPy, and FFmpeg does the encoding. No image, video, voice or sound generation models are used, and there are no samples or stock assets.

| File | What it is |
|---|---|
| `timeline.js` | Shared timing: title, dialogue lines (subtitles + lip-sync + voices), sound cues |
| `lib.js` | Character rig (body, face, brows, eyelids, lip-sync mouth, cloth cape, shield, gladius), poses, walk/run cycles |
| `envs.js` | Sets (battlefield, city street, burger restaurant, plaza, museum) and props (cars, self-driving car, scooters, portal, pigeons, bags) |
| `film.js` | Choreography, cameras and 2D overlay (title, subtitles, social-media UI) for all six scenes; `renderFrame(frame)` |
| `audio.py` | Comedic march score, ~50 synthesized sound effects, formant-synthesized "gibberish" voices → `audio.wav` |
| `render.mjs` | Renders all 1800 frames in 4 parallel browsers, encodes, muxes the audio |
| `preview.mjs`, `sheet.py` | Render chosen frames and contact sheets for review |

Rebuild:

```bash
npm install            # in the repo root, for three.js (already vendored here as three.module.js)
pip install numpy scipy
python3 audio.py
node render.mjs        # about 10 minutes on 4 CPU cores
```

## Scenes

1. **0–8 s:** a portal opens on a Roman battlefield; Marcus walks through it into a 2026 street with scooters and cars. Title: "A ROMAN SOLDIER IN 2026".
2. **8–18 s:** a selfie. The phone screen is a live render-to-texture of its front camera, so his "reflection" really moves. He challenges it to a duel.
3. **18–28 s:** he raises his shield at a self-driving car. The car brakes ("PEDESTRIAN DETECTED") and he celebrates his victory.
4. **28–40 s:** the burger kiosk. His taps push the quantity counter to 40, and 40 bags pop onto the counter.
5. **40–50 s:** he rides an e-scooter through a plaza, scatters the pigeons, and goes viral (#ScooterCaesar).
6. **50–60 s:** the museum. He points at Augustus, sees himself in a meme (rendered from the plaza scene), and declares "I HAVE BECOME IMMORTAL!"

The voices are "Sims-style" gibberish made with formant synthesis, because no text-to-speech engine was available. The English subtitles carry the dialogue.
