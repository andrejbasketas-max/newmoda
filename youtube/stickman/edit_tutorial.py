#!/usr/bin/env python3
"""edit_tutorial.py raw.mp4 out.mp4 -> 1920x1080 tutorial from a silent screen recording.

Each section is either a stickman cutaway ("cut", drawn by render.py) or a screen section ("screen": chosen source spans,
sped up/down to fit the narration, cropped to hide browser chrome and sidebars). Narration is local Piper TTS; every
sentence is synthesised alone so captions and scenes follow the voice exactly. Cut/hide decisions live in SECTIONS.
"""
import json, os, subprocess, sys, tempfile, wave
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import render as R, make_short as MS

FONT = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"
CROPS = {"claude": (225, 90, 1055, 630), "full": (0, 90, 1280, 630), "hook": (0, 0, 1080, 720)}  # x, y, w, h in the 1280x720 source
BEAT = dict(scene="beat", side="right", py=480)

SECTIONS = [
 dict(id="intro", kind="screen", src="hook", crop="hook", sh=780, oy=100, badge="FREE METHOD", bsize=96, parts=[(0.5, 3.5), (9, 12), (22, 25), (30, 33)],
   text="Want to make stickman videos like this, for free? Here's the exact workflow, from idea to finished clips."),
 dict(id="s1", kind="screen", crop="claude", badge="STEP 1  PICK A MODEL", parts=[(58, 74)],
   text="Step one. Give Claude a model: a video that already works in your niche. It studies the structure and the pacing. You're learning the pattern, never copying the words."),
 dict(id="s2", kind="screen", crop="claude", badge="STEP 2  NICHE AND TITLES", parts=[(85, 100), (113, 125)],
   text="Step two. Claude suggests the niche, the audience and a list of title ideas that follow the same formula. Pick one you can make your own."),
 dict(id="s3", kind="screen", crop="claude", badge="STEP 3  SCRIPT AND BEATS", parts=[(130, 150), (246, 270)],
   text="Step three. Choose the length, and Claude writes a short script. Then it splits the script into beats, each with an image prompt, a camera angle, lighting and mood, so every scene keeps the same hand-drawn style."),
 dict(id="s4", kind="screen", crop="full", badge="STEP 4  GENERATE IMAGES", parts=[(176, 196), (200, 212), (295, 300), (309, 313)],
   text="Step four. Paste the image prompts into Google Flow and generate. In a minute or two you have a full set of consistent stickman scenes."),
 dict(id="s5a", kind="screen", crop="claude", badge="STEP 5  ANIMATE", parts=[(322, 330)],
   text="Step five. Ask Claude for a short video prompt for every beat."),
 dict(id="s5b", kind="screen", crop="full", badge="STEP 5  ANIMATE", parts=[(336, 356), (452, 470), (480, 500)],
   text="Pick a video model in Flow and animate each image into a clip. This takes a while, so let it run, and come back when the clips are ready."),
 dict(id="s6a", kind="screen", crop="full", badge="STEP 6  VOICEOVER", parts=[(545, 560), (570, 578)],
   text="Step six. Turn the script into a voiceover."),
 dict(id="s6b", kind="screen", crop="claude", badge="STEP 6  VOICEOVER", parts=[(606, 628)],
   text="Open text to speech in Google AI Studio, paste the script, choose a voice, and generate the audio."),
 dict(id="outro", kind="cut", scenes=[
   dict(BEAT, headline="LAST STEP", pose="think", prop="clock", text="Last step: put the clips and the voice together in your editor, and add captions."),
   dict(BEAT, headline="MAKE IT YOURS", pose="happy", prop="heart", text="Make every video different, so it stays yours. Subscribe for more.")]),
]

def dur(path):
    with wave.open(path) as w: return w.getnframes() / w.getframerate()

def build_cut(sec, raw, tmp):
    spec = {"scenes": sec["scenes"]}
    wav, starts = MS.synth(spec, tmp)
    json.dump(spec, open(f"{tmp}/spec.json", "w"))
    out = f"{tmp}/{sec['id']}.mp4"
    env = dict(os.environ, YT_W="1920", YT_H="1080")
    subprocess.check_call([sys.executable, os.path.join(HERE, "render.py"), f"{tmp}/spec.json", wav, out, starts], env=env)
    return out

def build_screen(sec, raw, tmp):
    spec = {"scenes": [{"scene": "beat", "text": sec["text"]}]}
    wav, starts = MS.synth(spec, tmp)
    T = dur(wav)
    tl = R.plan(spec, T, json.load(open(starts))[1:])
    caps = tl[0][3]
    L = sum(b - a for a, b in sec["parts"]); s = max(0.7, L / T)
    cx, cy, cw, ch = CROPS[sec["crop"]]
    sh = sec.get("sh", 740); sw = int(round(sh * cw / ch / 2) * 2); ox = (1920 - sw) // 2; oy = sec.get("oy", 110)
    f = []
    for i, (a, b) in enumerate(sec["parts"]):
        f.append(f"[0:v]trim=start={a}:end={b},setpts=PTS-STARTPTS,fps=30[p{i}]")
    n = len(sec["parts"])
    f.append("".join(f"[p{i}]" for i in range(n)) + f"concat=n={n}:v=1:a=0[cat]")
    f.append(f"[cat]setpts=PTS/{s:.4f},crop={cw}:{ch}:{cx}:{cy},scale={sw}:{sh},tpad=stop_mode=clone:stop_duration=3[scr]")
    f.append(f"[1:v][scr]overlay=x={ox}:y={oy}[bg]")
    open(f"{tmp}/badge.txt", "w").write(sec["badge"])
    cur = "bg"
    f.append(f"[{cur}]drawtext=fontfile={FONT}:textfile={tmp}/badge.txt:expansion=none:fontsize={sec.get('bsize', 54)}:fontcolor=0x38bdf8:x=60:y=12[b0]"); cur = "b0"
    for i, (c0, c1, text) in enumerate(caps):
        open(f"{tmp}/cap{i}.txt", "w").write(text.upper())
        nxt = f"c{i}"
        f.append(f"[{cur}]drawtext=fontfile={FONT}:textfile={tmp}/cap{i}.txt:expansion=none:fontsize=72:fontcolor=white:borderw=8:bordercolor=black"
                 f":x=(w-text_w)/2:y=930:enable='between(t,{c0:.3f},{c1 if i < len(caps) - 1 else T + 5:.3f})'[{nxt}]"); cur = nxt
    out = f"{tmp}/{sec['id']}.mp4"
    src = os.environ.get("HOOK_VIDEO") if sec.get("src") == "hook" else raw
    subprocess.check_call(["ffmpeg", "-loglevel", "error", "-y", "-i", src, "-f", "lavfi", "-i", f"color=c=0x0f172a:s=1920x1080:r=30:d={T + 3:.3f}", "-i", wav,
        "-filter_complex", ";".join(f), "-map", f"[{cur}]", "-map", "2:a", "-af", "apad", "-t", f"{T:.3f}", "-r", "30",
        "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2", out])
    return out

def main():
    raw, final = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
    only = sys.argv[3].split(",") if len(sys.argv) > 3 else None
    parts = []
    with tempfile.TemporaryDirectory() as tmp:
        for sec in SECTIONS:
            if only and sec["id"] not in only: continue
            d = f"{tmp}/{sec['id']}"; os.makedirs(d)
            p = (build_cut if sec["kind"] == "cut" else build_screen)(sec, raw, d)
            print("built", sec["id"], flush=True); parts.append(p)
        open(f"{tmp}/list.txt", "w").write("".join(f"file '{p}'\n" for p in parts))
        subprocess.check_call(["ffmpeg", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", f"{tmp}/list.txt", "-c", "copy", "-movflags", "+faststart", final])
    print("done", final)

if __name__ == "__main__":
    main()
