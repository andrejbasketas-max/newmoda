"""AUTOPILOT - daily automation that runs on the user's PC (Windows Task Scheduler) with ZERO Claude usage.

Every run (scheduled every 30 min by scripts/autopilot_install.bat, and also inside the dashboard):
  1. Once a day: research 10 fresh ideas and notify the user (the USER chooses the topic).
  2. Video clips dropped into FLOW_INBOX/ (any file names, in the order of FLOW_REQUESTS.md) are
     assigned to the waiting project's missing scenes and production continues automatically.
  3. Interrupted productions (PC shutdown / crash) are resumed.
  4. Notifies when a video is ready for review or when the user must decide something.
It never approves Google usage or fallbacks on the user's behalf, and never uploads anything.
"""
from __future__ import annotations

import datetime as dt
import os
import shutil
import subprocess
from pathlib import Path

from .core import ROOT, atomic_write_json, get_logger, get_project, list_projects, now_iso, read_json

GLOBAL_INBOX = ROOT / "FLOW_INBOX"
STATE = ROOT / "database" / "autopilot.json"
VIDEO_EXT = (".mp4", ".mov", ".webm")


def notify(title: str, text: str):
    """Windows balloon notification (no extra software). Elsewhere: log only."""
    get_logger().info("NOTIFY: %s - %s", title, text)
    if os.name != "nt":
        return
    t = title.replace("'", "`'")
    x = text.replace("'", "`'")
    ps = ("Add-Type -AssemblyName System.Windows.Forms;Add-Type -AssemblyName System.Drawing;"
          "$n=New-Object System.Windows.Forms.NotifyIcon;$n.Icon=[System.Drawing.SystemIcons]::Information;"
          f"$n.BalloonTipTitle='{t}';$n.BalloonTipText='{x}';$n.Visible=$true;$n.ShowBalloonTip(10000);"
          "Start-Sleep -Seconds 11;$n.Dispose()")
    try:
        subprocess.Popen(["powershell", "-NoProfile", "-WindowStyle", "Hidden", "-Command", ps], creationflags=0x08000000)
    except Exception as e:
        get_logger().warning("notification failed: %s", e)


def assign_global_inbox(p, missing_ids: list[int]) -> int:
    """Move clips from FLOW_INBOX (oldest first) to the project's flow/inbox/scene_XXX.ext for missing scenes."""
    GLOBAL_INBOX.mkdir(exist_ok=True)
    files = sorted((f for f in GLOBAL_INBOX.iterdir() if f.is_file() and f.suffix.lower() in VIDEO_EXT),
                   key=lambda f: f.stat().st_mtime)
    files = [f for f in files if not _still_downloading(f)]
    n = 0
    for sid, f in zip(sorted(missing_ids), files):
        dest = p.path("flow", "inbox", f"scene_{sid:03d}{f.suffix.lower()}")
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(f), dest)
        get_logger().info("[%s] FLOW_INBOX %s -> scene %d", p.id, f.name, sid)
        n += 1
    return n


def _still_downloading(f: Path) -> bool:
    import time
    return time.time() - f.stat().st_mtime < 20  # browser may still be writing it


def run_once(log=print, research=True) -> dict:
    from .production import is_running, run_pipeline
    st = read_json(STATE, {})
    summary = {"time": now_iso(), "actions": []}
    # 1) daily ideas
    today = dt.date.today().isoformat()
    if research and st.get("ideas_date") != today:
        try:
            from .agents.researcher import research_ideas
            res = research_ideas(log_cb=log, refresh=True)
            st["ideas_date"] = today
            summary["actions"].append(f"10 new ideas ({res['mode']})")
            notify("GLAVONJA: 10 novih ideja", "Otvori studio (start.bat) i izaberi temu za danas.")
        except Exception as e:
            summary["actions"].append(f"ideas failed: {e}")
    # 2) + 3) projects
    for pr in sorted(list_projects(), key=lambda x: x["updated"], reverse=True):
        p = get_project(pr["id"])
        if p is None or is_running(p.id) or p.path(".running").exists():
            continue
        b = p.state.get("blocker") or {}
        resume = False
        if p.state["status"] == "waiting" and b.get("kind") == "waiting_flow_clips":
            moved = assign_global_inbox(p, b.get("data", {}).get("missing", []))
            have = [i for i in b.get("data", {}).get("missing", []) if any(
                p.path("flow", "inbox", f"scene_{i:03d}{e}").exists() for e in VIDEO_EXT)]
            if moved or have:
                summary["actions"].append(f"{p.id}: {len(have)} Flow clips found -> continuing")
                resume = True
        elif p.state["status"] in ("interrupted", "running"):
            summary["actions"].append(f"{p.id}: resuming interrupted production")
            resume = True
        if resume:
            before = p.state.get("blocker", {}).get("message")
            res = run_pipeline(p, log)
            p = get_project(pr["id"])
            if res["status"] == "ready_for_review":
                notify("GLAVONJA: video je gotov", f"{p.state['title']} - pregledaj i odobri u studiju.")
            elif res["status"] == "waiting" and p.state["blocker"]["message"] != before:
                notify("GLAVONJA čeka tebe", p.state["blocker"]["message"][:200])
            elif res["status"] == "failed":
                notify("GLAVONJA: greška", p.state.get("last_error", {}).get("error", "")[:200])
    st["last_run"] = summary["time"]
    st.setdefault("history", []).append(summary)
    st["history"] = st["history"][-200:]
    atomic_write_json(STATE, st)
    for a in summary["actions"]:
        log("AUTOPILOT: " + a)
    return summary


def background_loop(interval_sec: int = 600):
    """Used by the dashboard: watch FLOW_INBOX + resume, every few minutes (ideas only via schedule)."""
    import threading
    import time

    def loop():
        while True:
            try:
                run_once(log=lambda *_: None, research=False)
            except Exception as e:
                get_logger().warning("autopilot loop: %s", e)
            time.sleep(interval_sec)
    threading.Thread(target=loop, daemon=True).start()
