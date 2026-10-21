#!/usr/bin/env python3
"""Thumbnail for A1. python3 thumb.py out_dir  -> A1-thumb-16x9.png (1280x720) and A1-thumb-9x16.png (1080x1920)."""
import sys, math
import render as R
from render import Canvas, figure, phone, FG, ACC, WARN

def slash(cv, c, r):
    cv.circle(c, r, outline=(239, 68, 68), w=22)
    a = math.radians(45)
    cv.line((c[0] - r * math.cos(a), c[1] - r * math.sin(a)), (c[0] + r * math.cos(a), c[1] + r * math.sin(a)), w=22, c=(239, 68, 68))

def make(w, h, path):
    R.W, R.H = w, h
    cv = Canvas(); land = w > h
    if land:
        cv.text((60, 250), "PHONE", 175, c=FG, anchor="lm")
        cv.text((60, 450), "DOWN", 175, c=ACC, anchor="lm")
        gx, ground = 1110, 700
    else:
        cv.text((w / 2, 330), "PHONE", 300, c=FG); cv.text((w / 2, 600), "DOWN", 300, c=ACC)
        gx, ground = w / 2 + 110, 1640
    hl, hr_, hd = figure(cv, gx, ground, upL=20, loL=10, upR=-80, loR=-110, smile=0.9)
    p = (hr_[0] - 30, hr_[1] - 70)
    phone(cv, p, ang=14, scroll=0.3, glow=False)
    slash(cv, p, 140)
    cv.out().save(path)

if __name__ == "__main__":
    out = sys.argv[1]
    make(1280, 720, f"{out}/A1-thumb-16x9.png"); make(1080, 1920, f"{out}/A1-thumb-9x16.png")


def make_generic(t, w, h, path):
    """t: {"words": ["PHONE","DOWN"], "prop": "phone", "pose": "point", "slash": false}"""
    R.W, R.H = w, h
    cv = Canvas()
    words = t.get("words", ["WATCH", "THIS"])
    cols = [FG, ACC, WARN]
    for i, wd in enumerate(words[:3]):
        cv.text((60, 230 + i * 200), wd, 175 if len(max(words, key=len)) <= 6 else 118, c=cols[i], anchor="lm")
    gx, ground = 1110, 700
    pose = dict(R.POSES[t.get("pose", "point")]); pose.update(t.get("pose_over", {}))
    hl, hr_, hd = figure(cv, gx, ground, **pose)
    pos = (hr_[0] - 30, hr_[1] - 70) if t.get("pose", "point") == "point" else (gx - 250, 110)
    prop_name = t.get("prop")
    if prop_name:
        R.prop(cv, prop_name, pos, 1.0, 0.3, t)
        if t.get("slash"): slash(cv, pos, 140)
    cv.out().save(path)
