"""Called by install.bat / update.bat.  Inspects hardware, installs FFmpeg + optional voice models.

Usage: python scripts/install_helper.py hardware | ffmpeg | models [--yes] | all
Nothing here needs administrator rights.  Large downloads check free disk space first.
"""
from __future__ import annotations

import json
import os
import platform
import shutil
import subprocess
import sys
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

FFMPEG_ZIP = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
PIPER = "https://huggingface.co/rhasspy/piper-voices/resolve/main/"
PIPER_VOICES = {"sr": "sr/sr_RS/serbski_institute/medium/sr_RS-serbski_institute-medium.onnx",
                "en": "en/en_US/lessac/medium/en_US-lessac-medium.onnx"}


def ps(cmd: str) -> str:
    try:
        r = subprocess.run(["powershell", "-NoProfile", "-Command", cmd], capture_output=True, text=True, timeout=60)
        return r.stdout.strip()
    except Exception as e:
        return f"unavailable ({e})"


def hardware() -> dict:
    info = {"os": platform.platform(), "python": platform.python_version(), "machine": platform.machine(),
            "cpu_count": os.cpu_count(), "disk_free_gb": round(shutil.disk_usage(ROOT).free / 1e9, 1)}
    if os.name == "nt":
        info["windows"] = ps("(Get-CimInstance Win32_OperatingSystem | Select Caption,Version,BuildNumber | ConvertTo-Json)")
        info["cpu"] = ps("(Get-CimInstance Win32_Processor).Name")
        info["ram_gb"] = ps("[math]::Round((Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory/1GB,1)")
        info["gpu"] = ps("Get-CimInstance Win32_VideoController | Select Name,DriverVersion,AdapterRAM | ConvertTo-Json")
    else:
        try:
            info["ram_gb"] = round(os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES") / 1e9, 1)
        except Exception:
            pass
    notes = []
    g = str(info.get("gpu", "")).lower()
    if "radeon" in g or "amd" in g:
        notes.append("AMD GPU detected: no CUDA. Local AI image/video models are not used; rendering is CPU (Pillow+FFmpeg), "
                     "animation comes from Google Flow. This is reliable on an i5 + 16 GB RAM.")
    notes.append("Ollama (optional, free) for script writing: qwen2.5:7b-instruct needs ~5 GB RAM and runs on CPU "
                 "(slow but works on 16 GB). Use qwen2.5:3b-instruct if it is too slow.")
    info["notes"] = notes
    out = ROOT / "docs" / "hardware_report.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(info, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(info, indent=2, ensure_ascii=False))
    return info


def _download(url: str, dest: Path, min_free_gb: float = 1.0):
    free = shutil.disk_usage(dest.parent).free / 1e9
    if free < min_free_gb:
        raise RuntimeError(f"Only {free:.1f} GB free - not downloading {dest.name}")
    tmp = dest.with_suffix(dest.suffix + ".part")
    print(f"  downloading {url.split('/')[-1]} ...")
    req = urllib.request.Request(url, headers={"User-Agent": "GLAVONJA-AI-STUDIO-installer"})
    with urllib.request.urlopen(req, timeout=120) as r, open(tmp, "wb") as f:
        shutil.copyfileobj(r, f, 1 << 20)
    os.replace(tmp, dest)


def ffmpeg():
    from studio.core import find_tool
    if find_tool("ffmpeg") and find_tool("ffprobe"):
        print("  FFmpeg OK:", find_tool("ffmpeg"))
        return True
    if os.name != "nt":
        print("  Please install ffmpeg with your package manager.")
        return False
    tools = ROOT / "tools"
    tools.mkdir(exist_ok=True)
    z = tools / "ffmpeg.zip"
    try:
        _download(FFMPEG_ZIP, z, 1.5)
        with zipfile.ZipFile(z) as zf:
            zf.extractall(tools)
        z.unlink()
        inner = next(p for p in tools.iterdir() if p.is_dir() and p.name.startswith("ffmpeg-"))
        if (tools / "ffmpeg").exists():
            shutil.rmtree(tools / "ffmpeg")
        inner.rename(tools / "ffmpeg")
        print("  FFmpeg installed in tools/ffmpeg (GPL build by BtbN)")
        return True
    except Exception as e:
        print("  FFmpeg download failed:", e, "-> falling back to imageio-ffmpeg (no ffprobe; QC uses ffmpeg)")
        return False


def models(yes=False):
    dest = ROOT / "models" / "piper"
    dest.mkdir(parents=True, exist_ok=True)
    for lang, path in PIPER_VOICES.items():
        f = dest / Path(path).name
        if f.exists() and Path(str(f) + ".json").exists():
            print(f"  Piper {lang}: present")
            continue
        if not yes:
            print(f"  Piper {lang} fallback voice skipped (optional; Gemini is the main voice). "
                  f"Later: .venv\\Scripts\\python scripts\\install_helper.py models --yes")
            continue
        try:
            _download(PIPER + path, f, 0.5)
            _download(PIPER + path + ".json", Path(str(f) + ".json"), 0.1)
            from studio.core import record_license
            record_license(f, "voice_model", PIPER + path, "see MODEL_CARD in rhasspy/piper-voices (voice-specific licence)")
        except Exception as e:
            print(f"  Piper {lang} download failed: {e} (espeak-ng fallback still works)")


if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else "all"
    yes = "--yes" in sys.argv
    if what in ("hardware", "all"):
        hardware()
    if what in ("ffmpeg", "all"):
        ffmpeg()
    if what in ("models", "all"):
        models(yes)
