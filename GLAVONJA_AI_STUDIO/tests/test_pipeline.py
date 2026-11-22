"""End-to-end pipeline test in an ISOLATED temporary copy of the studio.

It verifies the PART 3.1 rules: Gemini/Flow are never skipped silently (production blocks and asks),
Flow clips that do not match the channel references are rejected, approvals are recorded,
and the final video passes technical QC.  The test plays the role of the user inside the sandbox
copy only; it never touches your real projects or settings and never calls Google.
Run:  python -m pytest tests/test_pipeline.py -s     (set GLAVONJA_TEST_FULLHD=1 for a 1920x1080 test video)
"""
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

SRC = Path(__file__).resolve().parent.parent
SKIP = {".venv", "projects", "outputs", "database", "logs", "backups", "tools", "__pycache__", ".pytest_cache"}

SCRIPT = """# Udica
Zamisli da Zemlja na samo jednu sekundu prestane da se okreće.
Zvuči bezazleno, ali to bi bila najgora sekunda u istoriji čovečanstva.
# Šta se dešava
Ti stojiš na ekvatoru i krećeš se brzinom od oko 1600 kilometara na sat.
Zemlja stane, ali ti ne staneš.
Odjednom letiš kroz vazduh, zajedno sa kućama, drvećem i automobilima.
# Preokret
Ali čekaj, to nije najgori deo.
Okeani nastavljaju da se kreću i ogromni talasi udaraju u gradove.
# Kraj
Dobra vest je da fizika kaže da je ovo praktično nemoguće.
Napiši u komentarima šta bi ti uradio i zaprati GLAVONJU!
"""


@pytest.fixture(scope="module")
def app(tmp_path_factory):
    root = tmp_path_factory.mktemp("studio")
    for item in SRC.iterdir():
        if item.name in SKIP:
            continue
        (shutil.copytree if item.is_dir() else shutil.copy2)(item, root / item.name)
    for d in ("projects", "outputs", "database", "logs"):
        (root / d).mkdir(exist_ok=True)
    full = os.environ.get("GLAVONJA_TEST_FULLHD") == "1"
    settings = {"video": {"width": 1920 if full else 640, "height": 1080 if full else 360, "fps": 24 if full else 12,
                          "preset": "veryfast"},
                "research": {"use_wikipedia": False, "use_google_trends": False, "use_reddit": False},
                "llm": {"order": ["offline"]}, "dashboard": {"open_browser": False}}
    (root / "config" / "settings.json").write_text(json.dumps(settings), encoding="utf-8")
    (root / "script.txt").write_text(SCRIPT, encoding="utf-8")
    return root


def cli(app, *args):
    r = subprocess.run([sys.executable, "glavonja.py", *args], cwd=app, capture_output=True, text=True, encoding="utf-8")
    assert r.returncode == 0, r.stdout + r.stderr
    return r.stdout


def state(app):
    p = next((app / "projects").iterdir())
    return p, json.loads((p / "project_state.json").read_text(encoding="utf-8"))


def ffmpeg():
    sys.path.insert(0, str(SRC))
    from studio.core import ffmpeg as f
    return f()


def test_full_pipeline(app):
    cli(app, "make", "Šta ako Zemlja stane na 1 sekundu?", "--lang", "sr", "--duration", "45", "--script-file", "script.txt")
    p, st = state(app)
    # 1) Gemini is mandatory: without a key production must STOP and ask (never silently use local voice)
    assert st["status"] == "waiting" and st["blocker"]["kind"] == "gemini_unavailable"
    assert st["stages"]["voice"]["status"] == "blocked"
    # 2) user (simulated in this sandbox) explicitly approves the local voice fallback for this video
    cli(app, "approve", "local_voice_fallback")
    cli(app, "continue")
    p, st = state(app)
    # 3) Flow is mandatory: the system asks for approval with a credit estimate before any Flow work
    assert st["blocker"]["kind"] == "approval" and st["blocker"]["data"]["estimate"]["service"] == "Google Flow"
    cli(app, "approve", "flow_generation")
    cli(app, "continue")
    p, st = state(app)
    assert st["blocker"]["kind"] == "waiting_flow_clips"
    assert (p / "flow" / "FLOW_REQUESTS.md").exists()
    n = len(st["blocker"]["data"]["missing"])
    # 4) channel references (sandbox: studio frames stand in for real channel frames)
    refs = app / "references" / "frames"
    for f in (app / "docs").glob("test_scene_*.png"):
        shutil.copy2(f, refs / f.name)
    for f in sorted((p / "scenes").glob("scene_*.png"))[:3]:
        shutil.copy2(f, refs / ("ref_" + f.name))
    # a "Flow clip" in the channel style for scene 1, and an off-style clip for scene 2
    inbox = p / "flow" / "inbox"
    subprocess.run([ffmpeg(), "-y", "-loglevel", "error", "-loop", "1", "-i", str(p / "scenes" / "scene_001.png"), "-t", "6",
                    "-vf", "zoompan=z='1+0.002*on':d=1:s=1280x720,format=yuv420p", "-r", "24", str(inbox / "scene_001.mp4")], check=True)
    subprocess.run([ffmpeg(), "-y", "-loglevel", "error", "-f", "lavfi", "-i", "mandelbrot=s=1280x720:r=24", "-t", "5",
                    "-pix_fmt", "yuv420p", str(inbox / "scene_002.mp4")], check=True)
    cli(app, "continue")
    p, st = state(app)
    clips = json.loads((p / "animations" / "clips.json").read_text(encoding="utf-8"))["clips"]
    assert clips["1"]["source"] == "google_flow" and clips["1"]["consistency"] == "pass"
    assert "2" not in clips and list((p / "flow" / "rejected").glob("scene_002_*"))  # off-style clip rejected
    assert st["blocker"]["kind"] == "waiting_flow_clips" and 2 in st["blocker"]["data"]["missing"]
    # 5) user approves the local animation fallback for the remaining scenes
    cli(app, "approve", "flow_fallback_local")
    out = cli(app, "continue")
    p, st = state(app)
    assert st["status"] == "ready_for_review", out
    rep = json.loads((p / "final" / "production_report.json").read_text(encoding="utf-8"))
    assert rep["technical_ok"], rep
    assert rep["clip_sources"].get("google_flow") == 1 and rep["clip_sources"].get("procedural") == n - 1
    # export is NOT allowed: local voice + local animation + style not approved -> stays DRAFT
    assert st["export"]["status"] == "draft"
    assert len(list((p / "thumbnails").glob("thumb_?.png"))) == 3
    meta = json.loads((p / "final" / "metadata.json").read_text(encoding="utf-8"))
    assert len(meta["titles"]) == 5 and meta["tags"]
    print("\nTEST VIDEO:", SRC.parent, p / "final")
    keep = os.environ.get("GLAVONJA_TEST_KEEP")
    if keep:
        dst = Path(keep)
        dst.mkdir(parents=True, exist_ok=True)
        for f in list((p / "final").glob("*")) + list((p / "thumbnails").glob("thumb_?.png")) + [p / "subtitles" / "subtitles.srt",
                                                                                                 p / "storyboard" / "storyboard_sheet.jpg"]:
            if f.is_file() and f.suffix not in (".wav", ".txt"):
                shutil.copy2(f, dst / f.name)
