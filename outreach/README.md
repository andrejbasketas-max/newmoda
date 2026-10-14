# Outreach agent — Instagram profili bez sajta

Agent prolazi kroz listu Instagram profila, izbacuje one koji već imaju pravi sajt,
i za ostale (bez sajta ili samo sa Linktree / WhatsApp linkom) Claude piše personalizovanu
prvu poruku. Rezultat je `out/review.html`: kartica po profilu sa porukom koju možeš da izmeniš,
dugmetom **Kopiraj** i dugmetom **Otvori DM**, pa poruku šalješ sam.

> Poruke se namerno **ne šalju automatski**. Instagram zabranjuje botove koji šalju DM porukama
> nepoznatim ljudima, a zvanični API ne dozvoljava prvu poruku nekome ko ti nije pisao.
> Automatsko slanje brzo dovodi do blokade naloga. Ručno slanje uz pripremljen tekst traje oko 10 sekundi po poruci.

## Pokretanje

```bash
cd outreach
npm install
cp .env.example .env              # upiši ANTHROPIC_API_KEY i podatke o sebi
cp leads.example.csv leads.csv    # dodaj profile
npm start
```

Otvori `out/review.html` u browseru. `out/leads.csv` sadrži sve proverene profile.
Ponovno pokretanje preskače profile koje je već video (`out/seen.json`). `npm start -- --redo` ih proverava ponovo.

## Odakle profili (`leads.csv`)

Kolone: `username,website,bio,note`. Dobri izvori:
- Google: `site:instagram.com "kafić" "Beograd"`, `site:instagram.com frizerski salon Novi Sad`
- Instagram pretraga po lokaciji ili hešteg (#beogradkafic, #nailsbeograd…)
- Google Maps: biznisi bez linka ka sajtu, a sa Instagramom

**Bez Meta tokena** sam prepiši link iz bioa u kolonu `website`. Ostavi je praznu ako linka nema.
Bio dodaj za bolju poruku.

**Sa Meta tokenom** dovoljna je kolona `username`. Agent preko zvaničnog
[Business Discovery API-ja](https://developers.facebook.com/docs/instagram-platform/instagram-graph-api/reference/ig-user/business_discovery)
sam povlači bio, sajt, broj pratilaca i poslednje objave. Potrebno je:
1. Tvoj Instagram nalog prebačen u Business/Creator i povezan sa Facebook stranicom.
2. Meta app na developers.facebook.com sa dozvolama `instagram_basic` i `pages_show_list`.
3. `IG_USER_ID` (ID tvog IG business naloga) i `IG_ACCESS_TOKEN` (long-lived token) u `.env`.

API vidi samo business i creator naloge. Lične naloge agent označi „proveri ručno“.

## Podešavanje poruka

U `.env`: `STUDIO_NAME`, `OFFER` (šta nudiš), `PORTFOLIO_URL` (npr. link ka demo sajtu kafića iz `../kafic/`),
`SIGNATURE`. Ton i pravila poruke menjaš u `SYSTEM` promptu u `agent.mjs`.
Lista domena koji se ne računaju kao sajt je `NOT_A_SITE`.

Model: `claude-opus-5-5`, sa uključenim server-side fallbackom (`fallbacks: "default"`) za slučaj odbijenog zahteva.

## Mejlovi firmama bez sajta (`email-leads.mjs`)

Iz OpenStreetMap-a izvlači sve biznise u Beogradu koji imaju javni mejl, a nemaju sajt
(Facebook/Instagram link se ne računa kao sajt), i za svaki napiše poruku. Ne treba API ključ.

```bash
npm run emails               # Beograd
npm run emails -- Q55630     # drugi grad po Wikidata ID-ju (Q55630 = Novi Sad)
```

- `out/emails.html`: kartica po firmi, poruka koju možeš da izmeniš, dugme **Otvori mejl** (otvara
  tvoj mejl program sa popunjenim primaocem, naslovom i tekstom) i oznaka „poslato“.
- `out/email-leads.csv`: ista lista za Excel ili mail-merge.

Ime, telefon, `STUDIO_NAME` i `PORTFOLIO_URL` iz `.env` ulaze u potpis i poruku.
OSM ne pokriva sve firme. Za više firmi pretraži Google Maps po kategoriji i kraju i ručno dodaj one bez sajta.

Mejlove šalji ručno, 20–30 dnevno, sa svog pravog mejla. Masovno slanje ti brzo pošalje adresu u spam.
Poruka već sadrži rečenicu „ako vas ne zanima, neću vam više pisati“. Ispoštuj je.
