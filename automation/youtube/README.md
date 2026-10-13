# Newmoda YouTube Shorts autopilot

Once a day a GitHub Action makes and posts a ~45-second vertical Short about fragrance, tied to a Newmoda scent:

1. **Script.** Claude writes the hook, narration, title, description and tags from the brand facts in `brand.py`. It avoids topics from recent videos listed in `history.json`.
2. **Voice.** `edge-tts` reads the narration in a free neural voice (`en-GB-SoniaNeural`) and reports when each word is spoken.
3. **Video.** Pillow draws a background in the scent's colours with a bottle. ffmpeg adds a slow zoom, the hook as a title card and word-timed captions.
4. **Upload.** The YouTube Data API posts it. It's labelled as AI-generated (`containsSyntheticMedia`) and is not marked as made for kids.

## One-time setup

### 1. Create the channel
Sign in to YouTube with the Google account that will own the channel and create a channel (e.g. "Newmoda"). Verify it with your phone at <https://www.youtube.com/verify>, otherwise uploads are capped at 15 minutes and custom thumbnails are blocked.

### 2. Google Cloud OAuth client
1. At <https://console.cloud.google.com> create a project and enable **YouTube Data API v3**.
2. Go to **Google Auth Platform → Audience** and choose External. Add the channel's Google account as a test user, then click **Publish app**. If you leave it in Testing mode, the refresh token expires after 7 days.
3. Go to **Clients → Create client → Desktop app** and download the JSON file.
4. On your own computer:
   ```bash
   pip install google-auth-oauthlib google-api-python-client
   python get_refresh_token.py ~/Downloads/client_secret_XXXX.json
   ```
   Sign in as the channel account. The script prints the three values for the next step.

### 3. GitHub secrets
In the repo, go to **Settings → Secrets and variables → Actions** and add:

| Secret | Value |
|---|---|
| `ANTHROPIC_API_KEY` | from <https://console.anthropic.com> |
| `YT_CLIENT_ID` | printed by `get_refresh_token.py` |
| `YT_CLIENT_SECRET` | printed by `get_refresh_token.py` |
| `YT_REFRESH_TOKEN` | printed by `get_refresh_token.py` |

Optional: add a **variable** (not a secret) called `YT_PRIVACY` set to `private` or `unlisted` if you want to review videos before they go public.

### 4. Get the API project audited (important)
YouTube locks videos uploaded through a new, unaudited API project as **private**, even if you request public. Fill in the [YouTube API audit form](https://support.google.com/youtube/contact/yt_api_form) for your project. Until it's approved, uploads land as private and you can publish them by hand in YouTube Studio.

### 5. Test it
On GitHub, open **Actions → Daily YouTube Short → Run workflow**. The rendered video is also attached to each run as an artifact.

## Running locally

```bash
cd automation/youtube
pip install -r requirements.txt          # also needs ffmpeg and DejaVu fonts
export ANTHROPIC_API_KEY=...
python run.py --no-upload                # renders out/<date>/short.mp4 without posting
```

## Tuning
- **Schedule:** the `cron` line in `.github/workflows/youtube-short.yml` (UTC).
- **Voice:** `VOICE` in `make_video.py` (`edge-tts --list-voices` shows the options).
- **Topics and tone:** `SYSTEM` in `write_script.py`. **Brand facts:** `brand.py`.
- **Model:** set the `CLAUDE_MODEL` env var (default `claude-opus-5-5`). Each video costs a few cents in API calls.

## Cost and policy notes
- YouTube's free API quota is 10,000 units/day and an upload costs about 1,600, so you can post up to ~6 per day.
- YouTube doesn't monetize "inauthentic" or mass-produced repetitive content. Keep topics varied (the history check helps), and consider recording your own voice or adding real product footage once the channel grows.
- `edge-tts` uses Microsoft Edge's online read-aloud service. It's free and needs no key, but it's unofficial and could change. If it breaks, swap `_speak` in `make_video.py` for a paid text-to-speech API.
