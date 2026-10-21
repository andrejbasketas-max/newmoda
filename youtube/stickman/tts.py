#!/usr/bin/env python3
"""Runs in the Piper venv. tts.py segments.json outdir  -> outdir/seg_<i>.wav for each text in the JSON list."""
import json, os, sys, wave
from piper import PiperVoice
model = os.path.expanduser("~/.cache/yt-tts/voices/en_US-ryan-high.onnx")
voice = PiperVoice.load(model)
texts, out = json.load(open(sys.argv[1])), sys.argv[2]
os.makedirs(out, exist_ok=True)
for i, t in enumerate(texts):
    with wave.open(f"{out}/seg_{i}.wav", "wb") as w:
        voice.synthesize_wav(t, w)
