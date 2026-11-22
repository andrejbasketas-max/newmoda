"""Frame renderer: turns one storyboard scene + time into a finished 16:9 frame."""
from __future__ import annotations

import math
import random

from PIL import Image, ImageDraw, ImageFont

from ..core import font_path
from .character import Character, hex2rgb, pose_for
from .world import background, draw_prop

SS = 2          # supersampling for the vector foreground
BG_OVERSCAN = 1.25
DARK_BACKGROUNDS = {"night", "space", "cave", "black", "apocalypse", "volcano", "red_alert", "underwater"}

_font_cache: dict = {}


def font(size: int, bold=True):
    k = (size, bold)
    if k not in _font_cache:
        _font_cache[k] = ImageFont.truetype(font_path(bold), size)
    return _font_cache[k]


def _ease(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


def _back(x):  # overshoot ease for pops
    x = max(0.0, min(1.0, x))
    c1 = 1.70158
    return 1 + (c1 + 1) * (x - 1) ** 3 + c1 * (x - 1) ** 2


def camera(scene: dict, t: float, W: int, H: int, max_zoom: float):
    dur = max(0.01, scene.get("duration", 3))
    k = _ease(t / dur)
    mv = scene.get("camera", "static")
    z, cx, cy = 1.0, W / 2, H / 2
    if mv == "slow_zoom_in":
        z = 1.0 + (max_zoom - 1) * 0.6 * k
    elif mv == "slow_zoom_out":
        z = 1.0 + (max_zoom - 1) * 0.6 * (1 - k)
    elif mv == "punch_in":
        z = 1.0 + (max_zoom - 1) * _ease(t / 0.25)
    elif mv == "pan_left":
        z, cx = 1.08, W / 2 + W * 0.05 * (1 - 2 * k)
    elif mv == "pan_right":
        z, cx = 1.08, W / 2 - W * 0.05 * (1 - 2 * k)
    focus = scene.get("focus")  # optional (x,y) fractions to zoom toward
    if focus and z > 1:
        fx, fy = focus[0] * W, focus[1] * H
        amt = (z - 1) / max(1e-6, max_zoom - 1)
        cx += (fx - cx) * 0.5 * amt
        cy += (fy - cy) * 0.5 * amt
    if "shake" in scene.get("effects", []) and t < 0.5:
        r = random.Random(int(t * 60))
        a = (0.5 - t) * 18 * W / 1920
        cx += r.uniform(-a, a)
        cy += r.uniform(-a, a)
    # clamp so the visible window stays inside the overscanned background
    half_w, half_h = W / (2 * z), H / (2 * z)
    m = (BG_OVERSCAN - 1) / 2
    cx = max(-m * W + half_w, min(W * (1 + m) - half_w, cx))
    cy = max(-m * H + half_h, min(H * (1 + m) - half_h, cy))
    return z, cx, cy


class FrameRenderer:
    def __init__(self, style: dict, W: int = 1920, H: int = 1080):
        self.style = style
        self.W, self.H = W, H
        self.chars = {"main": Character(style["character"])}
        for name, ov in style.get("secondary_characters", {}).items():
            base = dict(style["character"])
            self.chars[name] = Character(base, ov)
        self._bg_cache = {}

    def _bg(self, kind):
        if kind not in self._bg_cache:
            self._bg_cache[kind] = background(kind, int(self.W * BG_OVERSCAN), int(self.H * BG_OVERSCAN), self.style)
        return self._bg_cache[kind]

    def render(self, scene: dict, t: float, mouth: float = 0.0, subtitle: tuple | None = None,
               prev_frame: Image.Image | None = None) -> Image.Image:
        W, H = self.W, self.H
        st = self.style
        z, cx, cy = camera(scene, t, W, H, st["animation"].get("max_zoom", 1.25))

        # ---- background: crop the overscanned image for the camera window
        bg = self._bg(scene.get("background", "white"))
        m = (BG_OVERSCAN - 1) / 2
        # world -> bg pixel: (wx + m*W) * (bgW / (W*(1+2m)))
        sx = bg.width / (W * (1 + 2 * m))
        box = ((cx - W / (2 * z) + m * W) * sx, (cy - H / (2 * z) + m * H) * sx,
               (cx + W / (2 * z) + m * W) * sx, (cy + H / (2 * z) + m * H) * sx)
        frame = bg.resize((W, H), Image.BILINEAR, box=box).convert("RGBA")

        # ---- foreground (supersampled vector layer)
        fg = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
        d = ImageDraw.Draw(fg)

        def X(x, y):
            return ((x - cx) * z + W / 2) * SS, ((y - cy) * z + H / 2) * SS

        S = z * SS
        ground = H * 0.80
        dur = scene.get("duration", 3)
        lw_base = max(2, int(st["character"]["line_width_px"] * H / 1080 * 0.85))
        for pr in scene.get("props", []):
            self._prop(d, pr, t, X, S, lw_base, dur)
        rim = ("#FFFFFF", 150) if scene.get("background") in DARK_BACKGROUNDS else None
        for i, ch in enumerate(scene.get("characters", [])):
            who = ch.get("who", "main")
            c = self.chars.get(who, self.chars["main"])
            k = _ease(t / max(0.01, dur * ch.get("move_time", 1.0)))
            xf = ch.get("x", 0.4) + (ch.get("to_x", ch.get("x", 0.4)) - ch.get("x", 0.4)) * k
            Hc = st["character"]["height_px"] * ch.get("scale", 1.0) * H / 1080
            pose = pose_for(ch.get("action", "idle"), t + ch.get("t_offset", 0.0), dur, seed=i)
            mo = mouth if ch.get("talks") else 0.0
            c.draw(d, (X, S), xf * W, ground + ch.get("y", 0) * H, Hc, pose, ch.get("expression", "neutral"),
                   ch.get("facing", 1), mo, t, blink_seed=i, rim=rim)
        if "speed_lines" in scene.get("effects", []):
            self._speed_lines(d, t, W * SS, H * SS)
        fg = fg.reduce(SS)
        frame.alpha_composite(fg)

        # ---- screen-space overlays
        eff = scene.get("effects", [])
        if "vignette" in eff or "dark" in eff:
            frame.alpha_composite(self._vignette(0.75 if "dark" in eff else 0.5))
        if "red_tint" in eff:
            frame.alpha_composite(Image.new("RGBA", (W, H), (200, 0, 0, 50)))
        if scene.get("caption"):
            self._caption(frame, scene["caption"], t)
        if "flash" in eff and t < 0.25:
            frame.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, int(255 * (1 - t / 0.25)))))
        frame = self._transition_in(frame, scene, t, prev_frame)
        if subtitle:
            self._subtitle(frame, *subtitle)
        return frame.convert("RGB")

    # ------------------------------------------------------------------ helpers
    def _prop(self, d, pr, t, X, S, lw, dur):
        delay = pr.get("delay", 0.0)
        if t < delay:
            return
        tl = t - delay
        anim = pr.get("anim", "pop")
        x, y = pr.get("x", 0.7) * self.W, pr.get("y", 0.45) * self.H
        size = pr.get("size", 0.2) * self.H
        sc = 1.0
        if anim == "pop":
            sc = _back(tl / 0.35)
        elif anim == "grow":
            sc = 0.3 + 0.7 * _ease(tl / max(0.3, dur - delay))
        elif anim == "float":
            y += math.sin(tl * 2.2) * size * 0.08
            sc = _back(tl / 0.35)
        elif anim == "fall":
            y = -size + (y + size) * min(1, (tl / 0.6) ** 2)
        elif anim == "slide_in":
            x = self.W * 1.2 + (x - self.W * 1.2) * _ease(tl / 0.45)
        elif anim == "shake":
            x += math.sin(tl * 40) * size * 0.04
        elif anim == "move":
            tx, ty = pr.get("to_x", pr.get("x", 0.7)) * self.W, pr.get("to_y", pr.get("y", 0.45)) * self.H
            k = _ease(tl / max(0.3, dur - delay))
            x, y = x + (tx - x) * k, y + (ty - y) * k
        if sc <= 0.01:
            return
        px, py = X(x, y)
        draw_prop(d, pr.get("name", "question"), px, py, size * S * sc, max(2, int(lw * S * 0.8)), tl, self.style)

    def _speed_lines(self, d, t, w, h):
        r = random.Random(int(t * 12))
        for _ in range(26):
            a = r.uniform(0, 2 * math.pi)
            r0, r1 = r.uniform(0.62, 0.72), r.uniform(0.85, 1.05)
            cx, cy = w / 2, h / 2
            R = math.hypot(w, h) / 2
            d.line([cx + math.cos(a) * R * r0, cy + math.sin(a) * R * r0, cx + math.cos(a) * R * r1, cy + math.sin(a) * R * r1],
                   fill=(20, 20, 20, 140), width=int(r.uniform(2, 6) * w / 3840 * 2))

    _vig = {}

    def _vignette(self, strength):
        k = (self.W, self.H, strength)
        if k not in self._vig:
            from PIL import ImageFilter
            m = Image.new("L", (self.W, self.H), int(255 * strength))
            ImageDraw.Draw(m).ellipse([self.W * 0.12, self.H * 0.08, self.W * 0.88, self.H * 0.95], fill=0)
            m = m.filter(ImageFilter.GaussianBlur(self.H * 0.12))
            v = Image.new("RGBA", (self.W, self.H), (0, 0, 0, 255))
            v.putalpha(m)
            self._vig[k] = v
        return self._vig[k]

    def _text_outlined(self, img, xy, text, fnt, fill, outline, ow, anchor="mm"):
        d = ImageDraw.Draw(img)
        d.text(xy, text, font=fnt, fill=fill, anchor=anchor, stroke_width=ow, stroke_fill=outline)

    def _caption(self, frame, text, t):
        cs = self.style["thumbnail"]
        sc = _back(t / 0.3)
        if sc <= 0.05:
            return
        size = int(self.H * 0.1 * sc)
        if size < 6:
            return
        f = font(size)
        self._text_outlined(frame, (self.W / 2, self.H * 0.14), text, f, hex2rgb(cs["highlight_color"]),
                            hex2rgb(cs["text_outline"]), max(2, int(size * 0.1)))

    def _subtitle(self, frame, words, active_idx):
        ss = self.style["subtitles"]
        size = int(ss["size_px"] * self.H / 1080)
        f = font(size)
        d = ImageDraw.Draw(frame)
        words = [w.upper() if ss.get("uppercase") else w for w in words]
        space = d.textlength(" ", font=f)
        widths = [d.textlength(w, font=f) for w in words]
        total = sum(widths) + space * (len(words) - 1)
        x = (self.W - total) / 2
        y = self.H * (0.9 if ss.get("position", "bottom") == "bottom" else 0.1)
        ow = max(2, int(ss["outline_px"] * self.H / 1080))
        for i, w in enumerate(words):
            col = ss["highlight_color"] if i == active_idx else ss["color"]
            d.text((x, y), w, font=f, fill=hex2rgb(col), anchor="lm", stroke_width=ow, stroke_fill=hex2rgb(ss["outline_color"]))
            x += widths[i] + space

    def _transition_in(self, frame, scene, t, prev):
        tr = scene.get("transition", "cut")
        if prev is None or tr == "cut":
            return frame
        D = 0.35
        if t >= D:
            return frame
        k = _ease(t / D)
        prev = prev.convert("RGBA")
        if tr == "fade":
            return Image.blend(prev, frame, k)
        if tr == "whip":
            out = Image.new("RGBA", frame.size)
            off = int(self.W * k)
            out.paste(prev, (-off, 0))
            out.paste(frame, (self.W - off, 0))
            return out
        if tr == "zoom":
            z = 1 + 0.6 * k
            w2, h2 = int(self.W / z), int(self.H / z)
            pz = prev.resize((self.W, self.H), Image.BILINEAR,
                             box=((self.W - w2) / 2, (self.H - h2) / 2, (self.W + w2) / 2, (self.H + h2) / 2))
            return Image.blend(pz, frame, k)
        if tr == "flash":
            a = 1 - abs(2 * k - 1)
            base = prev if k < 0.5 else frame
            return Image.blend(base, Image.new("RGBA", frame.size, (255, 255, 255, 255)), a)
        return frame
