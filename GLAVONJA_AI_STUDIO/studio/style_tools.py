"""Reference library + test scene (PART 1.2 / 1.3).

* assets/characters/character_sheet.png   - poses x expressions of the style.json character
* assets/characters/expressions.png        - all facial expressions
* assets/backgrounds/library.png           - every background type
* docs/style_comparison.png                - REAL channel frames (top) vs studio test scene (bottom)
"""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

from .consistency import check_image, comparison_sheet, has_references
from .core import ASSETS_DIR, ROOT, atomic_write_json, load_style, now_iso
from .render.character import ACTIONS, EXPRESSIONS, Character, pose_for
from .render.scene import FrameRenderer, font
from .render.world import BACKGROUNDS, PROPS, background, draw_prop


def _grid_chars(items, out: Path, label):
    st = load_style()
    ch = Character(st["character"])
    cols = 6
    cw, chh = 320, 420
    rows = (len(items) + cols - 1) // cols
    SS = 2
    im = Image.new("RGBA", (cols * cw * SS, rows * chh * SS), (255, 255, 255, 255))
    d = ImageDraw.Draw(im)
    X = (lambda x, y: (x * SS, y * SS), SS)
    for i, (action, expr, t) in enumerate(items):
        cx, cy = (i % cols) * cw + cw / 2, (i // cols) * chh
        ch.draw(d, X, cx - 20, cy + chh - 60, 300, pose_for(action, t), expr, 1, 0.5 if action == "talk" else 0, t=t)
        d.text((cx * SS, (cy + chh - 30) * SS), label(action, expr), fill=(80, 80, 80, 255), anchor="mm", font=font(36))
    im = im.reduce(SS).convert("RGB")
    out.parent.mkdir(parents=True, exist_ok=True)
    im.save(out)
    return out


def build_reference_library() -> dict:
    out = {}
    out["character_sheet"] = _grid_chars([(a, "neutral" if a in ("idle", "talk", "walk") else
                                            {"run": "scared", "jump": "excited", "point": "neutral", "shock": "shocked",
                                             "think": "thinking", "cheer": "happy", "scared": "scared", "fall": "shocked",
                                             "shrug": "confused", "wave": "happy", "lie": "dead"}.get(a, "neutral"), 0.6)
                                           for a in ACTIONS], ASSETS_DIR / "characters" / "character_sheet.png",
                                          lambda a, e: a)
    out["expressions"] = _grid_chars([("idle", e, 0.0) for e in EXPRESSIONS], ASSETS_DIR / "characters" / "expressions.png",
                                     lambda a, e: e)
    st = load_style()
    cols, w, h = 5, 384, 216
    rows = (len(BACKGROUNDS) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * w, rows * h), "white")
    d = ImageDraw.Draw(sheet)
    for i, b in enumerate(BACKGROUNDS):
        sheet.paste(background(b, w, h, st), ((i % cols) * w, (i // cols) * h))
        d.text(((i % cols) * w + 8, (i // cols) * h + 6), b, fill=(255, 0, 0), font=font(22))
    sheet.save(ASSETS_DIR / "backgrounds" / "library.png")
    out["backgrounds"] = ASSETS_DIR / "backgrounds" / "library.png"
    names = sorted(PROPS)
    cols = 10
    rows = (len(names) + cols - 1) // cols
    SS = 2
    pim = Image.new("RGBA", (cols * 160 * SS, rows * 180 * SS), (245, 245, 245, 255))
    pd = ImageDraw.Draw(pim)
    for i, n in enumerate(names):
        x, y = ((i % cols) * 160 + 80) * SS, ((i // cols) * 180 + 75) * SS
        draw_prop(pd, n, x, y, 110 * SS, 6 * SS, 0.5, st)
        pd.text((x, y + 80 * SS), n, fill=(60, 60, 60, 255), anchor="mm", font=font(36))
    (ASSETS_DIR / "props").mkdir(parents=True, exist_ok=True)
    pim.reduce(SS).convert("RGB").save(ASSETS_DIR / "props" / "props_library.png")
    out["props"] = ASSETS_DIR / "props" / "props_library.png"
    return {k: str(Path(v).relative_to(ROOT)) for k, v in out.items()}


TEST_SCENES = [
    dict(background="day", duration=3, camera="slow_zoom_in", characters=[dict(action="talk", expression="happy", x=0.4, talks=True)],
         props=[dict(name="earth", x=0.72, y=0.42, size=0.28, anim="float")], caption=""),
    dict(background="night", duration=3, camera="static", effects=["vignette"],
         characters=[dict(action="scared", expression="scared", x=0.35)], props=[dict(name="ghost", x=0.72, y=0.48, size=0.3)]),
    dict(background="city", duration=3, camera="punch_in", effects=["shake"],
         characters=[dict(action="shock", expression="shocked", x=0.4)], props=[dict(name="meteor", x=0.75, y=0.25, size=0.22)],
         caption="1 SEKUNDA"),
    dict(background="desert", duration=3, camera="pan_right", effects=["speed_lines"],
         characters=[dict(action="run", expression="determined", x=0.25, to_x=0.6)], props=[]),
]


def make_test_scene() -> str:
    lib = build_reference_library()
    st = load_style()
    r = FrameRenderer(st)
    frames = []
    res = []
    for i, sc in enumerate(TEST_SCENES):
        f = ROOT / "docs" / f"test_scene_{i + 1}.png"
        f.parent.mkdir(exist_ok=True)
        img = r.render(sc, 1.1, mouth=0.5)
        img.save(f)
        frames.append(f)
        res.append({"frame": f.name, **check_image(img)})
    cmp_ = comparison_sheet(frames, ROOT / "docs" / "style_comparison.png")
    atomic_write_json(ROOT / "docs" / "test_scene_report.json", {"created": now_iso(), "has_references": has_references(),
                                                                "library": lib, "checks": res})
    return str(cmp_.relative_to(ROOT))
