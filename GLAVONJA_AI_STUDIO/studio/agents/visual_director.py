"""AGENT 3 - VISUAL DIRECTOR.

Script lines -> shots (<= max_shot_sec, one Google Flow clip each) -> storyboard.json.
Each shot gets:
  * description  : what the viewer sees (used as the Google Flow prompt)
  * layout       : background / character action+expression / props / camera / effects
                   (used for the storyboard preview frames and the approved local fallback)
Only values from the asset vocabulary are allowed, so the LLM cannot invent a new character.
"""
from __future__ import annotations

import re

from ..core import Project, atomic_write_json, load_settings, load_style, read_json
from ..llm import LLMUnavailable, ask_json, load_prompt
from ..render.character import ACTIONS, EXPRESSIONS
from ..render.world import BACKGROUNDS, PROPS
from .scriptwriter import WPS

# keyword stems (English + Serbian latin) -> visual choice
BG_KW = {
    "space": ["space", "orbit", "astronaut", "planet", "galax", "black hole", "svemir", "planet", "crn rup", "orbit"],
    "ocean": ["ocean", "sea", "ship", "titanic", "wave", "okean", "more", "brod", "talas"],
    "underwater": ["underwater", "bottom of the ocean", "deep sea", "pod vodom", "dno okeana", "dubin"],
    "desert": ["desert", "sand", "pyramid", "egypt", "pustinj", "pesak", "piramid", "egip"],
    "forest": ["forest", "woods", "tree", "šum", "drveć", "drvo"],
    "jungle": ["jungle", "amazon", "džungl", "amazon"],
    "night": ["night", "dark", "midnight", "3 am", "noć", "mrak", "ponoć"],
    "city": ["city", "street", "people", "internet", "phone", "grad", "ulic", "ljudi", "telefon"],
    "cave": ["cave", "underground", "bunker", "hole", "pećin", "podzem", "bunker", "rup"],
    "snow": ["snow", "ice", "cold", "freez", "winter", "sneg", "led", "hladn", "smrz", "zim"],
    "volcano": ["volcano", "lava", "erupt", "pompeii", "vulkan", "lava", "erupc", "pompej"],
    "ancient": ["ancient", "rome", "roman", "medieval", "history", "king", "castle", "drevn", "rim", "srednj", "istorij", "kralj", "zamak"],
    "lab": ["science", "scientist", "experiment", "invent", "tesla", "nauk", "naučn", "eksperiment", "izum"],
    "school": ["school", "teacher", "learn", "škol", "učitelj", "uči"],
    "room": ["home", "bed", "sleep", "wake", "kuć", "krevet", "spav", "probud", "soba"],
    "island": ["island", "beach", "ostrv", "plaž"],
    "apocalypse": ["apocalypse", "end of the world", "war", "nuclear", "zombie", "apokalip", "kraj sveta", "rat", "nuklear", "zombi"],
    "office": ["office", "work", "job", "backrooms", "kancelarij", "posao", "posl"],
}
ACT_KW = [
    ("run", ["run", "escape", "chase", "flee", "hurry", "trč", "beža", "juri", "brzo"]),
    ("fall", ["fall", "crash", "collapse", "drop", "pad", "sruš", "pao", "pala"]),
    ("jump", ["jump", "leap", "skoč"]),
    ("shock", ["suddenly", "shock", "but then", "wait", "boom", "explod", "odjednom", "šok", "ali onda", "čekaj", "eksplod"]),
    ("scared", ["scary", "afraid", "fear", "horror", "monster", "ghost", "panic", "danger", "strah", "uplaš", "čudovi", "duh", "panik", "opasn"]),
    ("cheer", ["win", "success", "finally", "survive", "rich", "pobed", "uspe", "konačno", "preživ", "bogat"]),
    ("think", ["think", "wonder", "why", "how", "imagine", "question", "misl", "zašto", "kako", "zamisli", "pitanj"]),
    ("walk", ["walk", "go ", "travel", "explore", "journey", "hod", "ide", "putu", "istraž"]),
    ("point", ["this", "look", "here", "that's", "ovo", "pogledaj", "evo", "to je"]),
    ("shrug", ["maybe", "nobody knows", "no one knows", "možda", "niko ne zna"]),
    ("swim", ["swim", "pliv"]),
    ("climb", ["climb", "pen"]),
]
EXPR_FOR = {"run": "scared", "fall": "shocked", "jump": "excited", "shock": "shocked", "scared": "scared",
            "cheer": "happy", "think": "thinking", "walk": "determined", "point": "neutral", "shrug": "confused",
            "talk": "neutral", "idle": "neutral", "swim": "determined", "climb": "determined"}
PROP_KW = {
    "earth": ["earth", "world", "planet", "zemlj", "svet"], "sun": ["sun", "sunc"], "moon": ["moon", "mesec"],
    "skull": ["death", "die", "dead", "kill", "smrt", "umr", "mrtv", "ubi"], "clock": ["time", "hour", "minute", "second", "vreme", "sat", "minut", "sekund"],
    "money": ["money", "dollar", "rich", "cost", "pay", "novac", "para", "dolar", "bogat", "plat"],
    "fire": ["fire", "burn", "hot", "vatr", "gori", "vruć"], "ghost": ["ghost", "spirit", "haunt", "duh", "ukle"],
    "meteor": ["meteor", "asteroid"], "rocket": ["rocket", "launch", "raket"], "bomb": ["bomb", "explod", "bomb", "eksplo"],
    "lightbulb": ["idea", "smart", "realize", "ideja", "pamet", "shvat"], "heart": ["love", "heart", "ljub", "srce"],
    "book": ["book", "story", "knjig", "priča"], "phone": ["phone", "internet", "telefon"], "car": ["car", "drive", "auto", "vozi"],
    "shark": ["shark", "ajkul"], "pyramid": ["pyramid", "piramid"], "castle": ["castle", "king", "zamak", "kralj"],
    "crown": ["king", "queen", "emperor", "kralj", "car "], "sword": ["sword", "battle", "fight", "mač", "bitk", "bori"],
    "cloud": ["sky", "cloud", "neb", "oblak"], "lightning": ["storm", "lightning", "electric", "oluj", "munj", "struj"],
    "snowflake": ["snow", "ice", "freez", "sneg", "led"], "thermometer": ["temperature", "degree", "temperat", "stepen"],
    "hourglass": ["days", "years", "wait", "dana", "godin", "čeka"], "magnifier": ["search", "investigat", "clue", "traž", "istra", "trag"],
    "virus": ["virus", "disease", "plague", "sick", "bolest", "kuga", "bolest"], "planet": ["mars", "jupiter", "saturn"],
    "warning": ["danger", "warning", "opasn", "upozor"], "door": ["door", "enter", "vrata", "uđe"], "key": ["key", "secret", "ključ", "tajn"],
    "apple": ["food", "eat", "hungry", "hran", "jede", "glad"], "water": ["water", "drink", "thirst", "vod", "pij", "žeđ"],
    "tent": ["camp", "shelter", "kamp", "sklon"], "campfire": ["campfire", "warm", "logorsk", "greja"], "dinosaur": ["dinosaur", "dinosaur"],
    "atom": ["atom", "nuclear", "nuklear"], "chart_up": ["grow", "increase", "more and more", "raste", "poveća", "sve više"],
    "chart_down": ["decrease", "drop", "less", "opada", "smanj", "manje"], "zzz": ["sleep", "tired", "spav", "umor"],
    "bones": ["bones", "skeleton", "kost", "skelet"], "boat": ["boat", "raft", "čamac", "splav"], "plane": ["plane", "fly", "avion", "let"],
    "house": ["house", "home", "kuć"], "mountain": ["mountain", "planin"], "tree": ["tree", "drvo"], "palm": ["palm", "palm"],
}
SECOND_KW = {"expert": ["scientist", "expert", "doctor", "professor", "naučnik", "stručnjak", "doktor", "profesor"],
             "friend": ["friend", "together", "brother", "prijatelj", "zajedno", "brat", "drug"],
             "villain": ["enemy", "villain", "thief", "attack", "neprijatelj", "lopov", "napad"]}
CAMERAS = ["slow_zoom_in", "pan_right", "static", "slow_zoom_out", "pan_left", "slow_zoom_in"]


def _has(text, words):
    """Stem must start a word ('duh' matches 'duhovi' but not 'vazduh')."""
    t = text.lower()
    return any(re.search(r"(?<![\w])" + re.escape(w.strip()), t) for w in words if w.strip())


def rule_layout(text: str, i: int, default_bg: str, mood: str) -> dict:
    bg = next((b for b, kw in BG_KW.items() if _has(text, kw)), default_bg)
    action = next((a for a, kw in ACT_KW if _has(text, kw)), "talk" if i % 3 else "idle")
    expr = EXPR_FOR.get(action, "neutral")
    if "?" in text and action in ("talk", "idle"):
        action, expr = "think", "thinking"
    if "!" in text and expr == "neutral":
        expr = "excited"
    props = [p for p, kw in PROP_KW.items() if _has(text, kw)][:2]
    second = next((c for c, kw in SECOND_KW.items() if _has(text, kw)), None)
    nums = re.findall(r"(\$?\d[\d.,]*\s?(?:%|km|m|years|godina|dana|days|°C|million|miliona|billion|milijardi)?)", text)
    caption = nums[0].strip().upper() if nums and len(nums[0]) <= 14 else ""
    cam = "punch_in" if action in ("shock", "fall") else CAMERAS[i % len(CAMERAS)]
    effects = []
    if action in ("shock", "fall"):
        effects.append("shake")
    if action == "run":
        effects.append("speed_lines")
    if mood == "horror" or bg in ("cave", "night") and action == "scared":
        effects.append("vignette")
    return {"background": bg, "action": action, "expression": expr, "props": props, "camera": cam,
            "second": second, "effects": effects, "caption": caption}


def _describe(lay: dict, text: str) -> str:
    who = "GLAVONJA (the channel's stickman)"
    s = f"{who} {lay['action']}s with a {lay['expression']} face"
    if lay.get("second"):
        s += f", next to a second stickman ({lay['second']})"
    if lay["props"]:
        s += ", with " + " and ".join(p.replace("_", " ") for p in lay["props"])
    return f"{s}, {lay['background'].replace('_', ' ')} background. Shot illustrates: \"{text}\""


def group_shots(lines: list[dict], lang: str, max_sec: float, min_sec: float) -> list[list[dict]]:
    shots, cur, cur_s = [], [], 0.0
    for ln in lines:
        d = len(ln["text"].split()) / WPS[lang] + 0.2
        new_section = cur and cur[-1]["section"] != ln["section"]
        if cur and (cur_s + d > max_sec or new_section) and cur_s >= min_sec * 0.5:
            shots.append(cur)
            cur, cur_s = [], 0.0
        cur.append(ln)
        cur_s += d
    if cur:
        shots.append(cur)
    return shots


def _validate_sb(n):
    def v(data):
        sc = data.get("scenes") if isinstance(data, dict) else None
        if not isinstance(sc, list) or len(sc) != n:
            raise ValueError(f"expected {n} scenes")
        return sc
    return v


def build_storyboard(project: Project, log=print) -> dict:
    settings = load_settings()
    style = load_style()
    script = read_json(project.path("script", "script.json"))
    lang = project.state["language"]
    idea = project.state["idea"]
    mood = idea.get("mood", "mystery")
    default_bg = idea.get("background", "white") if idea.get("background") in BACKGROUNDS else "white"
    shots = group_shots(script["lines"], lang, settings["shots"]["max_shot_sec"], settings["shots"]["min_shot_sec"])
    texts = [" ".join(l["text"] for l in sh) for sh in shots]
    llm = None
    try:
        prompt = load_prompt("storyboard", backgrounds=", ".join(BACKGROUNDS), actions=", ".join(ACTIONS),
                             expressions=", ".join(EXPRESSIONS), props=", ".join(sorted(PROPS)),
                             lines="\n".join(f"{i + 1}. {t}" for i, t in enumerate(texts)))
        llm = ask_json("storyboard", prompt, _validate_sb(len(texts)), settings)
        log("  storyboard layout: local LLM (validated against asset vocabulary)")
    except LLMUnavailable:
        log("  storyboard layout: rule-based (no local LLM)")
    scenes = []
    transitions = style["animation"].get("transitions", ["cut"])
    last_x = 0.4
    for i, (sh, text) in enumerate(zip(shots, texts)):
        lay = rule_layout(text, i, default_bg, mood)
        desc = None
        if llm:
            l = llm[i] or {}
            for k, allowed in (("background", BACKGROUNDS), ("action", ACTIONS), ("expression", EXPRESSIONS)):
                if l.get(k) in allowed:
                    lay[k] = l[k]
            if isinstance(l.get("props"), list):
                lay["props"] = [p for p in l["props"] if p in PROPS][:2] or lay["props"]
            if l.get("second") in ("friend", "villain", "expert"):
                lay["second"] = l["second"]
            if isinstance(l.get("caption"), str) and len(l["caption"]) <= 24:
                lay["caption"] = l["caption"].upper()
            desc = l.get("description")
        # characters: keep GLAVONJA's screen position continuous between shots
        x = 0.38 if not lay["props"] else 0.32
        if lay["action"] in ("walk", "run"):
            chars = [{"who": "main", "action": lay["action"], "expression": lay["expression"], "x": 0.18, "to_x": 0.62,
                      "facing": 1}]
        else:
            chars = [{"who": "main", "action": lay["action"], "expression": lay["expression"], "x": x,
                      "facing": 1, "talks": lay["action"] in ("talk", "idle", "point", "shrug", "think")}]
        if lay.get("second"):
            chars.append({"who": lay["second"], "action": "talk" if lay["second"] != "villain" else "point",
                          "expression": "angry" if lay["second"] == "villain" else "neutral", "x": 0.72, "facing": -1})
            chars[0]["x"] = 0.3
        props = []
        for k, pn in enumerate(lay["props"]):
            if lay.get("second"):
                px, py = (0.52, 0.34) if k == 0 else (0.52, 0.62)
            else:
                px, py = (0.66, 0.46) if k == 0 else (0.86, 0.34)
            props.append({"name": pn, "x": px, "y": py, "size": 0.22 if k == 0 else 0.17,
                          "anim": "pop" if k == 0 else "float", "delay": 0.25 + 0.4 * k})
        tr = "cut" if i == 0 else ("whip" if sh[0]["section"] != shots[i - 1][-1]["section"] else transitions[i % len(transitions)])
        sfx = []
        if tr in ("whip", "zoom"):
            sfx.append({"name": "whoosh", "at": 0.0})
        if props:
            sfx.append({"name": "cash" if props[0]["name"] in ("money", "coin") else "pop", "at": props[0]["delay"]})
        if lay["action"] in ("shock", "fall"):
            sfx.append({"name": "boom" if lay["action"] == "shock" else "thud", "at": 0.15})
        scenes.append({
            "id": i + 1, "line_ids": [l["id"] for l in sh], "section": sh[0]["section"], "text": text,
            "description": desc or _describe(lay, text), "background": lay["background"], "characters": chars,
            "props": props, "camera": lay["camera"], "transition": tr, "caption": lay["caption"],
            "effects": lay["effects"], "sfx": sfx, "use_flow": bool(settings["google"].get("use_flow", True)),
            "duration": round(sum(len(l["text"].split()) for l in sh) / WPS[lang] + 0.3, 2), "duration_is_estimate": True,
        })
    sb = {"title": script["title"], "language": lang, "mood": mood, "scene_count": len(scenes), "scenes": scenes}
    atomic_write_json(project.path("storyboard", "storyboard.json"), sb)
    md = [f"# Storyboard - {script['title']}", ""]
    for s in scenes:
        md += [f"## Shot {s['id']} ({s['duration']}s, {s['transition']})", f"> {s['text']}", "",
               f"- **Flow prompt:** {s['description']}",
               f"- layout: {s['background']} | {s['characters'][0]['action']}/{s['characters'][0]['expression']} | "
               f"props {', '.join(p['name'] for p in s['props']) or '-'} | camera {s['camera']}", ""]
    project.path("storyboard", "storyboard.md").write_text("\n".join(md), encoding="utf-8")
    log(f"  storyboard: {len(scenes)} shots")
    return sb
