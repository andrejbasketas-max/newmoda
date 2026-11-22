"""VOICE ENGINE + music + sound effects.  100 % local and free.

Voice engines (tried in this order when engine = "auto"):
  1. piper   - neural TTS (MIT). Natural voice. Needs a voice model (.onnx) in models/piper/.
  2. sapi    - Windows built-in speech (System.Speech). Only voices installed in Windows.
  3. espeak  - espeak-ng (GPL-3) via the `espeakng-loader` pip wheel. Always available,
               supports Serbian ("sr") and English, but sounds robotic.

Music and sound effects are synthesised with NumPy => no licence risk (own work, CC0).
"""
from __future__ import annotations

import array
import ctypes
import json
import math
import os
import re
import subprocess
import tempfile
import wave
from pathlib import Path

import numpy as np

from .core import ASSETS_DIR, ROOT, ffmpeg, get_logger, load_settings, record_license, run

SR = 44100


# =========================================================================== wav helpers
def write_wav(path: Path, data: np.ndarray, sr: int = SR):
    data = np.clip(data, -1, 1)
    pcm = (data * 32767).astype("<i2")
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1 if pcm.ndim == 1 else pcm.shape[1])
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(pcm.tobytes())


def read_wav(path: Path) -> tuple[np.ndarray, int]:
    with wave.open(str(path), "rb") as w:
        sr, n, ch = w.getframerate(), w.getnframes(), w.getnchannels()
        raw = np.frombuffer(w.readframes(n), dtype="<i2").astype(np.float32) / 32768
    if ch > 1:
        raw = raw.reshape(-1, ch).mean(axis=1)
    return raw, sr


def wav_duration(path: Path) -> float:
    with wave.open(str(path), "rb") as w:
        return w.getnframes() / w.getframerate()


def envelope(path: Path, fps: int) -> list[float]:
    """Per-video-frame loudness 0..1, used for lip-sync."""
    x, sr = read_wav(path)
    hop = sr / fps
    n = int(len(x) / hop) + 1
    out = []
    for i in range(n):
        seg = x[int(i * hop): int((i + 1) * hop)]
        out.append(float(np.sqrt(np.mean(seg ** 2))) if len(seg) else 0.0)
    m = max(out) if out and max(out) > 0 else 1
    return [min(1.0, (v / m) ** 0.7 * 1.2) for v in out]


# =========================================================================== TTS engines
class EspeakEngine:
    name = "espeak"
    _lib = None
    _cb = None
    _buf = None
    _sr = 22050

    @classmethod
    def available(cls) -> bool:
        try:
            import espeakng_loader  # noqa
            return True
        except Exception:
            return False

    @classmethod
    def _init(cls):
        if cls._lib is not None:
            return
        import espeakng_loader as L
        lib = ctypes.CDLL(L.get_library_path())
        CB = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.POINTER(ctypes.c_short), ctypes.c_int, ctypes.c_void_p)
        cls._buf = array.array("h")

        def cb(wav, n, ev):
            if wav and n > 0:
                cls._buf.extend(wav[:n])
            return 0
        cls._cb = CB(cb)
        sr = lib.espeak_Initialize(2, 0, L.get_data_path().encode(), 0)  # AUDIO_OUTPUT_SYNCHRONOUS
        if sr <= 0:
            raise RuntimeError("espeak-ng failed to initialise")
        cls._sr = sr
        lib.espeak_SetSynthCallback(cls._cb)
        cls._lib = lib

    def synth(self, text: str, out: Path, lang: str, settings: dict):
        self._init()
        v = settings["voice"]
        lib = self._lib
        voice = v["espeak_voice"].get(lang, "en-us").encode()
        if lib.espeak_SetVoiceByName(voice) != 0:
            raise RuntimeError(f"espeak voice not found: {voice}")
        lib.espeak_SetParameter(1, int(v.get("espeak_rate", 160)), 0)   # espeakRATE
        lib.espeak_SetParameter(3, int(v.get("espeak_pitch", 45)), 0)   # espeakPITCH
        del self._buf[:]
        b = text.encode("utf-8")
        lib.espeak_Synth(b, len(b) + 1, 0, 1, 0, 1, None, None)
        lib.espeak_Synchronize()
        data = np.frombuffer(self._buf.tobytes(), dtype="<i2").astype(np.float32) / 32768
        write_wav(out, data, self._sr)


class PiperEngine:
    name = "piper"

    @staticmethod
    def model_for(lang, settings) -> Path | None:
        p = ROOT / settings["voice"]["piper_model"].get(lang, "")
        return p if p.suffix == ".onnx" and p.exists() and Path(str(p) + ".json").exists() else None

    @classmethod
    def available(cls, lang="en", settings=None) -> bool:
        settings = settings or load_settings()
        try:
            import piper  # noqa
        except Exception:
            return False
        return cls.model_for(lang, settings) is not None

    _voices: dict = {}

    def synth(self, text, out: Path, lang, settings):
        from piper import PiperVoice
        mp = self.model_for(lang, settings)
        if mp is None:
            raise RuntimeError(f"No Piper model for '{lang}'. Run: glavonja voices --download")
        if str(mp) not in self._voices:
            self._voices[str(mp)] = PiperVoice.load(str(mp))
        voice = self._voices[str(mp)]
        ls = float(settings["voice"].get("length_scale", 1.0))
        with wave.open(str(out), "wb") as wf:
            try:  # piper-tts >= 1.3
                from piper import SynthesisConfig
                voice.synthesize_wav(text, wf, syn_config=SynthesisConfig(length_scale=ls))
            except ImportError:
                voice.synthesize(text, wf, length_scale=ls)


class SapiEngine:
    name = "sapi"

    @staticmethod
    def available() -> bool:
        return os.name == "nt"

    def synth(self, text, out: Path, lang, settings):
        voice = settings["voice"].get("sapi_voice", "")
        tf = Path(tempfile.mkstemp(suffix=".txt")[1])
        tf.write_text(text, encoding="utf-8")
        ps = ("Add-Type -AssemblyName System.Speech;"
              "$s=New-Object System.Speech.Synthesis.SpeechSynthesizer;"
              + (f"$s.SelectVoice('{voice}');" if voice else "")
              + f"$s.SetOutputToWaveFile('{out}');"
              f"$s.Speak([IO.File]::ReadAllText('{tf}',[Text.Encoding]::UTF8));$s.Dispose()")
        try:
            run(["powershell", "-NoProfile", "-Command", ps], timeout=300)
        finally:
            tf.unlink(missing_ok=True)


def list_sapi_voices() -> list[str]:
    if os.name != "nt":
        return []
    ps = ("Add-Type -AssemblyName System.Speech;(New-Object System.Speech.Synthesis.SpeechSynthesizer)"
          ".GetInstalledVoices()|%{$_.VoiceInfo.Name + '|' + $_.VoiceInfo.Culture}")
    try:
        r = run(["powershell", "-NoProfile", "-Command", ps], timeout=60)
        return [l.strip() for l in r.stdout.decode(errors="replace").splitlines() if l.strip()]
    except Exception:
        return []


def pick_engine(lang: str, settings: dict, override: str | None = None):
    want = override or settings["voice"].get("engine", "auto")
    if want == "gemini":
        from .google_ai import GeminiEngine, gemini_available
        if gemini_available(settings):
            return GeminiEngine()
        get_logger().warning("Gemini TTS not available (disabled or no key) -> local voice fallback")
        want = "auto"
    if want == "piper" or (want == "auto" and PiperEngine.available(lang, settings)):
        return PiperEngine()
    if want == "sapi" and SapiEngine.available():
        return SapiEngine()
    if want in ("espeak", "auto", "piper", "sapi") and EspeakEngine.available():
        if want != "espeak" and want != "auto":
            get_logger().warning("Voice engine '%s' unavailable; falling back to espeak-ng", want)
        return EspeakEngine()
    raise RuntimeError("No TTS engine available. Run install.bat (installs espeakng-loader + piper-tts).")


def voice_status(settings=None) -> dict:
    s = settings or load_settings()
    return {"piper_sr": PiperEngine.available("sr", s), "piper_en": PiperEngine.available("en", s),
            "espeak": EspeakEngine.available(), "sapi": SapiEngine.available(),
            "sapi_voices": list_sapi_voices() if os.name == "nt" else []}


def tts_clean(text: str) -> str:
    t = re.sub(r"\[[^\]]*\]", "", text)          # stage directions
    return re.sub(r"\s+", " ", t).strip()


def synth_line(text: str, out: Path, lang: str, settings: dict, engine: str | None = None) -> str:
    eng = pick_engine(lang, settings, engine)
    raw = out.with_suffix(".raw.wav")
    eng.synth(tts_clean(text), raw, lang, settings)
    # resample to 44.1k mono, trim leading/trailing silence
    run([ffmpeg(), "-y", "-loglevel", "error", "-i", str(raw), "-af",
         "silenceremove=start_periods=1:start_threshold=-50dB,areverse,"
         "silenceremove=start_periods=1:start_threshold=-50dB,areverse",
         "-ar", str(SR), "-ac", "1", str(out)])
    raw.unlink(missing_ok=True)
    return eng.name


def normalize_and_concat(parts: list[Path], gaps: list[float], out_wav: Path, out_mp3: Path, lufs: float = -16):
    """Join segment WAVs with given silence gaps, loudness-normalise, export WAV+MP3."""
    chunks = []
    for p, g in zip(parts, gaps):
        x, sr = read_wav(p)
        chunks.append(x)
        chunks.append(np.zeros(int(g * SR), dtype=np.float32))
    full = np.concatenate(chunks) if chunks else np.zeros(SR, dtype=np.float32)
    tmp = out_wav.with_suffix(".tmp.wav")
    write_wav(tmp, full)
    run([ffmpeg(), "-y", "-loglevel", "error", "-i", str(tmp), "-af", f"loudnorm=I={lufs}:TP=-1.5:LRA=11",
         "-ar", str(SR), "-ac", "1", str(out_wav)])
    tmp.unlink(missing_ok=True)
    run([ffmpeg(), "-y", "-loglevel", "error", "-i", str(out_wav), "-b:a", "192k", str(out_mp3)])


# =========================================================================== music
MOODS = {
    # tempo, root midi, scale, progression (scale degrees), brightness
    "upbeat": (112, 60, [0, 2, 4, 5, 7, 9, 11], [0, 4, 5, 3], 1.0),
    "mystery": (84, 57, [0, 2, 3, 5, 7, 8, 10], [0, 5, 3, 4], 0.6),
    "horror": (66, 50, [0, 1, 3, 5, 6, 8, 10], [0, 1, 0, 6], 0.35),
    "epic": (96, 55, [0, 2, 3, 5, 7, 8, 10], [0, 5, 2, 6], 0.8),
    "chill": (90, 62, [0, 2, 4, 7, 9], [0, 3, 4, 2], 0.7),
    "tense": (128, 52, [0, 1, 3, 5, 7, 8, 10], [0, 0, 5, 6], 0.55),
}


def _midi(n):
    return 440.0 * 2 ** ((n - 69) / 12)


def _tone(freq, dur, kind="saw", sr=SR):
    t = np.arange(int(dur * sr)) / sr
    if kind == "sine":
        return np.sin(2 * np.pi * freq * t)
    if kind == "tri":
        return 2 * np.abs(2 * ((t * freq) % 1) - 1) - 1
    if kind == "square":
        return np.sign(np.sin(2 * np.pi * freq * t)) * 0.6
    # soft saw = few harmonics
    return sum(np.sin(2 * np.pi * freq * k * t) / k for k in range(1, 6)) * 0.6


def _adsr(n, a=0.01, d=0.1, s=0.6, r=0.1, sr=SR):
    env = np.ones(n) * s
    A, D, R = int(a * sr), int(d * sr), int(r * sr)
    A = min(A, n); env[:A] = np.linspace(0, 1, A) if A else env[:A]
    D2 = min(D, n - A)
    if D2 > 0:
        env[A:A + D2] = np.linspace(1, s, D2)
    R = min(R, n)
    if R:
        env[-R:] *= np.linspace(1, 0, R)
    return env


def make_music(mood: str, seconds: float, out: Path, seed: int = 0) -> Path:
    """Procedural background track (pads + bass + arp + light drums). Deterministic per seed."""
    tempo, root, scale, prog, bright = MOODS.get(mood, MOODS["upbeat"])
    rng = np.random.default_rng(seed)
    beat = 60 / tempo
    bar = beat * 4
    n_bars = int(math.ceil(seconds / bar)) + 1
    total = np.zeros(int((n_bars * bar + 2) * SR), dtype=np.float32)

    def add(sig, at):
        i = int(at * SR)
        j = min(len(total), i + len(sig))
        total[i:j] += sig[: j - i]

    def chord_notes(deg):
        return [root + scale[(deg + k) % len(scale)] + 12 * ((deg + k) // len(scale)) for k in (0, 2, 4)]

    kick = _tone(55, 0.25, "sine") * np.exp(-np.linspace(0, 12, int(0.25 * SR)))
    hat = rng.standard_normal(int(0.05 * SR)) * np.exp(-np.linspace(0, 30, int(0.05 * SR))) * 0.25
    for b in range(n_bars):
        deg = prog[b % len(prog)]
        notes = chord_notes(deg)
        t0 = b * bar
        pad = sum(_tone(_midi(n), bar, "tri") for n in notes) / 3
        add(pad * _adsr(len(pad), 0.4, 0.3, 0.8, 0.5) * 0.18, t0)
        bass = _tone(_midi(notes[0] - 24), bar, "saw")
        add(bass * _adsr(len(bass), 0.02, 0.2, 0.5, 0.2) * 0.22, t0)
        if mood != "horror":
            for k in range(8):
                n = notes[[0, 1, 2, 1, 0, 2, 1, 2][k]] + 12
                s = _tone(_midi(n), beat * 0.45, "square" if bright > 0.7 else "tri")
                add(s * _adsr(len(s), 0.005, 0.12, 0.2, 0.1) * 0.06 * bright, t0 + k * beat / 2)
        if mood in ("upbeat", "epic", "tense"):
            for k in range(4):
                add(kick * 0.5, t0 + k * beat)
                add(hat, t0 + k * beat + beat / 2)
        if mood == "horror":
            drone = _tone(_midi(root - 12) * (1 + 0.003 * math.sin(b)), bar, "sine")
            add(drone * 0.15, t0)
    total = total[: int(seconds * SR)]
    fade = min(len(total), int(1.5 * SR))
    total[:fade] *= np.linspace(0, 1, fade)
    total[-fade:] *= np.linspace(1, 0, fade)
    total /= max(1e-6, np.max(np.abs(total))) / 0.7
    write_wav(out, total)
    record_license(out, "music", "procedurally generated by GLAVONJA AI STUDIO (studio/audio.py)", "CC0 / own work")
    return out


# =========================================================================== SFX
SFX_NAMES = ["whoosh", "pop", "boom", "ding", "riser", "thud", "glitch", "heartbeat", "cash", "swoosh_down"]


def sfx_path(name: str) -> Path:
    folder = ASSETS_DIR / "sound_effects"
    folder.mkdir(parents=True, exist_ok=True)
    p = folder / f"{name}.wav"
    if not p.exists():
        write_wav(p, _make_sfx(name))
        record_license(p, "sfx", "procedurally generated (studio/audio.py)", "CC0 / own work")
    return p


def _make_sfx(name: str) -> np.ndarray:
    rng = np.random.default_rng(abs(hash(name)) % 2 ** 32)
    def n(d): return rng.standard_normal(int(d * SR)).astype(np.float32)
    def lin(a, b, d): return np.linspace(a, b, int(d * SR))
    if name in ("whoosh", "swoosh_down"):
        d = 0.45
        x = n(d)
        # crude moving band-pass via cumulative smoothing with varying alpha
        env = np.sin(np.linspace(0, np.pi, len(x))) ** 2
        y = np.zeros_like(x); acc = 0.0
        alphas = lin(0.05, 0.5, d) if name == "whoosh" else lin(0.5, 0.05, d)
        for i in range(len(x)):
            acc += alphas[i] * (x[i] - acc); y[i] = acc
        return y * env * 1.6
    if name == "pop":
        d = 0.12
        f = lin(900, 300, d)
        return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-lin(0, 25, d))
    if name in ("boom", "thud"):
        d = 1.2 if name == "boom" else 0.35
        f = lin(90, 30, d)
        s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-lin(0, 5 if name == "boom" else 14, d))
        return (s + n(d) * 0.3 * np.exp(-lin(0, 9, d))) * 0.9
    if name == "ding":
        d = 1.0
        t = np.arange(int(d * SR)) / SR
        return (np.sin(2 * np.pi * 1318 * t) + 0.5 * np.sin(2 * np.pi * 2637 * t)) * np.exp(-t * 4) * 0.5
    if name == "riser":
        d = 1.5
        f = lin(200, 1200, d)
        return (np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.4 + n(d) * 0.15) * lin(0, 1, d) ** 2
    if name == "glitch":
        d = 0.3
        x = np.sign(np.sin(2 * np.pi * np.cumsum(rng.choice([200, 800, 1500], int(d * SR))) / SR))
        return x * 0.3 * (rng.random(int(d * SR)) > 0.3)
    if name == "heartbeat":
        d = 1.0
        out = np.zeros(int(d * SR), dtype=np.float32)
        b = _make_sfx("thud")[: int(0.25 * SR)]
        for at in (0.0, 0.25):
            i = int(at * SR); out[i:i + len(b)] += b[: len(out) - i]
        return out
    if name == "cash":
        d = 0.6
        t = np.arange(int(d * SR)) / SR
        return (np.sin(2 * np.pi * 2000 * t) * np.exp(-t * 8) + n(d) * np.exp(-t * 30) * 0.4) * 0.5
    return n(0.1) * 0.1


# =========================================================================== final mix
def mix_audio(voice_wav: Path, music_wav: Path | None, sfx_events: list[tuple[str, float]], duration: float,
              out: Path, settings: dict):
    """Voice + ducked music + SFX -> AAC-ready WAV (stereo 44.1k)."""
    a = settings["audio"]
    inputs = ["-i", str(voice_wav)]
    has_music = bool(music_wav and a.get("music", True))
    split = ",asplit=2[voice][vkey]" if has_music else "[voice]"
    filters = ["[0:a]aformat=sample_rates=44100:channel_layouts=stereo,apad" + split]
    mixes = ["[voice]"]
    idx = 1
    if has_music:
        inputs += ["-i", str(music_wav)]
        filters.append(f"[{idx}:a]aformat=sample_rates=44100:channel_layouts=stereo,volume={a['music_volume_db']}dB[mus]")
        filters.append("[mus][vkey]sidechaincompress=threshold=0.03:ratio=6:attack=20:release=400[ducked]")
        mixes.append("[ducked]")
        idx += 1
    if a.get("sfx", True):
        for name, at in sfx_events[:120]:
            inputs += ["-i", str(sfx_path(name))]
            ms = int(max(0, at) * 1000)
            filters.append(f"[{idx}:a]aformat=sample_rates=44100:channel_layouts=stereo,"
                           f"volume={a['sfx_volume_db']}dB,adelay={ms}|{ms}[s{idx}]")
            mixes.append(f"[s{idx}]")
            idx += 1
    filters.append(f"{''.join(mixes)}amix=inputs={len(mixes)}:normalize=0:duration=first,"
                   f"atrim=0:{duration:.3f},alimiter=limit=0.95[out]")
    fc = ";".join(filters)
    out.with_suffix(".filter.txt").write_text(fc, encoding="utf-8")  # kept for debugging
    run([ffmpeg(), "-y", "-loglevel", "error", *inputs, "-filter_complex", fc, "-map", "[out]",
         "-ar", "44100", "-ac", "2", str(out)])
