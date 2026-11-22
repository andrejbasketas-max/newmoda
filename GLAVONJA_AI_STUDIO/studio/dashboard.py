"""Local web dashboard (stdlib only) - http://127.0.0.1:8765 . Works without Claude Code."""
from __future__ import annotations

import json
import mimetypes
import os
import re
import threading
import traceback
import urllib.parse
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from . import consistency, google_ai
from .core import (ROOT, STAGE_LABELS, STAGES, Project, db_exec, ensure_dirs, get_logger, get_project, list_projects,
                   load_settings, load_style, read_json, save_style, set_setting)

UI = ROOT / "dashboard" / "index.html"
SERVE_DIRS = ("projects", "assets", "docs", "outputs", "references")
JOBS: dict[str, dict] = {}


def _job(name, fn):
    if JOBS.get(name, {}).get("running"):
        return False
    JOBS[name] = {"running": True, "log": [], "result": None, "error": None}

    def run():
        try:
            JOBS[name]["result"] = fn(lambda m: JOBS[name]["log"].append(str(m)))
        except Exception as e:
            JOBS[name]["error"] = str(e)
            get_logger().error("job %s failed: %s", name, traceback.format_exc())
        finally:
            JOBS[name]["running"] = False
    threading.Thread(target=run, daemon=True).start()
    return True


def masked_settings():
    s = load_settings()
    for path in (("google", "api_key"), ("research", "youtube_api_key")):
        if s[path[0]].get(path[1]):
            s[path[0]][path[1]] = "***set***"
    return s


def project_detail(p: Project) -> dict:
    from .production import is_running
    rel = lambda f: f.relative_to(ROOT).as_posix()
    d = {"state": {k: v for k, v in p.state.items() if k != "settings_snapshot"}, "progress": p.progress(),
         "running": is_running(p.id), "stage_labels": STAGE_LABELS, "stages": STAGES}
    d["script_text"] = p.path("script", "script.txt").read_text(encoding="utf-8") if p.path("script", "script.txt").exists() else ""
    d["script"] = read_json(p.path("script", "script.json"))
    d["storyboard"] = read_json(p.path("storyboard", "storyboard.json"))
    d["scene_images"] = [rel(f) for f in sorted(p.path("scenes").glob("scene_*.png"))]
    d["clips"] = read_json(p.path("animations", "clips.json"), {"clips": {}})["clips"]
    d["audio"] = rel(p.path("voice", "narration.mp3")) if p.path("voice", "narration.mp3").exists() else None
    d["video"] = p.state.get("final_video")
    d["thumbnails"] = read_json(p.path("thumbnails", "thumbnails.json"))
    d["metadata"] = read_json(p.path("final", "metadata.json"))
    d["report"] = read_json(p.path("final", "production_report.json"))
    d["flow_requests"] = rel(p.path("flow", "FLOW_REQUESTS.md")) if p.path("flow", "FLOW_REQUESTS.md").exists() else None
    lg = p.path("logs.txt")
    d["log"] = lg.read_text(encoding="utf-8").splitlines()[-40:] if lg.exists() else []
    return d


def overview():
    from .agents.researcher import latest_ideas
    from .audio import voice_status
    st = load_style()
    s = load_settings()
    return {"settings": masked_settings(), "style": {"status": st.get("status"), "verified": st.get("verified"),
                                                     "measured": st.get("measured_from_references")},
            "references": len(consistency.reference_files()), "voice": voice_status(s),
            "gemini_ready": google_ai.gemini_available(s), "gemini_voices": google_ai.GEMINI_VOICES,
            "ideas": latest_ideas(), "projects": list_projects(), "jobs": {k: {kk: v[kk] for kk in ("running", "error")} | {"log": v["log"][-15:]}
                                                                         for k, v in JOBS.items()},
            "audition": sorted(f.name for f in (ROOT / "assets" / "voice_audition").glob("*.wav")) if (ROOT / "assets" / "voice_audition").exists() else []}


def handle_command(text: str, body: dict):
    """Slash commands typed into the dashboard command box."""
    t = text.strip()
    cmd, _, arg = t.partition(" ")
    cmd = cmd.lower().lstrip("/").replace("glavonja-", "")
    if cmd == "ideas":
        from .agents.researcher import research_ideas
        _job("ideas", lambda log: research_ideas(arg or None, log, refresh=True))
        return {"ok": True, "msg": "Researching 10 ideas..."}
    if cmd == "make":
        return api_make({"idea_id": int(arg)} if arg.isdigit() else {"topic": arg})
    if cmd in ("continue", "status"):
        p = get_project(arg or None)
        if not p:
            return {"ok": False, "msg": "No project"}
        if cmd == "continue":
            from .production import run_in_background
            run_in_background(p)
        return {"ok": True, "project": p.id, "progress": p.progress()}
    if cmd == "history":
        return {"ok": True, "projects": list_projects()}
    if cmd in ("style", "settings"):
        return {"ok": True, "open": cmd}
    return {"ok": False, "msg": f"Unknown command: {text}"}


def api_make(b: dict):
    from .agents.researcher import get_idea
    from .production import run_in_background
    s = load_settings()
    if b.get("idea_id"):
        idea = get_idea(int(b["idea_id"]))
        if not idea:
            return {"ok": False, "msg": "idea not found"}
        db_exec("UPDATE ideas SET status='chosen' WHERE id=?", (idea["id"],))
    else:
        if not b.get("topic"):
            return {"ok": False, "msg": "no topic"}
        idea = {"topic": b["topic"], "title": b["topic"], "mood": "mystery"}
    lang = b.get("lang") or idea.get("language") or s["language"]
    dur = int(b.get("duration") or 0) or int(idea.get("duration_min", 0) * 60) or s["target_duration_sec"]
    p = Project.create(idea["title"], lang, idea, dur)
    run_in_background(p)
    return {"ok": True, "project": p.id}


class H(BaseHTTPRequestHandler):
    server_version = "GLAVONJA/1.0"

    def log_message(self, *a):
        pass

    def _json(self, obj, code=200):
        data = json.dumps(obj, ensure_ascii=False, default=str).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _body(self):
        n = int(self.headers.get("Content-Length", 0) or 0)
        return self.rfile.read(n) if n else b""

    def do_GET(self):
        u = urllib.parse.urlparse(self.path)
        try:
            if u.path in ("/", "/index.html"):
                data = UI.read_bytes()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)
            elif u.path == "/api/overview":
                self._json(overview())
            elif u.path.startswith("/api/project/"):
                p = get_project(u.path.rsplit("/", 1)[1])
                self._json(project_detail(p) if p else {"error": "not found"}, 200 if p else 404)
            elif u.path.startswith("/files/"):
                self._file(urllib.parse.unquote(u.path[len("/files/"):]))
            else:
                self._json({"error": "not found"}, 404)
        except (BrokenPipeError, ConnectionResetError):
            pass
        except Exception as e:
            self._json({"error": str(e)}, 500)

    def _file(self, relpath):
        f = (ROOT / relpath).resolve()
        if not any(str(f).startswith(str((ROOT / d).resolve()) + os.sep) for d in SERVE_DIRS) or not f.is_file():
            return self._json({"error": "forbidden"}, 403)
        size = f.stat().st_size
        ctype = mimetypes.guess_type(f.name)[0] or "application/octet-stream"
        if f.suffix in (".md", ".txt", ".srt", ".json"):
            ctype += "; charset=utf-8"
        rng = self.headers.get("Range")
        start, end = 0, size - 1
        if rng and (m := re.match(r"bytes=(\d*)-(\d*)", rng)):
            if m.group(1):
                start = int(m.group(1))
            if m.group(2):
                end = min(int(m.group(2)), size - 1)
            self.send_response(206)
            self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
        else:
            self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Content-Length", str(end - start + 1))
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        with f.open("rb") as fh:
            fh.seek(start)
            left = end - start + 1
            while left > 0:
                chunk = fh.read(min(1 << 20, left))
                if not chunk:
                    break
                self.wfile.write(chunk)
                left -= len(chunk)

    def do_POST(self):
        u = urllib.parse.urlparse(self.path)
        q = dict(urllib.parse.parse_qsl(u.query))
        try:
            if u.path in ("/api/upload_flow", "/api/upload_reference"):
                return self._json(self._upload(u.path, q))
            raw = self._body()
            b = json.loads(raw or b"{}")
            self._json(self._post(u.path, b))
        except (BrokenPipeError, ConnectionResetError):
            pass
        except Exception as e:
            get_logger().error("POST %s failed: %s", u.path, traceback.format_exc())
            self._json({"ok": False, "msg": str(e)}, 500)

    def _upload(self, path, q):
        name = re.sub(r"[^\w.\-]", "_", q.get("name", "upload"))[:80]
        data = self._body()
        if path == "/api/upload_flow":
            p = get_project(q["id"])
            scene = int(q["scene"])
            ext = Path(name).suffix.lower() or ".mp4"
            if ext not in (".mp4", ".mov", ".webm"):
                return {"ok": False, "msg": "video files only"}
            dest = p.path("flow", "inbox", f"scene_{scene:03d}{ext}")
        else:
            ext = Path(name).suffix.lower()
            sub = "videos" if ext in consistency.VID_EXT else ("character" if q.get("kind") == "character" else "frames")
            if ext not in consistency.VID_EXT + consistency.IMG_EXT:
                return {"ok": False, "msg": "images or videos only"}
            dest = ROOT / "references" / sub / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
        return {"ok": True, "saved": dest.relative_to(ROOT).as_posix()}

    def _post(self, path, b):
        from .production import reset_stage, run_in_background
        if path == "/api/command":
            return handle_command(b.get("text", ""), b)
        if path == "/api/ideas":
            from .agents.researcher import research_ideas
            ok = _job("ideas", lambda log: research_ideas(b.get("lang"), log, refresh=bool(b.get("refresh"))))
            return {"ok": ok}
        if path == "/api/make":
            return api_make(b)
        if path == "/api/continue":
            p = get_project(b["id"])
            return {"ok": run_in_background(p)}
        if path == "/api/approve":
            p = get_project(b["id"])
            google_ai.approve(p, b["key"], bool(b.get("approved", True)))
            if b.get("continue", True):
                run_in_background(p)
            return {"ok": True}
        if path == "/api/script":
            from .agents.scriptwriter import import_text
            p = get_project(b["id"])
            import_text(p, b["text"])
            reset_stage(p, "storyboard")
            p.mark("script", "done")
            return {"ok": True}
        if path == "/api/redo":
            p = get_project(b["id"])
            reset_stage(p, b["stage"])
            run_in_background(p)
            return {"ok": True}
        if path == "/api/settings":
            for k, v in b.items():
                if k.endswith("api_key") and v in ("***set***",):
                    continue
                set_setting(k, v)
            return {"ok": True, "settings": masked_settings()}
        if path == "/api/style":
            act = b.get("action")
            if act == "learn":
                _job("style", lambda log: consistency.learn_style(log))
            elif act == "test":
                from .style_tools import make_test_scene
                _job("style", lambda log: make_test_scene())
            elif act == "approve":
                st = load_style()
                st["verified"], st["status"] = True, "APPROVED by the channel owner"
                save_style(st)
            return {"ok": True}
        if path == "/api/voice/audition":
            s = load_settings()
            voices = b.get("voices") or ["Charon", "Puck", "Fenrir", "Orus", "Kore", "Zephyr"]
            from .cli import _sample
            _job("audition", lambda log: google_ai.audition_voices(_sample(s["language"]), voices,
                                                                   ROOT / "assets" / "voice_audition", s))
            return {"ok": True, "estimate": google_ai.estimate_tts([_sample(s["language"])] * len(voices))}
        if path == "/api/voice/lock":
            set_setting("google.tts_voice", b["voice"])
            set_setting("google.tts_voice_locked", "true")
            return {"ok": True}
        if path == "/api/final":
            p = get_project(b["id"])
            if b.get("thumbnail"):
                p.state["chosen_thumbnail"] = b["thumbnail"]
            if b.get("approve"):
                if p.state.get("export", {}).get("status") != "exported":
                    return {"ok": False, "msg": "Video nije prošao proveru konzistentnosti - ne može biti odobren za objavu."}
                p.state["approved"] = True
                p.state["status"] = "approved"
            p.save()
            return {"ok": True}
        return {"ok": False, "msg": "unknown endpoint"}


def serve():
    ensure_dirs()
    s = load_settings()["dashboard"]
    srv = ThreadingHTTPServer((s["host"], s["port"]), H)
    url = f"http://{s['host']}:{s['port']}/"
    print(f"GLAVONJA AI STUDIO dashboard: {url}  (close this window to stop)")
    # resume projects interrupted by a crash/shutdown
    for pr in list_projects():
        if pr["status"] == "running":
            p = get_project(pr["id"])
            p.state["status"] = "interrupted"
            p.save()
    from .autopilot import GLOBAL_INBOX, background_loop
    GLOBAL_INBOX.mkdir(exist_ok=True)
    background_loop(300)   # watches FLOW_INBOX every 5 min while the dashboard is open
    if s.get("open_browser", True):
        threading.Timer(1.0, lambda: webbrowser.open(url)).start()
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
