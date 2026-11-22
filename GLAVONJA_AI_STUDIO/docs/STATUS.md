# Build status – what is tested and what is not

Development environment: Linux cloud container (Python 3.13, FFmpeg 6.1). **Not your Windows PC.**
YouTube, Google APIs and HuggingFace were blocked there.

## Tested here (automated tests in `tests/`, all passing)
- Project state, SQLite, resume after every stage, blockers/approvals (pipeline test in an isolated copy).
- Gate behaviour: no Gemini key → production stops and asks; Flow → estimate + approval → requests file →
  clip import; an off-style clip is **rejected** and re-requested; a matching clip passes; local fallbacks
  only after explicit approval; export blocked (draft) when voice/animation/style rules are not met.
- Procedural renderer (19 poses, 12 expressions, 22 backgrounds, 57 props, camera, transitions, effects).
- Local voice fallback espeak-ng (Serbian + English); music + SFX synthesis; ducked mix; loudness normalisation.
- Editor: concat, ASS/SRT subtitles burned in sync, 1920×1080 H.264 + AAC, faststart.
- QC: playable, resolution, 16:9, audio present/not silent, A/V duration sync, subtitle range, missing
  scenes, corrupt images, black frames, consistency check, report.
- Thumbnails (3 × 1280×720 + small previews), SEO metadata (offline templates), RSS/Trends/Wikipedia parsers.
- Dashboard: all pages/API endpoints, command box, file serving with path-traversal protection.
- Test video: `docs/test_video/` (Serbian, ~35 s, 1080p). It uses the **local fallbacks** (espeak voice,
  procedural animation) because Gemini/Flow were unreachable. Its report correctly says *draft – not exportable*.

## Written but NOT testable here (first run happens on your PC)
- `install.bat`, `start.bat`, `update.bat` (cmd.exe not available; ASCII + CRLF, standard commands only).
- Gemini TTS calls (Google blocked) – follows the documented REST API; first test: `glavonja.py voices --audition`.
- Live research fetches (network blocked) – parsers are tested with fixtures.
- Piper voices download (HuggingFace blocked) and Ollama LLM path (not installed; tested logic with offline mode).
- Windows SAPI voices (Windows only).

## Not possible / not done
- Analysing the real channel: no access. Provide frames → `style learn` → compare → approve.
- Automating the Google Flow website: no public API. The bridge + upload is the safe solution.
- Local AI image/video generation (ComfyUI/SD): not used. RX 470 4 GB + no CUDA makes it slow/unreliable,
  and it would not reproduce your Flow look. Flow is the animation source; procedural art is the fallback.
