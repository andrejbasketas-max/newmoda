"""Fast unit tests (no network, no Google)."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
FIX = ROOT / "tests" / "fixtures"


def test_youtube_rss_parser():
    from studio.agents.researcher import parse_youtube_rss
    v = parse_youtube_rss((FIX / "yt_rss.xml").read_bytes())
    assert v[0]["views"] == 1200000 and v[0]["channel"] == "Example Stickman Channel"
    assert v[0]["views_per_day"] and v[0]["measured"]


def test_google_trends_parser():
    from studio.agents.researcher import parse_google_trends_rss
    t = parse_google_trends_rss((FIX / "gtrends.xml").read_bytes())
    assert t[0]["title"] == "meteor shower" and t[0]["approx_traffic"] == "200000+"


def test_wikipedia_parser():
    from studio.agents.researcher import parse_wikipedia_top
    raw = json.dumps({"items": [{"articles": [{"article": "Main_Page", "views": 9}, {"article": "Black_hole", "views": 5}]}]})
    assert parse_wikipedia_top(raw.encode()) == [{"source": "wikipedia_most_read", "title": "Black hole",
                                                  "views_yesterday": 5, "measured": True}]


def test_offline_ideas_never_invent_stats():
    from studio.agents.researcher import offline_ideas
    ideas = offline_ideas("sr", {"items": [], "competitor_videos": []}, seed=1)
    assert len(ideas) == 10
    for i in ideas:
        assert "estimate" in i["viral_potential"] and "estimate" in i["competition"]
        assert i["stats_measured"] == {}


def test_extract_json():
    from studio.llm import extract_json
    assert extract_json('blah ```json\n{"a": 1}\n``` x') == {"a": 1}
    assert extract_json('text [1, 2] tail') == [1, 2]


def test_renderer_all_backgrounds_and_actions():
    from studio.core import load_style
    from studio.render.character import ACTIONS
    from studio.render.scene import FrameRenderer
    from studio.render.world import BACKGROUNDS
    r = FrameRenderer(load_style(), 320, 180)
    for i, b in enumerate(BACKGROUNDS):
        im = r.render({"background": b, "duration": 2, "characters": [{"action": ACTIONS[i % len(ACTIONS)]}],
                       "props": [{"name": "earth"}], "effects": ["shake", "vignette"]}, 0.7)
        assert im.size == (320, 180)


def test_consistency_pass_and_fail():
    from PIL import Image
    from studio.consistency import distance, signature
    from studio.core import load_style
    from studio.render.scene import FrameRenderer
    r = FrameRenderer(load_style(), 640, 360)
    a = signature(r.render({"background": "day", "duration": 2, "characters": [{"action": "idle"}]}, 0.5))
    b = signature(r.render({"background": "day", "duration": 2, "characters": [{"action": "walk"}]}, 1.0))
    noise = Image.effect_noise((640, 360), 120).convert("RGB")
    c = signature(noise)
    assert distance(a, b)["total"] < 0.2 < distance(a, c)["total"]


def test_subtitle_time_format():
    from studio.production import _ass_time, _srt_time
    assert _srt_time(62.5) == "00:01:02,500" and _ass_time(62.5) == "0:01:02.50"


def test_shot_grouping_respects_max():
    from studio.agents.visual_director import group_shots
    lines = [{"id": i, "text": "jedan dva tri četiri pet šest sedam osam", "section": "A"} for i in range(10)]
    shots = group_shots(lines, "sr", 8.0, 2.0)
    assert all(sum(len(l["text"].split()) for l in s) / 2.3 <= 8.5 for s in shots)
