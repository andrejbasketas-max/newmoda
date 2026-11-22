"""Procedural GLAVONJA stickman: one parametric character driven ONLY by config/style.json.

Because every frame is drawn from the same parameters, the character cannot drift
between scenes (the main weakness of diffusion-generated stickmen).

Pose angles are in degrees.  Limb angles: 0 = pointing down, +90 = pointing in the
facing direction, 180 = pointing up, -90 = pointing backwards.
"""
from __future__ import annotations

import math

from PIL import ImageDraw

EXPRESSIONS = ["neutral", "happy", "excited", "shocked", "scared", "angry", "sad",
               "thinking", "smirk", "dead", "determined", "confused"]
ACTIONS = ["idle", "talk", "walk", "run", "jump", "point", "shock", "think", "cheer",
           "scared", "fall", "shrug", "wave", "lie", "sit", "facepalm", "push", "climb", "swim"]


def hex2rgb(h: str, a: int = 255):
    h = h.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), a)


def _ease(x: float) -> float:
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


BASE_POSE = dict(lean=0.0, arm_l_up=-12.0, arm_l_lo=-8.0, arm_r_up=12.0, arm_r_lo=8.0,
                 leg_l_up=-7.0, leg_l_lo=-7.0, leg_r_up=7.0, leg_r_lo=7.0,
                 head_tilt=0.0, body_rot=0.0, y_off=0.0, x_off=0.0, look=0.0)


def pose_for(action: str, t: float, dur: float = 3.0, seed: int = 0) -> dict:
    """Return a pose dict for an action at time t (seconds)."""
    p = dict(BASE_POSE)
    ph = seed * 1.7
    breathe = math.sin(t * 2.2 + ph)
    p["arm_l_up"] += 3 * breathe
    p["arm_r_up"] -= 3 * breathe
    p["y_off"] = 0.004 * breathe

    if action in ("idle", "talk"):
        if action == "talk":
            g = math.sin(t * 3.1 + ph)
            p["arm_r_up"] = 35 + 25 * g
            p["arm_r_lo"] = 95 + 20 * math.sin(t * 4.3 + ph)
            p["head_tilt"] = 4 * math.sin(t * 1.7 + ph)
    elif action in ("walk", "run"):
        run = action == "run"
        speed = 2.6 if run else 1.6
        a = t * speed * 2 * math.pi + ph
        amp = 42 if run else 24
        bend = 85 if run else 30
        for side, off in (("l", 0.0), ("r", math.pi)):
            s = math.sin(a + off)
            p[f"leg_{side}_up"] = amp * s + (10 if run else 0)
            knee = bend * max(0.0, math.sin(a + off - math.pi / 2)) + (12 if run else 4)
            p[f"leg_{side}_lo"] = p[f"leg_{side}_up"] - knee
            p[f"arm_{side}_up"] = -amp * 0.9 * s
            p[f"arm_{side}_lo"] = p[f"arm_{side}_up"] + (90 if run else 25)
        p["lean"] = 14 if run else 3
        p["y_off"] = (0.03 if run else 0.012) * abs(math.sin(a))
    elif action == "jump":
        c = (t % 1.1) / 1.1
        if c < 0.2:                       # crouch
            k = _ease(c / 0.2)
            p.update(leg_l_up=35 * k, leg_l_lo=-40 * k, leg_r_up=40 * k, leg_r_lo=-35 * k,
                     y_off=-0.07 * k, arm_l_up=-40 * k, arm_r_up=-40 * k)
        elif c < 0.75:                    # air
            k = (c - 0.2) / 0.55
            p.update(y_off=0.32 * math.sin(math.pi * k), arm_l_up=-110, arm_l_lo=-135,
                     arm_r_up=110, arm_r_lo=135, leg_l_up=20, leg_l_lo=-30, leg_r_up=-10, leg_r_lo=-20)
        else:                             # land
            k = 1 - _ease((c - 0.75) / 0.25)
            p.update(leg_l_up=30 * k, leg_l_lo=-35 * k, leg_r_up=35 * k, leg_r_lo=-30 * k,
                     y_off=-0.05 * k)
    elif action == "point":
        k = _ease(t / 0.25)
        p["arm_r_up"] = 12 + (95 - 12) * k
        p["arm_r_lo"] = 8 + (95 - 8) * k
        p["lean"] = 4 * k
        p["head_tilt"] = -3
    elif action == "shock":
        k = _ease(t / 0.18)
        jit = math.sin(t * 40) * 1.5 * max(0, 1 - t)
        p.update(arm_l_up=-12 + (-105 + 12) * k, arm_l_lo=-8 + (-135 + 8) * k,
                 arm_r_up=12 + (105 - 12) * k, arm_r_lo=8 + (135 - 8) * k,
                 lean=-12 * k, head_tilt=-6 * k + jit)
        p["y_off"] = 0.06 * math.sin(math.pi * min(1, t / 0.35)) if t < 0.35 else 0
        p["x_off"] = -0.05 * k
    elif action == "think":
        p.update(arm_r_up=25, arm_r_lo=160, arm_l_up=40, arm_l_lo=95, head_tilt=8 + 2 * math.sin(t * 1.5))
        p["look"] = 0.6
    elif action == "cheer":
        w = math.sin(t * 9 + ph)
        p.update(arm_l_up=-112 + 8 * w, arm_l_lo=-132 + 14 * w, arm_r_up=112 - 8 * w,
                 arm_r_lo=132 - 14 * w)
        p["y_off"] = 0.05 * abs(math.sin(t * 4.5 + ph))
    elif action == "scared":
        sh = math.sin(t * 38) * 0.006
        p.update(arm_l_up=55, arm_l_lo=150, arm_r_up=50, arm_r_lo=145, lean=-6,
                 leg_l_up=12, leg_l_lo=-12, leg_r_up=18, leg_r_lo=-8, x_off=sh, head_tilt=-4)
    elif action in ("fall", "lie"):
        k = 1.0 if action == "lie" else _ease(t / 0.55)
        p["body_rot"] = -88 * k
        p["y_off"] = -0.11 * k
        p.update(arm_l_up=-12 + 90 * k, arm_r_up=12 + 70 * k, arm_l_lo=-8 + 100 * k, arm_r_lo=8 + 60 * k,
                 leg_l_up=-7 - 10 * k, leg_r_up=7 + 10 * k)
        if action == "fall" and t < 0.55:
            p["arm_l_up"], p["arm_r_up"] = -120 * (1 - k), 125 * (1 - k)
    elif action == "shrug":
        k = _ease(t / 0.3)
        p.update(arm_l_up=-12 - 38 * k, arm_l_lo=-8 - 162 * k, arm_r_up=12 + 38 * k, arm_r_lo=8 + 162 * k,
                 head_tilt=10 * k)
    elif action == "wave":
        w = math.sin(t * 8 + ph)
        p.update(arm_r_up=105, arm_r_lo=140 + 20 * w)
    elif action == "sit":
        p.update(leg_l_up=85, leg_l_lo=5, leg_r_up=90, leg_r_lo=10, y_off=-0.15, arm_r_up=40, arm_r_lo=80)
    elif action == "facepalm":
        p.update(arm_r_up=40, arm_r_lo=170, head_tilt=12, lean=6)
    elif action == "push":
        p.update(lean=22, arm_l_up=85, arm_l_lo=88, arm_r_up=80, arm_r_lo=85,
                 leg_l_up=25 + 6 * math.sin(t * 5), leg_l_lo=10, leg_r_up=-30, leg_r_lo=-30)
    elif action == "climb":
        a = t * 4
        p.update(arm_l_up=150 + 20 * math.sin(a), arm_l_lo=170, arm_r_up=150 - 20 * math.sin(a), arm_r_lo=170,
                 leg_l_up=40 + 30 * math.sin(a), leg_l_lo=-20, leg_r_up=40 - 30 * math.sin(a), leg_r_lo=-20,
                 y_off=0.02 * math.sin(a * 2))
    elif action == "swim":
        a = t * 5
        p.update(body_rot=-75, y_off=-0.2, arm_l_up=120 + 60 * math.sin(a), arm_l_lo=130 + 60 * math.sin(a),
                 arm_r_up=120 - 60 * math.sin(a), arm_r_lo=130 - 60 * math.sin(a),
                 leg_l_up=10 * math.sin(a * 2), leg_r_up=-10 * math.sin(a * 2))
    return p


class Character:
    """Draws the stickman.  `style` is the 'character' block of style.json (+ overrides)."""

    def __init__(self, style: dict, overrides: dict | None = None):
        self.s = dict(style)
        if overrides:
            self.s.update(overrides)

    # ------------------------------------------------------------------ geometry
    def skeleton(self, x: float, ground: float, H: float, pose: dict, facing: int):
        f = 1 if facing >= 0 else -1
        hip = (x + pose["x_off"] * H, ground - 0.31 * H - pose["y_off"] * H)
        thigh = shin = 0.155 * H
        torso = 0.23 * H
        arm = 0.13 * H

        def vec(a, length):
            r = math.radians(a)
            return (math.sin(r) * f * length, math.cos(r) * length)

        lean = math.radians(pose["lean"])
        neck = (hip[0] + math.sin(lean) * f * torso, hip[1] - math.cos(lean) * torso)
        pts = {"hip": hip, "neck": neck}
        for side in ("l", "r"):
            v = vec(pose[f"leg_{side}_up"], thigh)
            knee = (hip[0] + v[0], hip[1] + v[1])
            v2 = vec(pose[f"leg_{side}_lo"], shin)
            pts[f"knee_{side}"] = knee
            pts[f"foot_{side}"] = (knee[0] + v2[0], knee[1] + v2[1])
            sh = (neck[0] + (hip[0] - neck[0]) * 0.22, neck[1] + (hip[1] - neck[1]) * 0.22)
            v = vec(pose[f"arm_{side}_up"], arm)
            elbow = (sh[0] + v[0], sh[1] + v[1])
            v2 = vec(pose[f"arm_{side}_lo"], arm)
            pts[f"sh_{side}"] = sh
            pts[f"elbow_{side}"] = elbow
            pts[f"hand_{side}"] = (elbow[0] + v2[0], elbow[1] + v2[1])
        r = H * self.s["head_ratio"] / 2
        tilt = math.radians(pose["head_tilt"] + pose["lean"] * 0.5) * f
        head = (neck[0] + math.sin(tilt) * r * 0.92, neck[1] - math.cos(tilt) * r * 0.92)
        pts["head"] = head
        # whole-body rotation around the hip (falls, lying, swimming)
        if abs(pose["body_rot"]) > 0.01:
            br = math.radians(pose["body_rot"]) * f
            c, s_ = math.cos(br), math.sin(br)
            for k, (px, py) in list(pts.items()):
                dx, dy = px - hip[0], py - hip[1]
                pts[k] = (hip[0] + dx * c - dy * s_, hip[1] + dx * s_ + dy * c)
        return pts, r, tilt + (math.radians(pose["body_rot"]) * f)

    # ------------------------------------------------------------------ drawing
    def draw(self, d: ImageDraw.ImageDraw, xf, x: float, ground: float, H: float, pose: dict,
             expression: str = "neutral", facing: int = 1, mouth_open: float = 0.0,
             t: float = 0.0, blink_seed: int = 0, rim=None):
        """xf(x, y) -> canvas coords; xs = scale factor world->canvas."""
        X, S = xf
        s = self.s
        pts, r, head_rot = self.skeleton(x, ground, H, pose, facing)
        lw = max(2, int(s["line_width_px"] * S * H / s["height_px"]))
        col = hex2rgb(s.get("body_color", s["line_color"]))
        line = hex2rgb(s["line_color"])

        def L(a, b, w=lw, c=col):
            pa, pb = X(*pts[a]) if isinstance(a, str) else X(*a), X(*pts[b]) if isinstance(b, str) else X(*b)
            d.line([pa, pb], fill=c, width=w)
            for q in (pa, pb):
                d.ellipse([q[0] - w / 2, q[1] - w / 2, q[0] + w / 2, q[1] + w / 2], fill=c)

        back, front = ("l", "r") if facing >= 0 else ("r", "l")
        if rim:  # light outline so a black body stays readable on dark backgrounds
            rc, rw = hex2rgb(rim[0], rim[1]), int(lw * 1.9)
            for side in (back, front):
                L("hip", f"knee_{side}", rw, rc); L(f"knee_{side}", f"foot_{side}", rw, rc)
                L(f"sh_{side}", f"elbow_{side}", rw, rc); L(f"elbow_{side}", f"hand_{side}", rw, rc)
            L("hip", "neck", rw, rc)
            hx0, hy0 = X(*pts["head"])
            R0 = r * S + lw * 0.9
            d.ellipse([hx0 - R0, hy0 - R0, hx0 + R0, hy0 + R0], fill=rc)

        # limbs (back side first)
        for side in (back, front):
            L("hip", f"knee_{side}"); L(f"knee_{side}", f"foot_{side}")
        if s.get("shirt"):
            sc = hex2rgb(s["shirt_color"])
            L("hip", "neck", w=int(lw * 2.6), c=sc)
        L("hip", "neck")
        for side in (back, front):
            L(f"sh_{side}", f"elbow_{side}"); L(f"elbow_{side}", f"hand_{side}")
        if s.get("outfit"):
            self._outfit(d, X, pts, r, S, lw, facing, H)
        # head (white sphere with soft shading, like the channel)
        hx, hy = X(*pts["head"])
        R = r * S
        d.ellipse([hx - R, hy - R, hx + R, hy + R], fill=hex2rgb(s.get("head_shade", s["head_fill"])))
        f_ = 1 if facing >= 0 else -1
        d.ellipse([hx - R * 0.97 - f_ * R * 0.08, hy - R * 0.99, hx + R * 0.9 - f_ * R * 0.08, hy + R * 0.86],
                  fill=hex2rgb(s["head_fill"]))
        d.ellipse([hx - R, hy - R, hx + R, hy + R], outline=line, width=lw)
        self._face(d, hx, hy, R, lw, expression, facing, mouth_open, t, blink_seed, head_rot,
                   look=pose.get("look", 0.0))
        self._accessory(d, hx, hy, R, lw, facing)
        return pts

    def _outfit(self, d, X, pts, r, S, lw, facing, H):
        """GLAVONJA's outfit seen on the channel: green puffer vest, orange scarf, white gloves, brown boots."""
        s = self.s
        ink = hex2rgb(s["line_color"])
        hip, neck = pts["hip"], pts["neck"]
        # puffer vest: a rounded quad around the torso
        vx, vy = neck[0] - hip[0], neck[1] - hip[1]
        L = math.hypot(vx, vy) or 1
        nx, ny = -vy / L, vx / L
        w_top, w_bot = 0.085 * H, 0.075 * H
        top = (neck[0] - vx * 0.05, neck[1] - vy * 0.05)
        bot = (hip[0] + vx * 0.02, hip[1] + vy * 0.02)
        poly = [(top[0] + nx * w_top, top[1] + ny * w_top), (top[0] - nx * w_top, top[1] - ny * w_top),
                (bot[0] - nx * w_bot, bot[1] - ny * w_bot), (bot[0] + nx * w_bot, bot[1] + ny * w_bot)]
        P = [X(*q) for q in poly]
        d.polygon(P, fill=hex2rgb(s["vest_color"]))
        for k in (0.3, 0.55, 0.8):   # quilting
            a = (top[0] + (bot[0] - top[0]) * k, top[1] + (bot[1] - top[1]) * k)
            wk = w_top + (w_bot - w_top) * k
            d.line([X(a[0] + nx * wk * 0.95, a[1] + ny * wk * 0.95), X(a[0] - nx * wk * 0.95, a[1] - ny * wk * 0.95)],
                   fill=hex2rgb(s["vest_dark"]), width=max(2, lw // 2))
        d.line(P + [P[0]], fill=ink, width=max(2, int(lw * 0.8)), joint="curve")
        # scarf: band at the neck + hanging end
        sc = hex2rgb(s["scarf_color"])
        n1 = (neck[0] + nx * w_top * 1.1 + vx * -0.12, neck[1] + ny * w_top * 1.1 - vy * 0.12)
        n2 = (neck[0] - nx * w_top * 1.1 + vx * -0.12, neck[1] - ny * w_top * 1.1 - vy * 0.12)
        d.line([X(*n1), X(*n2)], fill=sc, width=int(0.035 * H * S))
        f = 1 if facing >= 0 else -1
        tail0 = (neck[0] + f * 0.035 * H - vx * 0.12, neck[1] - vy * 0.12)
        d.line([X(*tail0), X(tail0[0] + f * 0.012 * H, tail0[1] + 0.11 * H)], fill=sc, width=int(0.03 * H * S))
        # gloves + boots
        for side in ("l", "r"):
            gx, gy = X(*pts[f"hand_{side}"])
            gr = 0.03 * H * S
            d.ellipse([gx - gr, gy - gr, gx + gr, gy + gr], fill=hex2rgb(s["glove_color"]), outline=ink, width=max(2, lw // 2))
            fx, fy = pts[f"foot_{side}"]
            kx, ky = pts[f"knee_{side}"]
            bx0, by0 = X(fx + (kx - fx) * 0.32, fy + (ky - fy) * 0.32)
            bx1, by1 = X(fx + f * 0.035 * H, fy + 0.008 * H)
            bw = int(0.038 * H * S)
            d.line([bx0, by0, (bx0 + bx1) / 2 - f * bw * 0.2, by1 - bw * 0.3], fill=hex2rgb(s["boot_color"]), width=bw)
            d.ellipse([min(bx0, bx1) - bw * 0.5, by1 - bw * 0.85, max(bx0, bx1) + bw * 0.4, by1 + bw * 0.15],
                      fill=hex2rgb(s["boot_color"]))

    def _face(self, d, hx, hy, R, lw, expr, facing, mouth_open, t, blink_seed, rot, look=0.0):
        s = self.s
        f = 1 if facing >= 0 else -1
        ink = hex2rgb(s["eye_color"])
        cos, sin = math.cos(rot), math.sin(rot)

        def P(u, v):  # face-local (u right, v down) in units of R -> canvas
            u = u + 0.13 * f
            return (hx + (u * cos - v * sin) * R, hy + (u * sin + v * cos) * R)

        er = s["eye_size"] * R
        ey = s["eye_height"]
        sp = s["eye_spacing"]
        blink = ((t + 1.3 + blink_seed * 0.77) % 3.7) < 0.12
        big = expr in ("shocked", "scared", "confused")
        lookv = -0.06 * look
        for i, side in enumerate((-1, 1)):
            cx, cy = P(side * sp, ey + lookv)
            if expr == "dead":
                k = er * 1.1
                d.line([cx - k, cy - k, cx + k, cy + k], fill=ink, width=max(2, lw // 2))
                d.line([cx - k, cy + k, cx + k, cy - k], fill=ink, width=max(2, lw // 2))
                continue
            if blink and not big:
                d.line([cx - er, cy, cx + er, cy], fill=ink, width=max(2, lw // 2))
                continue
            if expr == "happy" and not big:
                d.arc([cx - er * 1.2, cy - er * 0.9, cx + er * 1.2, cy + er * 1.3], 200, 340, fill=ink,
                      width=max(2, int(lw * 0.6)))
                continue
            if big:
                k = er * 1.9
                d.ellipse([cx - k, cy - k * 1.15, cx + k, cy + k * 1.15], fill=(255, 255, 255, 255),
                          outline=ink, width=max(2, lw // 2))
                pr = er * 0.75
                px_ = cx + 0.25 * k * f
                d.ellipse([px_ - pr, cy - pr, px_ + pr, cy + pr], fill=ink)
            else:
                d.ellipse([cx - er, cy - er * 1.25, cx + er, cy + er * 1.25], fill=ink)
                hl = er * 0.35
                d.ellipse([cx - hl + er * 0.3, cy - er * 0.6 - hl, cx + hl + er * 0.3, cy - er * 0.6 + hl],
                          fill=(255, 255, 255, 255))
            if s.get("brows", True):
                by = ey - 0.27 - (0.08 if big else 0) + lookv
                tilt = {"angry": 0.11, "determined": 0.07, "sad": -0.09, "scared": -0.1,
                        "thinking": (-0.1 if side == 1 else 0.03), "confused": (0.1 if side == 1 else -0.06)}.get(expr, 0)
                inner = -side * 0.08
                outer = side * 0.17
                a = P(side * sp + inner, by + tilt)
                b = P(side * sp + outer, by - tilt * 0.4)
                d.line([a, b], fill=ink, width=max(2, int(lw * 0.55)))
        if s.get("blush") and expr in ("happy", "excited"):
            bc = hex2rgb(s["blush_color"], 160)
            for side in (-1, 1):
                cx, cy = P(side * (sp + 0.08), ey + 0.22)
                d.ellipse([cx - er * 1.3, cy - er * 0.6, cx + er * 1.3, cy + er * 0.6], fill=bc)
        # mouth
        mw = max(2, int(lw * 0.6))
        mx, my = P(0.0, 0.33)
        W = 0.28 * R
        mo = max(0.0, min(1.0, mouth_open))
        if mo > 0.08 or expr in ("shocked", "excited"):
            h = R * (0.05 + 0.2 * max(mo, 0.5 if expr == "shocked" else 0.35 if expr == "excited" else 0))
            w = W * (0.55 if expr == "shocked" else 0.8)
            d.ellipse([mx - w, my - h * 0.6, mx + w, my + h], fill=hex2rgb(s["mouth_fill"]), outline=ink, width=mw)
        elif expr in ("happy",):
            d.chord([mx - W, my - W * 0.7, mx + W, my + W * 0.8], 0, 180, fill=hex2rgb(s["mouth_fill"]),
                    outline=ink, width=mw)
        elif expr in ("sad", "angry", "scared"):
            d.arc([mx - W * 0.8, my, mx + W * 0.8, my + W * 1.0], 200, 340, fill=ink, width=mw)
        elif expr == "smirk":
            d.arc([mx - W * 0.2, my - W * 0.8, mx + W * 1.0, my + W * 0.3], 20, 120, fill=ink, width=mw)
        elif expr in ("thinking", "confused", "determined", "dead"):
            d.line([mx - W * 0.55, my + W * 0.15, mx + W * 0.5, my - W * 0.05], fill=ink, width=mw)
        else:
            d.arc([mx - W * 0.75, my - W * 0.7, mx + W * 0.75, my + W * 0.45], 30, 150, fill=ink, width=mw)
        if expr == "scared":
            sx, sy = P(-0.62 * f, -0.35)
            k = R * 0.09
            d.polygon([(sx, sy - k * 2), (sx - k, sy), (sx + k, sy)], fill=(120, 190, 255, 255))
            d.ellipse([sx - k, sy - k, sx + k, sy + k], fill=(120, 190, 255, 255))

    def _accessory(self, d, hx, hy, R, lw, facing):
        a = self.s.get("accessory", "none")
        if a in (None, "", "none"):
            return
        c = hex2rgb(self.s.get("accessory_color", "#E53935"))
        ink = hex2rgb(self.s["line_color"])
        f = 1 if facing >= 0 else -1
        if a == "cap":
            d.chord([hx - R, hy - R * 1.02, hx + R, hy + R * 0.6], 180, 360, fill=c, outline=ink, width=lw)
            x0, x1 = sorted((hx + f * R * 0.4, hx + f * R * 1.45))
            d.rectangle([x0, hy - R * 0.28, x1, hy - R * 0.12], fill=c, outline=ink, width=max(2, lw // 2))
        elif a == "glasses":
            for side in (-1, 1):
                cx = hx + (side * self.s["eye_spacing"] + 0.13 * f) * R
                cy = hy + self.s["eye_height"] * R
                k = R * 0.2
                d.ellipse([cx - k, cy - k, cx + k, cy + k], outline=c, width=max(2, lw // 2))
            d.line([hx + (-self.s["eye_spacing"] + 0.13 * f) * R + R * 0.2, hy + self.s["eye_height"] * R,
                    hx + (self.s["eye_spacing"] + 0.13 * f) * R - R * 0.2, hy + self.s["eye_height"] * R],
                   fill=c, width=max(2, lw // 2))
        elif a == "bandana":
            d.rectangle([hx - R * 0.98, hy - R * 0.62, hx + R * 0.98, hy - R * 0.4], fill=c)
            d.polygon([(hx - f * R * 0.95, hy - R * 0.5), (hx - f * R * 1.45, hy - R * 0.2),
                       (hx - f * R * 1.35, hy - R * 0.65)], fill=c)
        elif a == "tophat":
            d.rectangle([hx - R * 0.95, hy - R * 1.02, hx + R * 0.95, hy - R * 0.86], fill=ink)
            d.rectangle([hx - R * 0.6, hy - R * 1.9, hx + R * 0.6, hy - R * 0.9], fill=ink)
            d.rectangle([hx - R * 0.6, hy - R * 1.12, hx + R * 0.6, hy - R * 0.98], fill=c)
        elif a == "crown":
            pts = [(hx - R * 0.6, hy - R * 0.85), (hx - R * 0.6, hy - R * 1.4), (hx - R * 0.3, hy - R * 1.1),
                   (hx, hy - R * 1.5), (hx + R * 0.3, hy - R * 1.1), (hx + R * 0.6, hy - R * 1.4),
                   (hx + R * 0.6, hy - R * 0.85)]
            d.polygon(pts, fill=(255, 200, 0, 255), outline=ink)
