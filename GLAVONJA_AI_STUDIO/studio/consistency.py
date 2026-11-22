"""Visual consistency against the REAL GLAVONJA channel (PART 1, 3.1, 10).

Reference material = screenshots / the user's own videos placed in references/frames and
references/videos.  From them we measure a "style signature" (palette, line thickness,
brightness, edge density, ink ratio).  Every scene keyframe (and every imported Flow clip)
is compared with the closest reference.  Final export is blocked if a scene fails or if there
are no references (then the video stays a clearly-marked DRAFT).
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

from .core import ROOT, atomic_write_json, ffmpeg, get_logger, load_settings, load_style, now_iso, read_json, run, save_style

REF_DIR = ROOT / "references"
SIG_PATH = REF_DIR / "signatures.json"
IMG_EXT = (".png", ".jpg", ".jpeg", ".webp", ".bmp")
VID_EXT = (".mp4", ".mov", ".mkv", ".webm", ".avi")


# --------------------------------------------------------------------------- signature
def signature(img: Image.Image) -> dict:
    im = img.convert("RGB").resize((320, 180), Image.BILINEAR)
    a = np.asarray(im).astype(np.float32)
    lum = a @ np.array([0.299, 0.587, 0.114], dtype=np.float32)
    mx, mn = a.max(axis=2), a.min(axis=2)
    sat = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1), 0)
    gx = np.abs(np.diff(lum, axis=1))[:-1, :]
    gy = np.abs(np.diff(lum, axis=0))[:, :-1]
    edges = (np.hypot(gx, gy) > 40).mean()
    dark = lum < 60
    # line thickness: median horizontal run length of dark pixels on a 1080p-equivalent scale
    full = img.convert("L")
    scale = 1080 / full.height
    fa = np.asarray(full.resize((int(full.width * scale), 1080))) < 70
    runs = []
    for row in fa[::12]:
        r = np.diff(np.concatenate(([0], row.astype(np.int8), [0])))
        starts, ends = np.where(r == 1)[0], np.where(r == -1)[0]
        lens = ends - starts
        runs.extend(int(x) for x in lens if 2 <= x <= 40)
    thick = float(np.median(runs)) if runs else 0.0
    q = im.quantize(colors=8, method=Image.Quantize.MEDIANCUT)
    pal = q.getpalette()[:24]
    counts = sorted(q.getcolors(), reverse=True)
    palette = [{"rgb": pal[i * 3:i * 3 + 3], "frac": round(c / (320 * 180), 4)} for c, i in counts]
    return {"brightness": float(lum.mean() / 255), "saturation": float(sat.mean()), "edges": float(edges),
            "ink": float(dark.mean()), "white": float((lum > 235).mean()), "line_px": thick, "palette": palette}


def _pal_dist(p1, p2) -> float:
    """Weighted nearest-colour distance between two palettes (0..1)."""
    def one_way(a, b):
        tot = 0.0
        for c in a:
            d = min(math.dist(c["rgb"], o["rgb"]) for o in b) / 441.7
            tot += c["frac"] * d
        return tot / max(1e-6, sum(c["frac"] for c in a))
    return (one_way(p1, p2) + one_way(p2, p1)) / 2


def distance(s: dict, r: dict) -> dict:
    parts = {
        "palette": _pal_dist(s["palette"], r["palette"]),
        "brightness": abs(s["brightness"] - r["brightness"]),
        "saturation": abs(s["saturation"] - r["saturation"]),
        "edges": min(1.0, abs(s["edges"] - r["edges"]) * 5),
        "line": min(1.0, abs(s["line_px"] - r["line_px"]) / max(4.0, r["line_px"])) if r["line_px"] else 0.0,
    }
    w = {"palette": 0.35, "brightness": 0.15, "saturation": 0.15, "edges": 0.15, "line": 0.20}
    parts["total"] = sum(parts[k] * w[k] for k in w)
    return parts


# --------------------------------------------------------------------------- references
def extract_video_frames(every_sec: float = 4.0, max_per_video: int = 40, log=print) -> int:
    vids = [p for p in (REF_DIR / "videos").glob("*") if p.suffix.lower() in VID_EXT]
    out_dir = REF_DIR / "frames"
    out_dir.mkdir(parents=True, exist_ok=True)
    n = 0
    for v in vids:
        pattern = out_dir / f"vid_{v.stem[:30]}_%03d.png"
        if list(out_dir.glob(f"vid_{v.stem[:30]}_*.png")):
            continue
        run([ffmpeg(), "-y", "-loglevel", "error", "-i", str(v), "-vf", f"fps=1/{every_sec},scale=1280:-2",
             "-frames:v", str(max_per_video), str(pattern)])
        k = len(list(out_dir.glob(f"vid_{v.stem[:30]}_*.png")))
        n += k
        log(f"  extracted {k} frames from {v.name}")
    return n


def reference_files() -> list[Path]:
    return sorted(p for p in (REF_DIR / "frames").glob("*") if p.suffix.lower() in IMG_EXT)


def build_signatures(log=print) -> dict:
    extract_video_frames(log=log)
    files = reference_files()
    old = read_json(SIG_PATH, {"refs": {}})
    refs = {}
    for f in files:
        key = f"{f.name}:{f.stat().st_size}"
        refs[key] = old["refs"].get(key) or {"file": f.name, **signature(Image.open(f))}
    data = {"updated": now_iso(), "count": len(refs), "refs": refs}
    atomic_write_json(SIG_PATH, data)
    log(f"  {len(refs)} reference frames analysed")
    return data


def has_references() -> bool:
    return bool(read_json(SIG_PATH, {"refs": {}})["refs"]) or bool(reference_files())


def check_image(img: Image.Image, refs: dict | None = None) -> dict:
    refs = refs or read_json(SIG_PATH, {"refs": {}})["refs"]
    if not refs:
        return {"status": "unverified", "reason": "no channel reference frames (references/frames is empty)"}
    s = signature(img)
    best = min(((distance(s, r), r["file"]) for r in refs.values()), key=lambda x: x[0]["total"])
    lim = load_settings()["consistency"]["max_distance"]
    return {"status": "pass" if best[0]["total"] <= lim else "fail", "distance": round(best[0]["total"], 3),
            "closest_reference": best[1], "parts": {k: round(v, 3) for k, v in best[0].items()}, "limit": lim}


# --------------------------------------------------------------------------- style learning
def _hex(rgb):
    return "#%02X%02X%02X" % tuple(int(x) for x in rgb)


def learn_style(log=print) -> dict:
    """Measure the references and write the measurements into config/style.json.

    Measured values update only things that can be measured reliably (line thickness,
    colours, background brightness). The style stays "verified": false until the user
    approves the side-by-side comparison in the dashboard (/glavonja-style approve).
    """
    sigs = build_signatures(log)["refs"]
    if not sigs:
        raise RuntimeError("No reference frames. Put screenshots in references/frames or your own videos in references/videos.")
    vals = list(sigs.values())
    line = float(np.median([v["line_px"] for v in vals if v["line_px"] > 0] or [0]))
    colours = {}
    for v in vals:
        for c in v["palette"]:
            k = tuple(int(x) // 16 * 16 for x in c["rgb"])
            colours[k] = colours.get(k, 0) + c["frac"]
    ranked = sorted(colours.items(), key=lambda kv: -kv[1])
    light = [k for k, _ in ranked if sum(k) / 3 > 200]
    sat = sorted(ranked, key=lambda kv: -(max(kv[0]) - min(kv[0])) * kv[1])
    accents = [k for k, _ in sat if max(k) - min(k) > 80][:3]
    st = load_style()
    meas = {"measured_at": now_iso(), "frames": len(vals), "median_line_px_at_1080p": round(line, 1),
            "mean_brightness": round(float(np.mean([v["brightness"] for v in vals])), 3),
            "mean_saturation": round(float(np.mean([v["saturation"] for v in vals])), 3),
            "dominant_colours": [_hex(k) for k, _ in ranked[:10]], "accent_candidates": [_hex(k) for k in accents]}
    st["measured_from_references"] = meas
    if line >= 2:
        st["character"]["line_width_px"] = int(round(line))
    if light:
        st["palette"]["background_default"] = _hex(light[0])
    for name, k in zip(("accent", "accent2", "accent3"), accents):
        st["palette"][name] = _hex(k)
    st["status"] = "MEASURED from reference frames - waiting for your visual approval"
    st["verified"] = False
    save_style(st)
    log(f"  style.json updated from {len(vals)} frames (line {line:.1f}px, accents {meas['accent_candidates']})")
    return meas


def comparison_sheet(test_frames: list[Path], out: Path) -> Path:
    """Side-by-side: real channel frames (top) vs studio test scene frames (bottom)."""
    refs = reference_files()[:4]
    W, H = 480, 270
    cols = max(len(refs), len(test_frames), 1)
    sheet = Image.new("RGB", (cols * W, 2 * H + 60), (30, 30, 30))
    d = ImageDraw.Draw(sheet)
    d.text((10, 5), "REAL GLAVONJA CHANNEL (references/frames)" if refs else "NO REFERENCES YET - add screenshots to references/frames",
           fill=(255, 255, 0))
    d.text((10, H + 35), "GLAVONJA AI STUDIO test scene", fill=(255, 255, 0))
    for i, f in enumerate(refs):
        sheet.paste(Image.open(f).convert("RGB").resize((W, H)), (i * W, 25))
    for i, f in enumerate(test_frames[:cols]):
        sheet.paste(Image.open(f).convert("RGB").resize((W, H)), (i * W, H + 55))
    out.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out)
    return out
