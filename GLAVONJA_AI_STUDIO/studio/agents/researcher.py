"""AGENT 1 - VIRAL RESEARCHER.

Collects REAL signals from free sources, then (optionally with a local LLM) turns them into
10 original GLAVONJA video ideas.  Numbers are only ever reported from measured sources;
everything else is explicitly labelled "estimate".

Free sources (no key needed):  Wikipedia most-read API, Google Trends daily RSS, Reddit top JSON,
YouTube channel RSS feeds (competitors, includes view counts).
Optional free key:            YouTube Data API v3 (10 000 units/day free quota).
"""
from __future__ import annotations

import datetime as dt
import json
import random
import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

from ..core import CONFIG_DIR, cache_get, cache_put, db_exec, db_query, get_logger, load_settings, now_iso, read_json, sha
from ..llm import LLMUnavailable, ask_json, load_prompt

UA = "GLAVONJA-AI-STUDIO/1.0 (local research tool)"


def http_get(url: str, timeout: int = 15) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def cached_fetch(kind: str, url: str, hours: float, parser):
    key = f"research:{kind}:{sha(url)}"
    hit = cache_get(key, hours)
    if hit is not None:
        return hit
    data = parser(http_get(url))
    cache_put(key, data, "research")
    return data


# --------------------------------------------------------------------------- parsers (unit tested)
def parse_wikipedia_top(raw: bytes, limit=40) -> list[dict]:
    j = json.loads(raw)
    arts = j["items"][0]["articles"]
    out = []
    for a in arts:
        t = a["article"]
        if t in ("Main_Page", "-") or ":" in t:
            continue
        out.append({"source": "wikipedia_most_read", "title": t.replace("_", " "), "views_yesterday": a["views"],
                    "measured": True})
        if len(out) >= limit:
            break
    return out


def parse_google_trends_rss(raw: bytes) -> list[dict]:
    root = ET.fromstring(raw)
    ns = {"ht": "https://trends.google.com/trending/rss"}
    out = []
    for it in root.iter("item"):
        title = (it.findtext("title") or "").strip()
        traffic = None
        for child in it:
            if child.tag.endswith("approx_traffic"):
                traffic = (child.text or "").strip()
        out.append({"source": "google_trends_daily", "title": title, "approx_traffic": traffic, "measured": True})
    return out


def parse_reddit(raw: bytes, sub: str) -> list[dict]:
    j = json.loads(raw)
    out = []
    for c in j.get("data", {}).get("children", []):
        d = c.get("data", {})
        if d.get("over_18"):
            continue
        out.append({"source": f"reddit_r/{sub}", "title": d.get("title", ""), "score": d.get("score"),
                    "comments": d.get("num_comments"), "measured": True})
    return out


def parse_youtube_rss(raw: bytes) -> list[dict]:
    ns = {"a": "http://www.w3.org/2005/Atom", "yt": "http://www.youtube.com/xml/schemas/2015",
          "media": "http://search.yahoo.com/mrss/"}
    root = ET.fromstring(raw)
    channel = root.findtext("a:title", default="", namespaces=ns)
    out = []
    for e in root.findall("a:entry", ns):
        vid = e.findtext("yt:videoId", default="", namespaces=ns)
        pub = e.findtext("a:published", default="", namespaces=ns)
        st = e.find("media:group/media:community/media:statistics", ns)
        views = int(st.get("views")) if st is not None and st.get("views", "").isdigit() else None
        age = None
        try:
            age = max(1, (dt.datetime.now(dt.timezone.utc) - dt.datetime.fromisoformat(pub.replace("Z", "+00:00"))).days)
        except Exception:
            pass
        out.append({"source": "youtube_rss", "channel": channel, "title": e.findtext("a:title", default="", namespaces=ns),
                    "video_id": vid, "url": f"https://www.youtube.com/watch?v={vid}", "views": views,
                    "published": pub, "age_days": age,
                    "views_per_day": round(views / age, 1) if views and age else None, "measured": views is not None})
    return out


# --------------------------------------------------------------------------- sources
def youtube_api_search(key: str, query: str, days: int = 60, region="US", max_results=15) -> list[dict]:
    """YouTube Data API: search (100 units) + videos (1) + channels (1)."""
    after = (dt.datetime.utcnow() - dt.timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%SZ")
    q = urllib.parse.urlencode({"part": "snippet", "q": query, "type": "video", "order": "viewCount",
                                "publishedAfter": after, "maxResults": max_results, "regionCode": region, "key": key})
    search = json.loads(http_get("https://www.googleapis.com/youtube/v3/search?" + q))
    ids = [i["id"]["videoId"] for i in search.get("items", [])]
    if not ids:
        return []
    v = json.loads(http_get("https://www.googleapis.com/youtube/v3/videos?" + urllib.parse.urlencode(
        {"part": "statistics,snippet,contentDetails", "id": ",".join(ids), "key": key})))
    chans = list({i["snippet"]["channelId"] for i in v.get("items", [])})
    c = json.loads(http_get("https://www.googleapis.com/youtube/v3/channels?" + urllib.parse.urlencode(
        {"part": "statistics", "id": ",".join(chans), "key": key})))
    subs = {i["id"]: int(i["statistics"].get("subscriberCount", 0) or 0) for i in c.get("items", [])}
    out = []
    for it in v.get("items", []):
        sn, stt = it["snippet"], it.get("statistics", {})
        views = int(stt.get("viewCount", 0))
        pub = sn["publishedAt"]
        age = max(1, (dt.datetime.now(dt.timezone.utc) - dt.datetime.fromisoformat(pub.replace("Z", "+00:00"))).days)
        sc = subs.get(sn["channelId"], 0)
        out.append({"source": "youtube_api", "title": sn["title"], "channel": sn["channelTitle"], "video_id": it["id"],
                    "url": f"https://www.youtube.com/watch?v={it['id']}", "views": views,
                    "likes": int(stt["likeCount"]) if "likeCount" in stt else None,
                    "comments": int(stt["commentCount"]) if "commentCount" in stt else None,
                    "subscribers": sc, "views_per_sub": round(views / sc, 2) if sc else None,
                    "age_days": age, "views_per_day": round(views / age, 1), "duration": it["contentDetails"]["duration"],
                    "published": pub, "measured": True})
    return out


def gather_signals(settings=None, log_cb=print) -> dict:
    s = (settings or load_settings())["research"]
    hours = s.get("cache_hours", 12)
    sig = {"collected": now_iso(), "sources_ok": [], "sources_failed": [], "items": [], "competitor_videos": []}

    def attempt(name, fn):
        try:
            res = fn()
            sig["sources_ok"].append(name)
            log_cb(f"  OK   {name}: {len(res)} items")
            return res
        except Exception as e:
            sig["sources_failed"].append(f"{name}: {type(e).__name__}: {str(e)[:120]}")
            log_cb(f"  FAIL {name}: {type(e).__name__}")
            return []

    y = (dt.date.today() - dt.timedelta(days=2))
    if s.get("use_wikipedia", True):
        url = f"https://wikimedia.org/api/rest_v1/metrics/pageviews/top/en.wikipedia/all-access/{y:%Y/%m/%d}"
        sig["items"] += attempt("Wikipedia most-read", lambda: cached_fetch("wiki", url, hours, parse_wikipedia_top))
    if s.get("use_google_trends", True):
        url = f"https://trends.google.com/trending/rss?geo={s.get('region', 'US')}"
        sig["items"] += attempt("Google Trends", lambda: cached_fetch("gtrends", url, hours, parse_google_trends_rss))
    if s.get("use_reddit", True):
        for sub in ("todayilearned", "AskReddit", "nosleep", "history"):
            url = f"https://www.reddit.com/r/{sub}/top.json?t=week&limit=25"
            sig["items"] += attempt(f"Reddit r/{sub}", lambda u=url, sb=sub: cached_fetch("reddit", u, hours,
                                                                                        lambda r: parse_reddit(r, sb)))
    for cid in s.get("competitor_channel_ids", []):
        url = f"https://www.youtube.com/feeds/videos.xml?channel_id={cid}"
        sig["competitor_videos"] += attempt(f"YouTube RSS {cid}", lambda u=url: cached_fetch("ytrss", u, hours, parse_youtube_rss))
    key = s.get("youtube_api_key", "").strip()
    if key:
        for q in ("stickman what if", "stickman survival", "stickman animation story"):
            sig["competitor_videos"] += attempt(f"YouTube API '{q}'",
                                                lambda qq=q: _yt_cached(key, qq, hours, s.get("region", "US")))
    return sig


def _yt_cached(key, q, hours, region):
    ck = f"research:ytapi:{sha([q, region, str(dt.date.today())])}"
    hit = cache_get(ck, hours)
    if hit is not None:
        return hit
    res = youtube_api_search(key, q, region=region)
    cache_put(ck, res, "research")
    return res


# --------------------------------------------------------------------------- idea generation
def _bank():
    return read_json(CONFIG_DIR / "idea_bank.json", {"formats": [], "seeds": []})


def used_topics() -> set:
    return {r["topic"].lower() for r in db_query("SELECT topic FROM ideas WHERE status IN ('chosen','produced')")}


def comparables_for(topic: str, videos: list[dict], n=3) -> list[dict]:
    words = {w for w in re.findall(r"[a-zA-Z]{4,}", topic.lower())}
    scored = []
    for v in videos:
        if not v.get("measured"):
            continue
        tw = set(re.findall(r"[a-zA-Z]{4,}", v["title"].lower()))
        overlap = len(words & tw)
        if overlap:
            scored.append((overlap, v.get("views") or 0, v))
    scored.sort(key=lambda x: (-x[0], -x[1]))
    keep = ("title", "channel", "url", "views", "subscribers", "views_per_sub", "age_days", "views_per_day", "source")
    return [{k: v.get(k) for k in keep if v.get(k) is not None} for _, _, v in scored[:n]]


def offline_ideas(lang: str, signals: dict, n: int = 10, seed: int | None = None) -> list[dict]:
    """Deterministic idea generator (no LLM). Evergreen stickman formats + live trending signals."""
    bank = _bank()
    rng = random.Random(seed if seed is not None else dt.date.today().toordinal())
    used = used_topics()
    seeds = [x for x in bank["seeds"] if x["topic_en"].lower() not in used]
    rng.shuffle(seeds)
    ideas = []
    vids = signals.get("competitor_videos", [])
    for sd in seeds[: n]:
        fmt = next(f for f in bank["formats"] if f["id"] == sd["format"])
        title = (sd.get(f"title_{lang}") or sd["title_en"])
        comps = comparables_for(sd["topic_en"], vids)
        ideas.append({
            "topic": sd.get(f"topic_{lang}") or sd["topic_en"], "topic_en": sd["topic_en"], "title": title,
            "why": fmt[f"why_{lang}"] if f"why_{lang}" in fmt else fmt["why_en"],
            "comparables": comps,
            "stats_measured": {"comparable_videos": len(comps)} if comps else {},
            "stats_note": ("Measured stats come from the listed comparable videos." if comps else
                           "No measured YouTube data for this topic yet (add a free YouTube API key or competitor channel IDs "
                           "in Settings). Scores below are ESTIMATES."),
            "competition": sd.get("competition", "medium") + " (estimate)",
            "duration_min": fmt.get("duration_min", 8), "thumbnail_concept": sd.get("thumb") or fmt["thumb"],
            "difficulty": sd.get("difficulty", fmt.get("difficulty", "medium")),
            "viral_potential": f"{sd.get('potential', 7)}/10 (estimate)", "format": fmt["id"],
            "mood": sd.get("mood", fmt.get("mood", "mystery")), "background": sd.get("bg", "day"),
            "source": "offline idea bank" + (" + measured comparables" if comps else ""),
        })
    # one or two ideas from live trending signals (measured interest), if any were collected
    trend = [i for i in signals.get("items", []) if i["source"] in ("wikipedia_most_read", "google_trends_daily")]
    for tr in trend[:2]:
        if len(ideas) >= n + 2:
            break
        t = tr["title"]
        stat = {k: tr[k] for k in ("views_yesterday", "approx_traffic") if tr.get(k)}
        ideas.insert(0, {
            "topic": t, "topic_en": t,
            "title": (f"{t}: šta se zaista desilo?" if lang == "sr" else f"{t}: What Actually Happened?"),
            "why": ("Tema je trenutno u trendu (izmereno) - brza objašnjenja trend-tema često dobijaju pretragu."
                    if lang == "sr" else "Currently trending (measured). Fast explainers on trending topics catch search traffic."),
            "comparables": comparables_for(t, vids), "stats_measured": {"source": tr["source"], **stat},
            "stats_note": "Interest is measured; YouTube performance is an estimate.",
            "competition": "unknown (estimate: trending topics get crowded fast)", "duration_min": 6,
            "thumbnail_concept": "GLAVONJA shocked, pointing at a big symbol of the topic, 3-word text",
            "difficulty": "medium", "viral_potential": "6/10 (estimate, time-sensitive)", "format": "explainer",
            "mood": "mystery", "background": "city", "source": tr["source"]})
    return ideas[:n]


def _validate_ideas(data):
    items = data.get("ideas") if isinstance(data, dict) else data
    if not isinstance(items, list) or len(items) < 5:
        raise ValueError("expected list of ideas")
    req = ("topic", "title", "why")
    return [i for i in items if all(k in i for k in req)][:10]


def research_ideas(lang: str | None = None, log_cb=print, refresh=False) -> dict:
    settings = load_settings()
    lang = lang or settings["language"]
    log_cb("VIRAL RESEARCHER: collecting signals...")
    signals = gather_signals(settings, log_cb)
    ideas, mode = None, "offline"
    try:
        compact = {"trending": [{k: v for k, v in i.items() if k != "measured"} for i in signals["items"][:40]],
                   "competitor_videos": sorted(signals["competitor_videos"], key=lambda v: -(v.get("views_per_day") or 0))[:25],
                   "already_made": sorted(used_topics())[:50]}
        prompt = load_prompt("ideas", language="Serbian (latin script)" if lang == "sr" else "English",
                             signals=compact, bank=_bank()["formats"])
        ideas = ask_json("ideas", prompt, _validate_ideas, settings, use_cache=not refresh)
        mode = "llm"
        for i in ideas:  # attach measured comparables from our own data (never trust LLM numbers)
            i["comparables"] = comparables_for(i.get("topic_en") or i["topic"], signals["competitor_videos"])
            i["stats_measured"] = {"comparable_videos": len(i["comparables"])} if i["comparables"] else {}
            for k in ("viral_potential", "competition"):
                if k in i and "estimate" not in str(i[k]).lower():
                    i[k] = f"{i[k]} (estimate)"
            i.setdefault("source", "local LLM + live signals")
    except LLMUnavailable as e:
        log_cb(f"  No local LLM available -> using offline idea engine ({str(e)[:80]})")
        ideas = offline_ideas(lang, signals, seed=random.randint(0, 10 ** 6) if refresh else None)
    batch = now_iso()
    for i in ideas:
        i["language"] = lang
        i["id"] = db_exec("INSERT INTO ideas(batch, created, language, topic, title, data) VALUES (?,?,?,?,?,?)",
                          (batch, batch, lang, i["topic"], i["title"], json.dumps(i, ensure_ascii=False)))
    db_exec("UPDATE ideas SET data=json_set(data,'$.id',id) WHERE batch=?", (batch,))
    result = {"batch": batch, "mode": mode, "language": lang, "sources_ok": signals["sources_ok"],
              "sources_failed": signals["sources_failed"], "ideas": ideas}
    cache_put("ideas:latest", result, "ideas")
    log_cb(f"VIRAL RESEARCHER: {len(ideas)} ideas ready (mode: {mode}).")
    return result


def latest_ideas() -> dict | None:
    return cache_get("ideas:latest")


def get_idea(idea_id: int) -> dict | None:
    r = db_query("SELECT data FROM ideas WHERE id=?", (idea_id,))
    return json.loads(r[0]["data"]) if r else None
