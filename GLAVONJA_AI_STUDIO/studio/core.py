"""Core infrastructure: paths, settings, logging, SQLite database, project state.

Everything here is plain Python (no AI, no network) so it is cheap and reliable.
"""
from __future__ import annotations

import copy
import datetime as _dt
import hashlib
import json
import logging
import os
import re
import shutil
import sqlite3
import subprocess
import sys
import threading
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG_DIR = ROOT / "config"
PROJECTS_DIR = ROOT / "projects"
OUTPUTS_DIR = ROOT / "outputs"
ASSETS_DIR = ROOT / "assets"
MODELS_DIR = ROOT / "models"
DB_PATH = ROOT / "database" / "glavonja.db"
LOG_DIR = ROOT / "logs"
PROMPTS_DIR = ROOT / "prompts"
TOOLS_DIR = ROOT / "tools"
FONTS_DIR = ASSETS_DIR / "fonts"

PROJECT_SUBDIRS = ["research", "script", "storyboard", "voice", "scenes", "animations",
                   "music", "subtitles", "thumbnails", "final"]

# --------------------------------------------------------------------------- settings
DEFAULT_SETTINGS = {
    "language": "sr",                 # "sr" (Serbian, latin script) or "en"
    "target_duration_sec": 60,
    "video": {"width": 1920, "height": 1080, "fps": 24, "crf": 20, "preset": "medium",
              "burn_subtitles": True},
    "voice": {
        "engine": "gemini",          # MANDATORY: gemini. Local (piper/espeak/sapi) only as approved fallback
        "piper_model": {"sr": "models/piper/sr_RS-serbski_institute-medium.onnx",
                         "en": "models/piper/en_US-lessac-medium.onnx"},
        "espeak_voice": {"sr": "sr", "en": "en-us"},
        "espeak_rate": 160, "espeak_pitch": 45,
        "sapi_voice": "",            # empty = Windows default voice
        "length_scale": 1.0,         # piper speed (bigger = slower)
    },
    "audio": {"music": True, "music_volume_db": -20, "sfx": True, "sfx_volume_db": -8,
              "voice_lufs": -16},
    "llm": {
        "order": ["ollama", "claude_cli", "offline"],
        "ollama_url": "http://127.0.0.1:11434",
        "ollama_model": "qwen2.5:7b-instruct",
        "claude_cli_model": "",       # empty = Claude Code default; costs Claude usage!
        "allow_claude_cli": False,    # off by default to keep Claude usage at zero
        "timeout_sec": 900,
    },
    "research": {
        "youtube_api_key": "",        # optional, free quota (see docs/RESEARCH_SOURCES.md)
        "competitor_channel_ids": [],  # e.g. ["UCxxxx"]; resolved via RSS (no key needed)
        "region": "US",
        "use_wikipedia": True, "use_google_trends": True, "use_reddit": True,
        "cache_hours": 12,
    },
    "dashboard": {"host": "127.0.0.1", "port": 8765, "open_browser": True},
    "google": {
        "enabled": True,              # PART 3.1.1 - MANDATORY for every video; each use is estimated + approved
        "api_key": "",                # Gemini API key from https://aistudio.google.com/apikey
        "tts_model": "gemini-3.8-flash-tts",   # verified available with the user's key (2026-11-22)
        "tts_chunk_chars": 700,       # several sentences per request -> far fewer requests (free quota)
        "tts_voice": "",              # chosen once via voice audition, then LOCKED
        "tts_voice_locked": False,
        "tts_style_prompt": "Narrate like an energetic, curious YouTube storyteller:",
        "use_flow": True,             # MANDATORY: every scene is animated in Google Flow (bridge: prompts -> your clips)
        "flow_mode": "fast",
        "auto_approve_under_free_tier": False,
    },
    "consistency": {"max_distance": "auto", "require_references_for_export": True},
    "shots": {"max_shot_sec": 8.0, "min_shot_sec": 2.0},   # Flow clips are ~8 s, so narration is grouped into shots
}


def _deep_merge(base: dict, extra: dict) -> dict:
    out = copy.deepcopy(base)
    for k, v in (extra or {}).items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _deep_merge(out[k], v)
        else:
            out[k] = v
    return out


def load_settings() -> dict:
    p = CONFIG_DIR / "settings.json"
    user = {}
    if p.exists():
        try:
            user = json.loads(p.read_text(encoding="utf-8"))
        except Exception as e:  # corrupted settings must never kill the app
            get_logger().error("settings.json unreadable (%s); using defaults", e)
    return _deep_merge(DEFAULT_SETTINGS, user)


def save_settings(s: dict) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    atomic_write_json(CONFIG_DIR / "settings.json", s)


def set_setting(dotted: str, value) -> dict:
    s = load_settings()
    cur = s
    keys = dotted.split(".")
    for k in keys[:-1]:
        cur = cur.setdefault(k, {})
    old = cur.get(keys[-1])
    if isinstance(old, bool):
        value = str(value).lower() in ("1", "true", "yes", "da", "on")
    elif isinstance(old, int) and not isinstance(old, bool):
        value = int(value)
    elif isinstance(old, float):
        value = float(value)
    elif isinstance(old, list) and isinstance(value, str):
        value = [x.strip() for x in value.split(",") if x.strip()]
    cur[keys[-1]] = value
    save_settings(s)
    return s


def load_style() -> dict:
    """config/style.json is YOUR style (measured/approved, never overwritten by updates).
    It is created from config/style.default.json the first time."""
    p = CONFIG_DIR / "style.json"
    default = json.loads((CONFIG_DIR / "style.default.json").read_text(encoding="utf-8"))
    if not p.exists():
        shutil.copy2(CONFIG_DIR / "style.default.json", p)
    else:  # an old, never measured/approved style file is replaced by the new channel-based default
        cur = json.loads(p.read_text(encoding="utf-8"))
        if not cur.get("verified") and "channel_look" not in cur and not cur.get("measured_from_references"):
            shutil.copy2(p, p.with_suffix(".old.json"))
            shutil.copy2(CONFIG_DIR / "style.default.json", p)
    # new keys from updates (e.g. prompt_style) reach existing installations; your own values win
    return _deep_merge(default, json.loads(p.read_text(encoding="utf-8")))


def save_style(style: dict) -> None:
    atomic_write_json(CONFIG_DIR / "style.json", style)


# --------------------------------------------------------------------------- utils
def atomic_write_json(path: Path, data) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(tmp, path)


def read_json(path: Path, default=None):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except Exception:
        return default


def now_iso() -> str:
    return _dt.datetime.now().replace(microsecond=0).isoformat()


def slugify(text: str, maxlen: int = 40) -> str:
    t = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    t = re.sub(r"[^a-zA-Z0-9]+", "-", t).strip("-").lower()
    return (t[:maxlen].strip("-")) or "video"


def sha(obj) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, ensure_ascii=False).encode()).hexdigest()[:16]


def rel(path: Path) -> str:
    try:
        return Path(path).resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return str(path)


# --------------------------------------------------------------------------- logging
_logger = None
_SECRET_RE = re.compile(r"(key=|api_key\"?:\s*\"?|Bearer\s+)[A-Za-z0-9_\-]{8,}")


class _RedactFilter(logging.Filter):
    def filter(self, record):
        try:
            msg = record.getMessage()
        except Exception:
            return True
        red = _SECRET_RE.sub(r"\1***", msg)
        if red != msg:
            record.msg, record.args = red, ()
        return True


def get_logger() -> logging.Logger:
    global _logger
    if _logger:
        return _logger
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    lg = logging.getLogger("glavonja")
    lg.setLevel(logging.INFO)
    fh = logging.FileHandler(LOG_DIR / "studio.log", encoding="utf-8")
    fh.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))
    for h in (fh, sh):
        h.addFilter(_RedactFilter())
        lg.addHandler(h)
    _logger = lg
    return lg


# --------------------------------------------------------------------------- tools
def find_tool(name: str) -> str | None:
    """Find ffmpeg/ffprobe: bundled tools/ folder first, then PATH, then imageio-ffmpeg."""
    exe = name + (".exe" if os.name == "nt" else "")
    for cand in (TOOLS_DIR / "ffmpeg" / "bin" / exe, TOOLS_DIR / exe):
        if cand.exists():
            return str(cand)
    p = shutil.which(name)
    if p:
        return p
    if name == "ffmpeg":
        try:
            import imageio_ffmpeg  # optional fallback
            return imageio_ffmpeg.get_ffmpeg_exe()
        except Exception:
            pass
    return None


def run(cmd: list, check=True, capture=True, input_bytes=None, timeout=None) -> subprocess.CompletedProcess:
    kw = {}
    if os.name == "nt":
        kw["creationflags"] = 0x08000000  # CREATE_NO_WINDOW
    r = subprocess.run(cmd, input=input_bytes, capture_output=capture, timeout=timeout, **kw)
    if check and r.returncode != 0:
        err = (r.stderr or b"").decode("utf-8", "replace")[-2000:]
        raise RuntimeError(f"Command failed ({r.returncode}): {' '.join(map(str, cmd[:6]))} ...\n{err}")
    return r


def ffmpeg() -> str:
    p = find_tool("ffmpeg")
    if not p:
        raise RuntimeError("FFmpeg not found. Run install.bat (it downloads a free FFmpeg build).")
    return p


# --------------------------------------------------------------------------- database
_db_lock = threading.Lock()
SCHEMA = """
CREATE TABLE IF NOT EXISTS ideas (
  id INTEGER PRIMARY KEY AUTOINCREMENT, batch TEXT, created TEXT, language TEXT,
  topic TEXT, title TEXT, data TEXT, status TEXT DEFAULT 'new');
CREATE TABLE IF NOT EXISTS projects (
  id TEXT PRIMARY KEY, created TEXT, updated TEXT, title TEXT, language TEXT,
  status TEXT, stage TEXT, folder TEXT, idea_id INTEGER, final_video TEXT, approved INTEGER DEFAULT 0);
CREATE TABLE IF NOT EXISTS cache (
  key TEXT PRIMARY KEY, created TEXT, kind TEXT, value TEXT);
CREATE TABLE IF NOT EXISTS assets_license (
  path TEXT PRIMARY KEY, kind TEXT, source TEXT, license TEXT, notes TEXT, added TEXT);
CREATE TABLE IF NOT EXISTS events (
  id INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT, project TEXT, level TEXT, message TEXT);
"""


def db() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB_PATH, timeout=30, check_same_thread=False)
    con.row_factory = sqlite3.Row
    con.executescript(SCHEMA)
    return con


def db_exec(sql: str, params=()):
    with _db_lock:
        con = db()
        try:
            cur = con.execute(sql, params)
            con.commit()
            return cur.lastrowid
        finally:
            con.close()


def db_query(sql: str, params=()) -> list[dict]:
    with _db_lock:
        con = db()
        try:
            return [dict(r) for r in con.execute(sql, params).fetchall()]
        finally:
            con.close()


def cache_get(key: str, max_age_hours: float | None = None):
    rows = db_query("SELECT created, value FROM cache WHERE key=?", (key,))
    if not rows:
        return None
    if max_age_hours is not None:
        age = _dt.datetime.now() - _dt.datetime.fromisoformat(rows[0]["created"])
        if age.total_seconds() > max_age_hours * 3600:
            return None
    return json.loads(rows[0]["value"])


def cache_put(key: str, value, kind: str = "") -> None:
    db_exec("INSERT OR REPLACE INTO cache(key, created, kind, value) VALUES (?,?,?,?)",
            (key, now_iso(), kind, json.dumps(value, ensure_ascii=False)))


def record_license(path, kind: str, source: str, license_: str, notes: str = "") -> None:
    db_exec("INSERT OR REPLACE INTO assets_license VALUES (?,?,?,?,?,?)",
            (rel(Path(path)), kind, source, license_, notes, now_iso()))


def event(project: str, level: str, message: str) -> None:
    db_exec("INSERT INTO events(ts, project, level, message) VALUES (?,?,?,?)",
            (now_iso(), project, level, message[:4000]))
    getattr(get_logger(), "error" if level == "error" else "info")(f"[{project}] {message}")


# --------------------------------------------------------------------------- project state
STAGES = ["research", "script", "storyboard", "voice", "visuals", "animation",
          "edit", "thumbnails", "seo", "qc"]

STAGE_LABELS = {
    "research": "Topic research", "script": "Scriptwriting", "storyboard": "Storyboard",
    "voice": "Voice narration", "visuals": "Illustrations", "animation": "Animation",
    "edit": "Video editing", "thumbnails": "Thumbnails", "seo": "SEO metadata",
    "qc": "Quality control",
}


class Project:
    def __init__(self, folder: Path):
        self.folder = Path(folder)
        self.state_path = self.folder / "project_state.json"
        self.state = read_json(self.state_path, None)
        if self.state is None:
            raise FileNotFoundError(f"No project_state.json in {folder}")

    @property
    def id(self) -> str:
        return self.state["id"]

    def path(self, *parts) -> Path:
        return self.folder.joinpath(*parts)

    @classmethod
    def create(cls, title: str, language: str, idea: dict | None = None,
               duration: int | None = None) -> "Project":
        stamp = _dt.datetime.now().strftime("%Y%m%d-%H%M%S")
        pid = f"{stamp}-{slugify(title, 30)}"
        folder = PROJECTS_DIR / pid
        for d in PROJECT_SUBDIRS:
            (folder / d).mkdir(parents=True, exist_ok=True)
        settings = load_settings()
        state = {
            "id": pid, "title": title, "language": language, "created": now_iso(),
            "updated": now_iso(), "idea": idea or {"topic": title, "title": title},
            "target_duration_sec": duration or settings["target_duration_sec"],
            "status": "created", "approved": False, "chosen_thumbnail": None,
            "stages": {s: {"status": "pending"} for s in STAGES},
            "settings_snapshot": settings,
        }
        atomic_write_json(folder / "project_state.json", state)
        db_exec("INSERT OR REPLACE INTO projects(id, created, updated, title, language, status, stage, folder, idea_id)"
                " VALUES (?,?,?,?,?,?,?,?,?)",
                (pid, state["created"], state["updated"], title, language, "created", "",
                 rel(folder), (idea or {}).get("id")))
        event(pid, "info", f"Project created: {title}")
        return cls(folder)

    def save(self) -> None:
        self.state["updated"] = now_iso()
        atomic_write_json(self.state_path, self.state)
        cur = next((s for s in STAGES if self.state["stages"][s]["status"] != "done"), "")
        final = self.state.get("final_video")
        db_exec("UPDATE projects SET updated=?, status=?, stage=?, title=?, final_video=?, approved=? WHERE id=?",
                (self.state["updated"], self.state["status"], cur, self.state["title"], final,
                 int(bool(self.state.get("approved"))), self.id))

    def stage_status(self, stage: str) -> str:
        return self.state["stages"][stage]["status"]

    def mark(self, stage: str, status: str, **info) -> None:
        st = self.state["stages"][stage]
        st["status"] = status
        st[f"{status}_at"] = now_iso()
        st.update(info)
        self.save()

    def progress(self) -> dict:
        done = sum(1 for s in STAGES if self.state["stages"][s]["status"] == "done")
        cur = next((s for s in STAGES if self.state["stages"][s]["status"] != "done"), None)
        return {"done": done, "total": len(STAGES), "percent": round(100 * done / len(STAGES)),
                "current": cur, "current_label": STAGE_LABELS.get(cur, "Finished"),
                "status": self.state["status"]}


def list_projects() -> list[dict]:
    out = []
    if not PROJECTS_DIR.exists():
        return out
    for d in sorted(PROJECTS_DIR.iterdir(), reverse=True):
        st = read_json(d / "project_state.json")
        if st:
            p = Project(d)
            out.append({"id": st["id"], "title": st["title"], "language": st["language"],
                        "created": st["created"], "updated": st["updated"], "status": st["status"],
                        "approved": st.get("approved", False), "final_video": st.get("final_video"),
                        "progress": p.progress()})
    return out


def get_project(pid: str | None = None) -> Project | None:
    """Return project by id (or unique prefix); None -> most recently updated."""
    projs = list_projects()
    if not projs:
        return None
    if pid:
        m = [p for p in projs if p["id"] == pid] or [p for p in projs if p["id"].startswith(pid)]
        return Project(PROJECTS_DIR / m[0]["id"]) if m else None
    projs.sort(key=lambda p: p["updated"], reverse=True)
    return Project(PROJECTS_DIR / projs[0]["id"])


def ensure_dirs() -> None:
    for d in ["config", "agents", "skills", "scripts", "models", "assets/characters",
              "assets/backgrounds", "assets/animations", "assets/music", "assets/sound_effects",
              "assets/fonts", "projects", "outputs", "thumbnails", "database", "logs", "docs",
              "references/frames"]:
        (ROOT / d).mkdir(parents=True, exist_ok=True)
    db().close()


def font_path(bold: bool = True) -> str:
    name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    p = FONTS_DIR / name
    if p.exists():
        return str(p)
    for c in (r"C:\Windows\Fonts\arialbd.ttf", "/usr/share/fonts/truetype/dejavu/" + name):
        if Path(c).exists():
            return c
    raise RuntimeError("No font found")
