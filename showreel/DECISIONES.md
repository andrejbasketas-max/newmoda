# DECISIONES — CLAUDE / Motion Reel 26

*(Written in English at the requester's follow-up request; the file keeps the name from the brief.)*

**Deliverable:** `showreel.mp4`: 1920×1080, 60 fps, 900 frames, exactly 15.000 s, H.264 High (yuv420p, CRF 14) with 320 kb/s AAC stereo audio, about 34 MB.
**Made with:** Canvas 2D in headless Chromium for the images, NumPy for the music, and FFmpeg to encode. No image, video or audio generation models, and no samples. Every pixel and every sample comes from code in this folder.

| File | What it is |
|---|---|
| `reel.js` + `reel.html` | The whole film as one function of time, `renderFrame(frame)` |
| `music.py` | Synthesizer and arrangement → `music.wav` |
| `render.mjs` | Renders the frames in 3 parallel browsers, encodes the segments, joins them and adds the audio |
| `preview.mjs` | Renders individual frames for review |

To rebuild: `python3 music.py && node render.mjs` (needs Playwright and FFmpeg).

---

## 1. The core decision: music sets the edit

Before drawing anything I fixed the tempo at **128 BPM**. At that tempo one 4/4 bar lasts exactly **1.875 s**, so **8 bars = 15.000 s**. The structure follows from that:

| Bar | Time | Scene | What it shows off | Music |
|---|---|---|---|---|
| 0 | 0.00 | Intro | Restraint: a dot turns into a line, then typing, then a coral iris | Filtered pad opening, riser, one click per typed letter |
| 1 | 1.88 | Kinetic type | Per-letter slot-machine roll on each beat, outlined marquee | Drop: kick, clap, off-beat bass |
| 2 | 3.75 | Shape morph | Circle → square → triangle → star with echoes, elastic easing | Rising blips, one per morph |
| 3 | 5.63 | Particles | 2,600 particles swirl, then gather into the word **CODE** and explode | Whoosh into the word, then a "pop" |
| 4 | 7.50 | 3D | Cubes in real perspective with backface culling and Lambert shading, snapping 90° in a wave | 16th hats and arpeggio come in |
| 5 | 9.38 | Liquid | Metaballs computed per pixel, with volume shading and a specular highlight | Same groove |
| 6 | 11.25 | Montage | 4 cuts in 4 beats: halftone, radial burst, frame counter, 32nd-note words | Zaps, a snare roll matched to the words, riser |
| 7 | 13.13 | End card | CLAUDE. / MOTION DESIGNER, and the intro dot comes back | Big impact, sub boom, chord, reverb tail |

Every visual hit has a matching sound, and every sound has a matching visual. The JS and Python share the same constants (BPM, typing times, morph times), so sync is exact by construction rather than nudged by hand.

## 2. Visual decisions

- **Palette of 5 tokens:** ink `#0B0B10`, cream `#F2ECE1`, coral `#FF4B1F`, cobalt `#2438F5`, yellow `#FFD12A`. Each scene has its own dominant background (black, coral, black, cream, cobalt, black, mixed). That variety reads as range, and the colours stay family.
- **Typography:** Inter Display Black for impact, Inter Display ExtraLight Italic as counterpoint (the "kinetic type, on the beat" caption and "liquid"), and DejaVu Sans Mono for the technical layer. These fonts were already installed locally, so nothing was downloaded.
- **HUD as a designer's signature:** crop marks, a real timecode (SS:FF at 60 fps), scene name, bar indicator and a tempo pulse. It is drawn with `difference` blending, so it inverts by itself on any background. It goes on *after* motion blur so it stays sharp.
- **Real motion blur:** each frame is the average of 6 sub-frames with a 180° shutter, accumulated on a canvas. It is the detail that most separates "animated web page" from "motion graphics".
- **Easing as language:** `outExpo` for entrances, `inExpo` for exits, `outBack` and `outElastic` only where play is wanted (the shape, the dot), and `inOutExpo` for wipes.
- **Bookend:** the dot the film opens with comes back as the full stop of "CLAUDE." and shrinks away on the last frame.
- **Finish:** vignette, 6 cycling grain textures at 4.5% in overlay, small camera shake on strong hits, a 4-frame white flash on the impact, and a fade to black over the last 7 frames.
- **Meta-detail:** in the montage the counter shows the *actual frame number being rendered* ("0742 / FRAME / 900"), along with "0 IMAGES · 0 SAMPLES · 100% CODE".

## 3. Audio decisions

- **Key and harmony:** A minor. Am – Am – F – C – G – Am – F→**E** (a major dominant for tension) → Am(add9) on the end card.
- **Synthesis:** additive band-limited saws and squares, so there is no aliasing. Pad: 3 voices per note detuned ±9 cents. Kick: a sine with a pitch envelope from 164→44 Hz plus a click. Clap: band-passed noise with 3 bursts. Hats: high-passed noise. Bass: off-beat 8ths with a sub layer. Arpeggio: 16th-note square plucks with ping-pong delay.
- **Time-varying filter:** I wrote a resonant low-pass using STFT with overlap-add. It drives the intro pad opening, the risers and the whooshes.
- **Sidechain:** the pad ducks with every kick, which gives the "pump" you can also see in the visual pulses.
- **Reverb:** stereo convolution with a 2.4 s impulse response of decaying filtered noise.
- **Master:** soft `tanh` saturation and peak normalization. Result: **-11.6 LUFS integrated, -0.8 dBFS true peak**, measured with `ebur128`.

## 4. What I discarded and why

- **WebGL/shaders:** headless Chromium renders them in software (SwiftShader), with no real speed gain, and Canvas 2D is deterministic and easier to check. The metaballs are computed per pixel in JS at 640×360 and scaled up smoothly; the liquid look forgives that softness.
- **Python + Cairo/Skia:** they aren't installed, and the browser already gives antialiasing, text and compositing modes.
- **A fixed cell per letter in the kinetic type (v1):** the slot effect was simpler, but "I" left visible holes ("MOT I ON"). Replaced with real glyph advances, so the roll happens per letter at its true position.
- **Video transitions ("crossfades"):** discarded in favour of transitions that belong to the scenes themselves (iris, bars, shape filling the screen, particle curtain) and hard cuts on the beat.
- **Text at the start:** the intro opens on a lone dot. Putting the name at 0 s killed the reveal at the end.
- **Samples or a drum kit:** forbidden by the brief and unnecessary. Everything is oscillators and noise.
- **A longer arrangement:** 15 s doesn't allow a verse and chorus. I chose intro + drop + build + impact, the classic showreel shape.

## 5. Iterations

1. **v1 visuals:** all 8 scenes were written at once and checked with a contact sheet of 16 frames.
   - Problems found: holes in the kinetic type, particles that formed "CODE" for only ~0.01 s (no time to read it), and cubes in a dull greyish-lavender.
2. **v2 visuals:**
   - Kinetic type moved to real glyph widths.
   - Particle convergence moved earlier (0.54–1.25 s within the scene), giving about 0.3 s of readable word before the explosion.
   - Cube shading got brighter, with more contrast.
   - Comments moved to English after the follow-up request.
3. **v1 audio:** a bug where a negative time inside the filter made a complex power. Fixed by clamping time to 0.
4. **v2 audio:** measured at **-2.9 LUFS**, absurdly loud. Measuring each stem showed the cause: the reverb impulse wasn't normalized (wet peak 6.0). I normalized the impulse to unit energy and softened the saturation, which brought the mix to -11.6 LUFS.
   - Checked on a spectrogram: intro, drop at 1.875 s, snare roll at 12.7 s, impact at 13.125 s.
5. **Final render:** 900 frames × 6 sub-frames over 3 parallel workers in **137 s**.
   - Verified with `ffprobe`: 1920×1080, 60/1, 900 frames, 15.000 s, plus a full decode with no errors.
   - Checked with a 60-frame contact sheet (4 per second).

## 6. Total time

About **12 minutes** of wall-clock time from the first command (00:47 UTC) to the verified video (00:59 UTC). That includes writing the code (~3 min of visuals and ~1 min of audio as text), two visual iterations, two audio iterations, and the final render (137 s).
