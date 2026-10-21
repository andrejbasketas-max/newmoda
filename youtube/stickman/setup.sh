#!/usr/bin/env bash
# One-time setup for a fresh container: local TTS (Piper) in ~/.cache/yt-tts. Idempotent.
set -euo pipefail
D="$HOME/.cache/yt-tts"; mkdir -p "$D/voices"
[ -x "$D/venv/bin/python" ] || { python3 -m venv "$D/venv"; "$D/venv/bin/pip" install -q piper-tts; }
V="en_US-ryan-high"
for f in "$V.onnx" "$V.onnx.json"; do
  [ -s "$D/voices/$f" ] || curl -sL --fail -o "$D/voices/$f" "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/ryan/high/$f"
done
command -v ffmpeg >/dev/null || { echo "ffmpeg missing" >&2; exit 1; }
python3 -c "import PIL, numpy" 2>/dev/null || pip install -q pillow numpy
echo "ready: $D"
