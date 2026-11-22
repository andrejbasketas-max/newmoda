"""AGENT 8 - YOUTUBE SEO AGENT: 5 titles, recommended title, description with chapters,
tags, hashtags, pinned comment, thumbnail recommendation.  LLM if available, else templates."""
from __future__ import annotations

import re

from ..core import Project, atomic_write_json, load_settings, read_json
from ..llm import LLMUnavailable, ask_json, load_prompt

STOP = {"the", "a", "an", "of", "to", "in", "on", "for", "and", "if", "you", "your", "what", "how", "is", "it", "da", "li",
        "je", "se", "i", "u", "na", "šta", "ako", "kako", "bi", "sa", "za", "od", "this", "that", "with"}


def chapters(p: Project) -> list[str]:
    sb = read_json(p.path("storyboard", "storyboard.json"))
    out, seen = [], set()
    for sc in sb["scenes"]:
        if sc["section"] in seen:
            continue
        seen.add(sc["section"])
        t = int(sc.get("start", 0))
        out.append(f"{t // 60}:{t % 60:02d} {sc['section']}")
    if out and not out[0].startswith("0:00"):
        out[0] = "0:00 " + out[0].split(" ", 1)[1]
    return out if len(out) >= 3 else []  # YouTube needs >= 3 chapters starting at 0:00


def _keywords(text: str, n=12) -> list[str]:
    words = [w.lower() for w in re.findall(r"[\wčćžšđČĆŽŠĐ]{4,}", text)]
    freq = {}
    for w in words:
        if w not in STOP:
            freq[w] = freq.get(w, 0) + 1
    return [w for w, _ in sorted(freq.items(), key=lambda kv: -kv[1])[:n]]


def offline_metadata(p: Project) -> dict:
    lang = p.state["language"]
    idea = p.state["idea"]
    t = idea.get("title", p.state["title"])
    topic = idea.get("topic", t)
    script = read_json(p.path("script", "script.json"))
    kw = _keywords(" ".join(l["text"] for l in script["lines"]) + " " + topic)
    if lang == "sr":
        titles = [t, f"{topic} - šta bi se stvarno desilo?", f"Da li bi preživeo: {topic}?", f"{topic} (animacija)",
                  f"Niko ne priča o ovome: {topic}"]
        desc = (f"{script['lines'][0]['text']} {script['lines'][1]['text'] if len(script['lines']) > 1 else ''}\n\n"
                f"U ovom GLAVONJA videu saznaćeš šta se zaista dešava kada {topic[0].lower() + topic[1:]}.\n")
        pinned = "Šta bi TI uradio na mom mestu? Napiši u komentarima 👇"
        base_tags = ["glavonja", "stickman", "animacija", "stickman animacija", "šta ako", "na srpskom"]
    else:
        titles = [t, f"What Would REALLY Happen: {topic}", f"Could You Survive {topic}?", f"{topic} (Animated)",
                  f"Nobody Talks About This: {topic}"]
        desc = (f"{script['lines'][0]['text']} {script['lines'][1]['text'] if len(script['lines']) > 1 else ''}\n\n"
                f"In this GLAVONJA video we find out what really happens: {topic}.\n")
        pinned = "What would YOU do in this situation? Tell me below 👇"
        base_tags = ["glavonja", "stickman", "animation", "stickman animation", "what if", "story"]
    ch = chapters(p)
    if ch:
        desc += "\n" + "\n".join(ch) + "\n"
    tags = list(dict.fromkeys(base_tags + kw + [topic.lower()]))[:25]
    hashtags = ["#glavonja", "#stickman", "#" + re.sub(r"\W", "", (kw[0] if kw else "animation"))]
    desc += "\n" + " ".join(hashtags)
    return {"titles": [x[:100] for x in titles], "recommended_title": titles[0], "description": desc, "tags": tags,
            "hashtags": hashtags, "pinned_comment": pinned, "thumbnail_text": None, "mode": "offline_template"}


def _validate(d):
    if not isinstance(d, dict) or len(d.get("titles", [])) < 3 or not d.get("description"):
        raise ValueError("incomplete metadata")
    return d


def make_metadata(p: Project, log=print) -> dict:
    s = load_settings()
    script = read_json(p.path("script", "script.json"))
    lang = p.state["language"]
    try:
        prompt = load_prompt("seo", language="Serbian (latin)" if lang == "sr" else "English",
                             title=p.state["idea"].get("title", p.state["title"]), topic=p.state["idea"].get("topic", ""),
                             summary=" ".join(l["text"] for l in script["lines"][:12]), chapters="\n".join(chapters(p)) or "(none)")
        meta = ask_json("seo", prompt, _validate, s)
        meta["mode"] = "llm"
        ch = chapters(p)
        if ch and ch[0] not in meta["description"]:
            meta["description"] += "\n\n" + "\n".join(ch)
    except LLMUnavailable:
        meta = offline_metadata(p)
    thumbs = read_json(p.path("thumbnails", "thumbnails.json"), {})
    meta["thumbnail_recommendation"] = thumbs.get("recommended", "A")
    meta["chapters"] = chapters(p)
    atomic_write_json(p.path("final", "metadata.json"), meta)
    md = [f"# YouTube metadata - {p.state['title']}", "", "## Recommended title", meta["recommended_title"], "",
          "## Title options", *[f"{i + 1}. {t}" for i, t in enumerate(meta["titles"])], "", "## Description", "```",
          meta["description"], "```", "", "## Tags", ", ".join(meta["tags"]), "", "## Hashtags", " ".join(meta["hashtags"]),
          "", "## Pinned comment", meta["pinned_comment"], "", f"## Thumbnail: {meta['thumbnail_recommendation']}",
          "", "_Not uploaded. Upload manually after your approval._"]
    p.path("final", "metadata.md").write_text("\n".join(md), encoding="utf-8")
    log(f"  SEO metadata ({meta['mode']}): {meta['recommended_title']}")
    return meta
