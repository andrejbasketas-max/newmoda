#!/usr/bin/env python3
"""make_short.py spec.json  -> youtube/out/<id>.mp4, <id>-thumb-16x9.png, <id>-upload.md

Spec: {"id","title","description","tags","thumb":{"words":[..],"prop":"phone","pose":"point","slash":true},"scenes":[{scene params, "text": narration}]}
Voice is local Piper TTS (free). Each segment (split at . ? ! ,) is synthesised alone and joined with fixed pauses,
so caption/scene timing is exact instead of estimated.
"""
import json, os, subprocess, sys, tempfile, wave
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, "..", "out")
sys.path.insert(0, HERE)
import render as R

def synth(spec, tmp):
    segs = R.segments(spec); texts = [t for _, t in segs]
    json.dump(texts, open(f"{tmp}/segs.json", "w"))
    py = os.path.expanduser("~/.cache/yt-tts/venv/bin/python")
    subprocess.check_call([py, os.path.join(HERE, "tts.py"), f"{tmp}/segs.json", tmp])
    pcm, starts, rate = b"", [], None
    for i, t in enumerate(texts):
        with wave.open(f"{tmp}/seg_{i}.wav") as w:
            rate = w.getframerate(); data = w.readframes(w.getnframes()); width, ch = w.getsampwidth(), w.getnchannels()
        starts.append(len(pcm) / (rate * width * ch))
        pause = 0.55 if t[-1] in ".?!" else 0.22
        pcm += data + b"\x00" * int(rate * pause) * width * ch
    wav = f"{tmp}/voice.wav"
    with wave.open(wav, "wb") as w:
        w.setnchannels(ch); w.setsampwidth(width); w.setframerate(rate); w.writeframes(pcm)
    json.dump(starts, open(f"{tmp}/starts.json", "w"))
    return wav, f"{tmp}/starts.json"

def thumb(spec, path):
    import thumb as T
    T.make_generic(spec["thumb"], 1280, 720, path)

def main():
    spec = json.load(open(sys.argv[1])); sid = spec["id"]; os.makedirs(OUT, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        wav, starts = synth(spec, tmp)
        json.dump(spec, open(f"{tmp}/spec.json", "w"))
        subprocess.check_call([sys.executable, os.path.join(HERE, "render.py"), f"{tmp}/spec.json", wav, f"{OUT}/{sid}.mp4", starts])
    thumb(spec, f"{OUT}/{sid}-thumb-16x9.png")
    open(f"{OUT}/{sid}-upload.md", "w").write(
        f"# {sid}\n\n**Title:** {spec['title']}\n\n**Description:**\n```\n{spec['description']}\n```\n\n**Tags:** {', '.join(spec.get('tags', []))}\n")
    print("made", sid)

if __name__ == "__main__":
    main()
