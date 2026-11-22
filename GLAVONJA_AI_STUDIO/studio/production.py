"""Production pipeline: stages, resume, blockers (approvals), editor and quality control.

Every stage writes its outputs + project_state.json before the next one starts, so a crash or
shutdown resumes at the first unfinished stage and never redoes finished work.

A stage that needs the user (approval of Google credits, a missing Gemini key, Flow clips to
upload, a failed consistency check) raises `Blocked`.  The project then waits in the dashboard
with clear options - nothing is silently skipped.
"""
from __future__ import annotations

import json
import os
import shutil
import threading
import time
import traceback
import urllib.error
from pathlib import Path

from PIL import Image

from . import audio, consistency, google_ai
from .agents import researcher, scriptwriter, seo, thumbnails, visual_director
from .core import (OUTPUTS_DIR, ROOT, STAGES, STAGE_LABELS, Project, atomic_write_json, db_exec, event, ffmpeg,
                   find_tool, load_settings, load_style, now_iso, read_json, run, sha, slugify)
from .render.scene import FrameRenderer


class Blocked(Exception):
    def __init__(self, kind: str, message: str, options: list[dict] | None = None, data: dict | None = None):
        super().__init__(message)
        self.kind, self.message, self.options, self.data = kind, message, options or [], data or {}


def _approved(p: Project, key: str) -> bool:
    return bool(p.state.get("approvals", {}).get(key, {}).get("approved"))


def _declined(p: Project, key: str) -> bool:
    return bool(p.state.get("approvals", {}).get(key, {}).get("declined"))


# =========================================================================== stage: research / script / storyboard
def stage_research(p: Project, log):
    scriptwriter.research_topic(p, log)


def stage_script(p: Project, log):
    if p.path("script", "script.json").exists() and read_json(p.path("script", "script.json"), {}).get("mode") == "user_edited":
        log("  using your edited script")
        return
    data = scriptwriter.write_script(p, log)
    if data.get("warning"):
        p.state["warnings"] = sorted(set(p.state.get("warnings", []) + [data["warning"]]))


def stage_storyboard(p: Project, log):
    visual_director.build_storyboard(p, log)


# =========================================================================== stage: voice (Gemini mandatory)
GAP = 0.18  # seconds between sentences


def _voice_engine(p: Project, s: dict, texts: list[str]) -> str:
    """Return 'gemini' or 'local'. Raises Blocked when the user must decide."""
    if _approved(p, "local_voice_fallback"):
        return "local"
    fallback_opt = {"action": "approve", "key": "local_voice_fallback",
                    "label": "Odobri lokalni glas SAMO za ovaj video (Piper/espeak)"}
    if not google_ai.gemini_available(s):
        raise Blocked("gemini_unavailable",
                      "Gemini TTS je obavezan, ali nije podešen: u Settings upiši Gemini API ključ "
                      "(besplatan: https://aistudio.google.com/apikey).",
                      [{"action": "settings", "label": "Otvori Settings i upiši ključ"}, fallback_opt])
    g = s["google"]
    if not (g.get("tts_voice") and g.get("tts_voice_locked")):
        raise Blocked("choose_voice",
                      "Gemini glas još nije izabran. Pokreni probu glasova, preslušaj i ZAKLJUČAJ jedan - "
                      "on se koristi u svakom budućem videu.",
                      [{"action": "voice_audition", "label": "Proba glasova (6 glasova)"}, fallback_opt])
    est = google_ai.estimate_tts(texts)
    if _declined(p, "gemini_tts"):
        raise Blocked("declined", "Odbio si Gemini generisanje za ovaj video. Odobri ga ili odobri lokalni glas.",
                      [{"action": "approve", "key": "gemini_tts", "label": "Ipak odobri Gemini TTS"}, fallback_opt],
                      {"estimate": est})
    if not _approved(p, "gemini_tts"):
        if g.get("auto_approve_under_free_tier") and est["fits_free_tier"]:
            google_ai.approve(p, "gemini_tts")
        else:
            google_ai.request_approval(p, "gemini_tts", est)
            raise Blocked("approval", f"Odobri Gemini TTS: {est['requests']} zahteva, ~{est['audio_seconds_est']}s zvuka "
                                      f"(procena; besplatni limit ~{est['free_tier_requests_per_day']}/dan).",
                          [{"action": "approve", "key": "gemini_tts", "label": "Odobri Gemini TTS"},
                           {"action": "decline", "key": "gemini_tts", "label": "Odbij"}], {"estimate": est})
    return "gemini"


def stage_voice(p: Project, log):
    s = load_settings()
    script = read_json(p.path("script", "script.json"))
    lines = script["lines"]
    lang = p.state["language"]
    engine = _voice_engine(p, s, [l["text"] for l in lines])
    vdir = p.path("voice")
    meta = read_json(vdir / "lines.json", {"lines": {}})
    if meta.get("engine_kind") and meta["engine_kind"] != engine:
        # switching engine mid-video would make the voice inconsistent -> keep old files, redo all lines
        keep = vdir / f"previous_{meta['engine_kind']}"
        keep.mkdir(exist_ok=True)
        for f in vdir.glob("line_*.wav"):
            shutil.move(str(f), keep / f.name)
        meta = {"lines": {}}
        log(f"  voice engine changed -> previous files kept in {keep.name}/")
    meta["engine_kind"] = engine
    for ln in lines:
        out = vdir / f"line_{ln['id']:03d}.wav"
        key = sha([ln["text"], engine, s["google"].get("tts_voice") if engine == "gemini" else s["voice"]])
        if out.exists() and meta["lines"].get(str(ln["id"]), {}).get("key") == key:
            continue
        try:
            if engine == "gemini":
                raw = out.with_suffix(".gem.wav")
                google_ai.gemini_tts(ln["text"], raw, s)
                run([ffmpeg(), "-y", "-loglevel", "error", "-i", str(raw), "-af",
                     "silenceremove=start_periods=1:start_threshold=-50dB,areverse,"
                     "silenceremove=start_periods=1:start_threshold=-50dB,areverse", "-ar", "44100", "-ac", "1", str(out)])
                raw.unlink(missing_ok=True)
                name = f"gemini:{s['google']['tts_voice']}"
            else:
                name = audio.synth_line(ln["text"], out, lang, s, None if s["voice"]["engine"] == "gemini" else s["voice"]["engine"])
        except urllib.error.HTTPError as e:
            atomic_write_json(vdir / "lines.json", meta)
            if e.code in (429, 403):
                raise Blocked("google_credits_exhausted",
                              f"Gemini je odbio zahtev (HTTP {e.code}: kvota/krediti potrošeni ili ključ bez pristupa). "
                              "Sačekaj reset kvote (obično sutradan) ili izričito odobri lokalni glas.",
                              [{"action": "continue", "label": "Pokušaj ponovo (posle reseta kvote)"},
                               {"action": "approve", "key": "local_voice_fallback", "label": "Odobri lokalni glas"}])
            raise
        meta["lines"][str(ln["id"])] = {"key": key, "engine": name, "duration": audio.wav_duration(out)}
        atomic_write_json(vdir / "lines.json", meta)  # save after EVERY line (resume-safe)
        log(f"  voice {ln['id']}/{len(lines)} ({name})")
    files = [vdir / f"line_{l['id']:03d}.wav" for l in lines]
    audio.normalize_and_concat(files, [GAP] * len(files), vdir / "narration.wav", vdir / "narration.mp3",
                               s["audio"]["voice_lufs"])
    # timing: each line's start/end inside narration.wav
    t, timing = 0.0, []
    for l in lines:
        d = meta["lines"][str(l["id"])]["duration"]
        timing.append({"id": l["id"], "start": round(t, 3), "end": round(t + d, 3), "text": l["text"]})
        t += d + GAP
    atomic_write_json(vdir / "timing.json", {"lines": timing, "total": round(t, 3)})
    # update storyboard durations from real audio
    sb = read_json(p.path("storyboard", "storyboard.json"))
    tm = {x["id"]: x for x in timing}
    for sc in sb["scenes"]:
        st = tm[sc["line_ids"][0]]["start"]
        en = tm[sc["line_ids"][-1]]["end"] + GAP
        sc["start"], sc["duration"], sc["duration_is_estimate"] = round(st, 3), round(en - st, 3), False
    atomic_write_json(p.path("storyboard", "storyboard.json"), sb)
    engines = sorted({v["engine"] for v in meta["lines"].values()})
    p.state["voice_engines"] = engines
    if engine == "local":
        p.state.setdefault("notices", []).append("Gemini TTS NIJE korišćen za glas (odobren lokalni fallback).")
    log(f"  narration: {t:.1f}s, engines: {engines}")


# =========================================================================== stage: visuals (storyboard frames)
def stage_visuals(p: Project, log):
    style = load_style()
    s = load_settings()
    sb = read_json(p.path("storyboard", "storyboard.json"))
    r = FrameRenderer(style, s["video"]["width"], s["video"]["height"])
    thumbs = []
    for sc in sb["scenes"]:
        out = p.path("scenes", f"scene_{sc['id']:03d}.png")
        if not out.exists():
            r.render(sc, min(1.2, sc["duration"] * 0.5)).save(out)
        thumbs.append(out)
    # storyboard contact sheet
    cols = 4
    rows = (len(thumbs) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * 480, rows * 270), (20, 20, 20))
    for i, f in enumerate(thumbs):
        sheet.paste(Image.open(f).resize((480, 270)), ((i % cols) * 480, (i // cols) * 270))
    sheet.save(p.path("storyboard", "storyboard_sheet.jpg"), quality=85)
    log(f"  {len(thumbs)} storyboard frames")


# =========================================================================== stage: animation (Flow mandatory)
def _encode_args(s):
    v = s["video"]
    return ["-c:v", "libx264", "-preset", v["preset"], "-crf", str(v["crf"]), "-pix_fmt", "yuv420p", "-r", str(v["fps"])]


def render_procedural(p: Project, sc: dict, out: Path, prev_last: Path | None, env: list[float], s: dict, style: dict):
    W, H, fps = s["video"]["width"], s["video"]["height"], s["video"]["fps"]
    r = FrameRenderer(style, W, H)
    n = max(1, int(round(sc["duration"] * fps)))
    prev = Image.open(prev_last) if prev_last and prev_last.exists() else None
    start_f = int(sc.get("start", 0) * fps)
    tmp = out.with_suffix(".part.mp4")
    cmd = [ffmpeg(), "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
           "-r", str(fps), "-i", "-", *_encode_args(s), "-an", str(tmp)]
    kw = {"creationflags": 0x08000000} if os.name == "nt" else {}
    import subprocess
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE, **kw)
    last = None
    try:
        for f in range(n):
            t = f / fps
            mouth = env[start_f + f] if start_f + f < len(env) else 0.0
            frame = r.render(sc, t, mouth=mouth, prev_frame=prev)
            proc.stdin.write(frame.tobytes())
            last = frame
        proc.stdin.close()
        err = proc.stderr.read().decode(errors="replace")
        if proc.wait() != 0:
            raise RuntimeError("ffmpeg encode failed: " + err[-500:])
    except BrokenPipeError:
        raise RuntimeError("ffmpeg closed the pipe: " + proc.stderr.read().decode(errors="replace")[-500:])
    os.replace(tmp, out)
    last.save(out.with_name(out.stem + "_last.png"))


def conform_clip(src: Path, out: Path, duration: float, s: dict):
    """Scale/pad any Flow clip to 1920x1080, exact duration (trim or hold last frame), fps, no audio."""
    W, H, fps = s["video"]["width"], s["video"]["height"], s["video"]["fps"]
    vf = (f"scale={W}:{H}:force_original_aspect_ratio=decrease,pad={W}:{H}:(ow-iw)/2:(oh-ih)/2,setsar=1,fps={fps},"
          f"tpad=stop_mode=clone:stop_duration={duration + 1:.2f},trim=duration={duration:.3f},setpts=PTS-STARTPTS")
    run([ffmpeg(), "-y", "-loglevel", "error", "-i", str(src), "-vf", vf, *_encode_args(s), "-an", str(out)])
    run([ffmpeg(), "-y", "-loglevel", "error", "-sseof", "-0.1", "-i", str(out), "-frames:v", "1",
         str(out.with_name(out.stem + "_last.png"))])


def clip_frames(src: Path, n: int = 3) -> list[Image.Image]:
    dur = probe(src).get("duration", 4)
    imgs = []
    for k in range(n):
        tmp = src.with_suffix(f".chk{k}.png")
        run([ffmpeg(), "-y", "-loglevel", "error", "-ss", f"{dur * (k + 1) / (n + 1):.2f}", "-i", str(src),
             "-frames:v", "1", str(tmp)])
        imgs.append(Image.open(tmp).convert("RGB"))
        tmp.unlink(missing_ok=True)
    return imgs


def stage_animation(p: Project, log):
    s = load_settings()
    style = load_style()
    sb = read_json(p.path("storyboard", "storyboard.json"))
    adir = p.path("animations")
    info = read_json(adir / "clips.json", {"clips": {}})
    fallback = _approved(p, "flow_fallback_local")
    missing, rejected = [], []
    has_refs = consistency.has_references()
    for sc in sb["scenes"]:
        out = adir / f"scene_{sc['id']:03d}.mp4"
        key = sha([sc, s["video"]])
        rec = info["clips"].get(str(sc["id"]), {})
        if out.exists() and rec.get("key") == key:
            continue
        src = google_ai.flow_inbox_clip(p, sc["id"]) if sc.get("use_flow", True) else None
        if src:
            checks = [consistency.check_image(im) for im in clip_frames(src)]
            status = "unverified" if not has_refs else ("pass" if all(c["status"] == "pass" for c in checks) else "fail")
            if status == "fail":
                rej = p.path("flow", "rejected")
                rej.mkdir(parents=True, exist_ok=True)
                shutil.move(str(src), rej / f"{src.stem}_{int(time.time())}{src.suffix}")
                rejected.append({"id": sc["id"], "checks": checks})
                log(f"  scene {sc['id']}: Flow clip FAILED style check -> must be regenerated in Flow")
                continue
            conform_clip(src, out, sc["duration"], s)
            info["clips"][str(sc["id"])] = {"key": key, "source": "google_flow", "file": src.name, "consistency": status,
                                            "checks": checks}
            google_ai.record_google_asset(src, "video", "Google Flow", {"scene": sc["id"]})
            log(f"  scene {sc['id']}: Flow clip imported ({status})")
        elif fallback or not sc.get("use_flow", True):
            missing_note = "local fallback (approved)" if fallback else "local (Flow disabled for this scene)"
            env = audio.envelope(p.path("voice", "narration.wav"), s["video"]["fps"]) if p.path("voice", "narration.wav").exists() else []
            prev = adir / f"scene_{sc['id'] - 1:03d}_last.png"
            render_procedural(p, sc, out, prev, env, s, style)
            info["clips"][str(sc["id"])] = {"key": key, "source": "procedural", "note": missing_note}
            log(f"  scene {sc['id']}/{len(sb['scenes'])}: rendered procedurally ({missing_note})")
        else:
            missing.append(sc)
            continue
        atomic_write_json(adir / "clips.json", info)
    atomic_write_json(adir / "clips.json", info)
    if missing or rejected:
        est = google_ai.estimate_flow(len(missing) + len(rejected), s["google"].get("flow_mode"))
        if not _approved(p, "flow_generation"):
            google_ai.request_approval(p, "flow_generation", est)
            raise Blocked("approval", f"Odobri Google Flow za {est['clips']} klipova (~{est['credits_total_est']} kredita, procena).",
                          [{"action": "approve", "key": "flow_generation", "label": "Odobri Flow generisanje"},
                           {"action": "approve", "key": "flow_fallback_local",
                            "label": "Flow nije dostupan - odobri lokalnu animaciju"}], {"estimate": est})
        need = [sc for sc in sb["scenes"] if any(sc["id"] == m["id"] for m in missing)] + \
               [dict(next(x for x in sb["scenes"] if x["id"] == r["id"]), description="REGENERATE (previous clip did not match "
                     "the channel style): " + next(x for x in sb["scenes"] if x["id"] == r["id"])["description"]) for r in rejected]
        req = google_ai.flow_requests(p, [dict(x, use_flow=True) for x in need], style)
        p.state["notices"] = [n for n in p.state.get("notices", []) if not n.startswith("Flow")] + \
            [f"Flow: čeka se {len(need)} klipova ({len(rejected)} za ponovno generisanje)."]
        raise Blocked("waiting_flow_clips",
                      f"Čeka se {len(need)} Google Flow klipova. Otvori {req.relative_to(ROOT).as_posix()}, generiši klipove u Flow-u "
                      f"i ubaci ih (dugme Upload ili folder flow/inbox), pa klikni Continue.",
                      [{"action": "upload_flow", "label": "Ubaci Flow klipove"},
                       {"action": "continue", "label": "Continue (proveri inbox)"},
                       {"action": "approve", "key": "flow_fallback_local", "label": "Flow nije dostupan - odobri lokalnu animaciju"}],
                      {"missing": [x["id"] for x in need], "requests_file": req.relative_to(ROOT).as_posix(),
                       "rejected": rejected})
    if fallback:
        p.state.setdefault("notices", []).append("Google Flow NIJE korišćen za sve scene (odobrena lokalna animacija).")


# =========================================================================== stage: edit
def _ass_time(t):
    h, rem = divmod(max(0, t), 3600)
    m, s_ = divmod(rem, 60)
    return f"{int(h)}:{int(m):02d}:{s_:05.2f}"


def _srt_time(t):
    ms = int(round(max(0, t) * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    sec, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{sec:02d},{ms:03d}"


def build_subtitles(p: Project, style: dict, s: dict):
    timing = read_json(p.path("voice", "timing.json"))["lines"]
    ss = style["subtitles"]
    maxw = ss.get("max_words_per_line", 6)
    cues = []
    for l in timing:
        words = l["text"].split()
        chunks = [words[i:i + maxw] for i in range(0, len(words), maxw)]
        dur = l["end"] - l["start"]
        total = sum(len(" ".join(c)) for c in chunks) or 1
        t = l["start"]
        for c in chunks:
            d = dur * len(" ".join(c)) / total
            cues.append((t, t + d, " ".join(c)))
            t += d
    srt = [f"{i + 1}\n{_srt_time(a)} --> {_srt_time(b)}\n{txt}\n" for i, (a, b, txt) in enumerate(cues)]
    p.path("subtitles", "subtitles.srt").write_text("\n".join(srt), encoding="utf-8")

    def ass_col(h):
        h = h.lstrip("#")
        return f"&H00{h[4:6]}{h[2:4]}{h[0:2]}"
    H = s["video"]["height"]
    size = int(ss["size_px"] * H / 1080)
    ass = ["[Script Info]", "ScriptType: v4.00+", f"PlayResX: {s['video']['width']}", f"PlayResY: {H}", "",
           "[V4+ Styles]",
           "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, "
           "Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
           f"Style: Default,DejaVu Sans,{size},{ass_col(ss['color'])},{ass_col(ss['highlight_color'])},{ass_col(ss['outline_color'])},"
           f"&H64000000,-1,0,0,0,100,100,0,0,1,{ss['outline_px']},0,2,60,60,{int(H * 0.06)},1", "",
           "[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
    for a, b, txt in cues:
        txt = txt.upper() if ss.get("uppercase") else txt
        ass.append(f"Dialogue: 0,{_ass_time(a)},{_ass_time(b)},Default,,0,0,0,,{txt}")
    p.path("subtitles", "subtitles.ass").write_text("\n".join(ass), encoding="utf-8")
    return cues


def stage_edit(p: Project, log):
    s = load_settings()
    style = load_style()
    sb = read_json(p.path("storyboard", "storyboard.json"))
    clips = [p.path("animations", f"scene_{sc['id']:03d}.mp4") for sc in sb["scenes"]]
    miss = [c.name for c in clips if not c.exists()]
    if miss:
        raise RuntimeError(f"Missing scene clips: {miss[:5]}")
    lst = p.path("animations", "concat.txt")
    lst.write_text("\n".join(f"file '{c.name}'" for c in clips), encoding="utf-8")
    joined = p.path("animations", "joined.mp4")
    run([ffmpeg(), "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(joined)])
    narration = p.path("voice", "narration.wav")
    total = audio.wav_duration(narration)
    vdur = probe(joined).get("duration", 0)
    dur = max(total, vdur)
    music = p.path("music", "music.wav")
    if s["audio"]["music"] and not music.exists():
        audio.make_music(sb.get("mood", "mystery"), dur + 1, music, seed=int(sha(p.id), 16) % 1000)
    events = []
    for sc in sb["scenes"]:
        for fx in sc.get("sfx", []):
            events.append((fx["name"], sc.get("start", 0) + fx.get("at", 0)))
    mix = p.path("final", "mix.wav")
    audio.mix_audio(narration, music if s["audio"]["music"] else None, events, dur, mix, s)
    build_subtitles(p, style, s)
    slug = slugify(p.state["title"], 50)
    out = p.path("final", f"{slug}.mp4")
    vf = []
    if s["video"].get("burn_subtitles", True):
        fonts_rel = os.path.relpath(ROOT / "assets" / "fonts", p.folder).replace("\\", "/")
        vf = ["-vf", f"subtitles=subtitles/subtitles.ass:fontsdir={fonts_rel}"]
    _run_in(p.folder, [ffmpeg(), "-y", "-loglevel", "error", "-i", os.path.relpath(joined, p.folder),
                       "-i", os.path.relpath(mix, p.folder), *vf, *_encode_args(s), "-c:a", "aac", "-b:a", "192k",
                       "-ar", "48000", "-map", "0:v:0", "-map", "1:a:0", "-t", f"{dur:.3f}",
                       "-movflags", "+faststart", os.path.relpath(out, p.folder)])
    p.state["final_video"] = out.relative_to(ROOT).as_posix()
    log(f"  final video: {out.name} ({dur:.1f}s)")


def _run_in(cwd: Path, cmd: list):
    import subprocess
    kw = {"creationflags": 0x08000000} if os.name == "nt" else {}
    r = subprocess.run(cmd, cwd=str(cwd), capture_output=True, **kw)
    if r.returncode != 0:
        raise RuntimeError("ffmpeg failed: " + r.stderr.decode(errors="replace")[-1500:])


# =========================================================================== stage: thumbnails / seo
def stage_thumbnails(p: Project, log):
    thumbnails.make_thumbnails(p, log)


def stage_seo(p: Project, log):
    seo.make_metadata(p, log)


# =========================================================================== stage: QC
def probe(path: Path) -> dict:
    fp = find_tool("ffprobe")
    if fp:
        r = run([fp, "-v", "error", "-show_entries", "format=duration:stream=codec_type,codec_name,width,height,"
                 "r_frame_rate,sample_rate,channels", "-of", "json", str(path)])
        j = json.loads(r.stdout)
        out = {"duration": float(j.get("format", {}).get("duration", 0) or 0), "streams": j.get("streams", [])}
    else:  # parse ffmpeg -i
        import re
        r = run([ffmpeg(), "-hide_banner", "-i", str(path)], check=False)
        err = r.stderr.decode(errors="replace")
        m = re.search(r"Duration: (\d+):(\d+):([\d.]+)", err)
        out = {"duration": int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3)) if m else 0, "streams": []}
        v = re.search(r"Video: (\w+).*?, (\d{3,5})x(\d{3,5})", err)
        if v:
            out["streams"].append({"codec_type": "video", "codec_name": v.group(1), "width": int(v.group(2)), "height": int(v.group(3))})
        if "Audio:" in err:
            out["streams"].append({"codec_type": "audio"})
    return out


def stage_qc(p: Project, log):
    s = load_settings()
    sb = read_json(p.path("storyboard", "storyboard.json"))
    final = ROOT / p.state["final_video"]
    checks = []

    def ck(name, ok, detail=""):
        checks.append({"check": name, "ok": bool(ok), "detail": str(detail)})
        log(f"  [{'OK' if ok else 'FAIL'}] {name} {detail}")

    ck("video file exists", final.exists() and final.stat().st_size > 10000, final.name)
    info = probe(final) if final.exists() else {"streams": [], "duration": 0}
    v = next((x for x in info["streams"] if x.get("codec_type") == "video"), {})
    a = next((x for x in info["streams"] if x.get("codec_type") == "audio"), None)
    ck("playable (decodes fully)", _decodes(final), "")
    ck("resolution 1920x1080", (v.get("width"), v.get("height")) == (s["video"]["width"], s["video"]["height"]),
       f"{v.get('width')}x{v.get('height')}")
    ck("aspect ratio 16:9", v.get("width") and abs(v["width"] / v["height"] - 16 / 9) < 0.01)
    ck("codec H.264", v.get("codec_name") == "h264", v.get("codec_name"))
    ck("audio present", a is not None)
    vol = _mean_volume(final)
    ck("audio not silent", vol is not None and vol > -45, f"mean {vol} dB")
    narr = audio.wav_duration(p.path("voice", "narration.wav"))
    ck("audio/video in sync (durations)", abs(info["duration"] - narr) < 1.0, f"video {info['duration']:.2f}s / narration {narr:.2f}s")
    end_last = sb["scenes"][-1].get("start", 0) + sb["scenes"][-1]["duration"]
    ck("scenes cover narration", abs(end_last - narr) < 0.6, f"{end_last:.2f}s")
    srt = p.path("subtitles", "subtitles.srt").read_text(encoding="utf-8") if p.path("subtitles", "subtitles.srt").exists() else ""
    ck("subtitles inside video duration", srt and all(True for _ in [0]) and _srt_last(srt) <= info["duration"] + 0.2,
       f"last cue {_srt_last(srt):.2f}s")
    clips = read_json(p.path("animations", "clips.json"), {"clips": {}})["clips"]
    ck("no missing scenes", all(str(sc["id"]) in clips for sc in sb["scenes"]), f"{len(clips)}/{len(sb['scenes'])}")
    bad = []
    for f in sorted(p.path("scenes").glob("scene_*.png")):
        try:
            Image.open(f).verify()
        except Exception:
            bad.append(f.name)
    ck("no corrupted images", not bad, ",".join(bad))
    blacks = _black_segments(final)
    ck("no accidental black frames", not blacks, f"{blacks[:3]}")
    # ---- visual consistency gate (PART 3.1.2)
    has_refs = consistency.has_references()
    scene_res = []
    if has_refs:
        consistency.build_signatures(log=lambda *_: None)
        for sc in sb["scenes"]:
            rec = clips.get(str(sc["id"]), {})
            mid = _frame_at(final, sc.get("start", 0) + sc["duration"] / 2)
            res = consistency.check_image(mid)
            res.update({"scene": sc["id"], "source": rec.get("source")})
            scene_res.append(res)
        fails = [r["scene"] for r in scene_res if r["status"] == "fail"]
        ck("visual consistency vs GLAVONJA references", not fails, f"failed scenes: {fails}" if fails else f"{len(scene_res)} scenes pass")
    else:
        ck("visual consistency vs GLAVONJA references", False, "NO REFERENCES - add channel frames to references/frames")
    sources = {}
    for c in clips.values():
        sources[c.get("source")] = sources.get(c.get("source"), 0) + 1
    tech_ok = all(c["ok"] for c in checks if not c["check"].startswith("visual consistency"))
    visual_ok = next(c for c in checks if c["check"].startswith("visual consistency"))["ok"]
    style_ok = load_style().get("verified", False)
    report = {"generated": now_iso(), "technical_ok": tech_ok, "visual_consistency_ok": visual_ok,
              "style_approved_by_user": style_ok, "checks": checks, "scene_consistency": scene_res,
              "clip_sources": sources, "voice_engines": p.state.get("voice_engines"),
              "notices": p.state.get("notices", []), "warnings": p.state.get("warnings", [])}
    atomic_write_json(p.path("final", "production_report.json"), report)
    _write_report_md(p, report)
    if not tech_ok:
        raise RuntimeError("Technical QC failed: " + ", ".join(c["check"] for c in checks if not c["ok"]))
    export_ok = visual_ok and style_ok and sources.get("google_flow", 0) == len(sb["scenes"]) and \
        not any(str(e).startswith("local") for e in (p.state.get("voice_engines") or []))
    if export_ok or not s["consistency"].get("require_references_for_export", True):
        dest = OUTPUTS_DIR / p.id
        dest.mkdir(parents=True, exist_ok=True)
        for f in [final, p.path("subtitles", "subtitles.srt"), p.path("final", "metadata.md"), p.path("final", "production_report.md")]:
            if f.exists():
                shutil.copy2(f, dest / f.name)
        for f in p.path("thumbnails").glob("thumb_*.png"):
            shutil.copy2(f, dest / f.name)
        p.state["export"] = {"status": "exported", "folder": dest.relative_to(ROOT).as_posix()}
        log(f"  EXPORTED -> {dest}")
    else:
        why = []
        if not visual_ok:
            why.append("vizuelna provera nije prošla / nema referenci kanala")
        if not style_ok:
            why.append("stil još nije odobren (/glavonja-style approve)")
        if sources.get("google_flow", 0) != len(sb["scenes"]):
            why.append(f"samo {sources.get('google_flow', 0)}/{len(sb['scenes'])} scena iz Google Flow-a")
        if any(str(e).startswith("local") or not str(e).startswith("gemini") for e in (p.state.get("voice_engines") or [])):
            why.append("glas nije Gemini TTS")
        p.state["export"] = {"status": "draft", "reasons": why,
                             "folder": p.path("final").relative_to(ROOT).as_posix()}
        log("  DRAFT ONLY (not exported): " + "; ".join(why))


def _decodes(path: Path) -> bool:
    r = run([ffmpeg(), "-v", "error", "-i", str(path), "-f", "null", "-"], check=False)
    return r.returncode == 0 and not r.stderr.strip()


def _mean_volume(path: Path):
    import re
    r = run([ffmpeg(), "-hide_banner", "-i", str(path), "-af", "volumedetect", "-vn", "-f", "null", "-"], check=False)
    m = re.search(r"mean_volume: (-?[\d.]+) dB", r.stderr.decode(errors="replace"))
    return float(m.group(1)) if m else None


def _black_segments(path: Path):
    import re
    r = run([ffmpeg(), "-hide_banner", "-i", str(path), "-vf", "blackdetect=d=0.4:pic_th=0.97", "-an", "-f", "null", "-"], check=False)
    return re.findall(r"black_start:([\d.]+)", r.stderr.decode(errors="replace"))


def _frame_at(path: Path, t: float) -> Image.Image:
    import subprocess
    r = run([ffmpeg(), "-v", "error", "-ss", f"{t:.2f}", "-i", str(path), "-frames:v", "1", "-f", "image2pipe", "-vcodec", "png", "-"])
    import io
    return Image.open(io.BytesIO(r.stdout)).convert("RGB")


def _srt_last(srt: str) -> float:
    import re
    ts = re.findall(r"--> (\d+):(\d+):(\d+),(\d+)", srt)
    if not ts:
        return 0.0
    h, m, s_, ms = map(int, ts[-1])
    return h * 3600 + m * 60 + s_ + ms / 1000


def _write_report_md(p: Project, r: dict):
    L = [f"# Production report - {p.state['title']}", "", f"Generated: {r['generated']}", "",
         f"- Technical QC: **{'PASS' if r['technical_ok'] else 'FAIL'}**",
         f"- Visual consistency vs channel: **{'PASS' if r['visual_consistency_ok'] else 'NOT PASSED'}**",
         f"- Style approved by user: **{r['style_approved_by_user']}**",
         f"- Clip sources: {r['clip_sources']}", f"- Voice: {r['voice_engines']}", "", "## Checks", ""]
    L += [f"- {'✅' if c['ok'] else '❌'} {c['check']} {c['detail']}" for c in r["checks"]]
    if r["notices"] or r["warnings"]:
        L += ["", "## Notices", ""] + [f"- {n}" for n in r["notices"] + r["warnings"]]
    if r["scene_consistency"]:
        L += ["", "## Scene consistency", ""] + [f"- scene {x['scene']}: {x['status']} (distance {x.get('distance')}, "
                                                 f"closest {x.get('closest_reference')}, source {x.get('source')})"
                                                 for x in r["scene_consistency"]]
    p.path("final", "production_report.md").write_text("\n".join(L), encoding="utf-8")


# =========================================================================== runner
STAGE_FUNCS = {"research": stage_research, "script": stage_script, "storyboard": stage_storyboard, "voice": stage_voice,
               "visuals": stage_visuals, "animation": stage_animation, "edit": stage_edit, "thumbnails": stage_thumbnails,
               "seo": stage_seo, "qc": stage_qc}
_running: dict[str, threading.Thread] = {}
_lock = threading.Lock()


def is_running(pid: str) -> bool:
    t = _running.get(pid)
    return bool(t and t.is_alive())


def run_pipeline(p: Project, log=print, until: str | None = None) -> dict:
    """Run every unfinished stage in order. Safe to call again after a crash/shutdown."""
    lockf = p.path(".running")
    if lockf.exists():
        try:
            pid = int(lockf.read_text())
            if pid != os.getpid() and _pid_alive(pid):
                raise RuntimeError("This project is already being produced by another process.")
        except ValueError:
            pass
    lockf.write_text(str(os.getpid()))
    p.state["status"] = "running"
    p.state.pop("blocker", None)
    p.save()
    try:
        for st in STAGES:
            if p.stage_status(st) == "done":
                continue
            p.mark(st, "running")
            event(p.id, "info", f"STAGE {STAGE_LABELS[st]} started")
            try:
                STAGE_FUNCS[st](p, log)
            except Blocked as b:
                p.state["blocker"] = {"stage": st, "kind": b.kind, "message": b.message, "options": b.options,
                                      "data": b.data, "since": now_iso()}
                p.state["status"] = "waiting"
                p.mark(st, "blocked")
                event(p.id, "info", f"WAITING at {st}: {b.message}")
                return {"status": "waiting", "blocker": p.state["blocker"]}
            except Exception as e:
                p.state["status"] = "failed"
                p.state["last_error"] = {"stage": st, "error": str(e)[:2000], "trace": traceback.format_exc()[-4000:]}
                p.mark(st, "failed", error=str(e)[:500])
                event(p.id, "error", f"STAGE {st} FAILED: {e}")
                return {"status": "failed", "error": str(e)}
            p.mark(st, "done")
            event(p.id, "info", f"STAGE {STAGE_LABELS[st]} done")
            if until and st == until:
                p.state["status"] = "paused"
                p.save()
                return {"status": "paused"}
        p.state["status"] = "ready_for_review"
        p.save()
        db_exec("UPDATE ideas SET status='produced' WHERE id=?", (p.state["idea"].get("id"),))
        return {"status": "ready_for_review"}
    finally:
        lockf.unlink(missing_ok=True)


def _pid_alive(pid: int) -> bool:
    try:
        if os.name == "nt":
            import ctypes
            h = ctypes.windll.kernel32.OpenProcess(0x1000, False, pid)
            if h:
                ctypes.windll.kernel32.CloseHandle(h)
                return True
            return False
        os.kill(pid, 0)
        return True
    except Exception:
        return False


def run_in_background(p: Project, log=None) -> bool:
    with _lock:
        if is_running(p.id):
            return False
        lines = []

        def _log(msg):
            lines.append(msg)
            (log or print)(msg)
            p.path("logs.txt").open("a", encoding="utf-8").write(msg + "\n")
        t = threading.Thread(target=lambda: run_pipeline(Project(p.folder), _log), daemon=True)
        _running[p.id] = t
        t.start()
        return True


def reset_stage(p: Project, stage: str):
    """Mark a stage and everything after it as pending (files are kept; caches decide what to redo)."""
    i = STAGES.index(stage)
    for st in STAGES[i:]:
        p.state["stages"][st] = {"status": "pending"}
    p.save()
