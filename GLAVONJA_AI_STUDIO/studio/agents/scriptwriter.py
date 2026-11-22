"""AGENT 2 - SCRIPTWRITER (+ topic fact research).

LLM mode  : local Ollama (free) or Claude CLI (opt-in) writes the script from verified facts.
Offline   : a structured template draft - clearly labelled DRAFT; edit it in the dashboard
            (Script tab) before continuing, or enable Ollama for real scripts.
Imported  : any script.txt you write/edit yourself (one sentence per line, '# Section' headings).
"""
from __future__ import annotations

import json
import re
import urllib.parse

from ..core import Project, atomic_write_json, get_logger, load_settings, read_json
from ..llm import LLMUnavailable, ask_json, load_prompt
from .researcher import cached_fetch

WPS = {"sr": 2.3, "en": 2.5}  # spoken words per second (narration pace)


# --------------------------------------------------------------------------- research
def research_topic(project: Project, log=print) -> dict:
    idea = project.state["idea"]
    lang = project.state["language"]
    out = {"topic": idea.get("topic"), "summaries": [], "sources": [], "failed": []}
    queries = [idea.get("topic_en") or idea.get("topic")]
    for q in queries:
        for wl in (["sr", "en"] if lang == "sr" else ["en"]):
            try:
                api = f"https://{wl}.wikipedia.org/w/api.php?" + urllib.parse.urlencode(
                    {"action": "opensearch", "search": q, "limit": 3, "format": "json"})
                hits = cached_fetch("wikisearch", api, 24 * 30, lambda r: json.loads(r))
                for title in hits[1][:2]:
                    url = f"https://{wl}.wikipedia.org/api/rest_v1/page/summary/" + urllib.parse.quote(title.replace(" ", "_"))
                    sm = cached_fetch("wikisum", url, 24 * 30, lambda r: json.loads(r))
                    if sm.get("extract"):
                        out["summaries"].append({"lang": wl, "title": sm.get("title"), "extract": sm["extract"][:1500]})
                        out["sources"].append(sm.get("content_urls", {}).get("desktop", {}).get("page", url))
            except Exception as e:
                out["failed"].append(f"wikipedia {wl}: {type(e).__name__}")
    atomic_write_json(project.path("research", "facts.json"), out)
    log(f"  research: {len(out['summaries'])} Wikipedia summaries" + (f", failed: {out['failed']}" if out["failed"] else ""))
    return out


# --------------------------------------------------------------------------- offline template
OFFLINE = {
    "en": [
        ("Hook", ["Imagine this: {T}.", "It sounds impossible, but what would actually happen to you?",
                  "Stay until the end, because the last part is the scariest."]),
        ("The start", ["It all begins on a completely normal day.", "You wake up, you look around, and something feels wrong.",
                       "At first, nobody notices anything strange.", "But within minutes, the first problems appear."]),
        ("It gets worse", ["People start to panic.", "Phones stop working, and nobody knows what to do.",
                           "You realize you have to make a choice, and fast.", "Do you run, or do you stay and fight?"]),
        ("The twist", ["But here is the part nobody expects.", "The real danger was never the thing you were afraid of.",
                       "It was the time you were wasting."]),
        ("The end", ["So, could you survive {T}?", "Maybe. But only if you knew what you know now.",
                     "Tell me in the comments what you would do, and subscribe for the next scenario."]),
    ],
    "sr": [
        ("Udica", ["Zamisli ovo: {T}.", "Zvuči nemoguće, ali šta bi se tebi zaista desilo?",
                   "Ostani do kraja, jer je poslednji deo najstrašniji."]),
        ("Početak", ["Sve počinje jednog sasvim običnog dana.", "Probudiš se, pogledaš oko sebe i nešto nije u redu.",
                     "Isprva niko ne primećuje ništa čudno.", "Ali za samo nekoliko minuta pojavljuju se prvi problemi."]),
        ("Sve je gore", ["Ljudi počinju da paniče.", "Telefoni prestaju da rade i niko ne zna šta da radi.",
                         "Shvataš da moraš da doneseš odluku, i to brzo.", "Da li bežiš, ili ostaješ da se boriš?"]),
        ("Preokret", ["Ali evo dela koji niko ne očekuje.", "Prava opasnost nikada nije bila ono čega si se plašio.",
                      "Bilo je to vreme koje si gubio."]),
        ("Kraj", ["Dakle, da li bi preživeo ovo: {T}?", "Možda. Ali samo da si znao ono što sada znaš.",
                  "Napiši u komentarima šta bi ti uradio i zaprati kanal za sledeći scenario."]),
    ],
}


def offline_script(project: Project) -> dict:
    lang = project.state["language"]
    T = project.state["idea"].get("topic", project.state["title"]).rstrip(".")
    T = T[0].lower() + T[1:] if T else T
    secs = [{"name": n, "lines": [l.replace("{T}", T) for l in lines]} for n, lines in OFFLINE[lang]]
    return {"title": project.state["idea"].get("title", project.state["title"]), "sections": secs,
            "facts_used": [], "mode": "offline_template",
            "warning": ("OFFLINE DRAFT: written from a generic template because no local LLM (Ollama) was available. "
                        "Edit the text in the Script tab, or install Ollama and press 'Rewrite script'.")}


# --------------------------------------------------------------------------- helpers
def split_sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[.!?…])\s+", text.strip())
    return [p.strip() for p in parts if p.strip()]


def finalize(project: Project, data: dict) -> dict:
    lines, n = [], 0
    for sec in data["sections"]:
        clean = []
        for raw in sec["lines"]:
            for s in split_sentences(raw):
                n += 1
                lines.append({"id": n, "text": s, "section": sec["name"]})
                clean.append(s)
        sec["lines"] = clean
    data["lines"] = lines
    data["language"] = project.state["language"]
    data["word_count"] = sum(len(l["text"].split()) for l in lines)
    data["est_seconds"] = round(data["word_count"] / WPS[project.state["language"]], 1)
    atomic_write_json(project.path("script", "script.json"), data)
    md = [f"# {data['title']}", ""]
    if data.get("warning"):
        md += [f"> **{data['warning']}**", ""]
    txt = []
    for sec in data["sections"]:
        md += [f"## {sec['name']}", ""] + sec["lines"] + [""]
        txt += [f"# {sec['name']}"] + sec["lines"] + [""]
    project.path("script", "script.md").write_text("\n".join(md), encoding="utf-8")
    project.path("script", "script.txt").write_text("\n".join(txt), encoding="utf-8")
    return data


def import_text(project: Project, text: str, title: str | None = None) -> dict:
    """User-edited script: '# Section' headings + sentences."""
    sections, cur = [], {"name": "Intro", "lines": []}
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith("#"):
            if cur["lines"]:
                sections.append(cur)
            cur = {"name": line.lstrip("#").strip() or "Section", "lines": []}
        else:
            cur["lines"].append(line)
    if cur["lines"]:
        sections.append(cur)
    if not sections:
        raise ValueError("Script is empty")
    old = read_json(project.path("script", "script.json"), {})
    data = {"title": title or old.get("title") or project.state["title"], "sections": sections,
            "facts_used": old.get("facts_used", []), "mode": "user_edited"}
    return finalize(project, data)


def _validate(data):
    if not isinstance(data, dict) or not data.get("sections"):
        raise ValueError("missing sections")
    for s in data["sections"]:
        if not s.get("lines"):
            raise ValueError("empty section")
    return data


def write_script(project: Project, log=print, force_rewrite=False) -> dict:
    settings = load_settings()
    lang = project.state["language"]
    facts = read_json(project.path("research", "facts.json"), {}) or {}
    secs = project.state["target_duration_sec"]
    words = int(secs * WPS[lang])
    prompt = load_prompt("script", language="Serbian (latin script, natural spoken Serbian)" if lang == "sr" else "English",
                         topic=project.state["idea"].get("topic", ""), title=project.state["idea"].get("title", ""),
                         words=str(words), seconds=str(secs),
                         facts="\n".join(f"- [{s['lang']}] {s['title']}: {s['extract']}" for s in facts.get("summaries", []))
                         or "(no facts available - avoid specific numbers and dates)")
    try:
        data = ask_json("script", prompt, _validate, settings, use_cache=not force_rewrite)
        data["mode"] = "llm"
        data["sources"] = facts.get("sources", [])
    except LLMUnavailable as e:
        log(f"  no local LLM ({str(e)[:60]}) -> offline template draft")
        data = offline_script(project)
    data = finalize(project, data)
    log(f"  script: {len(data['lines'])} sentences, {data['word_count']} words (~{data['est_seconds']}s), mode={data['mode']}")
    return data
