"""AGENT 7 - THUMBNAIL DESIGNER: 3 real 1280x720 thumbnails per video.

A: hero shot      - frame from the most dramatic Google Flow clip (channel look) + big text
B: reaction       - GLAVONJA (style.json character) shocked + topic object + arrow + red circle
C: versus/split   - two halves (before / after, or me / the danger) with a contrasting colour bar
Text is max 4 words, outlined, readable at small size; every thumbnail gets a 168x94 readability preview.
"""
from __future__ import annotations

import math

from PIL import Image, ImageDraw, ImageFilter

from ..core import Project, ROOT, atomic_write_json, load_style, read_json
from ..render.character import Character, hex2rgb, pose_for
from ..render.scene import font
from ..render.world import background, draw_prop

W, H = 1280, 720


def _text_block(img, text, box, color, outline, ow, highlight=None):
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = box
    words = text.split()
    size = int((y1 - y0) * 0.55)
    while size > 30:
        f = font(size)
        lines, cur = [], ""
        for w in words:
            t = (cur + " " + w).strip()
            if d.textlength(t, font=f) <= (x1 - x0) or not cur:
                cur = t
            else:
                lines.append(cur)
                cur = w
        lines.append(cur)
        if len(lines) * size * 1.08 <= (y1 - y0) and all(d.textlength(l, font=f) <= x1 - x0 for l in lines):
            break
        size -= 6
    y = y0 + ((y1 - y0) - len(lines) * size * 1.08) / 2
    for i, l in enumerate(lines):
        col = highlight if (highlight and i == len(lines) - 1 and len(lines) > 1) else color
        d.text(((x0 + x1) / 2, y + size * 0.54), l, font=font(size), fill=col, anchor="mm", stroke_width=ow, stroke_fill=outline)
        y += size * 1.08


def _arrow(d, x0, y0, x1, y1, col, w):
    d.line([x0, y0, x1, y1], fill=col, width=w)
    a = math.atan2(y1 - y0, x1 - x0)
    L = w * 2.6
    d.polygon([(x1 + math.cos(a) * L * 0.6, y1 + math.sin(a) * L * 0.6),
               (x1 + math.cos(a + 2.4) * L, y1 + math.sin(a + 2.4) * L),
               (x1 + math.cos(a - 2.4) * L, y1 + math.sin(a - 2.4) * L)], fill=col)


def _character(img, style, x, ground, h, action, expr, facing=1):
    SS = 2
    layer = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    Character(style["character"]).draw(d, (lambda a, b: (a * SS, b * SS), SS), x, ground, h, pose_for(action, 0.6), expr,
                                       facing, 0.6 if expr in ("shocked", "scared") else 0, t=2.0,
                                       rim=("#FFFFFF", 255))
    img.alpha_composite(layer.reduce(SS))


def _prop(img, name, x, y, size, style):
    SS = 2
    layer = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
    draw_prop(ImageDraw.Draw(layer), name, x * SS, y * SS, size * SS, 12 * SS, 0.5, style)
    img.alpha_composite(layer.reduce(SS))


def _hero_scene(p: Project, sb: dict) -> dict:
    order = {"shock": 5, "fall": 4, "scared": 4, "run": 3, "cheer": 2}
    return max(sb["scenes"], key=lambda s: (order.get(s["characters"][0]["action"], 0), len(s["props"])))


def _clip_frame(p: Project, scene: dict):
    clips = read_json(p.path("animations", "clips.json"), {"clips": {}})["clips"]
    rec = clips.get(str(scene["id"]))
    f = p.path("animations", f"scene_{scene['id']:03d}.mp4")
    if not f.exists():
        return None, None
    from ..production import _frame_at
    im = _frame_at(f, scene["duration"] * 0.6).resize((W, H))
    return im, (rec or {}).get("source")


def make_thumbnails(p: Project, log=print) -> list[dict]:
    style = load_style()
    ts = style["thumbnail"]
    sb = read_json(p.path("storyboard", "storyboard.json"))
    meta = read_json(p.path("final", "metadata.json"), {})
    text = (meta.get("thumbnail_text") or _short_text(p.state["idea"].get("title", p.state["title"]))).upper()
    hero = _hero_scene(p, sb)
    prop = (hero["props"][0]["name"] if hero["props"] else next((s["props"][0]["name"] for s in sb["scenes"] if s["props"]), "question"))
    tc, oc, hc = hex2rgb(ts["text_color"]), hex2rgb(ts["text_outline"]), hex2rgb(ts["highlight_color"])
    out = []

    # ---- A: hero frame (Flow clip frame when available)
    frame, src = _clip_frame(p, hero)
    # a real Google Flow frame = channel look; otherwise build it cleanly from the style (no doubled characters)
    a = (frame if src == "google_flow" else background(hero["background"], W, H, style)).convert("RGBA")
    a = Image.blend(a, Image.new("RGBA", (W, H), (0, 0, 0, 255)), 0.18)
    if src != "google_flow":
        _character(a, style, W * 0.3, H * 0.95, H * 0.95, hero["characters"][0]["action"], "shocked")
        _prop(a, prop, W * 0.74, H * 0.5, H * 0.42, style)
    _text_block(a, text, (W * 0.04, H * 0.03, W * 0.96, H * 0.33), tc, oc, ts["text_outline_px"], hc)
    out.append(("A", "Hero frame" + (" (Google Flow)" if src == "google_flow" else ""), a))

    # ---- B: reaction + arrow + red circle
    b = Image.new("RGBA", (W, H))
    g = Image.new("RGBA", (W, H), hex2rgb(style["palette"].get("accent2", "#FFC107")))
    m = Image.new("L", (W, H), 0)
    ImageDraw.Draw(m).ellipse([-W * 0.2, -H * 0.4, W * 0.9, H * 1.3], fill=255)
    b.paste(Image.new("RGBA", (W, H), hex2rgb(style["palette"].get("accent", "#E53935"))), (0, 0))
    b.paste(g, (0, 0), m.filter(ImageFilter.GaussianBlur(120)))
    _character(b, style, W * 0.27, H * 1.02, H * 1.05, "shock", "shocked")
    _prop(b, prop, W * 0.72, H * 0.58, H * 0.4, style)
    d = ImageDraw.Draw(b)
    d.ellipse([W * 0.72 - H * 0.28, H * 0.58 - H * 0.28, W * 0.72 + H * 0.28, H * 0.58 + H * 0.28],
              outline=(230, 20, 20, 255), width=14)
    if ts.get("arrow", True):
        _arrow(d, W * 0.48, H * 0.86, W * 0.6, H * 0.7, (230, 20, 20, 255), 22)
    _text_block(b, " ".join(text.split()[:3]), (W * 0.42, H * 0.02, W * 0.98, H * 0.3), tc, oc, ts["text_outline_px"], hc)
    out.append(("B", "Reaction + arrow", b))

    # ---- C: split / versus
    c = Image.new("RGBA", (W, H))
    left = background(sb["scenes"][0]["background"], W, H, style).convert("RGBA")
    right = background(hero["background"] if hero["background"] != sb["scenes"][0]["background"] else "red_alert", W, H, style).convert("RGBA")
    c.paste(left.crop((0, 0, W // 2, H)), (0, 0))
    c.paste(right.crop((W // 2, 0, W, H)), (W // 2, 0))
    d = ImageDraw.Draw(c)
    d.polygon([(W * 0.47, 0), (W * 0.53, 0), (W * 0.51, H), (W * 0.45, H)], fill=(255, 255, 255, 255))
    _character(c, style, W * 0.25, H * 0.98, H * 0.8, "idle", "happy")
    _character(c, style, W * 0.75, H * 0.98, H * 0.8, "scared", "scared", -1)
    _prop(c, prop, W * 0.88, H * 0.42, H * 0.25, style)
    _text_block(c, text, (W * 0.1, H * 0.02, W * 0.9, H * 0.26), tc, oc, ts["text_outline_px"], hc)
    out.append(("C", "Before / after split", c))

    res = []
    for k, desc, im in out:
        f = p.path("thumbnails", f"thumb_{k}.png")
        im.convert("RGB").save(f, optimize=True)
        im.convert("RGB").resize((168, 94), Image.LANCZOS).save(p.path("thumbnails", f"thumb_{k}_small.png"))
        res.append({"id": k, "concept": desc, "file": f.relative_to(ROOT).as_posix(), "size": "1280x720"})
    atomic_write_json(p.path("thumbnails", "thumbnails.json"), {"text": text, "thumbnails": res,
                                                                "recommended": "A" if src == "google_flow" else "B"})
    log(f"  3 thumbnails created (text: {text})")
    return res


def _short_text(title: str) -> str:
    stop = {"the", "a", "an", "of", "to", "in", "on", "for", "and", "if", "you", "your", "what", "how", "da", "li", "je",
            "se", "i", "u", "na", "šta", "ako", "kako", "bi", "sa", "za", "od"}
    words = [w.strip("?!.,:;\"'") for w in title.split()]
    key = [w for w in words if w.lower() not in stop]
    return " ".join((key or words)[:3])
