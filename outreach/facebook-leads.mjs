// Facebook leads: pulls businesses from OpenStreetMap that link a Facebook page
// but have no website, and drafts a different first message for each. Nothing
// is sent: out/facebook.html has one card per business with an "Otvori Messenger"
// button, so you read the message, paste it and send it yourself.
//
// Usage: npm run facebook               (Beograd)
//        npm run facebook -- Q55630     (another city, by Wikidata ID: Novi Sad)
//        npm run facebook -- Q3711 data.json   (use a saved Overpass response)

import fs from "node:fs";
import path from "node:path";

const CITY = process.argv[2] || "Q3711"; // Wikidata ID for Beograd
const CACHE = process.argv[3]; // optional saved Overpass JSON
const OUT_DIR = "out";
const OVERPASS = process.env.OVERPASS_URL || "https://overpass-api.de/api/interpreter";

const ME = {
  name: process.env.SENDER_NAME || "",
  studio: process.env.STUDIO_NAME || "Newmoda",
  portfolio: process.env.PORTFOLIO_URL || "",
  phone: process.env.SENDER_PHONE || "",
};

const SITE_TAGS = ["website", "contact:website", "url", "brand:website"];
const NOT_A_SITE = /facebook|fb\.com|instagram|linktr\.ee|wa\.me|tiktok/i;

// OSM tag value → word used in the message ("vaš ___").
const KIND = {
  cafe: "kafić", bar: "bar", pub: "pab", restaurant: "restoran", fast_food: "restoran",
  bakery: "pekara", pastry: "poslastičarnica", confectionery: "poslastičarnica",
  hairdresser: "salon", beauty: "salon", cosmetics: "salon", massage: "salon",
  dentist: "ordinacija", doctors: "ordinacija", clinic: "ordinacija", veterinary: "ambulanta",
  car_repair: "servis", car: "salon automobila", bicycle: "radnja", electronics: "radnja",
  clothes: "butik", shoes: "radnja", jewelry: "zlatara", florist: "cvećara",
  fitness_centre: "teretana", sports_centre: "sportski centar", dance: "plesni studio",
  hotel: "hotel", hostel: "hostel", guest_house: "smeštaj", apartment: "smeštaj",
  lawyer: "kancelarija", accountant: "agencija", estate_agent: "agencija",
  travel_agency: "agencija", photographer: "studio", tattoo: "studio",
  carpenter: "radionica", electrician: "firma", plumber: "firma", painter: "firma",
  nightclub: "klub", biergarten: "bašta", hookah_lounge: "lounge bar", ice_cream: "poslastičarnica",
  deli: "radnja", wine: "vinoteka", pasta: "radnja", convenience: "radnja", gift: "radnja",
  fashion_accessories: "butik", leather: "radnja", fabric: "radnja", tailor: "krojačka radnja",
  books: "knjižara", stationery: "knjižara", computer: "radnja", mobile_phone: "radnja",
  car_parts: "radnja", flooring: "salon podova", glaziery: "radionica", optician: "optika",
  perfumery: "parfimerija", dancing_school: "plesni studio", language_school: "škola",
  driving_school: "auto-škola", gallery: "galerija", arts_centre: "galerija", atelier: "atelje",
  speech_therapist: "ordinacija", alternative: "ordinacija", animal_boarding: "pansion za ljubimce",
  caterer: "ketering", carpet_cleaner: "firma",
};

// Serbian Cyrillic → Latin, so names and streets match the Latin message.
const LAT = { а:"a",б:"b",в:"v",г:"g",д:"d",ђ:"đ",е:"e",ж:"ž",з:"z",и:"i",ј:"j",к:"k",л:"l",љ:"lj",м:"m",
  н:"n",њ:"nj",о:"o",п:"p",р:"r",с:"s",т:"t",ћ:"ć",у:"u",ф:"f",х:"h",ц:"c",ч:"č",џ:"dž",ш:"š" };
const latin = (s) => s.replace(/[\u0400-\u04FF]/g, (c) => {
  const l = LAT[c.toLowerCase()];
  return l === undefined ? c : c === c.toLowerCase() ? l : l[0].toUpperCase() + l.slice(1);
});

// What a site would show for each kind of business, used in the pitch.
const SHOWS = {
  kafić: "meni, radno vreme i lokaciju", bar: "meni, događaje i lokaciju", pab: "meni, događaje i lokaciju",
  restoran: "meni sa cenama, radno vreme i dugme za rezervaciju", pekara: "ponudu, radno vreme i lokaciju",
  poslastičarnica: "torte i kolače sa slikama, cene i poručivanje", salon: "usluge sa cenama i zakazivanje termina",
  ordinacija: "usluge, cene i zakazivanje pregleda", ambulanta: "usluge, radno vreme i hitan kontakt",
  servis: "usluge, cene i dugme za poziv", butik: "novu kolekciju sa slikama i lokaciju",
  zlatara: "nakit sa slikama i lokaciju", cvećara: "bukete sa cenama i poručivanje",
  teretana: "članarine, raspored treninga i lokaciju", hotel: "sobe sa slikama, cene i rezervaciju",
  smeštaj: "slike smeštaja, cene i direktnu rezervaciju bez provizije", studio: "radove, cene i zakazivanje",
  agencija: "usluge i kontakt formu", radionica: "radove sa slikama i kontakt", firma: "usluge i dugme za poziv",
};

const query = `
[out:json][timeout:300];
area["wikidata"="${CITY}"]->.city;
(
  nwr(area.city)["name"]["contact:facebook"];
  nwr(area.city)["name"]["facebook"];
);
out center tags;
`;

async function fetchBusinesses() {
  if (CACHE) return JSON.parse(fs.readFileSync(CACHE, "utf8")).elements;
  console.log("Preuzimam podatke iz OpenStreetMap-a (može da potraje 1–2 min)…");
  const res = await fetch(OVERPASS, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded", "User-Agent": "newmoda-outreach" },
    body: "data=" + encodeURIComponent(query),
  });
  if (!res.ok) throw new Error(`Overpass ${res.status}: ${(await res.text()).slice(0, 200)}`);
  return (await res.json()).elements;
}

// "https://www.facebook.com/zrno.kafic/", "fb.com/zrno.kafic", "zrno.kafic",
// "facebook.com/profile.php?id=123" → page id or username, or "" if unusable.
function fbPage(raw) {
  const s = String(raw || "").split(/[;\s]+/)[0].trim();
  if (!s) return "";
  const id = s.match(/[?&]id=(\d+)/);
  if (id) return id[1];
  const m = s.match(/^(?:https?:\/\/)?(?:[a-z]+\.)?(?:facebook|fb)\.com\/(?:pg\/|pages\/[^/]+\/)?([^/?#]+)/i);
  const page = m ? m[1] : /^[\w.-]+$/.test(s) ? s : "";
  return /^(groups|events|sharer|share|people|watch|photo\.php)$/i.test(page) ? "" : page;
}

function toLead(el) {
  const t = el.tags;
  const type = t.amenity || t.shop || t.craft || t.office || t.tourism || t.healthcare || t.leisure || "";
  const kind = KIND[type] || "biznis";
  const page = fbPage(t["contact:facebook"] || t.facebook);
  return {
    name: latin(t.name),
    page,
    facebook: page ? `https://www.facebook.com/${page}` : "",
    messenger: page ? `https://m.me/${page}` : "",
    type,
    kind,
    shows: SHOWS[kind] || "šta radite, cene i kontakt",
    street: latin(t["addr:street"] || ""),
    address: latin([t["addr:street"], t["addr:housenumber"]].filter(Boolean).join(" ")),
    phone: t.phone || t["contact:phone"] || "",
    // Chains (banks, fuel stations, Yettel…) and pages named after a domain already have a site.
    hasSite: SITE_TAGS.some((k) => t[k] && !NOT_A_SITE.test(t[k])) ||
      !!(t.brand || t["brand:wikidata"]) || /\.(rs|com|net|org|co)$/i.test(page),
    osm: `https://www.openstreetmap.org/${el.type}/${el.id}`,
  };
}

// ---------- message ----------
// Each message is put together from several interchangeable parts, picked by a
// hash of the business name, and filled with its name, street and kind of work.
// So every business gets its own wording, and the same business always gets the
// same message on a re-run.

function hash(s) {
  let h = 2166136261;
  for (const c of s) h = Math.imul(h ^ c.codePointAt(0), 16777619);
  return h >>> 0;
}

const GREETINGS = ["Dobar dan", "Pozdrav", "Zdravo", "Dobar dan, ekipo"];

const OPENERS = [
  (l) => `vidim da ${l.name} ima Facebook stranicu, ali nema svoj sajt.`,
  (l) => `tražim${l.street ? " biznise u ulici " + l.street : " lokalne biznise"} kojima bi koristio sajt, i ${l.name} je među prvima na listi.`,
  (l) => `gledam vašu Facebook stranicu i sviđa mi se šta radite, ali na Google-u nema sajta za ${l.name}.`,
  (l) => `kratko pitanje: da li ${l.name} ima sajt? Na Facebook-u ga ne vidim.`,
  (l) => `pišem vam jer ${l.name} ima lepu Facebook stranicu, ali ne i sajt.`,
];

const WHYS = [
  (l) => `Ljudi koji traže ${l.kind === "biznis" ? "ono što radite" : l.kind} preko Google-a ili Mapa najčešće kliknu na prvi rezultat koji ima sajt.`,
  () => "Mnogo ljudi nema Facebook ili ne želi da se prijavljuje samo da bi videli cene i radno vreme.",
  () => "Facebook objave brzo potonu, a sajt je mesto gde je sve važno uvek na jednom mestu.",
  () => "Sajt deluje ozbiljnije i ljudi lakše odluče da vas posete, pozovu ili zakažu.",
];

const OFFERS = [
  (l) => `Pravim jednostavne sajtove za male biznise, prilagođene telefonu, na kojima ljudi odmah vide ${l.shows}.`,
  (l) => `Bavim se izradom sajtova${ME.studio ? ` (${ME.studio})` : ""}. Za vas mogu da napravim brz sajt na kom ljudi vide ${l.shows}.`,
  (l) => `Mogu da vam napravim moderan sajt na kom ljudi lako nađu ${l.shows}, i to za par dana, bez da vi išta tehnički radite.`,
];

const ASKS = [
  (l) => `Ako želite, besplatno ću napraviti probnu početnu stranu za ${l.name}, pa vidite da li vam se dopada.`,
  () => "Da li biste hteli da vam pošaljem predlog kako bi izgledao? Bez ikakve obaveze.",
  () => "Ako vas zanima, javite se i poslaću cenu i par primera.",
  (l) => `Mogu da vam pošaljem kratak predlog za ${l.name}, pa vi odlučite.`,
];

const OUTS = [
  "Ako vas ne zanima, samo napišite i neću vam više pisati.",
  "Ako niste zainteresovani, slobodno recite, neću vas više uznemiravati.",
  "Ako vam ovo ne treba, nema problema, samo javite i neću ponovo pisati.",
];

const SIGNOFFS = ["Pozdrav", "Hvala i lep dan", "Srdačan pozdrav", "Sve najbolje"];

function draft(lead) {
  const pick = (arr, part) => arr[hash(lead.name + "|" + part) % arr.length];
  const lines = [
    `${pick(GREETINGS, "greetings")},`,
    "",
    pick(OPENERS, "openers")(lead) + " " + pick(WHYS, "whys")(lead),
    "",
    pick(OFFERS, "offers")(lead),
    ...(ME.portfolio ? [`Primer mog rada: ${ME.portfolio}`] : []),
    "",
    pick(ASKS, "asks")(lead),
    pick(OUTS, "outs"),
    "",
    `${pick(SIGNOFFS, "signoffs")},`,
    ...[ME.name, ME.phone].filter(Boolean),
  ];
  return { message: lines.join("\n") };
}

// ---------- output ----------

const csvCell = (s) => `"${String(s ?? "").replace(/"/g, '""')}"`;
const esc = (s) => String(s ?? "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);

function writeCsv(leads) {
  const cols = ["name", "kind", "address", "phone", "facebook", "messenger", "osm", "message"];
  const text = [cols.join(","), ...leads.map((l) => cols.map((c) => csvCell(l[c])).join(","))].join("\n");
  fs.writeFileSync(path.join(OUT_DIR, "facebook-leads.csv"), "﻿" + text);
}

function writeHtml(leads) {
  const cards = leads.map((l, i) => `
  <article data-i="${i}">
    <header><h2>${esc(l.name)}</h2><span>${esc(l.kind)}${l.address ? " · " + esc(l.address) : ""}</span></header>
    <p class="meta"><a href="${esc(l.facebook)}" target="_blank">Facebook stranica</a>${l.phone ? " · " + esc(l.phone) : ""} · <a href="${l.osm}" target="_blank">mapa</a></p>
    <textarea rows="12">${esc(l.message)}</textarea>
    <div class="row">
      <button class="send">Kopiraj i otvori Messenger</button>
      <label><input type="checkbox" class="done"> poslato</label>
    </div>
  </article>`).join("");

  fs.writeFileSync(path.join(OUT_DIR, "facebook.html"), `<!doctype html>
<html lang="sr"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Facebook poruke</title>
<style>
  :root { --bg:#f6f5f2; --card:#fff; --ink:#1b1b1b; --mute:#6b6b6b; --line:#e2e0da; --acc:#1f5eff; }
  @media (prefers-color-scheme: dark) { :root { --bg:#141414; --card:#1e1e1e; --ink:#eee; --mute:#9a9a9a; --line:#333; --acc:#6b93ff; } }
  body { margin:0; background:var(--bg); color:var(--ink); font:15px/1.5 system-ui,sans-serif; }
  main { max-width:760px; margin:0 auto; padding:24px 16px 80px; }
  h1 { font-size:22px; margin:0 0 4px; } main > p { color:var(--mute); margin:0 0 20px; }
  article { background:var(--card); border:1px solid var(--line); border-radius:12px; padding:16px; margin-bottom:14px; }
  article.sent { opacity:.45; }
  header { display:flex; flex-wrap:wrap; gap:4px 10px; align-items:baseline; }
  h2 { font-size:17px; margin:0; } header span, .meta { color:var(--mute); font-size:13px; }
  .meta { margin:4px 0 10px; } a { color:var(--acc); }
  textarea { width:100%; box-sizing:border-box; background:transparent; color:inherit; border:1px solid var(--line);
    border-radius:8px; padding:8px 10px; font:inherit; margin-bottom:8px; resize:vertical; }
  .row { display:flex; gap:10px; align-items:center; flex-wrap:wrap; }
  button { border:0; border-radius:8px; padding:8px 14px; font:inherit; cursor:pointer; background:var(--acc); color:#fff; }
  label { color:var(--mute); font-size:13px; margin-left:auto; }
</style>
<main>
  <h1>${leads.length} biznisa sa Facebook stranicom, bez sajta</h1>
  <p>Proveri stranicu (možda su u međuvremenu napravili sajt), prilagodi poruku, pa klikni dugme: poruka se kopira
  i otvara se Messenger, gde je nalepiš i pošalješ. Šalji ručno, najviše 20–30 dnevno, da ti Facebook ne blokira nalog.</p>
  ${cards}
</main>
<script>
  const leads = ${JSON.stringify(leads.map((l) => l.messenger))};
  const key = "sent:" + location.pathname;
  let sent = {}; try { sent = JSON.parse(localStorage.getItem(key)) || {}; } catch {}
  document.querySelectorAll("article").forEach((card) => {
    const i = card.dataset.i, box = card.querySelector(".done");
    const mark = () => { card.classList.toggle("sent", box.checked); sent[leads[i]] = box.checked;
      try { localStorage.setItem(key, JSON.stringify(sent)); } catch {} };
    box.checked = !!sent[leads[i]]; card.classList.toggle("sent", box.checked);
    box.onchange = mark;
    card.querySelector(".send").onclick = async (e) => {
      try { await navigator.clipboard.writeText(card.querySelector("textarea").value); } catch {}
      e.target.textContent = "Kopirano, nalepi u Messenger";
      setTimeout(() => (e.target.textContent = "Kopiraj i otvori Messenger"), 2500);
      window.open(leads[i], "_blank");
      box.checked = true; mark();
    };
  });
</script>
</html>`);
}

// ---------- main ----------

const elements = await fetchBusinesses();
const byPage = new Map();
for (const el of elements) {
  const lead = toLead(el);
  if (!lead.page || lead.hasSite || byPage.has(lead.page.toLowerCase())) continue;
  byPage.set(lead.page.toLowerCase(), { ...lead, ...draft(lead) });
}
const leads = [...byPage.values()].sort((a, b) => a.kind.localeCompare(b.kind, "sr") || a.name.localeCompare(b.name, "sr"));

fs.mkdirSync(OUT_DIR, { recursive: true });
writeCsv(leads);
writeHtml(leads);
console.log(`Pronađeno ${elements.length} biznisa sa Facebook-om, ${leads.length} bez sajta.`);
console.log(`→ ${OUT_DIR}/facebook.html (pregled i slanje)\n→ ${OUT_DIR}/facebook-leads.csv (za Excel)`);
