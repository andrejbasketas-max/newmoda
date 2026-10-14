// Email leads: pulls Belgrade businesses from OpenStreetMap that list a public
// email but no website, and drafts a first email for each. Nothing is sent —
// out/emails.html has one card per business with an "Otvori mejl" button that
// opens your mail app with the message filled in, so you read it and send it.
//
// Usage: npm run emails               (Beograd)
//        npm run emails -- Q55630     (another city, by Wikidata ID — Novi Sad)

import fs from "node:fs";
import path from "node:path";

const CITY = process.argv[2] || "Q3711"; // Wikidata ID for Beograd
const OUT_DIR = "out";
const OVERPASS = process.env.OVERPASS_URL || "https://overpass-api.de/api/interpreter";

const ME = {
  name: process.env.SENDER_NAME || "",
  studio: process.env.STUDIO_NAME || "Newmoda",
  portfolio: process.env.PORTFOLIO_URL || "",
  phone: process.env.SENDER_PHONE || "",
};

// Tags that mean the business already has a site (Facebook/Instagram don't count).
const SITE_TAGS = ["website", "contact:website", "url", "brand:website"];

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
nwr(area.city)["name"]["email"];
out center tags;
nwr(area.city)["name"]["contact:email"];
out center tags;
`;

async function fetchBusinesses() {
  console.log("Preuzimam podatke iz OpenStreetMap-a (može da potraje 1–2 min)…");
  const res = await fetch(OVERPASS, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded", "User-Agent": "newmoda-outreach" },
    body: "data=" + encodeURIComponent(query),
  });
  if (!res.ok) throw new Error(`Overpass ${res.status}: ${(await res.text()).slice(0, 200)}`);
  return (await res.json()).elements;
}

function toLead(el) {
  const t = el.tags;
  const email = (t.email || t["contact:email"] || "").split(/[;,\s]+/)[0].toLowerCase();
  const type = t.amenity || t.shop || t.craft || t.office || t.tourism || t.healthcare || t.leisure || "";
  const street = [t["addr:street"], t["addr:housenumber"]].filter(Boolean).join(" ");
  return {
    name: t.name,
    email,
    type,
    kind: KIND[type] || "biznis",
    address: street,
    phone: t.phone || t["contact:phone"] || "",
    social: t["contact:instagram"] || t["contact:facebook"] || t.facebook || "",
    hasSite: SITE_TAGS.some((k) => t[k] && !/facebook|instagram/i.test(t[k])),
    osm: `https://www.openstreetmap.org/${el.type}/${el.id}`,
  };
}

// ---------- message ----------

function draft(lead) {
  const subject = `Sajt za ${lead.name}`;
  const lines = [
    "Dobar dan,",
    "",
    `pišem vam jer vidim da ${lead.name} nema svoj sajt. Kada neko na Google-u traži ` +
      `${lead.kind === "biznis" ? "ono što radite" : lead.kind} u ${lead.address ? "vašem kraju" : "Beogradu"}, ` +
      "biznisi sa sajtom se prvi pojavljuju i deluju ozbiljnije, a ostali ostaju neprimećeni.",
    "",
    `Ja ${ME.studio ? `(${ME.studio}) ` : ""}pravim jednostavne, moderne sajtove za male biznise: ` +
      "prilagođeni telefonu, sa radnim vremenom, cenovnikom ili menijem, mapom i dugmetom za poziv. " +
      "Gotov je za par dana i ne morate ništa tehnički da znate.",
    ...(ME.portfolio ? ["", `Primer jednog mog sajta: ${ME.portfolio}`] : []),
    "",
    `Ako vas zanima, mogu besplatno da napravim probnu početnu stranu za ${lead.name}, ` +
      "pa da vidite kako bi izgledalo, bez ikakve obaveze.",
    "",
    "Ako vas ne zanima, samo mi odgovorite i neću vam više pisati.",
    "",
    "Pozdrav,",
    ...[ME.name, ME.phone].filter(Boolean),
  ];
  return { subject, body: lines.join("\n") };
}

// ---------- output ----------

const csvCell = (s) => `"${String(s ?? "").replace(/"/g, '""')}"`;
const esc = (s) => String(s ?? "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);

function writeCsv(leads) {
  const cols = ["name", "email", "kind", "address", "phone", "social", "osm", "subject", "body"];
  const text = [cols.join(","), ...leads.map((l) => cols.map((c) => csvCell(l[c])).join(","))].join("\n");
  fs.writeFileSync(path.join(OUT_DIR, "email-leads.csv"), "﻿" + text);
}

function writeHtml(leads) {
  const cards = leads.map((l, i) => `
  <article data-i="${i}">
    <header><h2>${esc(l.name)}</h2><span>${esc(l.kind)}${l.address ? " · " + esc(l.address) : ""}</span></header>
    <p class="meta"><b>${esc(l.email)}</b>${l.phone ? " · " + esc(l.phone) : ""} · <a href="${l.osm}" target="_blank">mapa</a></p>
    <input class="subject" value="${esc(l.subject)}">
    <textarea rows="14">${esc(l.body)}</textarea>
    <div class="row">
      <button class="send">Otvori mejl</button>
      <button class="copy">Kopiraj</button>
      <label><input type="checkbox" class="done"> poslato</label>
    </div>
  </article>`).join("");

  fs.writeFileSync(path.join(OUT_DIR, "emails.html"), `<!doctype html>
<html lang="sr"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Mejlovi za slanje</title>
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
  .meta { margin:4px 0 10px; } .meta b { color:var(--ink); font-weight:600; } a { color:var(--acc); }
  input.subject, textarea { width:100%; box-sizing:border-box; background:transparent; color:inherit; border:1px solid var(--line);
    border-radius:8px; padding:8px 10px; font:inherit; margin-bottom:8px; } textarea { resize:vertical; }
  .row { display:flex; gap:10px; align-items:center; flex-wrap:wrap; }
  button { border:0; border-radius:8px; padding:8px 14px; font:inherit; cursor:pointer; background:var(--line); color:var(--ink); }
  button.send { background:var(--acc); color:#fff; } label { color:var(--mute); font-size:13px; margin-left:auto; }
</style>
<main>
  <h1>${leads.length} biznisa bez sajta</h1>
  <p>Pročitaj i prilagodi poruku, pa klikni „Otvori mejl“. Šalji ih ručno, po 20–30 dnevno, da ti mejl ne završi u spamu.</p>
  ${cards}
</main>
<script>
  const leads = ${JSON.stringify(leads.map((l) => l.email))};
  const key = "sent:" + location.pathname;
  let sent = {}; try { sent = JSON.parse(localStorage.getItem(key)) || {}; } catch {}
  document.querySelectorAll("article").forEach((card) => {
    const i = card.dataset.i, box = card.querySelector(".done");
    const mark = () => { card.classList.toggle("sent", box.checked); sent[leads[i]] = box.checked;
      try { localStorage.setItem(key, JSON.stringify(sent)); } catch {} };
    box.checked = !!sent[leads[i]]; card.classList.toggle("sent", box.checked);
    box.onchange = mark;
    card.querySelector(".send").onclick = () => {
      const s = card.querySelector(".subject").value, b = card.querySelector("textarea").value;
      location.href = "mailto:" + leads[i] + "?subject=" + encodeURIComponent(s) + "&body=" + encodeURIComponent(b);
      box.checked = true; mark();
    };
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
const byEmail = new Map();
for (const el of elements) {
  const lead = toLead(el);
  if (!lead.email.includes("@") || lead.hasSite || byEmail.has(lead.email)) continue;
  byEmail.set(lead.email, { ...lead, ...draft(lead) });
}
const leads = [...byEmail.values()].sort((a, b) => a.kind.localeCompare(b.kind, "sr") || a.name.localeCompare(b.name, "sr"));

fs.mkdirSync(OUT_DIR, { recursive: true });
writeCsv(leads);
writeHtml(leads);
console.log(`Pronađeno ${elements.length} biznisa sa mejlom, ${leads.length} bez sajta.`);
console.log(`→ ${OUT_DIR}/emails.html (pregled i slanje)\n→ ${OUT_DIR}/email-leads.csv (za Excel / Gmail)`);
