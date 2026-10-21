# YouTube kanal — prvi paket

Napravljeno pomoću `yt-*` skillova (`.claude/skills/`). Ništa nije objavljeno; objavljuješ ti.

## 1. Šta radi u tvojoj niši (sajtovi + AI + klijenti)

Izvor: `niche-videos.json` — 485 on-topic videa sa 64 kanala (javne liste, preko `yt-dlp`, bez prijave).
Rangirano po višestruku medijane SVOG kanala (`yt-viral/swipe.py`). Napomena: pretraga je povukla i
nevezane kanale, pa je filtrirano po ključnim rečima; formula u izlazu je procena NASLOVA, ne razlog uspeha.

Najjači primeri (video / medijana kanala):

| x | Video | Šta delimo |
|---|---|---|
| 36.9x | "how to sell websites to local businesses in 2025" (6.2K vs 168) | **prodaja sajtova lokalnim biznisima** |
| 33x | "I Fully Automated My Video Editing Using Claude Code" (627K vs 19K) | konkretan proces + alat |
| 29x | "How I Make $8K a Month With Just HTML and CSS" (79K vs 2.7K) | konkretan rezultat + malo alata |
| 23.6x | "The EASY way to build a beautiful website with Claude" (849K vs 36K) | "lako" + Claude |
| 11.5x | "How to Book 3+ Meetings a Day Web Design Cold Calling" | outreach |
| 8.2x | "How to Sell AI Websites to Local Businesses in 2026" | AI + lokalni biznisi |

**Zajednička struktura:** svi nude jedan konkretan ishod ("prodaj sajt", "automatizuj montažu"), a ne opšti tutorijal.
**Rupa na srpskom:** balkanski kanali ove teme (Andrić Digital, Nauči Dizajn…) imaju medijane od nekoliko stotina do par hiljada
pregleda, a nijedan nije pokrio "sajt za lokalni biznis + outreach" onako kako ga ti već radiš u ovom repou
(`kafic/`, `outreach/`). To je tvoj ugao — ovo je zaključak iz uzorka, a ne garancija.

## 2. Video #1 (predlog)

**Radni naslov:** `Napravio sam sajt za kafić uz Claude` — thumbnail: `BEZ KODA` (title.py: 94/100; fali broj — dodaj pravi, npr. koliko sati je trajalo).

**Hook (popuni SVOJIM podacima, ne izmišljaj):**
1. "Kafići u Beogradu imaju Instagram, ali nemaju sajt. Ja sam [X] sati pravio jedan sa Claude-om — evo kako."
2. "Pitao sam [N] biznisa bez sajta da li ih zanima. Evo šta je [broj] njih odgovorilo."  ← samo ako stvarno imaš taj broj

> `hookscore.py` ocenjuje samo engleski (regexi, bez č/ć/š), pa srpske hookove ne može pošteno da oceni.
> Engleske verzije su dale 34–50 ("weak"). Zato hook proveri ovako: "da li u prvih 6 reči kažem TEBI/ti?" i "da li ima broj?".

**Struktura (prema skillu):** 0:00–0:15 hook → 0:15–0:45 "napravićemo ovo, evo gotovog" (bez intra) →
telo: (1) nađi biznis bez sajta, (2) generiši sajt (`kafic/index.html` kao demo na ekranu), (3) poruka vlasniku (`outreach/`) →
payoff: pokaži gotov sajt → jedan poziv: "pošalji mi svoj kafić".
Na svakom delu stavi `[NA EKRANU: …]`.

## 3. Šta fali da bi bilo gotovo

- `~/.claude/youtube/voice.md` — treba mi 2–3 tvoja videa ili transkripta; ovo ne mogu da izvedem iz koda.
- Pravi brojevi (sati, broj poruka, odgovori) i ime kanala.
- Dan objave iz tvoje analitike (ne pretpostavljam).
