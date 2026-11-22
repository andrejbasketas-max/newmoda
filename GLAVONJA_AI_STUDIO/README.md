# GLAVONJA AI STUDIO

Local production studio for the **GLAVONJA** stickman YouTube channel.
You choose a topic, the studio produces the whole video, and you approve it. It runs on your Windows PC, and
**Claude Code is not needed for everyday use**.

## Start (Windows 10/11)

1. Double-click **`install.bat`** (once). It installs Python packages into `.venv`, downloads FFmpeg into
   `tools\`, can download free Piper voices, inspects your hardware (`docs\hardware_report.json`) and runs a self-test.
   No admin rights are needed. If Python is missing, it tells you exactly what to install (python.org, free).
2. Double-click **`start.bat`**. The dashboard opens at http://127.0.0.1:8765
3. First-time setup in the dashboard:
   - ⚙ **Settings → Gemini API key** (free key: https://aistudio.google.com/apikey). This is required, because Gemini TTS is the narration voice.
   - 🎙 **Voice → Audition → 🔒 Lock** the voice that fits the channel. It is used in every video.
   - 🎨 **Style →** upload screenshots / your own videos of the channel → **Measure** → **Test scene** → **Approve**.
4. Type **`/glavonja-ideas`** → pick an idea → the studio produces it.
5. To update later, double-click **`update.bat`**. It backs up your settings, style and database and never touches projects or videos.

## AUTOPILOT – every day, no Claude usage

`install.bat` offers to turn it on (or double-click `autopilot_install.bat`; remove with `autopilot_uninstall.bat`).
Windows Task Scheduler then runs the studio every 30 minutes (and opens the dashboard when you log in). Claude is not involved, so it keeps running for months or years.

1. **Every morning:** 10 fresh ideas + a Windows notification. **You choose the topic** in the dashboard.
2. The studio writes the script, makes the **Gemini** voice (after your approval) and writes `FLOW_REQUESTS.md`.
3. Generate the clips in **Google Flow** in scene order and just drag the downloaded files into **`FLOW_INBOX\`**
   (any file names). The autopilot assigns them to the scenes, style-checks them (off-style clips are re-requested)
   and finishes the video by itself.
4. You get a notification "video je gotov" → review → approve. Nothing is ever uploaded automatically.

## Daily workflow

| Step | Who | What happens |
|---|---|---|
| `/glavonja-ideas` | studio | VIRAL RESEARCHER collects real signals (Wikipedia, Google Trends, Reddit, YouTube RSS, optional YouTube API) → 10 ideas; measured numbers vs estimates clearly marked |
| choose idea | **you** | nothing is produced before you choose |
| research + script | studio | facts from Wikipedia → script (local Ollama LLM, or an offline draft you can edit in the Script tab) |
| storyboard | studio | shots of up to 8 s, one Google Flow clip each, with a Flow prompt per shot |
| voice | studio | **Gemini TTS** (locked voice) → asks you to approve the estimated usage first |
| illustrations | studio | storyboard preview frames + contact sheet |
| animation | studio + **you** | studio writes `flow/FLOW_REQUESTS.md` (+ reference images) → you generate the clips in **Google Flow** and upload them per scene → every clip is style-checked; failures are rejected and re-requested |
| edit | studio | FFmpeg: clips + narration + ducked music + SFX + synced subtitles → 1920×1080 H.264 MP4 |
| thumbnails / SEO | studio | 3 thumbnails (1280×720), 5 titles, description with chapters, tags, hashtags, pinned comment |
| QC | studio | file, playback, resolution, 16:9, audio, A/V sync, subtitle sync, missing scenes, corrupt images, black frames, **visual consistency** → production report |
| approve | **you** | Video tab → ✔ Approve. The studio **never uploads** anything. |

If the PC shuts down, open the studio and press **Continue** (`/glavonja-continue`). Finished stages and assets are never redone.

## Commands (dashboard command box or `.venv\Scripts\python glavonja.py <cmd>`)

| Command | CLI |
|---|---|
| `/glavonja-ideas` | `glavonja.py ideas [--lang sr/en] [--refresh]` |
| `/glavonja-make 12` or `/glavonja-make my own topic` | `glavonja.py make 12 [--duration 480]` |
| `/glavonja-status` | `glavonja.py status` |
| `/glavonja-continue` | `glavonja.py continue` |
| `/glavonja-style` | `glavonja.py style show / learn / test / approve` |
| `/glavonja-settings` | `glavonja.py settings [key value]` |
| `/glavonja-history` | `glavonja.py history` |
| – | `glavonja.py approve <key>` · `voices --audition / --lock NAME` · `redo <stage>` · `selftest` |

## Costs (zero-budget rules)

| Part | Tool | Cost |
|---|---|---|
| Rendering, editing, subtitles, music, SFX, QC | Python + Pillow + NumPy + FFmpeg | free, local |
| Research | Wikipedia API, Google Trends RSS, Reddit JSON, YouTube RSS | free, no key |
| Research (optional) | YouTube Data API v3 | free key, 10,000 units/day (a search costs 100) |
| Scripts | Ollama + qwen2.5 (optional) | free, local (CPU; slow on an i5 but works) |
| **Voice (mandatory)** | **Gemini TTS** | free tier with a small daily limit; beyond that it's paid. The studio shows an estimate and asks every time |
| **Animation (mandatory)** | **Google Flow** | uses your Flow credits (from your Google plan). The studio shows an estimate before every batch |
| Fallback voice | Piper (MIT) / espeak-ng (GPL-3) | free, local; only after your approval |
| Fallback animation | procedural vector stickman | free, local; only after your approval |
| Claude | not used for production | optional `llm.allow_claude_cli=true` lets Claude Code write scripts (uses your Claude plan) |

The numbers in `config/google_pricing.json` are **unverified estimates**. Check Google's pricing and your Flow credit counter.

## Important limitations (honest)

- **Google Flow has no public API.** The studio does not automate the Flow website (it would break and could
  violate Google's terms). It prepares exact prompts + reference images and imports your clips automatically. Generating
  the clips in Flow is the one manual step: about 1 clip per 8 s of video, so roughly 60 clips for an 8-minute video.
  The only fully automatic alternative would be Veo through the paid Gemini API. It isn't enabled because of the zero budget.
- The channel was **not analysed during development**: YouTube was blocked in the build environment. Until you add reference
  frames, every video is exported only as a **draft**.
- Gemini TTS and Flow were not reachable in the build environment. Their code paths follow Google's documented API
  but are first tested on your PC (`glavonja.py voices --audition`).
- Without Ollama, scripts are template drafts. Edit them in the Script tab, or install Ollama (free) for real scripts.
- Your GPU (RX 470) has no CUDA. Nothing in the studio needs a GPU.

## Folders

`config/` settings, style, pricing, idea bank · `studio/` source code (agents in `studio/agents/`) · `agents/` agent configs ·
`.claude/skills/` + `skills/` Claude Code skills · `prompts/` reusable LLM prompts · `assets/` characters, backgrounds, props, music,
sfx, fonts · `references/` your channel frames · `projects/<id>/` one folder per video (research, script, storyboard, voice, scenes,
animations, music, subtitles, thumbnails, final, flow, project_state.json) · `outputs/` exported videos · `database/` SQLite
(ideas, projects, cache, licences) + `asset_license.json` · `logs/` · `docs/` · `tests/`

Tests: `.venv\Scripts\python -m pytest tests` (the pipeline test runs in an isolated temporary copy).
