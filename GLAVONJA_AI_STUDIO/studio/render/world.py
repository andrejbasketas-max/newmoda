"""Vector props + procedural backgrounds in the same flat, thick-outline style as the character.

Backgrounds are rendered once per (type, size, style) and cached as PNG in assets/backgrounds.
Props are drawn per frame (they animate) on the supersampled foreground layer.
"""
from __future__ import annotations

import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

from ..core import ASSETS_DIR, sha
from .character import hex2rgb

INK = (17, 17, 17, 255)
WHITE = (255, 255, 255, 255)


def C(h, a=255):
    return hex2rgb(h, a)


# =========================================================================== props
def _poly(d, pts, fill, lw):
    d.polygon(pts, fill=fill)
    d.line(pts + [pts[0]], fill=INK, width=lw, joint="curve")


def _circle(d, x, y, r, fill, lw):
    d.ellipse([x - r, y - r, x + r, y + r], fill=fill, outline=INK, width=lw)


def draw_prop(d: ImageDraw.ImageDraw, name: str, x: float, y: float, size: float, lw: int,
              t: float = 0.0, style: dict | None = None):
    """Draw prop centred at canvas coords (x, y) with height ~= size."""
    s = size / 2
    pal = (style or {}).get("palette", {})
    acc = C(pal.get("accent", "#E53935"))
    acc2 = C(pal.get("accent2", "#FFC107"))
    acc3 = C(pal.get("accent3", "#1E88E5"))
    fn = PROPS.get(name)
    if fn is None:
        fn = PROPS["question"]
    fn(d, x, y, s, lw, t, acc, acc2, acc3)


def _earth(d, x, y, s, lw, t, *_):
    _circle(d, x, y, s, C("#2E86DE"), lw)
    for dx, dy, r in ((-0.35, -0.3, 0.35), (0.3, 0.2, 0.4), (0.1, -0.55, 0.2), (-0.4, 0.45, 0.22)):
        rr = r * s
        cx = x + dx * s
        d.ellipse([cx - rr, y + dy * s - rr * 0.7, cx + rr, y + dy * s + rr * 0.7], fill=C("#43A047"))
    d.ellipse([x - s, y - s, x + s, y + s], outline=INK, width=lw)


def _sun(d, x, y, s, lw, t, a, a2, a3):
    for i in range(10):
        ang = i * math.pi / 5 + t * 0.6
        d.line([x + math.cos(ang) * s * 0.75, y + math.sin(ang) * s * 0.75,
                x + math.cos(ang) * s * 1.05, y + math.sin(ang) * s * 1.05], fill=C("#FFB300"), width=lw)
    _circle(d, x, y, s * 0.6, C("#FFD54F"), lw)


def _moon(d, x, y, s, lw, t, *_):
    _circle(d, x, y, s * 0.8, C("#FFF59D"), lw)
    for dx, dy, r in ((-0.2, -0.2, 0.15), (0.25, 0.15, 0.12), (-0.05, 0.35, 0.09)):
        d.ellipse([x + (dx - r) * s, y + (dy - r) * s, x + (dx + r) * s, y + (dy + r) * s], outline=C("#C9B458"),
                  width=max(2, lw // 2))


def _skull(d, x, y, s, lw, t, *_):
    _circle(d, x, y - s * 0.15, s * 0.7, WHITE, lw)
    d.rectangle([x - s * 0.35, y + s * 0.3, x + s * 0.35, y + s * 0.75], fill=WHITE, outline=INK, width=lw)
    for side in (-1, 1):
        d.ellipse([x + side * s * 0.28 - s * 0.17, y - s * 0.3, x + side * s * 0.28 + s * 0.17, y], fill=INK)
    d.polygon([(x, y + s * 0.05), (x - s * 0.09, y + s * 0.22), (x + s * 0.09, y + s * 0.22)], fill=INK)
    for i in (-1, 0, 1):
        d.line([x + i * s * 0.14, y + s * 0.42, x + i * s * 0.14, y + s * 0.72], fill=INK, width=max(2, lw // 2))


def _clock(d, x, y, s, lw, t, *_):
    _circle(d, x, y, s * 0.85, WHITE, lw)
    for i in range(12):
        a = i * math.pi / 6
        d.line([x + math.cos(a) * s * 0.65, y + math.sin(a) * s * 0.65, x + math.cos(a) * s * 0.75,
                y + math.sin(a) * s * 0.75], fill=INK, width=max(2, lw // 2))
    a = t * 2.0 - math.pi / 2
    d.line([x, y, x + math.cos(a) * s * 0.6, y + math.sin(a) * s * 0.6], fill=INK, width=lw)
    a = t * 0.2 - math.pi / 2
    d.line([x, y, x + math.cos(a) * s * 0.4, y + math.sin(a) * s * 0.4], fill=C("#E53935"), width=lw)


def _money(d, x, y, s, lw, t, *_):
    _poly(d, [(x - s, y - s * 0.5), (x + s, y - s * 0.5), (x + s, y + s * 0.5), (x - s, y + s * 0.5)], C("#66BB6A"), lw)
    _circle(d, x, y, s * 0.3, C("#A5D6A7"), max(2, lw // 2))
    _dollar(d, x, y, s * 0.28, lw)


def _dollar(d, x, y, s, lw):
    d.arc([x - s * 0.6, y - s, x + s * 0.6, y], 40, 300, fill=INK, width=max(2, lw // 2))
    d.arc([x - s * 0.6, y, x + s * 0.6, y + s], 220, 120, fill=INK, width=max(2, lw // 2))
    d.line([x, y - s * 1.2, x, y + s * 1.2], fill=INK, width=max(2, lw // 2))


def _coin(d, x, y, s, lw, t, *_):
    w = abs(math.cos(t * 3)) * 0.8 + 0.2
    d.ellipse([x - s * 0.8 * w, y - s * 0.8, x + s * 0.8 * w, y + s * 0.8], fill=C("#FFC107"), outline=INK, width=lw)
    if w > 0.5:
        _dollar(d, x, y, s * 0.35, lw)


def _question(d, x, y, s, lw, t, a, *_):
    d.arc([x - s * 0.45, y - s * 0.95, x + s * 0.45, y - s * 0.05], 180, 90, fill=a, width=int(lw * 2.2))
    d.line([x, y - s * 0.05, x, y + s * 0.3], fill=a, width=int(lw * 2.2))
    r = lw * 1.4
    d.ellipse([x - r, y + s * 0.62 - r, x + r, y + s * 0.62 + r], fill=a)


def _exclamation(d, x, y, s, lw, t, a, *_):
    d.line([x, y - s * 0.9, x, y + s * 0.3], fill=a, width=int(lw * 2.4))
    r = lw * 1.5
    d.ellipse([x - r, y + s * 0.65 - r, x + r, y + s * 0.65 + r], fill=a)


def _arrow(d, x, y, s, lw, t, a, *_):
    o = math.sin(t * 6) * s * 0.1
    pts = [(x - s + o, y - s * 0.2), (x + s * 0.2 + o, y - s * 0.2), (x + s * 0.2 + o, y - s * 0.55),
           (x + s + o, y), (x + s * 0.2 + o, y + s * 0.55), (x + s * 0.2 + o, y + s * 0.2), (x - s + o, y + s * 0.2)]
    _poly(d, pts, a, lw)


def _fire(d, x, y, s, lw, t, *_):
    fl = math.sin(t * 12) * 0.08
    outer = [(x, y - s * (1 + fl)), (x + s * 0.55, y - s * 0.1), (x + s * 0.5, y + s * 0.6), (x, y + s * 0.85),
             (x - s * 0.5, y + s * 0.6), (x - s * 0.55, y - s * 0.1), (x - s * 0.15, y - s * 0.4)]
    _poly(d, outer, C("#FF7043"), lw)
    inner = [(x, y - s * (0.3 - fl)), (x + s * 0.28, y + s * 0.3), (x, y + s * 0.65), (x - s * 0.28, y + s * 0.3)]
    d.polygon(inner, fill=C("#FFD54F"))


def _ghost(d, x, y, s, lw, t, *_):
    bob = math.sin(t * 3) * s * 0.08
    y += bob
    pts = [(x - s * 0.6, y + s * 0.8)]
    for i in range(5):
        pts.append((x - s * 0.6 + i * s * 0.3 + s * 0.15, y + s * (0.6 if i % 2 == 0 else 0.8)))
    pts += [(x + s * 0.6, y + s * 0.8), (x + s * 0.6, y - s * 0.2)]
    d.pieslice([x - s * 0.6, y - s * 0.85, x + s * 0.6, y + s * 0.4], 180, 360, fill=WHITE)
    d.polygon(pts + [(x - s * 0.6, y - s * 0.2)], fill=WHITE)
    d.arc([x - s * 0.6, y - s * 0.85, x + s * 0.6, y + s * 0.4], 180, 360, fill=INK, width=lw)
    d.line([(x - s * 0.6, y - s * 0.22)] + pts + [(x + s * 0.6, y - s * 0.22)], fill=INK, width=lw)
    for side in (-1, 1):
        d.ellipse([x + side * s * 0.22 - s * 0.08, y - s * 0.4, x + side * s * 0.22 + s * 0.08, y - s * 0.15], fill=INK)


def _tree(d, x, y, s, lw, t, *_):
    d.rectangle([x - s * 0.12, y, x + s * 0.12, y + s], fill=C("#8D6E63"), outline=INK, width=lw)
    _circle(d, x, y - s * 0.3, s * 0.6, C("#66BB6A"), lw)


def _palm(d, x, y, s, lw, t, *_):
    d.line([x, y + s, x + s * 0.15, y - s * 0.5], fill=C("#8D6E63"), width=int(lw * 2))
    for a in (-150, -110, -70, -30):
        r = math.radians(a + math.sin(t * 2) * 5)
        d.line([x + s * 0.15, y - s * 0.5, x + s * 0.15 + math.cos(r) * s * 0.7, y - s * 0.5 + math.sin(r) * s * 0.4 + s * 0.2],
               fill=C("#43A047"), width=int(lw * 1.6))


def _house(d, x, y, s, lw, t, a, *_):
    _poly(d, [(x - s * 0.7, y - s * 0.1), (x + s * 0.7, y - s * 0.1), (x + s * 0.7, y + s), (x - s * 0.7, y + s)], C("#FFE0B2"), lw)
    _poly(d, [(x - s * 0.9, y - s * 0.05), (x, y - s), (x + s * 0.9, y - s * 0.05)], a, lw)
    d.rectangle([x - s * 0.15, y + s * 0.45, x + s * 0.15, y + s], fill=C("#8D6E63"), outline=INK, width=max(2, lw // 2))


def _mountain(d, x, y, s, lw, t, *_):
    _poly(d, [(x - s, y + s * 0.8), (x, y - s), (x + s, y + s * 0.8)], C("#90A4AE"), lw)
    d.polygon([(x - s * 0.3, y - s * 0.4), (x, y - s), (x + s * 0.3, y - s * 0.4), (x, y - s * 0.3)], fill=WHITE)


def _meteor(d, x, y, s, lw, t, *_):
    for i in range(3):
        d.line([x + s * 0.3 + i * s * 0.12, y - s * 0.3 - i * s * 0.1, x + s * 1.2 + i * s * 0.1, y - s * 1.1 - i * s * 0.05],
               fill=C("#FF7043"), width=int(lw * 1.5))
    _circle(d, x, y, s * 0.45, C("#795548"), lw)


def _rocket(d, x, y, s, lw, t, a, *_):
    _poly(d, [(x, y - s), (x + s * 0.3, y - s * 0.4), (x + s * 0.3, y + s * 0.5), (x - s * 0.3, y + s * 0.5),
              (x - s * 0.3, y - s * 0.4)], WHITE, lw)
    _poly(d, [(x - s * 0.3, y + s * 0.1), (x - s * 0.6, y + s * 0.6), (x - s * 0.3, y + s * 0.5)], a, lw)
    _poly(d, [(x + s * 0.3, y + s * 0.1), (x + s * 0.6, y + s * 0.6), (x + s * 0.3, y + s * 0.5)], a, lw)
    _circle(d, x, y - s * 0.3, s * 0.13, C("#81D4FA"), max(2, lw // 2))
    fl = 0.3 + 0.15 * math.sin(t * 20)
    d.polygon([(x - s * 0.2, y + s * 0.55), (x + s * 0.2, y + s * 0.55), (x, y + s * (0.55 + fl * 2))], fill=C("#FF9800"))


def _bomb(d, x, y, s, lw, t, *_):
    _circle(d, x, y + s * 0.1, s * 0.7, C("#263238"), lw)
    d.line([x + s * 0.4, y - s * 0.45, x + s * 0.65, y - s * 0.8], fill=C("#8D6E63"), width=lw)
    if int(t * 10) % 2 == 0:
        _star_shape(d, x + s * 0.7, y - s * 0.88, s * 0.18, C("#FFC107"))


def _star_shape(d, x, y, r, fill, lw=0):
    pts = []
    for i in range(10):
        rr = r if i % 2 == 0 else r * 0.45
        a = -math.pi / 2 + i * math.pi / 5
        pts.append((x + math.cos(a) * rr, y + math.sin(a) * rr))
    d.polygon(pts, fill=fill)
    if lw:
        d.line(pts + [pts[0]], fill=INK, width=lw, joint="curve")


def _star(d, x, y, s, lw, t, a, a2, *_):
    _star_shape(d, x, y, s * (0.9 + 0.05 * math.sin(t * 5)), a2, lw)


def _lightbulb(d, x, y, s, lw, t, a, a2, *_):
    glow = 0.5 + 0.5 * math.sin(t * 6)
    for i in range(8):
        an = i * math.pi / 4
        d.line([x + math.cos(an) * s * 0.75, y - s * 0.2 + math.sin(an) * s * 0.75,
                x + math.cos(an) * s * (0.85 + 0.1 * glow), y - s * 0.2 + math.sin(an) * s * (0.85 + 0.1 * glow)],
               fill=a2, width=max(2, lw // 2))
    _circle(d, x, y - s * 0.2, s * 0.55, C("#FFF176"), lw)
    d.rectangle([x - s * 0.22, y + s * 0.35, x + s * 0.22, y + s * 0.7], fill=C("#9E9E9E"), outline=INK, width=lw)


def _heart(d, x, y, s, lw, t, a, *_):
    k = 1 + 0.08 * math.sin(t * 8)
    s *= k
    d.ellipse([x - s * 0.8, y - s * 0.6, x, y + s * 0.15], fill=a)
    d.ellipse([x, y - s * 0.6, x + s * 0.8, y + s * 0.15], fill=a)
    d.polygon([(x - s * 0.76, y - s * 0.1), (x + s * 0.76, y - s * 0.1), (x, y + s * 0.8)], fill=a)


def _book(d, x, y, s, lw, t, a, a2, a3):
    _poly(d, [(x - s * 0.7, y - s * 0.8), (x + s * 0.7, y - s * 0.8), (x + s * 0.7, y + s * 0.8), (x - s * 0.7, y + s * 0.8)], a3, lw)
    d.line([x - s * 0.5, y - s * 0.8, x - s * 0.5, y + s * 0.8], fill=INK, width=max(2, lw // 2))


def _phone(d, x, y, s, lw, t, *_):
    d.rounded_rectangle([x - s * 0.45, y - s * 0.85, x + s * 0.45, y + s * 0.85], radius=s * 0.12, fill=C("#263238"),
                        outline=INK, width=lw)
    d.rectangle([x - s * 0.35, y - s * 0.65, x + s * 0.35, y + s * 0.6], fill=C("#81D4FA"))


def _car(d, x, y, s, lw, t, a, *_):
    _poly(d, [(x - s, y), (x - s * 0.6, y - s * 0.45), (x + s * 0.4, y - s * 0.45), (x + s * 0.7, y), (x + s, y + s * 0.05),
              (x + s, y + s * 0.35), (x - s, y + s * 0.35)], a, lw)
    for wx in (-0.55, 0.55):
        _circle(d, x + wx * s, y + s * 0.38, s * 0.22, C("#263238"), lw)


def _shark(d, x, y, s, lw, t, *_):
    o = math.sin(t * 3) * s * 0.1
    _poly(d, [(x - s + o, y), (x - s * 0.3 + o, y - s * 0.35), (x - s * 0.1 + o, y - s * 0.8), (x + s * 0.1 + o, y - s * 0.35),
              (x + s + o, y - s * 0.05), (x + s * 0.5 + o, y + s * 0.3), (x - s * 0.6 + o, y + s * 0.25)], C("#90A4AE"), lw)
    d.ellipse([x + s * 0.55 + o, y - s * 0.12, x + s * 0.65 + o, y - s * 0.02], fill=INK)


def _pyramid(d, x, y, s, lw, t, *_):
    _poly(d, [(x - s, y + s * 0.8), (x, y - s * 0.8), (x + s, y + s * 0.8)], C("#E0B060"), lw)
    d.polygon([(x, y - s * 0.8), (x + s, y + s * 0.8), (x + s * 0.3, y + s * 0.8)], fill=C("#C49340"))
    d.line([(x - s, y + s * 0.8), (x, y - s * 0.8), (x + s, y + s * 0.8), (x - s, y + s * 0.8)], fill=INK, width=lw)


def _castle(d, x, y, s, lw, t, *_):
    g = C("#B0BEC5")
    _poly(d, [(x - s * 0.8, y - s * 0.2), (x + s * 0.8, y - s * 0.2), (x + s * 0.8, y + s), (x - s * 0.8, y + s)], g, lw)
    for tx in (-0.8, 0.5):
        _poly(d, [(x + tx * s, y - s * 0.8), (x + (tx + 0.3) * s, y - s * 0.8), (x + (tx + 0.3) * s, y + s), (x + tx * s, y + s)], g, lw)
    d.chord([x - s * 0.2, y + s * 0.4, x + s * 0.2, y + s * 1.2], 180, 360, fill=C("#5D4037"))


def _crown(d, x, y, s, lw, t, a, a2, *_):
    pts = [(x - s * 0.8, y + s * 0.4), (x - s * 0.8, y - s * 0.4), (x - s * 0.4, y), (x, y - s * 0.6), (x + s * 0.4, y),
           (x + s * 0.8, y - s * 0.4), (x + s * 0.8, y + s * 0.4)]
    _poly(d, pts, a2, lw)


def _sword(d, x, y, s, lw, t, *_):
    _poly(d, [(x - s * 0.08, y + s * 0.4), (x - s * 0.08, y - s), (x, y - s * 1.15), (x + s * 0.08, y - s), (x + s * 0.08, y + s * 0.4)],
          C("#CFD8DC"), lw)
    d.rectangle([x - s * 0.35, y + s * 0.4, x + s * 0.35, y + s * 0.5], fill=C("#8D6E63"), outline=INK, width=max(2, lw // 2))
    d.rectangle([x - s * 0.06, y + s * 0.5, x + s * 0.06, y + s * 0.9], fill=C("#5D4037"))


def _shield(d, x, y, s, lw, t, a, *_):
    _poly(d, [(x - s * 0.7, y - s * 0.8), (x + s * 0.7, y - s * 0.8), (x + s * 0.7, y), (x, y + s * 0.9), (x - s * 0.7, y)], a, lw)


def _cloud(d, x, y, s, lw, t, *_):
    o = math.sin(t * 0.8) * s * 0.1
    for dx, dy, r in ((-0.5, 0.1, 0.4), (0, -0.15, 0.55), (0.5, 0.1, 0.4)):
        d.ellipse([x + (dx - r) * s + o, y + (dy - r) * s, x + (dx + r) * s + o, y + (dy + r) * s], fill=WHITE)


def _lightning(d, x, y, s, lw, t, a, a2, *_):
    if int(t * 8) % 3 == 0:
        return
    _poly(d, [(x + s * 0.1, y - s), (x - s * 0.45, y + s * 0.1), (x, y + s * 0.1), (x - s * 0.2, y + s), (x + s * 0.5, y - s * 0.15),
              (x + s * 0.05, y - s * 0.15)], a2, lw)


def _snowflake(d, x, y, s, lw, t, *_):
    for i in range(3):
        a = i * math.pi / 3 + t * 0.5
        d.line([x - math.cos(a) * s * 0.8, y - math.sin(a) * s * 0.8, x + math.cos(a) * s * 0.8, y + math.sin(a) * s * 0.8],
               fill=C("#4FC3F7"), width=lw)


def _thermometer(d, x, y, s, lw, t, a, *_):
    d.rounded_rectangle([x - s * 0.15, y - s, x + s * 0.15, y + s * 0.5], radius=s * 0.15, fill=WHITE, outline=INK, width=lw)
    _circle(d, x, y + s * 0.65, s * 0.3, a, lw)
    lvl = 0.3 + 0.6 * (0.5 + 0.5 * math.sin(t * 1.5))
    d.rectangle([x - s * 0.07, y + s * 0.5 - lvl * s * 1.4, x + s * 0.07, y + s * 0.5], fill=a)


def _hourglass(d, x, y, s, lw, t, *_):
    _poly(d, [(x - s * 0.5, y - s * 0.8), (x + s * 0.5, y - s * 0.8), (x, y), (x + s * 0.5, y + s * 0.8), (x - s * 0.5, y + s * 0.8), (x, y)],
          C("#FFF8E1"), lw)
    k = (t * 0.3) % 1
    d.polygon([(x - s * 0.4 * (1 - k), y - s * 0.7 * (1 - k)), (x + s * 0.4 * (1 - k), y - s * 0.7 * (1 - k)), (x, y)], fill=C("#FFB300"))
    d.polygon([(x - s * 0.4 * k, y + s * 0.8 - s * 0.6 * k), (x + s * 0.4 * k, y + s * 0.8 - s * 0.6 * k), (x + s * 0.45, y + s * 0.78),
               (x - s * 0.45, y + s * 0.78)], fill=C("#FFB300"))


def _magnifier(d, x, y, s, lw, t, *_):
    d.line([x + s * 0.3, y + s * 0.3, x + s * 0.9, y + s * 0.9], fill=C("#5D4037"), width=int(lw * 2))
    _circle(d, x - s * 0.1, y - s * 0.1, s * 0.55, C("#B3E5FC"), lw)


def _virus(d, x, y, s, lw, t, *_):
    for i in range(8):
        a = i * math.pi / 4 + t * 0.5
        d.line([x, y, x + math.cos(a) * s * 0.85, y + math.sin(a) * s * 0.85], fill=INK, width=lw)
        r = s * 0.1
        d.ellipse([x + math.cos(a) * s * 0.85 - r, y + math.sin(a) * s * 0.85 - r, x + math.cos(a) * s * 0.85 + r,
                   y + math.sin(a) * s * 0.85 + r], fill=C("#E53935"))
    _circle(d, x, y, s * 0.55, C("#81C784"), lw)


def _planet(d, x, y, s, lw, t, *_):
    _circle(d, x, y, s * 0.55, C("#FFB74D"), lw)
    d.arc([x - s, y - s * 0.25, x + s, y + s * 0.25], 0, 180, fill=INK, width=lw)


def _check(d, x, y, s, lw, t, a, a2, a3):
    d.line([(x - s * 0.6, y), (x - s * 0.15, y + s * 0.5), (x + s * 0.7, y - s * 0.6)], fill=C("#43A047"), width=int(lw * 2.5),
           joint="curve")


def _cross(d, x, y, s, lw, t, a, *_):
    d.line([x - s * 0.6, y - s * 0.6, x + s * 0.6, y + s * 0.6], fill=a, width=int(lw * 2.5))
    d.line([x - s * 0.6, y + s * 0.6, x + s * 0.6, y - s * 0.6], fill=a, width=int(lw * 2.5))


def _warning(d, x, y, s, lw, t, a, a2, *_):
    _poly(d, [(x, y - s * 0.9), (x + s, y + s * 0.8), (x - s, y + s * 0.8)], a2, lw)
    _exclamation(d, x, y + s * 0.15, s * 0.5, lw, t, INK)


def _door(d, x, y, s, lw, t, *_):
    d.rectangle([x - s * 0.5, y - s, x + s * 0.5, y + s], fill=C("#8D6E63"), outline=INK, width=lw)
    _circle(d, x + s * 0.3, y, s * 0.07, C("#FFC107"), max(2, lw // 2))


def _key(d, x, y, s, lw, t, a, a2, *_):
    _circle(d, x - s * 0.5, y, s * 0.35, a2, lw)
    d.line([x - s * 0.15, y, x + s * 0.9, y], fill=INK, width=lw)
    d.line([x + s * 0.6, y, x + s * 0.6, y + s * 0.25], fill=INK, width=lw)


def _apple(d, x, y, s, lw, t, a, *_):
    _circle(d, x, y + s * 0.1, s * 0.65, a, lw)
    d.line([x, y - s * 0.5, x + s * 0.1, y - s * 0.85], fill=C("#5D4037"), width=lw)


def _water(d, x, y, s, lw, t, *_):
    d.polygon([(x, y - s), (x + s * 0.5, y + s * 0.1), (x - s * 0.5, y + s * 0.1)], fill=C("#4FC3F7"))
    _circle(d, x, y + s * 0.3, s * 0.5, C("#4FC3F7"), lw)


def _tent(d, x, y, s, lw, t, a, *_):
    _poly(d, [(x - s, y + s * 0.7), (x, y - s * 0.8), (x + s, y + s * 0.7)], C("#FF8A65"), lw)
    d.polygon([(x, y - s * 0.2), (x + s * 0.3, y + s * 0.7), (x - s * 0.3, y + s * 0.7)], fill=INK)


def _campfire(d, x, y, s, lw, t, *_):
    d.line([x - s * 0.7, y + s * 0.7, x + s * 0.7, y + s * 0.4], fill=C("#6D4C41"), width=int(lw * 2))
    d.line([x - s * 0.7, y + s * 0.4, x + s * 0.7, y + s * 0.7], fill=C("#6D4C41"), width=int(lw * 2))
    _fire(d, x, y - s * 0.05, s * 0.6, lw, t)


def _dino(d, x, y, s, lw, t, *_):
    g = C("#7CB342")
    _poly(d, [(x - s, y + s * 0.2), (x - s * 0.4, y - s * 0.1), (x + s * 0.3, y - s * 0.2), (x + s * 0.4, y - s * 0.8),
              (x + s * 0.95, y - s * 0.75), (x + s * 0.95, y - s * 0.5), (x + s * 0.6, y - s * 0.45), (x + s * 0.6, y + s * 0.3),
              (x + s * 0.3, y + s * 0.4), (x - s * 0.3, y + s * 0.4)], g, lw)
    for lx in (-0.2, 0.3):
        d.line([x + lx * s, y + s * 0.35, x + lx * s, y + s * 0.85], fill=INK, width=int(lw * 1.6))
    d.ellipse([x + s * 0.6, y - s * 0.72, x + s * 0.7, y - s * 0.62], fill=INK)


def _atom(d, x, y, s, lw, t, a, a2, a3):
    for i in range(3):
        ang = i * 60 + t * 40
        box = Image.new("RGBA", (1, 1))
        r = math.radians(ang)
        pts = [(x + math.cos(u) * s * 0.9 * math.cos(r) - math.sin(u) * s * 0.3 * math.sin(r),
                y + math.cos(u) * s * 0.9 * math.sin(r) + math.sin(u) * s * 0.3 * math.cos(r)) for u in
               [k * math.pi / 18 for k in range(37)]]
        d.line(pts, fill=a3, width=max(2, lw // 2))
    _circle(d, x, y, s * 0.18, a, max(2, lw // 2))


def _chart_up(d, x, y, s, lw, t, a, a2, a3):
    d.line([(x - s, y - s), (x - s, y + s), (x + s, y + s)], fill=INK, width=lw)
    k = min(1, (t % 3) / 1.2)
    pts = [(x - s * 0.9, y + s * 0.6), (x - s * 0.4, y + s * 0.2), (x, y + s * 0.4), (x + s * 0.4, y - s * 0.3), (x + s * 0.9, y - s * 0.8)]
    n = max(2, int(len(pts) * k + 0.999))
    d.line(pts[:n], fill=C("#43A047"), width=int(lw * 1.5), joint="curve")


def _chart_down(d, x, y, s, lw, t, a, *_):
    d.line([(x - s, y - s), (x - s, y + s), (x + s, y + s)], fill=INK, width=lw)
    pts = [(x - s * 0.9, y - s * 0.8), (x - s * 0.4, y - s * 0.3), (x, y - s * 0.5), (x + s * 0.4, y + s * 0.2), (x + s * 0.9, y + s * 0.7)]
    d.line(pts, fill=a, width=int(lw * 1.5), joint="curve")


def _zzz(d, x, y, s, lw, t, *_):
    for i in range(3):
        k = ((t * 0.8 + i / 3) % 1)
        cx, cy, r = x + k * s * 0.6, y - k * s, s * (0.15 + 0.1 * i)
        d.line([(cx - r, cy - r), (cx + r, cy - r), (cx - r, cy + r), (cx + r, cy + r)], fill=INK, width=max(2, lw // 2))


def _bones(d, x, y, s, lw, t, *_):
    for a in (35, -35):
        r = math.radians(a)
        dx, dy = math.cos(r) * s * 0.8, math.sin(r) * s * 0.8
        d.line([x - dx, y - dy, x + dx, y + dy], fill=WHITE, width=int(lw * 2.2))
        for q in ((x - dx, y - dy), (x + dx, y + dy)):
            _circle(d, q[0], q[1], lw * 1.3, WHITE, max(2, lw // 3))


def _boat(d, x, y, s, lw, t, a, *_):
    b = math.sin(t * 2) * s * 0.05
    _poly(d, [(x - s, y + b), (x + s, y + b), (x + s * 0.7, y + s * 0.4 + b), (x - s * 0.7, y + s * 0.4 + b)], C("#8D6E63"), lw)
    d.line([x, y + b, x, y - s + b], fill=INK, width=lw)
    _poly(d, [(x + lw, y - s + b), (x + s * 0.6, y - s * 0.2 + b), (x + lw, y - s * 0.2 + b)], WHITE, max(2, lw // 2))


def _plane(d, x, y, s, lw, t, *_):
    _poly(d, [(x - s, y), (x + s * 0.8, y - s * 0.1), (x + s, y), (x + s * 0.8, y + s * 0.1)], WHITE, lw)
    _poly(d, [(x - s * 0.1, y), (x + s * 0.1, y - s * 0.6), (x + s * 0.3, y - s * 0.6), (x + s * 0.2, y)], C("#90A4AE"), lw)


def _food(d, x, y, s, lw, t, a, a2, *_):
    d.chord([x - s * 0.8, y - s * 0.6, x + s * 0.8, y + s * 0.6], 180, 360, fill=C("#FFB74D"), outline=INK, width=lw)
    d.rectangle([x - s * 0.8, y + s * 0.05, x + s * 0.8, y + s * 0.2], fill=C("#8D6E63"), outline=INK, width=max(2, lw // 2))
    d.rectangle([x - s * 0.8, y - s * 0.05, x + s * 0.8, y + s * 0.05], fill=C("#7CB342"))
    d.chord([x - s * 0.8, y - s * 0.1, x + s * 0.8, y + s * 0.5], 0, 180, fill=C("#FFB74D"), outline=INK, width=lw)


def _box(d, x, y, s, lw, t, a, a2, *_):
    _poly(d, [(x - s * 0.7, y - s * 0.5), (x + s * 0.7, y - s * 0.5), (x + s * 0.7, y + s * 0.7), (x - s * 0.7, y + s * 0.7)], C("#D7A86E"), lw)
    d.line([x, y - s * 0.5, x, y + s * 0.7], fill=INK, width=max(2, lw // 2))


PROPS = {
    "earth": _earth, "sun": _sun, "moon": _moon, "skull": _skull, "clock": _clock, "money": _money, "coin": _coin,
    "question": _question, "exclamation": _exclamation, "arrow": _arrow, "fire": _fire, "ghost": _ghost, "tree": _tree,
    "palm": _palm, "house": _house, "mountain": _mountain, "meteor": _meteor, "rocket": _rocket, "bomb": _bomb,
    "star": _star, "lightbulb": _lightbulb, "heart": _heart, "book": _book, "phone": _phone, "car": _car,
    "shark": _shark, "pyramid": _pyramid, "castle": _castle, "crown": _crown, "sword": _sword, "shield": _shield,
    "cloud": _cloud, "lightning": _lightning, "snowflake": _snowflake, "thermometer": _thermometer,
    "hourglass": _hourglass, "magnifier": _magnifier, "virus": _virus, "planet": _planet, "check": _check,
    "cross": _cross, "warning": _warning, "door": _door, "key": _key, "apple": _apple, "water": _water,
    "tent": _tent, "campfire": _campfire, "dinosaur": _dino, "atom": _atom, "chart_up": _chart_up,
    "chart_down": _chart_down, "zzz": _zzz, "bones": _bones, "boat": _boat, "plane": _plane, "food": _food,
    "box": _box,
}


# =========================================================================== backgrounds
BACKGROUNDS = ["white", "room", "day", "night", "city", "desert", "forest", "ocean", "space", "cave", "lab",
               "island", "snow", "volcano", "ancient", "school", "apocalypse", "underwater", "black", "red_alert",
               "office", "jungle"]


def _grad(img, top, bot):
    w, h = img.size
    d = ImageDraw.Draw(img)
    for y in range(h):
        k = y / max(1, h - 1)
        d.line([(0, y), (w, y)], fill=tuple(int(top[i] + (bot[i] - top[i]) * k) for i in range(3)) + (255,))


def background(kind: str, w: int, h: int, style: dict) -> Image.Image:
    """Return a cached RGB background; caller crops/scales for camera moves."""
    if kind not in BACKGROUNDS:
        kind = "white"
    key = sha({"k": kind, "w": w, "h": h, "pal": style.get("palette"), "bg": style.get("backgrounds"), "v": 4})
    folder = ASSETS_DIR / "backgrounds" / "cache"
    folder.mkdir(parents=True, exist_ok=True)
    p = folder / f"{kind}_{w}x{h}_{key}.png"
    if p.exists():
        try:
            return Image.open(p).convert("RGB")
        except Exception:
            p.unlink(missing_ok=True)
    img = _render_bg(kind, w, h, style)
    img.save(p)
    return img


def _render_bg(kind, w, h, style):
    pal = style["palette"]
    lw = max(3, int(style["backgrounds"].get("outline_px", 6) * h / 1080))
    rnd = random.Random(kind)
    img = Image.new("RGBA", (w, h), C(pal["background_default"]))
    d = ImageDraw.Draw(img)
    gy = int(h * 0.74)  # ground line = world y 0.80*H after 1.25x overscan (character feet)

    def ground(col, line=True):
        d.rectangle([0, gy, w, h], fill=col)
        if line and style["backgrounds"].get("ground_line", True):
            d.line([0, gy, w, gy], fill=INK, width=lw)

    def hills(col, n=4, amp=0.08, base=0.78):
        pts = [(0, h)]
        for i in range(0, w + 40, 40):
            pts.append((i, h * base - h * amp * (0.5 + 0.5 * math.sin(i / w * math.pi * n + rnd.random()))))
        pts.append((w, h))
        d.polygon(pts, fill=col)
        d.line(pts[1:-1], fill=INK, width=lw)

    def clouds(n=4):
        for _ in range(n):
            _cloud(d, rnd.uniform(0.05, 0.95) * w, rnd.uniform(0.08, 0.35) * h, h * 0.09, lw, 0)

    def stars(n=160):
        for _ in range(n):
            x, y, r = rnd.uniform(0, w), rnd.uniform(0, h * 0.75), rnd.choice([1, 1, 2, 3]) * h / 1080
            d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255, rnd.randint(120, 255)))

    if kind == "white":
        ground(C(pal["background_default"]))
    elif kind == "black":
        img.paste(C("#0D0D0D"), [0, 0, w, h])
        d.line([0, gy, w, gy], fill=(80, 80, 80, 255), width=lw)
    elif kind == "red_alert":
        _grad(img, C("#7F0000"), C("#D32F2F"))
        ground(C("#3E0000"))
    elif kind == "room" or kind == "office":
        img.paste(C("#F5EBDD" if kind == "room" else "#E3EAF0"), [0, 0, w, h])
        ground(C("#C8A27A" if kind == "room" else "#9AA5AE"))
        d.rectangle([w * 0.62, h * 0.18, w * 0.86, h * 0.5], fill=C("#BFE6FF"), outline=INK, width=lw)
        d.line([w * 0.74, h * 0.18, w * 0.74, h * 0.5], fill=INK, width=lw)
        d.rectangle([w * 0.12, h * 0.22, w * 0.27, h * 0.42], fill=C(pal["accent2"]), outline=INK, width=lw)
        if kind == "office":
            d.rectangle([w * 0.05, gy - h * 0.18, w * 0.3, gy - h * 0.15], fill=C("#8D6E63"), outline=INK, width=lw)
    elif kind in ("day", "island", "jungle", "forest"):
        _grad(img, C(pal["sky_day"][0]), C(pal["sky_day"][1]))
        _sun(d, w * 0.85, h * 0.17, h * 0.1, lw, 0, None, None, None)
        clouds()
        if kind == "island":
            d.rectangle([0, h * 0.6, w, h], fill=C("#4FC3F7"))
            d.chord([-w * 0.1, gy - h * 0.12, w * 1.1, gy + h * 0.5], 180, 360, fill=C("#FFE082"), outline=INK, width=lw)
            d.rectangle([0, gy, w, h], fill=C("#FFE082"))
            _palm(d, w * 0.15, gy - h * 0.18, h * 0.25, lw, 0)
            _palm(d, w * 0.88, gy - h * 0.15, h * 0.22, lw, 0)
        else:
            hills(C("#A5D6A7"), 3, 0.06, 0.66)
            ground(C("#81C784"))
            if kind in ("forest", "jungle"):
                for i in range(7):
                    tx = (i + 0.5) / 7 * w + rnd.uniform(-40, 40)
                    (_palm if kind == "jungle" else _tree)(d, tx, gy - h * 0.13, h * rnd.uniform(0.17, 0.24), lw, 0)
    elif kind == "night":
        _grad(img, C(pal["sky_night"][0]), C(pal["sky_night"][1]))
        stars()
        _moon(d, w * 0.82, h * 0.18, h * 0.1, lw, 0)
        hills(C("#1B2A3A"), 3, 0.06, 0.68)
        ground(C("#16212C"))
    elif kind == "city" or kind == "apocalypse":
        if kind == "city":
            _grad(img, C(pal["sky_day"][0]), C(pal["sky_day"][1]))
        else:
            _grad(img, C("#5D1A0B"), C("#E65100"))
        x = 0
        while x < w:
            bw, bh = rnd.uniform(0.06, 0.12) * w, rnd.uniform(0.25, 0.6) * h
            col = C("#90A4AE") if kind == "city" else C("#3E2723")
            d.rectangle([x, gy - bh, x + bw, gy], fill=col, outline=INK, width=lw)
            if kind == "city":
                for wy in range(int(gy - bh + 20), gy - 30, 45):
                    for wx in range(int(x + 15), int(x + bw - 20), 35):
                        d.rectangle([wx, wy, wx + 14, wy + 22], fill=C("#FFF59D"))
            else:
                d.polygon([(x, gy - bh), (x + bw * 0.5, gy - bh + 40), (x + bw, gy - bh)], fill=C("#5D1A0B"))
            x += bw + rnd.uniform(5, 40)
        ground(C("#9E9E9E") if kind == "city" else C("#4E342E"))
    elif kind == "desert":
        _grad(img, C("#FFCC80"), C("#FFF3E0"))
        _sun(d, w * 0.8, h * 0.2, h * 0.12, lw, 0, None, None, None)
        hills(C("#FFB74D"), 2, 0.07, 0.69)
        ground(C("#FFCA7A"))
        _pyramid(d, w * 0.25, gy - h * 0.14, h * 0.18, lw, 0)
    elif kind == "ocean" or kind == "underwater":
        if kind == "ocean":
            _grad(img, C(pal["sky_day"][0]), C(pal["sky_day"][1]))
            clouds(3)
            d.rectangle([0, h * 0.55, w, h], fill=C("#1E88E5"))
            for i in range(0, w, 120):
                d.arc([i, h * 0.53, i + 120, h * 0.6], 180, 360, fill=INK, width=lw)
            ground(C("#FFE082"))
        else:
            _grad(img, C("#4FC3F7"), C("#01579B"))
            for _ in range(30):
                x, y, r = rnd.uniform(0, w), rnd.uniform(0, h * 0.75), rnd.uniform(4, 14) * h / 1080
                d.ellipse([x - r, y - r, x + r, y + r], outline=(255, 255, 255, 160), width=2)
            ground(C("#C2A36B"))
    elif kind == "space":
        img.paste(C("#070B1A"), [0, 0, w, h])
        stars(320)
        _planet(d, w * 0.18, h * 0.22, h * 0.14, lw, 0)
        _earth(d, w * 0.84, h * 0.3, h * 0.12, lw, 0)
        d.chord([-w * 0.2, gy - h * 0.05, w * 1.2, gy + h * 0.8], 180, 360, fill=C("#B0BEC5"), outline=INK, width=lw)
        d.rectangle([0, gy + h * 0.05, w, h], fill=C("#B0BEC5"))
        for _ in range(6):
            cx, cy, r = rnd.uniform(0, w), rnd.uniform(gy + 20, h - 20), rnd.uniform(15, 40) * h / 1080
            d.ellipse([cx - r * 2, cy - r * 0.6, cx + r * 2, cy + r * 0.6], fill=C("#90A4AE"))
    elif kind == "cave":
        img.paste(C("#2B2B2B"), [0, 0, w, h])
        for i in range(0, w, 90):
            d.polygon([(i, 0), (i + 90, 0), (i + 45, rnd.uniform(0.08, 0.2) * h)], fill=C("#3E3E3E"), outline=INK)
        ground(C("#4A4A4A"))
        glow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        ImageDraw.Draw(glow).ellipse([w * 0.25, h * 0.2, w * 0.75, h * 1.0], fill=(255, 190, 90, 60))
        img.alpha_composite(glow.filter(ImageFilter.GaussianBlur(h * 0.08)))
    elif kind == "lab":
        img.paste(C("#ECEFF1"), [0, 0, w, h])
        for sx in (0.08, 0.7):
            for sy in (0.25, 0.45):
                d.line([w * sx, h * sy, w * (sx + 0.22), h * sy], fill=INK, width=lw)
                for k in range(3):
                    bx = w * (sx + 0.03 + k * 0.07)
                    d.rectangle([bx, h * sy - h * 0.08, bx + w * 0.03, h * sy], fill=[C("#81D4FA"), C("#A5D6A7"), C("#F48FB1")][k],
                                outline=INK, width=max(2, lw // 2))
        ground(C("#CFD8DC"))
    elif kind == "snow":
        _grad(img, C("#CFD8DC"), C("#ECEFF1"))
        hills(C("#FFFFFF"), 3, 0.08, 0.66)
        ground(C("#FFFFFF"))
        for _ in range(120):
            x, y, r = rnd.uniform(0, w), rnd.uniform(0, h), rnd.uniform(2, 5) * h / 1080
            d.ellipse([x - r, y - r, x + r, y + r], fill=WHITE)
    elif kind == "volcano":
        _grad(img, C("#4E342E"), C("#FF7043"))
        _poly(d, [(w * 0.25, gy), (w * 0.45, h * 0.25), (w * 0.55, h * 0.25), (w * 0.75, gy)], C("#5D4037"), lw)
        d.polygon([(w * 0.45, h * 0.25), (w * 0.55, h * 0.25), (w * 0.53, h * 0.38), (w * 0.5, h * 0.33), (w * 0.47, h * 0.4)],
                  fill=C("#FF5722"))
        ground(C("#3E2723"))
    elif kind == "ancient":
        _grad(img, C("#FFE0B2"), C("#FFF8E1"))
        for cx in (0.1, 0.25, 0.75, 0.9):
            d.rectangle([w * cx - 30, h * 0.25, w * cx + 30, gy], fill=C("#EEE3CF"), outline=INK, width=lw)
            d.rectangle([w * cx - 45, h * 0.22, w * cx + 45, h * 0.26], fill=C("#EEE3CF"), outline=INK, width=lw)
        ground(C("#D7C29E"))
    elif kind == "school":
        img.paste(C("#FFF3E0"), [0, 0, w, h])
        d.rectangle([w * 0.2, h * 0.14, w * 0.8, h * 0.55], fill=C("#2E5E4E"), outline=C("#8D6E63"), width=lw * 3)
        ground(C("#BCAAA4"))
    return img.convert("RGB")
