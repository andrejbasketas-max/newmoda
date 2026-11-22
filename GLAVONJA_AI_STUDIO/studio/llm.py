"""Text-generation backend for the creative agents.

Order is configurable (settings.llm.order).  Defaults keep cost at ZERO:
  * ollama      - free local LLM (https://ollama.com).  Recommended: qwen2.5:7b-instruct (~4.7 GB).
  * claude_cli  - `claude -p` (Claude Code).  Uses your Claude plan -> disabled unless
                  settings.llm.allow_claude_cli = true.
  * offline     - no LLM: agents fall back to deterministic template logic.

All responses are cached in SQLite by prompt hash, so nothing is generated twice.
"""
from __future__ import annotations

import json
import re
import shutil
import urllib.request

from .core import PROMPTS_DIR, cache_get, cache_put, get_logger, load_settings, run, sha


class LLMUnavailable(Exception):
    pass


def load_prompt(name: str, **vars) -> str:
    txt = (PROMPTS_DIR / f"{name}.md").read_text(encoding="utf-8")
    for k, v in vars.items():
        txt = txt.replace("{{" + k + "}}", v if isinstance(v, str) else json.dumps(v, ensure_ascii=False, indent=1))
    return txt


def ollama_ok(settings=None) -> bool:
    s = (settings or load_settings())["llm"]
    try:
        with urllib.request.urlopen(s["ollama_url"].rstrip("/") + "/api/tags", timeout=3) as r:
            tags = json.loads(r.read())
        names = [m.get("name", "") for m in tags.get("models", [])]
        return any(n == s["ollama_model"] or n.split(":")[0] == s["ollama_model"].split(":")[0] for n in names)
    except Exception:
        return False


def _ollama(prompt: str, s: dict) -> str:
    body = json.dumps({"model": s["ollama_model"], "prompt": prompt, "stream": False, "format": "json",
                       "options": {"temperature": 0.8, "num_ctx": 8192}}).encode()
    req = urllib.request.Request(s["ollama_url"].rstrip("/") + "/api/generate", data=body,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=s.get("timeout_sec", 900)) as r:
        return json.loads(r.read())["response"]


def _claude_cli(prompt: str, s: dict) -> str:
    exe = shutil.which("claude")
    if not exe:
        raise LLMUnavailable("claude CLI not on PATH")
    cmd = [exe, "-p", "--output-format", "text"]
    if s.get("claude_cli_model"):
        cmd += ["--model", s["claude_cli_model"]]
    r = run(cmd, input_bytes=prompt.encode("utf-8"), timeout=s.get("timeout_sec", 900))
    return r.stdout.decode("utf-8", "replace")


def extract_json(text: str):
    text = text.strip()
    try:
        return json.loads(text)
    except Exception:
        pass
    m = re.search(r"```(?:json)?\s*(.+?)```", text, re.S)
    if m:
        try:
            return json.loads(m.group(1))
        except Exception:
            pass
    for open_, close in (("{", "}"), ("[", "]")):
        i, j = text.find(open_), text.rfind(close)
        if i != -1 and j > i:
            try:
                return json.loads(text[i:j + 1])
            except Exception:
                continue
    raise ValueError("No JSON found in model output")


def available_providers(settings=None) -> list[str]:
    s = (settings or load_settings())["llm"]
    out = []
    for p in s["order"]:
        if p == "ollama" and ollama_ok(settings):
            out.append(p)
        elif p == "claude_cli" and s.get("allow_claude_cli") and shutil.which("claude"):
            out.append(p)
    return out


def ask_json(task: str, prompt: str, validate=None, settings=None, use_cache=True):
    """Return parsed JSON from the first working provider, or raise LLMUnavailable (=> offline)."""
    settings = settings or load_settings()
    s = settings["llm"]
    key = "llm:" + sha({"task": task, "prompt": prompt, "model": s["ollama_model"]})
    if use_cache:
        hit = cache_get(key)
        if hit is not None:
            return hit
    log = get_logger()
    errors = []
    for prov in available_providers(settings):
        for attempt in range(2):
            try:
                log.info("LLM %s -> %s (attempt %d)", task, prov, attempt + 1)
                raw = _ollama(prompt, s) if prov == "ollama" else _claude_cli(prompt, s)
                data = extract_json(raw)
                if validate:
                    data = validate(data)
                cache_put(key, data, "llm")
                return data
            except Exception as e:  # try again / next provider
                errors.append(f"{prov}: {e}")
                log.warning("LLM %s via %s failed: %s", task, prov, e)
    raise LLMUnavailable("; ".join(errors) or "no LLM provider available (offline mode)")
