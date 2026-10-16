# What Happens to Your Brain When You Stop Using Your Phone — frames

132 flat, hand-drawn stick-figure frames (1920×1080 PNG, 16:9), one per script beat: `png/beat_001.png` … `png/beat_132.png`.

Drawn procedurally as SVG (no AI image model) and rendered with headless Chromium.

## Rebuild

```bash
cd src
ln -s "$(npm root -g)" node_modules   # needs the global `playwright` package
python3 build.py          # all beats  -> ../svg + ../png
python3 build.py 12 40    # only selected beats
```

- `src/lib.py` — drawing kit (stick figure with poses/faces/hair, brain, pigeon, phone, hands, props).
- `src/beats1.py`, `beats2.py`, `beats3.py` — the 132 scenes.
- Lettering font: Permanent Marker (Apache 2.0, `src/marker-LICENSE.txt`).
