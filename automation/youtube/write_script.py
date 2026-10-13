"""Ask Claude for the next Short: topic, narration and YouTube metadata."""

import json
import os

import anthropic

from brand import BRAND_BRIEF, PALETTES

MODEL = os.environ.get("CLAUDE_MODEL", "claude-opus-5-5")

SCHEMA = {
    "type": "object",
    "properties": {
        "scent": {"type": "string", "enum": list(PALETTES)},
        "hook": {"type": "string", "description": "On-screen title card, max 6 words."},
        "narration": {"type": "string", "description": "Voiceover, 95-130 words, plain text."},
        "title": {"type": "string", "description": "YouTube title, max 70 characters, no hashtags."},
        "description": {"type": "string", "description": "2-4 short sentences."},
        "tags": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["scent", "hook", "narration", "title", "description", "tags"],
    "additionalProperties": False,
}

SYSTEM = f"""You write 40-50 second vertical YouTube Shorts for a perfume house.

{BRAND_BRIEF}
Each Short teaches one specific, true thing about fragrance (a raw material, how a note
behaves on skin, how to wear or layer scent, perfume history, how perfume is made) and ties it
naturally to one Newmoda scent, or to the house ("house") when no scent fits. Open with a hook
in the first sentence. Only state facts from the brief or well-established perfumery knowledge;
never invent awards, reviews, customers or health claims. End with a soft line, not a hard sell.
The narration is read by a text-to-speech voice: no emojis, no stage directions, no hashtags."""


def write_script(recent_titles: list[str]) -> dict:
    client = anthropic.Anthropic()
    avoid = "\n".join(f"- {t}" for t in recent_titles) or "- (none yet)"
    response = client.beta.messages.create(
        model=MODEL,
        max_tokens=16000,
        betas=["server-side-fallback-2026-07-01"],
        fallbacks="default",
        output_config={"effort": "medium", "format": {"type": "json_schema", "schema": SCHEMA}},
        system=SYSTEM,
        messages=[{
            "role": "user",
            "content": f"Write today's Short. Pick an angle that is clearly different from these "
                       f"recent videos:\n{avoid}",
        }],
    )
    if response.stop_reason == "refusal":
        raise RuntimeError(f"Claude declined the request: {response.stop_details}")
    if response.stop_reason == "max_tokens":
        raise RuntimeError("Claude's reply was cut off at max_tokens")
    text = next(b.text for b in response.content if b.type == "text")
    return json.loads(text)


if __name__ == "__main__":
    print(json.dumps(write_script([]), indent=2, ensure_ascii=False))
