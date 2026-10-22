# Dnevni zadatak — 14 dana (22. okt – 4. nov 2026)

Svakog dana napravi video(e) za taj dan, pa pošalji korisniku ovde (SendUserFile): `.mp4`, thumbnail `.png` i tekst
za upload (naslov, opis, tagovi). **Ne objavljuj na YouTube** — korisnik ovo traži samo kao pravljenje videa i
thumbnaila (YouTube upload nije dostupan: dnevna kvota Composio-a).

## VAŽNO: glas
VidIQ krediti su potrošeni (ostalo 5; jedan glas košta 14+). Obnavljaju se **10. novembra**. Do tada koristi **lokalni glas** (podrazumevan u `make_short.py`) i ne zovi `vidiq_voiceover_generate`. B4 je urađen umesto B1/B4 iz tabele (B1 i B4 gotovi).

## Priprema (nova sesija/kontejner)
`bash youtube/stickman/setup.sh` (lokalni glas Piper, besplatan). Zatim `python3 youtube/stickman/make_short.py youtube/specs/<ID>.json`.
Izlaz: `youtube/out/<ID>.mp4`, `<ID>-thumb-16x9.png`, `<ID>-upload.md`. Primer spec-a: `youtube/specs/A2.json`.

## Raspored (dan 1 = 22. oktobar; izračunaj dan iz današnjeg datuma)
| Dan | Datum | Napravi |
|---|---|---|
| 1 | 22.10 | B1 (A3 je već gotov) |
| 2 | 23.10 | A4 |
| 3 | 24.10 | B2, A5 |
| 4 | 25.10 | A6 |
| 5 | 26.10 | B3, A7 |
| 6 | 27.10 | A8 |
| 7 | 28.10 | B4 + DUGI 1 (sleep, 8–9 min) |
| 8 | 29.10 | A9, A10 |
| 9 | 30.10 | B5, A11 |
| 10 | 31.10 | A12 |
| 11 | 1.11 | B6 |
| 12 | 2.11 | B7 |
| 13 | 3.11 | B8 |
| 14 | 4.11 | DUGI 2 (Stone Age brain) + onemogući zakazani zadatak |

Teme su u `youtube/plan-14-dana.md` (serija A „What happens to your brain if you…“, serija B „Why you…“).
A1, A2 i A3 su već gotovi. Za bolji glas: VidIQ voiceover (Brian) pa `make_short.py spec.json glas.mp3`; besplatan lokalni glas je podrazumevan.

## Thumbnail
`make_short.py` sada pravi **oba**: `<ID>-thumb-9x16.png` (1080×1920, za Shorts, šalji ovaj) i `<ID>-thumb-16x9.png` (za dugi video).

## Pravila za svaki video
1. **Svaka činjenica mora imati izvor** koji znaš (autor, godina, časopis) i koji staje u opis. Ako nisi siguran u
   istraživanje, zameni ugao ili temu, ne izmišljaj. Nema brojeva koje ne možeš da potkrepiš.
2. Hook u prvoj rečenici sa konkretnim vremenom/brojem, „you“ u prvih 6 reči. Provjeri `python3 .claude/skills/yt-script/hookscore.py --hook "..."`.
3. Short 25–35 s (60–85 reči). Naslov ≤ 60 znakova (`.claude/skills/yt-package/title.py`), thumbnail tekst različit od naslova, max 3 reči.
4. Struktura: hook → 3 koraka → rečenica koja se vraća na hook. Bez medicinskih saveta.
5. Pogledaj kadrove pre slanja (ffmpeg izvuci 5–6 frejmova): nema isečenog teksta, preklapanja, praznih scena.
6. Dugi video: ~8–9 min, ~1300 reči, 25+ scena; render radi u pozadini (nekoliko minuta).
7. U poruci korisniku (srpski): naslov, opis sa izvorom, šta je u videu, i jedna rečenica o tome šta ne valja ako ima.
8. Commit i push `youtube/specs` i `youtube/out` na granu `claude/modest-lovelace-co5kdg`.
