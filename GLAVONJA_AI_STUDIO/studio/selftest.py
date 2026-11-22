"""Installation self-test: every check is real (nothing is assumed)."""
from __future__ import annotations

import os
import platform
import shutil
import tempfile
from pathlib import Path


def selftest(verbose=True) -> bool:
    ok_all = True

    def ck(name, fn, required=True):
        nonlocal ok_all
        try:
            detail = fn()
            print(f"  [OK]   {name}: {detail}")
            return True
        except Exception as e:
            print(f"  [{'FAIL' if required else 'WARN'}] {name}: {type(e).__name__}: {str(e)[:200]}")
            if required:
                ok_all = False
            return False

    from .core import ROOT, db, ensure_dirs, find_tool, load_settings, load_style
    print("GLAVONJA AI STUDIO self-test")
    ck("python", lambda: platform.python_version())
    ck("folders + database", lambda: (ensure_dirs(), db().close(), "ok")[2])
    ck("settings/style", lambda: f"lang={load_settings()['language']} style_verified={load_style().get('verified')}")
    ck("ffmpeg", lambda: find_tool("ffmpeg") or (_ for _ in ()).throw(RuntimeError("missing")))
    ck("ffprobe", lambda: find_tool("ffprobe") or (_ for _ in ()).throw(RuntimeError("missing (QC uses ffmpeg fallback)")), False)
    ck("numpy + pillow", lambda: (__import__("numpy").__version__, __import__("PIL").__version__))

    def render():
        from .render.scene import FrameRenderer
        im = FrameRenderer(load_style(), 640, 360).render({"background": "day", "duration": 1,
                                                           "characters": [{"action": "walk", "x": 0.4}]}, 0.5)
        return f"frame {im.size}"
    ck("renderer", render)

    def espeak():
        from .audio import EspeakEngine, wav_duration
        from .core import load_settings as ls
        d = Path(tempfile.mkdtemp())
        EspeakEngine().synth("Zdravo, ovo je test.", d / "t.wav", "sr", ls())
        return f"Serbian test {wav_duration(d / 't.wav'):.1f}s"
    ck("local voice fallback (espeak-ng, Serbian)", espeak)
    ck("piper voices (optional, better local fallback)", lambda: _piper(), False)

    def gem():
        from .google_ai import gemini_available
        s = load_settings()
        if not gemini_available(s):
            raise RuntimeError("Gemini API key not set (Settings -> Google). REQUIRED for production voice.")
        return f"key set, voice={s['google'].get('tts_voice') or 'NOT CHOSEN'} locked={s['google'].get('tts_voice_locked')}"
    ck("Gemini TTS (mandatory)", gem, False)

    def oll():
        from .llm import available_providers
        p = available_providers()
        if not p:
            raise RuntimeError("no local LLM - scripts use offline templates (install Ollama for real scripts)")
        return p
    ck("LLM for scripts", oll, False)

    def refs():
        from .consistency import reference_files
        n = len(reference_files())
        if not n:
            raise RuntimeError("no channel frames in references/frames - export is blocked until you add them")
        return f"{n} frames"
    ck("channel reference frames", refs, False)
    du = shutil.disk_usage(ROOT)
    ck("disk space", lambda: f"{du.free / 1e9:.1f} GB free" if du.free > 3e9 else (_ for _ in ()).throw(RuntimeError(f"only {du.free / 1e9:.1f} GB")))
    print("RESULT:", "OK" if ok_all else "PROBLEMS FOUND")
    return ok_all


def _piper():
    from .audio import PiperEngine
    from .core import load_settings
    s = load_settings()
    have = [l for l in ("sr", "en") if PiperEngine.available(l, s)]
    if not have:
        raise RuntimeError("no Piper model downloaded (scripts/download_models.py)")
    return have
