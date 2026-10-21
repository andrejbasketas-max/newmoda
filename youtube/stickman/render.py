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

W, H, FPS, SS = 1080, 1920, 30, 2
BG, FG, ACC, WARN, DIM = (15, 23, 42), (248, 250, 252), (56, 189, 248), (251, 146, 60), (71, 85, 105)
FONT = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"
LW = 14  # stick line width at 1x

def font(size):
    try: return ImageFont.truetype(FONT, size * SS)
    except OSError: return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size * SS)

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
    for s in (-1, 1): cv.circle((head[0] + s * 20 + look * 6, head[1] - 8), 5, fill=c)
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

def label(cv, s, y=250, size=110, c=ACC): cv.text((W/2, y), s, size, c=c)

# ---- scenes: f(cv, t, tt) with t = 0..1 progress in scene, tt = seconds in scene -------------------
G = 1280  # ground line

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

SCENES = {"intro": sc_intro, "day1": sc_day1, "mood": sc_mood, "hours": sc_hours, "reach": sc_reach, "notice": sc_notice}

# ---- timing and captions --------------------------------------------------------------------------
def weight(s): return len(s) + 6 * sum(s.count(p) for p in ".?!") + 2 * s.count(",")

def silences(voice):
    """Midpoints of the pauses in the voiceover (ffmpeg silencedetect)."""
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", voice, "-af", "silencedetect=noise=-32dB:d=0.12", "-f", "null", "-"],
                       capture_output=True, text=True).stderr
    st = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", r)]
    en = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", r)]
    return [(a + b) / 2 for a, b in zip(st, en)]

def chunk(words):
    ww = [weight(x) + 3 for x in words]; out, cur, cw = [], [], 0
    for x, wx in zip(words, ww):
        cur.append(x); cw += wx
        if len(cur) >= 3 or len(" ".join(cur)) >= 15: out.append((" ".join(cur), cw)); cur, cw = [], 0
    if cur: out.append((" ".join(cur), cw))
    return out

def plan(spec, dur, sil=None):
    """Segments are split at . ? ! , - each ends in a pause. If the voiceover has exactly one detected pause
    per segment boundary the pauses are the boundaries; otherwise timing falls back to proportional."""
    segs = []  # (scene index, text)
    for si, sc in enumerate(spec["scenes"]):
        for m in re.findall(r"[^.?!,]+[.?!,]?", sc["text"]):
            if m.strip(): segs.append((si, m.strip()))
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
    return [(v["a"], v["b"], spec["scenes"][si]["scene"], v["caps"]) for si, v in sorted(scenes.items())]

def frame(args):
    i, tl = args; T = i / FPS
    cv = Canvas()
    for a, b, name, caps in tl:
        if a <= T < b or (name == tl[-1][2] and T >= b):
            SCENES[name](cv, min(1.0, (T - a) / max(b - a, 1e-6)), T - a)
            for c0, c1, ch in caps:
                if c0 <= T < c1 or (T >= c1 and (c0, c1, ch) == caps[-1] and name == tl[-1][2]):
                    cv.text((W/2, 1560), ch.upper(), 92, c=FG, stroke=8)
            break
    return cv.out().tobytes()

def main():
    spec = json.load(open(sys.argv[1])); voice, out = sys.argv[2], sys.argv[3]
    dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", voice]))
    tl = plan(spec, dur, silences(voice)); n = int((dur + 0.5) * FPS)
    ff = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                           "-i", "-", "-i", voice, "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
                           "-af", "apad", "-c:a", "aac", "-b:a", "192k", "-t", f"{n / FPS:.3f}", "-movflags", "+faststart", out], stdin=subprocess.PIPE)
    with Pool(4) as p:
        for k, buf in enumerate(p.imap(frame, ((i, tl) for i in range(n)), chunksize=4)):
            ff.stdin.write(buf)
            if k % 60 == 0: print(f"frame {k}/{n}", flush=True)
    ff.stdin.close(); ff.wait(); print("done", out, f"{dur:.1f}s audio")

if __name__ == "__main__":
    main()
