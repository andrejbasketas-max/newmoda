# Lock in Animations — plan za 14 dana

**Kanal:** @andrejbjelanovic1049 · **Stil:** stickman · **Jezik:** engleski (jedan jezik, bez mešanja)
**Niša:** psihologija / mozak. Jedina tema koja ti se ponavlja u podacima (dva Shorta sa preko 1.100 pregleda).
**Pauziraj:** mačke/životinje 8 s klipove, dečje pesmice, srpske Shortove. Ništa ne brišeš, samo ne objavljuješ novo.

Cilj: 20 Shortova + 2 duga videa. Više od 2 Shorta dnevno ne objavljuješ.

## Dve serije

**A. „What happens to your brain when…“** — vreme u naslovu (hook sa konkretnim vremenom je u alatu ocenjen najbolje).
**B. „Your Stone Age brain“** — „zašto radiš X“ (objašnjenje običnog ponašanja).

| Hook (test hookscore, heuristika) | Ocena |
|---|---|
| What happens to your brain when you stop scrolling for 7 days? | 67 workable |
| What happens to your brain when you sleep 5 hours a night? | 56 workable |
| Why do you overthink at 3 a.m. when nothing is wrong? | 54 weak |
| Why does silence feel uncomfortable to your brain? | 39 weak |

Ocena je gruba i nije predviđanje. Vidi zaključak: broj/vreme u prvoj rečenici pomaže, a „Why…“ pitanja bez konkretnosti slabije prolaze.

## Raspored

| Dan | Šta objaviti |
|---|---|
| 1 | A1 + B1 |
| 2 | A2 |
| 3 | A3 + B2 |
| 4 | A4 |
| 5 | A5 + B3 |
| 6 | A6 |
| 7 | A7 + B4 + **DUGI 1** |
| 8 | A8 |
| 9 | A9 + B5 |
| 10 | A10 |
| 11 | A11 + B6 |
| 12 | A12 |
| 13 | B7 + B8 |
| 14 | **DUGI 2** |

### Serija A (12)
1. What happens to your brain when you stop scrolling for 7 days?
2. What happens to your brain when you sleep 5 hours a night for a week?
3. What happens to your brain when you stay awake for 24 hours?
4. What happens to your brain when you talk to no one for a week?
5. What happens to your brain when you take a cold shower every day?
6. What happens to your brain when you read 20 minutes a day for a month?
7. What happens to your brain when you quit sugar for 2 weeks?
8. What happens to your brain when you meditate 10 minutes a day?
9. What happens to your brain when you walk 30 minutes every day?
10. What happens to your brain when you hold a grudge for years?
11. What happens to your brain when you are bored for a whole day?
12. What happens to your brain when you learn something new every day?

### Serija B (8)
1. Why you can't stop checking your phone (your brain thinks it is hunting)
2. Why you overthink at 3 a.m.
3. Why you crave junk food
4. Why you remember embarrassing moments forever
5. Why silence feels uncomfortable
6. Why crowds make you anxious
7. Why you procrastinate when the deadline is far away
8. Why bad news pulls you in

### Dugi videi (8–9 min)
- **Dan 7:** What Happens to Your Brain When You Don't Sleep, Hour by Hour (pravi se od A2 + A3)
- **Dan 14:** Why You Can't Focus: Your Brain Is Still Living in the Stone Age (pravi se od serije B)

Dugi se skuplja iz materijala koji već snimiš za Shortove. Tvoj srpski dugi („Šta su praistorijski ljudi radili zimi?“) imao je ~33% zadržavanja, više od Shortova, pa dugi formati vrede probati.

## Šablon jednog Shorta (25–35 s, stickman)

1. **0–3 s hook:** konkretno vreme u prvoj rečenici, obraćanje sa „you“.
2. **3–25 s:** 3 koraka (npr. dan 1 → dan 3 → dan 7), jedna slika po rečenici.
3. **Zadnja rečenica:** vraća se na prvu (loop).
4. **Tekst na ekranu:** druge reči nego što se govori.
5. **Naslov:** cela rečenica. Ne samo hashtagovi. Najviše 3 hashtaga u opisu.
6. **Skripta:** oko 60–85 reči (150 reči/min).
7. Svaka tvrdnja mora da ima izvor koji možeš da pokažeš. Ništa ne izmišljaš. Ne dajemo medicinske savete, samo objašnjavamo istraživanja.
8. **Jedan upload po videu**, nema duplikata (prošli put: dva ista Shorta u 20 min).

## Merenje

- Dan 7 i dan 14: uporedi **medijanu pregleda** i **prosečan % pregledanog** po seriji (YouTube Studio → Analytics).
- Tvoja trenutna mera uspeha su ~1.200 pregleda po Shortu.
- Ako jedna serija ima bolju medijanu, drugoj daješ upola manje videa.
- Ako ni jedna ne dostiže tvoj raniji nivo, problem je u hookovima, ne u temi. Tada vraćamo analizu.

## Šta mi još treba
- Dan i sat kad ti je publika aktivna (Studio → Analytics → Audience), pa objavljuješ tad.
- Kad me pozoveš, pišem skriptu za svaki Short pomoću `/yt-script`.


## Ažuriranje (21. okt)
- Glas je sada lokalni (Piper), pa više ne troši VidIQ kredite. Pipeline: `youtube/stickman/make_short.py`.
- A2 je promenjen na „6 hours a night“ da odgovara istraživanju (Van Dongen i sar., 2003).
- Dnevni raspored i pravila su u `youtube/DAILY.md`. A1 i A2 su gotovi.
