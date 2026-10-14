// Social leads: pulls businesses from OpenStreetMap that list an Instagram,
// Facebook or TikTok profile but no real website, and drafts a short first DM
// for each. Nothing is sent — out/social.html has one card per business with
// buttons that open the profile and copy the message, so you send it yourself.
//
// Usage: npm run social               (Beograd)
//        npm run social -- Q55630     (another city, by Wikidata ID — Novi Sad)
//        npm run social -- --only=facebook   (only businesses with that network)

import fs from "node:fs";
import path from "node:path";

const args = process.argv.slice(2);
const CITY = args.find((a) => !a.startsWith("--")) || "Q3711"; // Wikidata ID for Beograd
const ONLY = (args.find((a) => a.startsWith("--only=")) || "").slice(7); // instagram | facebook | tiktok
const SUFFIX = ONLY ? "-" + ONLY : "";
const OUT_DIR = "out";
const OVERPASS = process.env.OVERPASS_URL || "https://overpass-api.de/api/interpreter";

const ME = {
  name: process.env.SENDER_NAME || "",
  studio: process.env.STUDIO_NAME || "Newmoda",
  portfolio: process.env.PORTFOLIO_URL || "",
};

const SITE_TAGS = ["website", "contact:website", "url", "brand:website"];
const SOCIAL_HOST = /facebook\.com|fb\.com|instagram\.com|tiktok\.com|linktr\.ee|wa\.me/i;

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
};

const query = `
[out:json][timeout:300];
area["wikidata"="${CITY}"]->.city;
(
  nwr(area.city)["name"][~"^(contact:)?(instagram|facebook|tiktok)$"~"."];
  nwr(area.city)["name"]["website"~"facebook|instagram|tiktok",i];
  nwr(area.city)["name"]["contact:website"~"facebook|instagram|tiktok",i];
);
out center tags;
`;

async function fetchBusinesses() {
  console.log("Preuzimam podatke iz OpenStreetMap-a (može da potraje 1–2 min)…");
  let res;
  // Overpass answers 429/504 when it is busy; wait and try again a few times.
  for (let attempt = 1; attempt <= 5; attempt++) {
    res = await fetch(OVERPASS, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded", "User-Agent": "newmoda-outreach" },
      body: "data=" + encodeURIComponent(query),
    });
    if (res.ok || ![429, 502, 503, 504].includes(res.status) || attempt === 5) break;
    console.log(`Server je zauzet (${res.status}), pokušavam ponovo za ${attempt * 20} s…`);
    await new Promise((r) => setTimeout(r, attempt * 20000));
  }
  if (!res.ok) throw new Error(`Overpass ${res.status}: ${(await res.text()).slice(0, 200)}`);
  return (await res.json()).elements;
}

// "@zrno.bg", "zrno.bg", "instagram.com/zrno.bg/" → "https://instagram.com/zrno.bg"
function profileUrl(network, value) {
  const v = String(value || "").split(";")[0].trim();
  if (!v) return "";
  if (/^https?:\/\//i.test(v)) return v.replace(/\/+$/, "");
  if (/\.(com|me)\//i.test(v)) return "https://" + v.replace(/\/+$/, "");
  return `https://${network}.com/${v.replace(/^@/, "")}`;
}

function socials(t) {
  const found = { instagram: "", facebook: "", tiktok: "" };
  for (const net of Object.keys(found)) {
    found[net] = profileUrl(net, t[`contact:${net}`] || t[net]);
  }
  for (const k of SITE_TAGS) {
    const v = t[k] || "";
    for (const net of Object.keys(found)) {
      if (!found[net] && new RegExp(net, "i").test(v)) found[net] = profileUrl(net, v);
    }
  }
  return found;
}

function toLead(el) {
  const t = el.tags;
  const type = t.amenity || t.shop || t.craft || t.office || t.tourism || t.healthcare || t.leisure || "";
  const s = socials(t);
  return {
    name: t.name,
    type,
    kind: KIND[type] || "biznis",
    address: [t["addr:street"], t["addr:housenumber"]].filter(Boolean).join(" "),
    phone: t.phone || t["contact:phone"] || "",
    email: (t.email || t["contact:email"] || "").split(/[;,\s]+/)[0],
    ...s,
    hasSite: SITE_TAGS.some((k) => t[k] && !SOCIAL_HOST.test(t[k])),
    osm: `https://www.openstreetmap.org/${el.type}/${el.id}`,
  };
}

// ---------- message ----------

// What a site does for each kind of business — the reason in the message.
const BENEFIT = {
  food: "gostima odmah pokazuju meni, radno vreme i kako da vas nađu",
  beauty: "klijentima pokazuju usluge i cene i omogućavaju zakazivanje online",
  health: "pacijentima pokazuju usluge, radno vreme i kako da zakažu pregled",
  shop: "kupcima pokazuju ponudu, radno vreme i adresu",
  stay: "donose direktne rezervacije, bez provizije Bookinga",
  trade: "dovode ljude koji baš sada traže nekoga kao vi",
  default: "donose nove klijente sa Google-a",
};
const GROUP = {
  kafić: "food", bar: "food", pab: "food", restoran: "food", pekara: "food", poslastičarnica: "food",
  salon: "beauty", teretana: "beauty", "plesni studio": "beauty", "sportski centar": "beauty", studio: "beauty",
  ordinacija: "health", ambulanta: "health",
  butik: "shop", radnja: "shop", zlatara: "shop", cvećara: "shop", "salon automobila": "shop",
  hotel: "stay", hostel: "stay", smeštaj: "stay",
  servis: "trade", firma: "trade", radionica: "trade", agencija: "trade", kancelarija: "trade",
};

// Several wordings per part, so messages sent one after another don't look
// identical (Facebook blocks repeated identical messages as spam).
const GREETING = ["Dobar dan,", "Pozdrav,", "Zdravo,", "Poštovani,"];
const OPENING = [
  "Vidim da {name} ima {page}, ali nemate sajt, a većina novih klijenata vas prvo traži na Google-u.",
  "Pregledam lokalne biznise i zapao mi je za oko {name}. Jedino što nedostaje je sajt, a tu vas ljudi danas najčešće prvo traže.",
  "{name} ima {page}, ali kad vas neko potraži na Google-u, ne pronađe sajt, a tu se danas odlučuje gde se ide.",
  "Javljam se kratko u vezi sa sajtom za {name}. Primećujem da ga još nemate, a većina ljudi prvo pogleda Google pre nego što se odluči.",
];
const OFFER_LINE = [
  "Pravim moderne sajtove koji {benefit}. Gotovi su za nekoliko dana, bez ikakvog posla sa vaše strane.",
  "Moji sajtovi {benefit}, a vi ne morate ništa tehnički da radite. Sve završavam za nekoliko dana.",
  "Radim sajtove za male lokalne biznise. Brzi su, lepo izgledaju na telefonu i {benefit}.",
];
const CLOSING = [
  "Mogu besplatno da vam napravim probnu verziju, pa odlučite kad je vidite. Da vam je pošaljem?",
  "Ako želite, besplatno vam pripremim probnu verziju, bez ikakve obaveze. Da li bi vas zanimalo?",
  "Rado vam napravim besplatan predlog kako bi vaš sajt izgledao. Javite mi ako želite da ga vidite.",
  "Prvu verziju pravim besplatno, pa tek ako vam se dopadne pričamo dalje. Da je napravim?",
];

function draft(lead) {
  const network = ONLY || (lead.instagram ? "instagram" : lead.facebook ? "facebook" : "tiktok");
  const page = network === "facebook" ? "odličnu Facebook stranicu" : `odličan ${network === "instagram" ? "Instagram" : "TikTok"} profil`;
  const fill = (t) => t.replace("{name}", lead.name).replace("{page}", page).replace("{benefit}", BENEFIT[GROUP[lead.kind] || "default"]);
  // Pick each part from the name, so the same business always gets the same message.
  const h = [...lead.name].reduce((sum, c) => sum + c.codePointAt(0), 0);
  return [
    GREETING[h % 4],
    fill(OPENING[Math.floor(h / 4) % 4]),
    fill(OFFER_LINE[Math.floor(h / 16) % 3]),
    ...(ME.portfolio ? [`Primer: ${ME.portfolio}`] : []),
    CLOSING[Math.floor(h / 48) % 4],
    [ME.name, ME.studio].filter(Boolean).join(", "),
  ].filter(Boolean).join("\n\n");
}

// ---------- output ----------

const csvCell = (s) => `"${String(s ?? "").replace(/"/g, '""')}"`;
const esc = (s) => String(s ?? "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);

function writeCsv(leads) {
  const cols = ["name", "kind", "address", "instagram", "facebook", "tiktok", "phone", "email", "osm", "message"];
  const text = [cols.join(","), ...leads.map((l) => cols.map((c) => csvCell(l[c])).join(","))].join("\n");
  fs.writeFileSync(path.join(OUT_DIR, `social-leads${SUFFIX}.csv`), "﻿" + text);
}

function writeHtml(leads) {
  const link = (url, label) => (url ? `<a class="btn" href="${esc(url)}" target="_blank" rel="noopener">${label}</a>` : "");
  const cards = leads.map((l, i) => `
  <article data-i="${i}">
    <header><h2>${esc(l.name)}</h2><span>${esc(l.kind)}${l.address ? " · " + esc(l.address) : ""}</span></header>
    <p class="meta">${[l.phone, l.email].filter(Boolean).map(esc).join(" · ")}${l.phone || l.email ? " · " : ""}<a href="${l.osm}" target="_blank">mapa</a></p>
    <textarea rows="9">${esc(l.message)}</textarea>
    <div class="row">
      ${link(l.instagram, "Instagram")}${link(l.facebook, "Facebook")}${link(l.tiktok, "TikTok")}
      <button class="copy">Kopiraj</button>
      <label><input type="checkbox" class="done"> poslato</label>
    </div>
  </article>`).join("");

  fs.writeFileSync(path.join(OUT_DIR, `social${SUFFIX}.html`), `<!doctype html>
<html lang="sr"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Poruke za društvene mreže</title>
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
  button, .btn { border:0; border-radius:8px; padding:8px 14px; font:inherit; cursor:pointer; background:var(--line); color:var(--ink); text-decoration:none; }
  .btn { background:var(--acc); color:#fff; } label { color:var(--mute); font-size:13px; margin-left:auto; }
</style>
<main>
  <h1>${leads.length} biznisa bez sajta, sa društvenim mrežama</h1>
  <p>Klikni „Kopiraj“, otvori profil i pošalji poruku ručno. Do 20–30 dnevno, da ti nalog ne bude ograničen.</p>
  ${cards}
</main>
<script>
  const ids = ${JSON.stringify(leads.map((l) => l.osm))};
  const key = "sent:" + location.pathname;
  let sent = {}; try { sent = JSON.parse(localStorage.getItem(key)) || {}; } catch {}
  document.querySelectorAll("article").forEach((card) => {
    const i = card.dataset.i, box = card.querySelector(".done");
    const mark = () => { card.classList.toggle("sent", box.checked); sent[ids[i]] = box.checked;
      try { localStorage.setItem(key, JSON.stringify(sent)); } catch {} };
    box.checked = !!sent[ids[i]]; card.classList.toggle("sent", box.checked);
    box.onchange = mark;
    card.querySelector(".copy").onclick = (e) => {
      navigator.clipboard.writeText(card.querySelector("textarea").value);
      e.target.textContent = "Kopirano"; setTimeout(() => (e.target.textContent = "Kopiraj"), 1200);
    };
  });
</script>
</html>`);
}

// ---------- main ----------

const elements = await fetchBusinesses();
const byProfile = new Map();
for (const el of elements) {
  const lead = toLead(el);
  const id = ONLY ? lead[ONLY] : lead.instagram || lead.facebook || lead.tiktok;
  if (!id || lead.hasSite || byProfile.has(id.toLowerCase())) continue;
  byProfile.set(id.toLowerCase(), { ...lead, message: draft(lead) });
}
const leads = [...byProfile.values()].sort((a, b) => a.kind.localeCompare(b.kind, "sr") || a.name.localeCompare(b.name, "sr"));

fs.mkdirSync(OUT_DIR, { recursive: true });
writeCsv(leads);
writeHtml(leads);
console.log(`Pronađeno ${elements.length} biznisa sa društvenim mrežama, ${leads.length} bez sajta.`);
console.log(`→ ${OUT_DIR}/social${SUFFIX}.html (pregled i slanje)\n→ ${OUT_DIR}/social-leads${SUFFIX}.csv (za Excel)`);
