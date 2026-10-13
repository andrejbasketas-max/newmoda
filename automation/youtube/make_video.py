"""Turn a script into a 1080x1920 Short: AI voiceover, branded background, word-timed captions."""

import asyncio
import os
import subprocess
from pathlib import Path

import edge_tts
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from brand import PALETTES

W, H, FPS = 1080, 1920, 30
VOICE = "en-GB-SoniaNeural"
SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"


def _rgb(hex_color: str) -> tuple[int, int, int]:
    return tuple(int(hex_color[i:i + 2], 16) for i in (1, 3, 5))


async def _speak(text: str, mp3: Path) -> list[tuple[float, float, str]]:
    """Write the voiceover and return (start, end, word) timings in seconds."""
    words = []
    with mp3.open("wb") as f:
        async for chunk in edge_tts.Communicate(text, VOICE, rate="-4%", boundary="WordBoundary",
                                           proxy=os.environ.get("HTTPS_PROXY")).stream():
            if chunk["type"] == "audio":
                f.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                start = chunk["offset"] / 1e7
                words.append((start, start + chunk["duration"] / 1e7, chunk["text"]))
    return words


def _background(scent: str, path: Path) -> None:
    top, bottom, accent = (_rgb(c) for c in PALETTES.get(scent, PALETTES["house"]))
    img = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(img)
    for y in range(H):
        t = y / (H - 1)
        draw.line([(0, y), (W, y)], fill=tuple(round(a + (b - a) * t) for a, b in zip(top, bottom)))

    # Soft glow behind the bottle.
    glow = Image.new("L", (W, H), 0)
    ImageDraw.Draw(glow).ellipse((W / 2 - 420, 560, W / 2 + 420, 1400), fill=90)
    img.paste(Image.new("RGB", (W, H), accent), mask=glow.filter(ImageFilter.GaussianBlur(160)))

    # Bottle silhouette: glass body, liquid, neck and cap.
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    bx0, bx1, by0, by1 = W / 2 - 200, W / 2 + 200, 760, 1300
    d.rounded_rectangle((bx0, by0, bx1, by1), 56, fill=(*accent, 46), outline=(*accent, 150), width=4)
    d.rounded_rectangle((bx0 + 18, by0 + 210, bx1 - 18, by1 - 18), 42, fill=(*accent, 110))
    d.rectangle((W / 2 - 46, by0 - 70, W / 2 + 46, by0), fill=(*accent, 90))
    d.rounded_rectangle((W / 2 - 92, by0 - 210, W / 2 + 92, by0 - 70), 18, fill=(*accent, 220))
    d.line((bx0 + 60, by0 + 40, bx0 + 60, by1 - 60), fill=(255, 255, 255, 60), width=10)
    img.paste(layer, mask=layer)

    d = ImageDraw.Draw(img)
    mark = ImageFont.truetype(SERIF, 54)
    d.text((W / 2, 150), "N E W M O D A", font=mark, fill=accent, anchor="mm")
    small = ImageFont.truetype(SERIF, 34)
    label = "Maison de Parfum" if scent == "house" else scent
    d.text((W / 2, 1360), label, font=small, fill=accent, anchor="mm")
    img.save(path)


def _ass_time(s: float) -> str:
    cs = round(s * 100)
    return f"{cs // 360000}:{cs // 6000 % 60:02d}:{cs // 100 % 60:02d}.{cs % 100:02d}"


def _ass_text(s: str) -> str:
    return s.replace("\\", "").replace("{", "(").replace("}", ")")


def _captions(hook: str, words: list[tuple[float, float, str]], end: float, path: Path) -> None:
    """Captions in chunks of up to three words, plus the hook as a title for the first seconds."""
    chunks, cur = [], []
    for w in words:
        cur.append(w)
        if len(cur) == 3 or w[2][-1:] in ".,!?;:":
            chunks.append(cur)
            cur = []
    if cur:
        chunks.append(cur)

    lines = [f"Dialogue: 0,{_ass_time(0)},{_ass_time(min(3.0, end))},Hook,,0,0,0,,{_ass_text(hook)}"]
    for i, chunk in enumerate(chunks):
        start = chunk[0][0]
        stop = chunks[i + 1][0][0] if i + 1 < len(chunks) else end
        text = _ass_text(" ".join(w[2] for w in chunk))
        lines.append(f"Dialogue: 1,{_ass_time(start)},{_ass_time(stop)},Cap,,0,0,0,,{text}")

    path.write_text(f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Hook,DejaVu Serif,78,&H00FFFFFF,&H00FFFFFF,&H64000000,&H00000000,0,0,0,0,100,100,0,0,1,3,0,8,90,90,300,1
Style: Cap,DejaVu Sans,80,&H00FFFFFF,&H00FFFFFF,&H00101010,&H78000000,1,0,0,0,100,100,0,0,1,5,2,2,80,80,330,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
""" + "\n".join(lines) + "\n", encoding="utf-8")


def make_video(script: dict, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    mp3, bg, ass, mp4 = (out_dir / n for n in ("voice.mp3", "bg.png", "captions.ass", "short.mp4"))

    words = asyncio.run(_speak(script["narration"], mp3))
    if not words:
        raise RuntimeError("Text-to-speech returned no word timings")
    duration = min(words[-1][1] + 0.8, 59.0)
    frames = round(duration * FPS)

    _background(script["scent"], bg)
    _captions(script["hook"], words, duration, ass)

    zoom = (f"scale={W * 2}:{H * 2},zoompan=z='1+0.08*on/{frames}':x='iw/2-(iw/zoom/2)'"
            f":y='ih/2-(ih/zoom/2)':d=1:s={W}x{H}:fps={FPS},ass={ass.name},format=yuv420p")
    subprocess.run([
        "ffmpeg", "-y", "-loglevel", "error",
        "-loop", "1", "-framerate", str(FPS), "-i", bg.name,
        "-i", mp3.name,
        "-vf", zoom, "-af", "apad",
        "-t", f"{duration:.2f}",
        "-c:v", "libx264", "-preset", "medium", "-crf", "20",
        "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart",
        mp4.name,
    ], check=True, cwd=out_dir)
    return mp4
