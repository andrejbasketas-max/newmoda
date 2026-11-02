# Gold Tycoon (Roblox)

Tycoon igra. Celu mapu (placevi, traka, dropperi, kolektor, dugme) pravi kod, pa ne treba ništa da modeluješ u Studiju.

## Kako igra radi
1. Svaki igrač automatski dobija svoj plac (staje 8 igrača).
2. Staneš na **žuto dugme** i kupiš sledeću nadogradnju: Dropper 1 → Dropper 2 → Ruda x2 → …
3. Dropperi spuštaju rudu na traku. Kad stigne do zelenog kolektora, dobijaš novac.
4. Novac i nadogradnje se čuvaju kad izađeš (DataStore).

## Postavljanje u Roblox Studio (bez dodatnih programa)
1. Otvori Roblox Studio → **New** → **Baseplate**.
2. U **Explorer** prozoru desni klik na **ServerScriptService** → **Insert Object** → **Script**. Preimenuj ga u `Tycoon`.
   Obriši sav kod u njemu i nalepi ceo sadržaj fajla `src/server/Tycoon.server.lua`.
3. Desni klik na **StarterPlayer → StarterPlayerScripts** → **Insert Object** → **LocalScript**. Preimenuj ga u `Hud`.
   Obriši sav kod i nalepi sadržaj fajla `src/client/Hud.client.lua`.
4. Pritisni **Play** da probaš. Dugme je ispred tebe, stani na njega kad imaš dovoljno novca.

(Opciono: ako koristiš Rojo, pokreni `rojo serve` u folderu `roblox/` i poveži se iz Studija. Projekat je u `default.project.json`.)

## Objavljivanje
1. **File → Publish to Roblox** i daj igri ime.
2. **Home → Game Settings → Security** → uključi **Enable Studio Access to API Services**. To je potrebno da bi radilo čuvanje napretka.
3. **Game Settings → Players** → postavi **Maximum Players** na 8 (ili manje ako smanjiš `MAX_PLOTS`).
4. **Game Settings → Permissions** → postavi na Public kad si spreman, pa **Save to Roblox**.

## Podešavanja
Sve je na vrhu `Tycoon.server.lua`: početni novac, brzina trake, vrednost rude i spisak nadogradnji (`ITEMS`). Da dodaš novu nadogradnju, dodaj red u `ITEMS`.

## Napomena
Kod nisam mogao da pokrenem u Roblox Studiju (nema ga u ovom okruženju), pa ga prvi put isprobaj u Play modu. Ako se pojavi greška, pošalji mi poruku iz **Output** prozora.
