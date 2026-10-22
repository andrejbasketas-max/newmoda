#!/usr/bin/env python3
"""Stickman Short renderer: spec.json + voiceover.mp3 -> 1080x1920 mp4.

    python3 render.py spec.json voice.mp3 out.mp4

spec.json: {"title": "...", "scenes": [{"scene": "intro|day1|mood|hours|reach|notice|...", "text": "narration for this scene"}]}
Scene length and caption timing are proportional to the characters spoken (plus a short pause on
sentence ends), so sync is approximate - check it by watching, not by trusting it.
"""
import json, math, re, subprocess, sys
from multiprocessing import Pool
from PIL import Image, ImageDraw, ImageFont

import os
W, H, FPS, SS = int(os.environ.get("YT_W", 1080)), int(os.environ.get("YT_H", 1920)), 30, 2  # YT_W/YT_H=1920/1080 for landscape
BG, FG, ACC, WARN, DIM = (15, 23, 42), (248, 250, 252), (56, 189, 248), (251, 146, 60), (71, 85, 105)
FONT = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"
LW = 14  # stick line width at 1x

def font(size):
    try: return ImageFont.truetype(FONT, size * SS)
    except OSError: return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size * SS)

CUR_TT = 0.0

def ease(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)

class Canvas:
    def __init__(self):
        self.im = Image.new("RGB", (W * SS, H * SS), BG)
        self.d = ImageDraw.Draw(self.im)
    def line(self, a, b, w=LW, c=FG):
        self.d.line([(a[0]*SS, a[1]*SS), (b[0]*SS, b[1]*SS)], fill=c, width=int(w*SS))
        r = w * SS / 2
        for p in (a, b): self.d.ellipse([p[0]*SS-r, p[1]*SS-r, p[0]*SS+r, p[1]*SS+r], fill=c)
    def circle(self, c0, r, fill=None, outline=None, w=LW):
        x, y = c0[0]*SS, c0[1]*SS
        self.d.ellipse([x-r*SS, y-r*SS, x+r*SS, y+r*SS], fill=fill, outline=outline, width=int(w*SS))
    def rect(self, box, r=0, fill=None, outline=None, w=6):
        b = [v*SS for v in box]
        self.d.rounded_rectangle(b, radius=r*SS, fill=fill, outline=outline, width=int(w*SS))
    def text(self, xy, s, size, c=FG, anchor="mm", stroke=0):
        self.d.text((xy[0]*SS, xy[1]*SS), s, font=font(size), fill=c, anchor=anchor,
                    stroke_width=stroke*SS, stroke_fill=(0, 0, 0))
    def arc(self, c0, r, a0, a1, w=LW, c=FG):
        x, y = c0[0]*SS, c0[1]*SS
        self.d.arc([x-r*SS, y-r*SS, x+r*SS, y+r*SS], a0, a1, fill=c, width=int(w*SS))
    def out(self): return self.im.resize((W, H), Image.LANCZOS)

def pol(o, ang, ln):  # angle in degrees, 0 = straight down, positive = toward +x
    a = math.radians(ang); return (o[0] + math.sin(a) * ln, o[1] + math.cos(a) * ln)

def figure(cv, x, ground, upL=20, loL=10, upR=-20, loR=-10, legs=14, lean=0, smile=0.5, c=FG, look=0):
    """Returns hand positions (left, right) so scenes can attach props."""
    leg_u, leg_l, torso, arm_u, arm_l, hr = 120, 120, 190, 95, 95, 58
    hip = (x, ground - leg_u - leg_l)
    neck = (hip[0] + math.sin(math.radians(lean)) * torso, hip[1] - math.cos(math.radians(lean)) * torso)
    for s in (-1, 1):
        k = pol(hip, s * legs, leg_u); f = (k[0] + s * 6, ground)
        cv.line(hip, k, c=c); cv.line(k, f, c=c)
        cv.line(f, (f[0] + s * 34, ground), c=c)
    cv.line(hip, neck, c=c)
    sh = (neck[0], neck[1] + 28)
    el = pol(sh, upL, arm_u); hl = pol(el, loL, arm_l); cv.line(sh, el, c=c); cv.line(el, hl, c=c)
    er = pol(sh, upR, arm_u); hr_ = pol(er, loR, arm_l); cv.line(sh, er, c=c); cv.line(er, hr_, c=c)
    head = (neck[0] + math.sin(math.radians(lean)) * 40, neck[1] - hr - 8)
    cv.circle(head, hr, fill=BG, outline=c)
    blink = (CUR_TT + 1.7) % 3.3 < 0.13
    for s in (-1, 1):
        ep = (head[0] + s * 20 + look * 6, head[1] - 8)
        cv.line((ep[0] - 7, ep[1]), (ep[0] + 7, ep[1]), w=4, c=c) if blink else cv.circle(ep, 5, fill=c)
    cv.arc((head[0] + look * 6, head[1] + 10 - 14 * smile), 22, 20 if smile >= 0 else 200, 160 if smile >= 0 else 340, w=6, c=c) if abs(smile) > 0.05 else cv.line((head[0]-16, head[1]+22), (head[0]+16, head[1]+22), w=6, c=c)
    return hl, hr_, head

def phone(cv, c0, ang=0, scroll=0.0, glow=True):
    w, h = 120, 210
    pts = [(-w/2, -h/2), (w/2, -h/2), (w/2, h/2), (-w/2, h/2)]
    ca, sa = math.cos(math.radians(ang)), math.sin(math.radians(ang))
    P = lambda p: (c0[0] + p[0]*ca - p[1]*sa, c0[1] + p[0]*sa + p[1]*ca)
    cv.d.polygon([(P(p)[0]*SS, P(p)[1]*SS) for p in pts], fill=(30, 41, 59), outline=ACC if glow else FG, width=6*SS)
    for i in range(4):
        yy = -h/2 + 30 + ((i * 46 + scroll * 120) % 184)
        a, b = P((-w/2 + 16, yy)), P((w/2 - 16, yy))
        cv.line(a, b, w=10, c=ACC if glow else DIM)

def label(cv, s, y=250, size=110, c=ACC):
    k = 0.75 + 0.25 * ease(CUR_TT / 0.25)  # headline pops in
    size = int(size * k)
    while size > 40 and font(size).getlength(s) / SS > W - 100: size -= 4  # never wider than the frame
    cv.text((W/2, y), s, size, c=c)

# ---- scenes: f(cv, t, tt) with t = 0..1 progress in scene, tt = seconds in scene -------------------
G = 1280 if H > W else H - 170  # ground line

def sc_intro(cv, t, tt):
    label(cv, "7 DAYS", 250, 150, FG); label(cv, "NO SCROLLING", 400, 96, ACC)
    reach = 0.5 + 0.5 * math.sin(tt * 3)
    hl, hr_, hd = figure(cv, W/2 - 60, G, upL=10, loL=-5, upR=-60 + 10 * reach, loR=-120, smile=-0.3)
    phone(cv, (hr_[0] - 20, hr_[1] - 70), ang=10, scroll=tt)
    for i, s in enumerate("???"):
        cv.text((hd[0] + 110 + i * 40, hd[1] - 120 - i * 40 - 10 * math.sin(tt * 4 + i)), s, 70 + i * 14, c=WARN)

def sc_day1(cv, t, tt):
    label(cv, "DAY 1", 250, 150, WARN)
    cyc = (tt * 0.9) % 1.0
    reach = ease(min(cyc * 3, 1)) * (1 - ease((cyc - 0.55) * 4))
    tbl_y = G - 230
    cv.rect((W/2 + 130, tbl_y, W/2 + 450, tbl_y + 24), fill=DIM)
    cv.line((W/2 + 160, tbl_y + 24), (W/2 + 160, G), c=DIM); cv.line((W/2 + 420, tbl_y + 24), (W/2 + 420, G), c=DIM)
    phone(cv, (W/2 + 290, tbl_y - 105), ang=-80, scroll=tt * 0.5, glow=reach > 0.5)
    hl, hr_, hd = figure(cv, W/2 - 140, G, upL=20, loL=10, upR=-30 - (-120) * 0 + 130 * reach, loR=-20 + 80 * reach, lean=6 * reach, smile=-0.4, look=1)
    if reach > 0.6: cv.text((hd[0] + 120, hd[1] - 110), "!", 120, c=WARN)

def sc_mood(cv, t, tt):
    label(cv, "CUT BACK ON SOCIAL MEDIA", 250, 62, FG)
    figure(cv, W/2 - 120, G, upL=-150, loL=-170, upR=150, loR=170, smile=0.4 + 0.5 * ease(t))
    bx, by, bh = W/2 + 300, G - 520, 520
    cv.rect((bx - 40, by, bx + 40, by + bh), r=30, outline=FG, w=8)
    fill = 90 + 120 * ease(t)
    cv.rect((bx - 28, by + bh - 12 - fill, bx + 28, by + bh - 12), r=22, fill=ACC)
    cv.text((bx, by - 50), "MOOD", 60, c=FG); cv.text((bx, by + bh + 55), "small ↑", 56, c=ACC)
    sx, sy = W/2 - 120, 520
    for k in range(10):
        a = math.radians(k * 36 + tt * 40)
        cv.line((sx + math.cos(a) * 85, sy + math.sin(a) * 85), (sx + math.cos(a) * 130, sy + math.sin(a) * 130), w=10, c=WARN)
    cv.circle((sx, sy), 62, fill=WARN)

def sc_hours(cv, t, tt):
    label(cv, "+ HOURS", 250, 150, ACC)
    cx, cy = W/2 + 230, 700
    cv.circle((cx, cy), 190, outline=FG, w=14)
    for k in range(12):
        a = math.radians(k * 30); cv.line((cx + math.sin(a) * 160, cy - math.cos(a) * 160), (cx + math.sin(a) * 180, cy - math.cos(a) * 180), w=8)
    am, ah = tt * 220, tt * 18
    cv.line((cx, cy), (cx + math.sin(math.radians(am)) * 150, cy - math.cos(math.radians(am)) * 150), w=10, c=ACC)
    cv.line((cx, cy), (cx + math.sin(math.radians(ah)) * 100, cy - math.cos(math.radians(ah)) * 100), w=14)
    figure(cv, W/2 - 200, G, upL=40, loL=60, upR=-40, loR=-60, smile=0.9)

def sc_reach(cv, t, tt):
    label(cv, "7 DAYS", 250, 150, FG)
    n = int(t * 7 + 0.99)
    for i in range(7):
        x = 150 + i * 125
        cv.rect((x, 420, x + 100, 560), r=14, outline=ACC if i < n else DIM, w=8)
        if i < n: cv.text((x + 50, 490), str(i + 1), 64, c=ACC)
    cyc = (tt * 1.1) % 1.0
    reach = ease(min(cyc * 3, 1)) * (1 - ease((cyc - 0.5) * 3))
    cv.text((W/2, 700), "how often did you reach?", 58, c=WARN)
    phone(cv, (W/2 + 280, G - 130), ang=-80, scroll=0, glow=False)
    figure(cv, W/2 - 150, G, upL=20, loL=10, upR=-30 + 125 * reach, loR=-20 + 90 * reach, lean=5 * reach, smile=0)

def sc_notice(cv, t, tt):
    label(cv, "YOU FINALLY NOTICE", 250, 90, ACC)
    figure(cv, W/2, G, upL=20, loL=15, upR=-20, loR=-15, smile=0.8, look=0)
    phone(cv, (W/2 + 330, G - 105), ang=-85, scroll=0, glow=False)
    pulse = 1 + 0.08 * math.sin(tt * 5)
    ex, ey = W/2, 640
    for sgn in (-1, 1):
        pts = [(ex + x, ey + sgn * 70 * pulse * (1 - (x / 130) ** 2)) for x in range(-130, 131, 10)]
        for a, b in zip(pts, pts[1:]): cv.line(a, b, w=10, c=ACC)
    cv.circle((ex, ey), 34 * pulse, fill=ACC)

# ---- generic, parameter-driven scenes -----------------------------------------------------------------
POSES = {
    "idle": dict(upL=20, loL=10, upR=-20, loR=-10, smile=0.4),
    "happy": dict(upL=-150, loL=-170, upR=150, loR=170, smile=0.9),
    "tired": dict(upL=8, loL=4, upR=-8, loR=-4, lean=14, smile=-0.7, legs=8),
    "shock": dict(upL=-120, loL=-100, upR=120, loR=100, smile=-0.9),
    "think": dict(upL=20, loL=10, upR=-35, loR=-165, smile=0.0),
    "point": dict(upL=20, loL=10, upR=-95, loR=-95, smile=0.3),
    "calm": dict(upL=35, loL=45, upR=-35, loR=-45, smile=0.8),
}
YEL, GRN, RED = (253, 224, 71), (74, 222, 128), (239, 68, 68)

def heart(cv, c0, r, col):
    pts = []
    for k in range(60):
        a = k / 60 * 2 * math.pi
        pts.append((c0[0] + r * 16 * math.sin(a) ** 3 / 16 * 1.0, c0[1] - r * (13 * math.cos(a) - 5 * math.cos(2*a) - 2 * math.cos(3*a) - math.cos(4*a)) / 16))
    cv.d.polygon([(x * SS, y * SS) for x, y in pts], fill=col)

def prop(cv, name, c0, t, tt, a):
    x, y = c0
    lo, hi = a.get("from", 0.5), a.get("to", 0.5)
    v = lo + (hi - lo) * ease(t)
    if name == "phone": phone(cv, c0, ang=-8, scroll=tt)
    elif name == "clock":
        cv.circle(c0, 150, outline=FG, w=12)
        for k in range(12):
            q = math.radians(k * 30); cv.line((x + math.sin(q) * 125, y - math.cos(q) * 125), (x + math.sin(q) * 142, y - math.cos(q) * 142), w=7)
        am = tt * 220
        cv.line(c0, (x + math.sin(math.radians(am)) * 115, y - math.cos(math.radians(am)) * 115), w=9, c=ACC)
        cv.line(c0, (x + math.sin(math.radians(tt * 18)) * 75, y - math.cos(math.radians(tt * 18)) * 75), w=12)
    elif name == "moon":
        cv.circle(c0, 110, fill=YEL); cv.circle((x + 55, y - 35), 98, fill=BG)
        for i, z in enumerate("ZZZ"): cv.text((x + 150 + i * 45, y - 60 - i * 55 - 8 * math.sin(tt * 3 + i)), z, 60 + i * 18, c=ACC)
    elif name == "brain":
        pulse = 1 + 0.04 * math.sin(tt * 4)
        for sx in (-1, 1): cv.circle((x + sx * 52, y), 85 * pulse, outline=ACC, w=12)
        cv.line((x, y - 80), (x, y + 80), w=6, c=ACC)
        for k in range(3):
            cv.arc((x - 52, y + k * 30 - 30), 40, 200, 340, w=6, c=ACC); cv.arc((x + 52, y + k * 30 - 30), 40, 200, 340, w=6, c=ACC)
    elif name == "bulb":
        cv.circle((x, y - 20), 80, fill=YEL); cv.rect((x - 35, y + 50, x + 35, y + 100), r=10, fill=DIM)
        for k in range(8):
            q = math.radians(k * 45 + tt * 20); cv.line((x + math.cos(q) * 105, y - 20 + math.sin(q) * 105), (x + math.cos(q) * 135, y - 20 + math.sin(q) * 135), w=8, c=YEL)
    elif name == "battery":
        cv.rect((x - 90, y - 150, x + 90, y + 150), r=24, outline=FG, w=10); cv.rect((x - 35, y - 175, x + 35, y - 150), r=6, fill=FG)
        col = GRN if v > 0.5 else (WARN if v > 0.25 else RED)
        cv.rect((x - 72, y + 132 - 264 * v, x + 72, y + 132), r=14, fill=col)
    elif name == "meter":
        cv.rect((x - 40, y - 200, x + 40, y + 200), r=30, outline=FG, w=8)
        cv.rect((x - 28, y + 188 - 376 * v, x + 28, y + 188), r=22, fill=a.get("color") and tuple(a["color"]) or ACC)
        cv.text((x, y - 245), a.get("label", ""), 56, c=FG)
    elif name == "heart":
        heart(cv, c0, 130 * (1 + 0.06 * math.sin(tt * 6)), RED)
    elif name == "book":
        cv.rect((x - 150, y - 90, x - 5, y + 90), r=8, fill=(30, 41, 59), outline=ACC, w=8); cv.rect((x + 5, y - 90, x + 150, y + 90), r=8, fill=(30, 41, 59), outline=ACC, w=8)
        for k in range(4): cv.line((x - 120, y - 50 + k * 35), (x - 30, y - 50 + k * 35), w=6, c=DIM); cv.line((x + 30, y - 50 + k * 35), (x + 120, y - 50 + k * 35), w=6, c=DIM)
    elif name == "calendar":
        n = int(a.get("count", 7) * ease(t) + 0.99)
        for i in range(a.get("count", 7)):
            xx = x - 3.5 * 125 + i * 125 + 62
            cv.rect((xx - 50, y - 70, xx + 50, y + 70), r=14, outline=ACC if i < n else DIM, w=8)
            if i < n: cv.text((xx, y), str(i + 1), 60, c=ACC)
    elif name == "eye":
        pulse = 1 + 0.08 * math.sin(tt * 5)
        for sg in (-1, 1):
            pts = [(x + k, y + sg * 70 * pulse * (1 - (k / 130) ** 2)) for k in range(-130, 131, 10)]
            for p, q in zip(pts, pts[1:]): cv.line(p, q, w=10, c=ACC)
        cv.circle(c0, 34 * pulse, fill=ACC)
    elif name == "sun":
        for k in range(10):
            q = math.radians(k * 36 + tt * 40); cv.line((x + math.cos(q) * 85, y + math.sin(q) * 85), (x + math.cos(q) * 130, y + math.sin(q) * 130), w=10, c=WARN)
        cv.circle(c0, 62, fill=WARN)
    elif name == "coffee":
        cv.rect((x - 70, y - 40, x + 70, y + 90), r=20, outline=FG, w=10); cv.arc((x + 70, y + 20), 40, 270, 90, w=10)
        for k in range(3): cv.arc((x - 30 + k * 30, y - 80 - 10 * math.sin(tt * 4 + k)), 18, 0, 180, w=6, c=DIM)
    elif name == "q":
        for i, s in enumerate("???"): cv.text((x + i * 55, y - i * 45 - 10 * math.sin(tt * 4 + i)), s, 90 + i * 16, c=WARN)
    elif name == "text":
        cv.text(c0, a.get("word", ""), a.get("size", 120), c=tuple(a["color"]) if a.get("color") else ACC)

BASE = dict(upL=20, loL=10, upR=-20, loR=-10, legs=14, lean=0, smile=0.4, look=0)

def pose_vals(name, tt):
    if name == "wave":
        return dict(upL=20, loL=10, upR=-135 + 20 * math.sin(tt * 9), loR=-160 + 30 * math.sin(tt * 9), smile=0.9)
    return POSES[name]

def get_pose(a, b, t, tt):
    """Blend pose a -> b with easing, then add breathing and small talking gestures."""
    pa, pb = {**BASE, **pose_vals(a, tt)}, {**BASE, **pose_vals(b or a, tt)}
    k = ease(t)
    p = {key: pa[key] + (pb[key] - pa[key]) * k for key in BASE}
    p["lean"] += 1.2 * math.sin(tt * 2.2)
    if a not in ("wave", "happy", "shock"):
        p["upR"] += 5 * math.sin(tt * 3.1); p["upL"] += 4 * math.sin(tt * 2.3 + 1)
    return p

def sc_beat(cv, t, tt, a):
    """headline + stickman (pose) + one prop. a: headline, sub, pose, prop, side, from, to, color."""
    if a.get("headline"): label(cv, a["headline"], 230, a.get("hsize", 120), tuple(a["hcolor"]) if a.get("hcolor") else ACC)
    if a.get("sub"): cv.text((W/2, 380), a["sub"], 60, c=WARN)
    side = -1 if a.get("side", "right") == "left" else 1
    pose = get_pose(a.get("pose", "idle"), a.get("pose_end"), t, tt)
    figure(cv, W/2 - side * 190, G, **pose)
    if a.get("prop"): prop(cv, a["prop"], (W/2 + side * 250, a.get("py", 760)), t, tt, a)

def sc_compare(cv, t, tt, a):
    label(cv, a.get("headline", ""), 230, 100, FG)
    for k, (key, c) in enumerate((("left", WARN), ("right", ACC))):
        cx = W/2 + (-1 if k == 0 else 1) * 250
        txt, sz = a.get(key, ""), 72
        while sz > 36 and font(sz).getlength(txt) / SS > 480: sz -= 4  # each half is ~500 px wide
        cv.text((cx, 400), txt, sz, c=c)
        pose = dict(POSES[a.get(key + "_pose", "idle")]); figure(cv, cx, G, **pose)
    cv.line((W/2, 470), (W/2, G), w=6, c=DIM)

def sc_bullets(cv, t, tt, a):
    label(cv, a.get("headline", ""), 230, 100, ACC)
    items = a.get("items", []); n = int(t * len(items) + 0.99)
    for i, s in enumerate(items):
        y = 520 + i * 190; on = i < n
        cv.rect((120, y - 70, W - 120, y + 70), r=30, outline=ACC if on else DIM, w=8)
        cv.text((W/2, y), s if on else "", 64, c=FG)
    figure(cv, W/2, G + 120, **POSES["think"]) if a.get("figure") else None

def sc_counter(cv, t, tt, a):
    v = a.get("from", 0) + (a.get("to", 7) - a.get("from", 0)) * ease(t * 1.3)
    cv.text((W/2, 400), f"{v:.0f}", 330, c=tuple(a["color"]) if a.get("color") else ACC)
    cv.text((W/2, 590), a.get("unit", "").strip(), 110, c=tuple(a["color"]) if a.get("color") else ACC)
    cv.text((W/2, 700), a.get("label", ""), 64, c=FG)
    figure(cv, W/2, G + 60, **POSES[a.get("pose", "idle")])

SCENES = {"intro": sc_intro, "day1": sc_day1, "mood": sc_mood, "hours": sc_hours, "reach": sc_reach, "notice": sc_notice,
          "beat": sc_beat, "compare": sc_compare, "bullets": sc_bullets, "counter": sc_counter}

def run_scene(sc, cv, t, tt):
    global CUR_TT
    CUR_TT = tt
    fn = SCENES[sc["scene"]]
    fn(cv, t, tt, sc) if fn.__code__.co_argcount == 4 else fn(cv, t, tt)

# ---- timing and captions --------------------------------------------------------------------------
def weight(s): return len(s) + 6 * sum(s.count(p) for p in ".?!") + 2 * s.count(",")

def silences(voice):
    """Midpoints of the pauses in the voiceover (ffmpeg silencedetect)."""
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", voice, "-af", "silencedetect=noise=-32dB:d=0.12", "-f", "null", "-"],
                       capture_output=True, text=True).stderr
    st = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", r)]
    en = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", r)]
    d = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", voice]))
    return [(a + b) / 2 for a, b in zip(st, en) if a > 0.3 and b < d - 0.05]  # drop leading/trailing silence

def chunk(words):
    ww = [weight(x) + 3 for x in words]; out, cur, cw = [], [], 0
    for x, wx in zip(words, ww):
        cur.append(x); cw += wx
        if len(cur) >= 3 or len(" ".join(cur)) >= 15: out.append((" ".join(cur), cw)); cur, cw = [], 0
    if cur: out.append((" ".join(cur), cw))
    return out

def segments(spec):
    segs = []
    for si, sc in enumerate(spec["scenes"]):
        for m in re.findall(r"[^.?!,]+[.?!,]?", sc["text"]):
            if m.strip(): segs.append((si, m.strip()))
    return segs

def plan(spec, dur, sil=None):
    """Segments are split at . ? ! , - each ends in a pause. If the voiceover has exactly one detected pause
    per segment boundary the pauses are the boundaries; otherwise timing falls back to proportional."""
    segs = segments(spec)
    if sil is not None and len(sil) == len(segs) - 1:
        bounds = [0.0] + list(sil) + [dur]
    else:
        ws = [weight(t) for _, t in segs]; tot = sum(ws); bounds = [0.0]
        for w in ws: bounds.append(bounds[-1] + dur * w / tot)
    scenes = {}
    for (si, text), a, b in zip(segs, bounds, bounds[1:]):
        sc = scenes.setdefault(si, {"a": a, "b": b, "caps": []}); sc["b"] = b
        ch = chunk(text.split()); tw = sum(w for _, w in ch); c0 = a
        for t, w in ch:
            d = (b - a) * w / tw; sc["caps"].append((c0, c0 + d, t)); c0 += d
    return [(v["a"], v["b"], spec["scenes"][si], v["caps"]) for si, v in sorted(scenes.items())]

def draw_caption(im, text):
    from PIL import ImageDraw, ImageFont
    sz = 92
    while True:
        f = ImageFont.truetype(FONT, sz)
        if sz <= 50 or f.getlength(text) <= W - 100: break
        sz -= 4
    ImageDraw.Draw(im).text((W / 2, 1560 if H > W else H - 80), text, font=f, fill=FG, anchor="mm", stroke_width=8, stroke_fill=(0, 0, 0))

def frame(args):
    i, tl = args; T = i / FPS
    cv = Canvas(); caption, zoom, fade = None, 1.0, 1.0
    for idx, (a, b, name, caps) in enumerate(tl):
        if a <= T < b or (name is tl[-1][2] and T >= b):
            t = min(1.0, (T - a) / max(b - a, 1e-6)); tt = T - a
            run_scene(name, cv, t, tt)
            zoom = 1.0 + 0.06 * (t if idx % 2 == 0 else 1 - t)
            fade = ease(tt / 0.18)
            for c0, c1, ch in caps:
                if c0 <= T < c1 or (T >= c1 and (c0, c1, ch) == caps[-1] and name is tl[-1][2]): caption = ch.upper()
            break
    im = cv.out()
    if zoom > 1.001:
        cw, chh = W / zoom, H / zoom; top = min(max(0, (760 if H > W else H / 2 - 40) - chh / 2), H - chh)
        im = im.crop((int(W / 2 - cw / 2), int(top), int(W / 2 + cw / 2), int(top + chh))).resize((W, H), Image.BICUBIC)
    if fade < 1: im = Image.blend(Image.new("RGB", (W, H), BG), im, fade)
    if caption: draw_caption(im, caption)
    return im.tobytes()

def main():
    spec = json.load(open(sys.argv[1])); voice, out = sys.argv[2], sys.argv[3]
    dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", voice]))
    if len(sys.argv) > 4:  # exact segment starts written by make_short.py
        starts = json.load(open(sys.argv[4])); tl = plan(spec, dur, starts[1:])
    else:
        tl = plan(spec, dur, silences(voice))
    n = int((dur + 0.5) * FPS)
    ff = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                           "-i", "-", "-i", voice, "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
                           "-af", "apad", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2", "-t", f"{n / FPS:.3f}", "-movflags", "+faststart", out], stdin=subprocess.PIPE)
    with Pool(4) as p:
        for k, buf in enumerate(p.imap(frame, ((i, tl) for i in range(n)), chunksize=4)):
            ff.stdin.write(buf)
            if k % 60 == 0: print(f"frame {k}/{n}", flush=True)
    ff.stdin.close(); ff.wait(); print("done", out, f"{dur:.1f}s audio")

if __name__ == "__main__":
    main()
