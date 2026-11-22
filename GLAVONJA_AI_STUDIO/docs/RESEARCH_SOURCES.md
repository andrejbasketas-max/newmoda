# Research sources (VIRAL RESEARCHER)

| Source | Key? | Cost | What it gives | Measured? |
|---|---|---|---|---|
| Wikipedia most-read (wikimedia.org REST) | no | free | yesterday's most-read articles + views | yes |
| Google Trends daily RSS (trends.google.com/trending/rss) | no | free | trending searches + approx. traffic | yes (approximate) |
| Reddit top JSON (r/todayilearned, AskReddit, nosleep, history) | no | free (rate-limited) | weekly top posts, score, comments | yes |
| YouTube channel RSS (`/feeds/videos.xml?channel_id=UC...`) | no | free | latest 15 videos of a competitor + view counts | yes |
| YouTube Data API v3 | free key | 10,000 units/day free; search = 100 units | views, likes, comments, subscribers, age, views/day, views/subscriber | yes |

**Getting a YouTube API key (free):** https://console.cloud.google.com → new project → *APIs & Services →
Library → YouTube Data API v3 → Enable* → *Credentials → Create API key*. Paste it into Settings
(`research.youtube_api_key`). One `/glavonja-ideas` uses ~306 units (3 searches + details).

All responses are cached (12 h by default), so repeated clicks cost nothing. Numbers shown in ideas come
**only** from these sources; viral potential and competition are always labelled *estimate*.
