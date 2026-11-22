"""Command line for GLAVONJA AI STUDIO (works without Claude Code).

  glavonja ideas [--lang sr|en] [--refresh]       /glavonja-ideas
  glavonja make <idea_id|"free topic"> [--duration 60] [--lang sr]   /glavonja-make
  glavonja status [project]                       /glavonja-status
  glavonja style [show|learn|test|approve]        /glavonja-style
  glavonja continue [project]                     /glavonja-continue
  glavonja settings [key value]                   /glavonja-settings
  glavonja history                                /glavonja-history
  glavonja approve <key> [project] [--no]          approve/decline Google credit use or a fallback
  glavonja voices [--audition] [--lock NAME]       Gemini voice audition + lock
  glavonja script-edit <project> <file.txt>        replace the script with your own text
  glavonja autopilot                              daily ideas + FLOW_INBOX import + resume (Task Scheduler)
  glavonja dashboard                              start the local web dashboard
  glavonja selftest                               check the installation
"""
from __future__ import annotations

import argparse
import json
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from . import consistency, google_ai
from .core import (ROOT, STAGE_LABELS, STAGES, Project, ensure_dirs, get_project, list_projects, load_settings,
                   load_style, save_style, set_setting)


def _print_ideas(res):
    print(f"\n10 IDEAS  (mode: {res['mode']}, sources OK: {', '.join(res['sources_ok']) or 'none'})")
    if res["sources_failed"]:
        print("  unreachable sources:", "; ".join(x.split(":")[0] for x in res["sources_failed"]))
    for i in res["ideas"]:
        print(f"\n[{i['id']}] {i['title']}")
        print(f"     topic: {i['topic']} | format: {i.get('format')} | ~{i.get('duration_min')} min | difficulty: {i.get('difficulty')}")
        print(f"     why: {i['why']}")
        print(f"     competition: {i.get('competition')} | viral potential: {i.get('viral_potential')}")
        print(f"     thumbnail: {i.get('thumbnail_concept')}")
        if i.get("stats_measured"):
            print(f"     MEASURED: {i['stats_measured']}")
        for c in i.get("comparables", [])[:3]:
            print(f"     comparable: {c.get('title')} ({c.get('channel')}) views={c.get('views')} subs={c.get('subscribers')}")
        if i.get("stats_note"):
            print(f"     note: {i['stats_note']}")
    print("\nStart production with:  glavonja make <id>")


def print_status(p: Project):
    pr = p.progress()
    print(f"\n{p.state['title']}  [{p.id}]")
    print(f"status: {p.state['status']}  |  {pr['done']}/{pr['total']} stages ({pr['percent']}%)")
    for st in STAGES:
        stt = p.state["stages"][st]["status"]
        mark = {"done": "✔", "running": "…", "blocked": "⏸", "failed": "✖"}.get(stt, " ")
        print(f"  {mark} {STAGE_LABELS[st]:<18} {stt}")
    b = p.state.get("blocker")
    if b:
        print(f"\nWAITING: {b['message']}")
        for o in b.get("options", []):
            print(f"   -> {o['label']}" + (f"   (glavonja approve {o['key']} {p.id[:15]})" if o.get("key") else ""))
        if b.get("data", {}).get("estimate"):
            print("   estimate:", json.dumps(b["data"]["estimate"], ensure_ascii=False))
    if p.state.get("last_error") and p.state["status"] == "failed":
        print("\nERROR:", p.state["last_error"]["error"][:600])
    for n in p.state.get("notices", []) + p.state.get("warnings", []):
        print("NOTE:", n)
    if p.state.get("final_video"):
        print("\nvideo:", ROOT / p.state["final_video"])
    if p.state.get("export"):
        print("export:", p.state["export"])


def main(argv=None):
    ensure_dirs()
    ap = argparse.ArgumentParser(prog="glavonja", description="GLAVONJA AI STUDIO")
    sub = ap.add_subparsers(dest="cmd")
    a = sub.add_parser("ideas"); a.add_argument("--lang"); a.add_argument("--refresh", action="store_true")
    a = sub.add_parser("make"); a.add_argument("what"); a.add_argument("--duration", type=int); a.add_argument("--lang")
    a.add_argument("--script-file"); a.add_argument("--wait", action="store_true", default=True)
    a = sub.add_parser("status"); a.add_argument("project", nargs="?")
    a = sub.add_parser("continue"); a.add_argument("project", nargs="?")
    a = sub.add_parser("style"); a.add_argument("action", nargs="?", default="show", choices=["show", "learn", "test", "approve"])
    a = sub.add_parser("settings"); a.add_argument("key", nargs="?"); a.add_argument("value", nargs="?")
    sub.add_parser("history")
    a = sub.add_parser("approve"); a.add_argument("key"); a.add_argument("project", nargs="?"); a.add_argument("--no", action="store_true")
    a = sub.add_parser("voices"); a.add_argument("--audition", action="store_true"); a.add_argument("--lock")
    a = sub.add_parser("script-edit"); a.add_argument("project"); a.add_argument("file")
    a = sub.add_parser("redo"); a.add_argument("stage", choices=STAGES); a.add_argument("project", nargs="?")
    a = sub.add_parser("autopilot"); a.add_argument("--no-research", action="store_true")
    sub.add_parser("dashboard")
    sub.add_parser("selftest")
    args = ap.parse_args(argv)

    if args.cmd == "ideas":
        from .agents.researcher import research_ideas
        _print_ideas(research_ideas(args.lang, refresh=args.refresh))
    elif args.cmd == "make":
        from .agents.researcher import get_idea
        from .core import db_exec
        from .production import run_pipeline
        s = load_settings()
        lang = args.lang or s["language"]
        if args.what.isdigit():
            idea = get_idea(int(args.what))
            if not idea:
                sys.exit(f"No idea with id {args.what}. Run: glavonja ideas")
            lang = args.lang or idea.get("language", lang)
            db_exec("UPDATE ideas SET status='chosen' WHERE id=?", (idea["id"],))
        else:
            idea = {"topic": args.what, "title": args.what, "mood": "mystery"}
        dur = args.duration or int(idea.get("duration_min", 0) * 60) or s["target_duration_sec"]
        p = Project.create(idea["title"], lang, idea, dur)
        if args.script_file:
            from .agents.scriptwriter import import_text
            import_text(p, open(args.script_file, encoding="utf-8").read())
        print(f"Project {p.id} created. Producing...")
        run_pipeline(p)
        print_status(Project(p.folder))
    elif args.cmd in ("status",):
        p = get_project(args.project)
        print_status(p) if p else print("No projects yet.")
    elif args.cmd == "continue":
        from .production import run_pipeline
        p = get_project(args.project)
        if not p:
            sys.exit("No project to continue.")
        run_pipeline(p)
        print_status(Project(p.folder))
    elif args.cmd == "redo":
        from .production import reset_stage
        p = get_project(args.project)
        reset_stage(p, args.stage)
        print(f"Stage '{args.stage}' and later reset. Run: glavonja continue")
    elif args.cmd == "approve":
        p = get_project(args.project)
        google_ai.approve(p, args.key, not args.no)
        print(f"{'Approved' if not args.no else 'Declined'}: {args.key} for {p.id}. Run: glavonja continue")
    elif args.cmd == "style":
        st = load_style()
        if args.action == "show":
            print(json.dumps({k: st[k] for k in ("status", "verified", "character", "palette", "measured_from_references")},
                             ensure_ascii=False, indent=1))
            print("references:", len(consistency.reference_files()), "frames in references/frames")
        elif args.action == "learn":
            print(json.dumps(consistency.learn_style(), ensure_ascii=False, indent=1))
        elif args.action == "test":
            from .style_tools import make_test_scene
            print("test scene:", make_test_scene())
        elif args.action == "approve":
            st["verified"] = True
            st["status"] = "APPROVED by the channel owner"
            save_style(st)
            print("Style approved. Videos that pass the consistency check can now be exported.")
    elif args.cmd == "settings":
        if args.key and args.value is not None:
            set_setting(args.key, args.value)
            print("saved", args.key)
        s = load_settings()
        if s["google"].get("api_key"):
            s["google"]["api_key"] = "***"
        if s["research"].get("youtube_api_key"):
            s["research"]["youtube_api_key"] = "***"
        print(json.dumps(s, ensure_ascii=False, indent=1))
    elif args.cmd == "history":
        for pr in list_projects():
            print(f"{pr['created'][:16]}  {pr['status']:<17} {pr['progress']['percent']:>3}%  {pr['title']}  [{pr['id']}]"
                  + ("  APPROVED" if pr["approved"] else ""))
    elif args.cmd == "voices":
        s = load_settings()
        if args.lock:
            set_setting("google.tts_voice", args.lock)
            set_setting("google.tts_voice_locked", "true")
            print(f"Gemini voice locked: {args.lock}")
        elif args.audition:
            from .core import ROOT as R
            print(google_ai.estimate_tts(["x" * 120] * 6))
            res = google_ai.audition_voices(_sample(s["language"]), ["Charon", "Puck", "Fenrir", "Orus", "Kore", "Zephyr"],
                                            R / "assets" / "voice_audition", s)
            print(json.dumps(res, indent=1))
        else:
            from .audio import voice_status
            print(json.dumps(voice_status(), indent=1), "\nGemini voices:", ", ".join(google_ai.GEMINI_VOICES))
    elif args.cmd == "script-edit":
        from .agents.scriptwriter import import_text
        from .production import reset_stage
        p = get_project(args.project)
        import_text(p, open(args.file, encoding="utf-8").read())
        reset_stage(p, "storyboard")
        p.mark("script", "done")
        print("Script replaced. Run: glavonja continue")
    elif args.cmd == "autopilot":
        from .autopilot import run_once
        run_once(research=not args.no_research)
    elif args.cmd == "dashboard":
        from .dashboard import serve
        serve()
    elif args.cmd == "selftest":
        from .selftest import selftest
        sys.exit(0 if selftest() else 1)
    else:
        ap.print_help()


def _sample(lang):
    return ("Zamisli da se jednog jutra probudiš, a Zemlja je prestala da se okreće. Šta bi uradio?" if lang == "sr"
            else "Imagine waking up one morning and the Earth has stopped spinning. What would you do?")


if __name__ == "__main__":
    main()
