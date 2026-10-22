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
CROPS = {"claude": (225, 125, 1055, 595), "claudeG": (225, 90, 1055, 630), "full": (0, 90, 1280, 630), "hook": (0, 0, 1080, 720)}
CLS = None  # per-frame class of the raw recording: C claude chat, F flow (dark), G google pages; anything else is never used

def load_cls():
    global CLS
    d = json.load(open(os.environ["CLS_JSON"])); CLS = (d["pts"], d["cls"])

def safe_parts(parts, allow):
    """Intersect the wanted spans with frames of an allowed class (no private tabs/popups); drop slivers under 1 s."""
    pts, cls = CLS; runs, s0 = [], None
    for i, c in enumerate(cls):
        ok = c in allow
        if ok and s0 is None: s0 = pts[i]
        if (not ok or i == len(cls) - 1) and s0 is not None:
            runs.append((s0, pts[i - 1] if not ok else pts[i])); s0 = None
    out = []
    for a, b in parts:
        for ra, rb in runs:
            lo, hi = max(a, ra), min(b, rb)
            if hi - lo >= 1.0: out.append((round(lo, 2), round(hi, 2)))
    return out  # x, y, w, h in the 1280x720 source
BEAT = dict(scene="beat", side="right", py=480)

SECTIONS = [
 dict(id="intro", kind="screen", src="hook", crop="hook", sh=780, oy=100, badge="FREE METHOD", bsize=96, allow="*",
   parts=[(0.5, 6), (8, 13), (16, 21), (24, 29), (31, 35)],
   text="What you're watching was made without filming a single shot. Every scene is a generated stickman clip, and the whole workflow runs on a chatbot, Google Flow and a text to speech voice. In this video I'll walk through every step, from the first prompt to the finished clips, so you can follow along and build your own. You'll need three things: a chatbot, Google Flow, and a text to speech tool. I'll show exactly where to click. Let's start."),
 dict(id="s1", kind="screen", crop="claude", allow="C", badge="STEP 1  SET UP THE CHAT", parts=[(55, 82)],
   text="Step one: set up your chatbot. I'm using Claude, but any capable chatbot can do the job. Create a new chat and give it the workflow instructions. They turn the chat into a step by step assistant that moves forward every time you type next. First it asks for a model: the source material it should learn from, such as transcripts and visual references from a channel in your niche, attached as a PDF. Treat that as research. You're studying the style and the pacing so you can create something original. A tip: keep one chat for one project, so the instructions and the style stay in its memory."),
 dict(id="s2", kind="screen", crop="claude", allow="C", badge="STEP 2  ANALYZE THE MODEL", parts=[(82, 110)],
   text="Step two: let it analyze the model. Claude reads the PDF, works out the writing style and the average length, and confirms that everything is absorbed. When you type next, it suggests channel names and descriptions, plus prompts for a logo and a banner. After another next, you get a niche analysis: the target audience, the hook style, how a script flows, the tone, the curiosity gaps and the emotional triggers. Read this part carefully, because it's the blueprint for every video you make. If a name or a description doesn't fit you, ask for more options before you continue."),
 dict(id="s3", kind="screen", crop="claude", allow="C", badge="STEP 3  PICK A TOPIC", parts=[(110, 128)],
   text="Step three: pick a topic. Claude drafts a batch of ten title ideas, and each one comes with the formula behind it, for example why do humans do a common thing. Choose the number you like, or ask for something different. I picked number three, why did humans start wearing clothes, and Claude locked it in. If none of the ten ideas feel right, describe your own topic, and the same formula gets applied to it."),
 dict(id="s4", kind="screen", crop="claude", allow="C", badge="STEP 4  WRITE THE SCRIPT", parts=[(128, 150)],
   text="Step four: the script. Claude asks how long the video should be, with options from sixty seconds up to ten minutes. I typed thirty seconds for this demo. It works out the word count from the speaking pace, about two and a half words per second, and writes a seventy four word script. For a longer video you pick a longer duration and get a longer script. Read it out loud, fix anything that doesn't sound right, and only then move on. Don't be afraid to ask for a rewrite with a different tone or a stronger first line."),
 dict(id="s5", kind="screen", crop="claude", allow="C", badge="STEP 5  BEATS AND IMAGE PROMPTS", parts=[(166, 173), (242, 271), (277, 295), (300, 309)],
   text="Step five: beats and image prompts. Type next and Claude splits the script into beats. Each beat has a time range, the line that is spoken, and an image prompt. Notice that every prompt starts with the same style description: hand drawn stick figure, thick black outlines, flat pastel colors. That repeated description is what keeps all the scenes looking like one video. Each beat also has a camera angle, lighting, mood and action, so you know exactly what the scene should show. If you want shorter or longer scenes, just ask Claude for them before you copy the prompts."),
 dict(id="s6", kind="screen", crop="full", allow="FG", badge="STEP 6  GENERATE THE IMAGES", parts=[(172, 222), (237, 242), (288, 292), (295, 300), (309, 313)],
   text="Step six: generate the images. Open Google Flow and start a project. Pick the image model, then copy a prompt from Claude and paste it into the box. While an image is generating you see a blurry placeholder with a percentage. When it finishes, the scene appears in your gallery. Repeat this for every beat, and you end up with a full set of consistent scenes. Don't rush this part. If an image has a distorted hand or the wrong mood, regenerate just that beat instead of starting over. Flow works with credits, so keep an eye on your balance and start with the scenes that matter most."),
 dict(id="s7", kind="screen", crop="claude", allow="C", badge="STEP 7  VIDEO PROMPTS", parts=[(313, 331), (379.9, 383), (389.7, 393), (396.4, 400.4), (404.7, 408.4), (412.9, 416.8), (420.9, 424.6), (430.3, 433.8), (439.6, 443.1)],
   text="Step seven: video prompts. Now ask Claude for a video prompt for each beat. Each one names the anchor image to animate, describes the motion and the camera movement, and gives the duration, in this case three seconds. Because the prompt points back to the image, the clip stays faithful to the scene you already approved. Keep every video prompt short and concrete: one clear movement and one camera move work better than many at once."),
 dict(id="s8", kind="screen", crop="full", allow="FG", badge="STEP 8  ANIMATE THE CLIPS", parts=[(331, 366), (376, 380), (383, 390), (392.7, 396.3), (400.4, 404.6), (408.5, 412.8), (416.8, 421), (450, 536)],
   text="Step eight: animate. Go back to Flow, attach the image you want to animate, and paste its video prompt. Pick a video model from the list. The options trade speed against quality, so start with a fast one and only switch to the best quality for scenes that really matter. Each clip is a few seconds long and takes a while to render, so queue several and let them run. While you wait, you can already start on the voiceover. When a clip finishes, open it to preview, check that the movement matches the prompt, and download the ones you like. Don't expect every clip to be perfect. Regenerate the weak ones, and keep the best take for each beat."),
 dict(id="s9a", kind="screen", crop="full", allow="FG", badge="STEP 9  THE VOICEOVER", parts=[(544.4, 600)],
   text="Step nine: the voiceover. You need a text to speech tool. I searched for Gemini speech generation, which led to Google AI Studio."),
 dict(id="s9b", kind="screen", crop="claudeG", allow="FG", badge="STEP 9  THE VOICEOVER", parts=[(600, 631)],
   text="In its playground you paste your script, choose a voice and a speaking style, and generate the audio. Listen to it before you move on, and if a line sounds off, edit the text and generate it again. Splitting a long script into smaller chunks tends to give cleaner audio. Pick one voice and keep it for the whole series, so your channel sounds consistent."),
 dict(id="s10", kind="cut", scenes=[
   dict(scene="bullets", headline="STEP 10  PUT IT TOGETHER", items=["Voiceover on the timeline", "Clips in beat order", "Trim, captions, music"], figure=False,
        text="Step ten: put it together. Drop the voiceover on the timeline of any editor, then place the clips in order so every scene change lands on a beat. Trim the extra seconds, add captions, and finish with background music you have the right to use. If a clip is a bit longer than its beat, trim it from the end, and if it's shorter, slow it down slightly or hold the last frame. Finally, check the audio levels so the music never competes with the voice.")]),
 dict(id="s11", kind="cut", scenes=[
   dict(scene="bullets", headline="BEFORE YOU PUBLISH", items=["Use the model for the pattern", "Write your own topics and scripts", "Label AI voice and visuals"], figure=False,
        text="Before you publish, make it yours. Use the model only for the pattern, write your own topics and scripts, and label AI voices and visuals in YouTube Studio. YouTube's rules target mass produced, near identical content, so variety is your protection. Add your own angle to every video: a new source, a surprising fact, a personal take. The more it feels like you, the better.")]),
 dict(id="outro", kind="cut", scenes=[
   dict(BEAT, headline="YOUR TURN", pose="happy", prop="heart", text="That's the whole workflow. Subscribe, and try it with your own idea.")]),
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
    if sec.get("allow", "*") != "*": sec = dict(sec, parts=safe_parts(sec["parts"], sec["allow"]))
    assert sec["parts"], f"no safe footage for {sec['id']}"
    L = sum(b - a for a, b in sec["parts"]); s = max(0.6, L / T)
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

import contextlib

@contextlib.contextmanager
def workdir():
    d = os.environ.get("WORKDIR")  # persistent folder: finished sections are reused after an interruption
    if d:
        os.makedirs(d, exist_ok=True); yield d
    else:
        with tempfile.TemporaryDirectory() as t: yield t

def main():
    raw, final = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
    only = sys.argv[3].split(",") if len(sys.argv) > 3 else None
    parts = []; chapters = []; load_cls()
    with workdir() as tmp:
        for sec in SECTIONS:
            if only and sec["id"] not in only: continue
            d = f"{tmp}/{sec['id']}"; os.makedirs(d, exist_ok=True)
            p = f"{d}/{sec['id']}.mp4"
            if not os.path.exists(p): p = (build_cut if sec["kind"] == "cut" else build_screen)(sec, raw, d)
            d_ = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p]))
            chapters.append((sec["id"], d_)); print("built", sec["id"], round(d_, 1), "s", flush=True); parts.append(p)
        open(f"{tmp}/list.txt", "w").write("".join(f"file '{p}'\n" for p in parts))
        subprocess.check_call(["ffmpeg", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", f"{tmp}/list.txt", "-c", "copy", "-movflags", "+faststart", final])
    t_ = 0.0; out_ = []
    for sid, d_ in chapters: out_.append({"id": sid, "start": round(t_, 1)}); t_ += d_
    json.dump(out_, open(final + ".chapters.json", "w"))
    print("done", final, round(t_), "s")

if __name__ == "__main__":
    main()
