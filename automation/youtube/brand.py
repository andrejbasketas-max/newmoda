"""Newmoda brand facts the scripts are written from, and a palette per scent for the visuals."""

BRAND_BRIEF = """\
Newmoda is an independent Maison de Parfum (founded 2026). Slow perfumery: every formula is
mixed by hand, matured for eight weeks, then filtered, chilled and poured in batches of 300.
40+ ingredients per formula. Naturally sourced absolutes. Refillable glass bottles.

The collection — four hours of the day, bottled (Eau de Parfum, 22% oils, 10–12 hrs, 100 ml):
- Nuit d'Ambre (00:40, midnight) — amber, smoked oud, Madagascan vanilla. €185.
  Top: bergamot, pink pepper, cardamom. Heart: amber resin, labdanum, oud.
  Base: vanilla, tonka bean, sandalwood. "Made for the hour after midnight."
- Fleur de Sel (06:15, first light) — sea salt, iris, white musk. €165.
- Rose Noire (21:00, evening) — black rose, saffron, patchouli. €195.
- Vert Silence (14:30, afternoon) — fig leaf, vetiver, cedar. €170.

Where the notes are grown:
- Bergamot, Reggio Calabria: cold-pressed from the peel in December, while still green and sharp.
- Iris, Florence: the root is dried for three years before it gives up its powdery butter.
- Rose, Grasse: picked by hand at dawn in May, before the sun burns off the scent.
- Oud, Assam: resinous agar heartwood, distilled slowly over several days.
- Vanilla, Sava, Madagascar: pods cured in the sun for months until dark, soft and sweet.

Discovery Set: four 2 ml vials for €28, credited against the first full bottle.
Voice: calm, sensory, precise, a little poetic; never pushy or hype-driven.
"""

# Background gradient (top, bottom) and accent for each scent; "house" is the neutral fallback.
PALETTES = {
    "Nuit d'Ambre": ("#1a0f0a", "#5a2e12", "#e0a96d"),
    "Fleur de Sel": ("#e9eef1", "#9fb3c0", "#2f4a5a"),
    "Rose Noire": ("#12060a", "#4a0f1f", "#d97a8c"),
    "Vert Silence": ("#0e1a12", "#3c5a3a", "#c9d6a3"),
    "house": ("#141210", "#3a332b", "#d8c3a5"),
}
