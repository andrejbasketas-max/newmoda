// Outreach agent: checks Instagram profiles, keeps the ones without a real
// website, and drafts a personalized DM for each. Messages are NOT sent
// automatically — they land in out/review.html for you to read, edit and send.
//
// Usage: npm start            (reads leads.csv, writes out/)
//        npm start -- --redo  (ignore out/seen.json and recheck everyone)

import fs from "node:fs";
import path from "node:path";
import Anthropic from "@anthropic-ai/sdk";

const LEADS_FILE = process.env.LEADS_FILE || "leads.csv";
const OUT_DIR = "out";
const SEEN_FILE = path.join(OUT_DIR, "seen.json");
const GRAPH = "https://graph.facebook.com/v21.0";
const { IG_USER_ID, IG_ACCESS_TOKEN } = process.env;

// Links that are not a real website — a profile with only these still needs one.
const NOT_A_SITE = [
  "linktr.ee", "beacons.ai", "linkin.bio", "bio.site", "taplink", "lnk.bio",
  "wa.me", "api.whatsapp.com", "t.me", "facebook.com", "fb.com", "instagram.com",
  "tiktok.com", "msha.ke", "carrd.co", "linkbio", "solo.to", "allmylinks",
];

const ME = {
  studio: process.env.STUDIO_NAME || "Newmoda",
  offer: process.env.OFFER ||
    "izrada brzih, modernih sajtova prilagođenih telefonu za male lokalne biznise",
  portfolio: process.env.PORTFOLIO_URL || "",
  signature: process.env.SIGNATURE || "",
};

// ---------- input ----------

function parseCsv(text) {
  const rows = [];
  for (const line of text.split(/\r?\n/)) {
    if (!line.trim() || line.trim().startsWith("#")) continue;
    const cells = [];
    let cur = "", quoted = false;
    for (let i = 0; i < line.length; i++) {
      const c = line[i];
      if (quoted) {
        if (c === '"' && line[i + 1] === '"') { cur += '"'; i++; }
        else if (c === '"') quoted = false;
        else cur += c;
      } else if (c === '"') quoted = true;
      else if (c === ",") { cells.push(cur); cur = ""; }
      else cur += c;
    }
    cells.push(cur);
    rows.push(cells.map((s) => s.trim()));
  }
  return rows;
}

function readLeads() {
  if (!fs.existsSync(LEADS_FILE)) {
    console.error(`Nema fajla ${LEADS_FILE}. Kopiraj leads.example.csv u leads.csv i dodaj profile.`);
    process.exit(1);
  }
  const rows = parseCsv(fs.readFileSync(LEADS_FILE, "utf8"));
  const header = rows[0].map((h) => h.toLowerCase());
  const hasHeader = header.includes("username");
  const cols = hasHeader ? header : ["username", "website", "bio", "note"];
  return (hasHeader ? rows.slice(1) : rows)
    .map((r) => Object.fromEntries(cols.map((c, i) => [c, r[i] ?? ""])))
    .map((r) => ({ ...r, username: r.username.replace(/^@/, "").replace(/.*instagram\.com\//, "").replace(/\/.*$/, "") }))
    .filter((r) => r.username);
}

// ---------- Instagram (official Graph API, Business Discovery) ----------

async function fetchProfile(username) {
  const fields = `business_discovery.username(${username}){username,name,biography,website,followers_count,media_count,media.limit(5){caption}}`;
  const url = `${GRAPH}/${IG_USER_ID}?fields=${encodeURIComponent(fields)}&access_token=${IG_ACCESS_TOKEN}`;
  const res = await fetch(url);
  const json = await res.json();
  if (json.error) return { error: json.error.message };
  const p = json.business_discovery;
  return {
    username: p.username,
    name: p.name || "",
    bio: p.biography || "",
    website: p.website || "",
    followers: p.followers_count ?? "",
    posts: p.media_count ?? "",
    captions: (p.media?.data || []).map((m) => m.caption).filter(Boolean).slice(0, 5),
  };
}

function siteStatus(website) {
  if (!website) return "nema sajt";
  const w = website.toLowerCase();
  if (NOT_A_SITE.some((d) => w.includes(d))) return "samo link-u-bio";
  return "ima sajt";
}

// ---------- message drafting (Claude) ----------

const client = new Anthropic();

const SYSTEM = `Pišeš prvu Instagram poruku (DM) u ime studija "${ME.studio}" koji se bavi sledećim: ${ME.offer}.
Pravila:
- Piši na srpskom (latinica), prirodno i ljudski, kao osoba a ne kao reklama. Persiraj ("Vi") osim ako profil očigledno komunicira opušteno.
- 3 do 5 kratkih rečenica, bez emodžija u svakoj rečenici (najviše jedan), bez velikih slova za naglašavanje.
- Pomeni nešto konkretno sa njihovog profila (proizvod, usluga, lokacija, stil) da se vidi da si ga stvarno pogledao.
- Objasni jednu konkretnu korist sajta za BAŠ njihov tip biznisa (npr. meni i rezervacije za kafić, cenovnik i zakazivanje za salon, katalog za butik).
- Završi laganim pitanjem, bez pritiska. Ne izmišljaj cene, popuste ni rokove.
${ME.portfolio ? `- Možeš da pomeneš primer radova: ${ME.portfolio}` : ""}
${ME.signature ? `- Potpiši se: ${ME.signature}` : ""}
Ako profil nije biznis kome bi sajt imao smisla (lični profil, influenser bez proizvoda, velika firma), postavi "fit" na false.`;

const SCHEMA = {
  type: "object",
  properties: {
    fit: { type: "boolean", description: "Da li je ovo dobar potencijalni klijent za sajt" },
    business_type: { type: "string", description: "Kratko: npr. kafić, frizerski salon, butik" },
    reason: { type: "string", description: "Jedna rečenica zašto jeste/nije dobar lead" },
    message: { type: "string", description: "Tekst DM poruke (prazno ako fit=false)" },
  },
  required: ["fit", "business_type", "reason", "message"],
  additionalProperties: false,
};

async function draftMessage(p) {
  const profile = [
    `Korisničko ime: @${p.username}`,
    p.name && `Ime: ${p.name}`,
    `Bio: ${p.bio || "(prazno)"}`,
    `Link u biou: ${p.website || "(nema)"} → ${p.site}`,
    p.followers !== "" && `Pratioci: ${p.followers}, objava: ${p.posts}`,
    p.captions?.length && `Poslednje objave:\n- ${p.captions.map((c) => c.slice(0, 300)).join("\n- ")}`,
    p.note && `Napomena: ${p.note}`,
  ].filter(Boolean).join("\n");

  const response = await client.beta.messages.create({
    model: "claude-opus-5-5",
    max_tokens: 16000,
    betas: ["server-side-fallback-2026-07-01"],
    fallbacks: "default",
    output_config: { effort: "medium", format: { type: "json_schema", schema: SCHEMA } },
    system: SYSTEM,
    messages: [{ role: "user", content: `Profil:\n${profile}` }],
  });
  if (response.stop_reason === "refusal") throw new Error("model je odbio zahtev");
  const text = response.content.find((b) => b.type === "text")?.text;
  return JSON.parse(text);
}

// ---------- output ----------

const esc = (s) => String(s ?? "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);
const csvCell = (s) => `"${String(s ?? "").replace(/"/g, '""')}"`;

function writeOutputs(results) {
  const leads = results.filter((r) => r.message);
  fs.writeFileSync(path.join(OUT_DIR, "leads.csv"),
    [["username", "business_type", "site", "website", "followers", "reason", "message"].join(","),
      ...results.map((r) => [r.username, r.business_type, r.site, r.website, r.followers, r.reason, r.message].map(csvCell).join(","))
    ].join("\n"));

  const cards = leads.map((r, i) => `
  <article class="card" data-i="${i}">
    <header>
      <a href="https://instagram.com/${esc(r.username)}" target="_blank" rel="noopener">@${esc(r.username)}</a>
      <span class="tag">${esc(r.business_type)}</span><span class="tag">${esc(r.site)}</span>
      ${r.followers !== "" ? `<span class="muted">${esc(r.followers)} pratilaca</span>` : ""}
    </header>
    <p class="muted">${esc(r.reason)}</p>
    <textarea>${esc(r.message)}</textarea>
    <div class="row">
      <button class="copy">Kopiraj</button>
      <a class="btn" href="https://ig.me/m/${esc(r.username)}" target="_blank" rel="noopener">Otvori DM</a>
      <label><input type="checkbox" class="sent"> Poslato</label>
    </div>
  </article>`).join("");

  fs.writeFileSync(path.join(OUT_DIR, "review.html"), `<!doctype html>
<html lang="sr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Outreach pregled</title>
<style>
:root{--bg:#f6f5f2;--card:#fff;--ink:#1b1b1b;--muted:#6b6b6b;--line:#e3e0da;--accent:#1b1b1b}
@media (prefers-color-scheme:dark){:root{--bg:#141414;--card:#1e1e1e;--ink:#eee;--muted:#9a9a9a;--line:#333;--accent:#eee}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.5 system-ui,sans-serif;padding:24px 16px}
main{max-width:720px;margin:auto}h1{font-size:22px;margin:0 0 4px}.muted{color:var(--muted);font-size:13px}
.card{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:16px;margin:14px 0}
.card.done{opacity:.45}header{display:flex;flex-wrap:wrap;gap:8px;align-items:center}header a{font-weight:600;color:var(--ink)}
.tag{font-size:12px;border:1px solid var(--line);border-radius:99px;padding:1px 8px}
textarea{width:100%;min-height:130px;margin:8px 0;padding:10px;border:1px solid var(--line);border-radius:8px;background:transparent;color:var(--ink);font:inherit;resize:vertical}
.row{display:flex;gap:10px;align-items:center;flex-wrap:wrap}
button,.btn{border:1px solid var(--accent);background:var(--accent);color:var(--bg);border-radius:8px;padding:6px 14px;font:inherit;cursor:pointer;text-decoration:none}
.btn{background:transparent;color:var(--ink)}
</style></head><body><main>
<h1>Outreach — ${leads.length} poruka za pregled</h1>
<p class="muted">Pročitaj i po potrebi izmeni svaku poruku, klikni „Kopiraj“, pa „Otvori DM“ i pošalji je sam. Šalji umereno (npr. 10–20 dnevno) da Instagram ne bi ograničio nalog.</p>
${cards || "<p>Nema novih leadova.</p>"}
</main><script>
const KEY="outreach-sent";let sent={};try{sent=JSON.parse(localStorage.getItem(KEY))||{}}catch{}
document.querySelectorAll(".card").forEach(card=>{
  const user=card.querySelector("header a").textContent, box=card.querySelector(".sent");
  box.checked=!!sent[user];card.classList.toggle("done",box.checked);
  box.onchange=()=>{sent[user]=box.checked;card.classList.toggle("done",box.checked);try{localStorage.setItem(KEY,JSON.stringify(sent))}catch{}};
  card.querySelector(".copy").onclick=async e=>{await navigator.clipboard.writeText(card.querySelector("textarea").value);e.target.textContent="Kopirano ✓";setTimeout(()=>e.target.textContent="Kopiraj",1500)};
});
</script></body></html>`);
  return leads.length;
}

// ---------- main ----------

fs.mkdirSync(OUT_DIR, { recursive: true });
const redo = process.argv.includes("--redo");
const seen = !redo && fs.existsSync(SEEN_FILE) ? JSON.parse(fs.readFileSync(SEEN_FILE, "utf8")) : {};
const useApi = Boolean(IG_USER_ID && IG_ACCESS_TOKEN);
if (!useApi) console.log("IG_USER_ID/IG_ACCESS_TOKEN nisu podešeni — koristim website/bio kolone iz CSV-a.");

const leads = readLeads().filter((l) => !seen[l.username.toLowerCase()]);
console.log(`${leads.length} novih profila za proveru.`);

for (const lead of leads) {
  const key = lead.username.toLowerCase();
  let p = { ...lead, followers: "", posts: "", captions: [] };
  if (useApi) {
    const fetched = await fetchProfile(lead.username);
    if (fetched.error) {
      console.log(`  @${lead.username}: ${fetched.error} (lični nalog ili ne postoji — proveri ručno)`);
      seen[key] = { username: lead.username, site: "nepoznato", reason: fetched.error };
      continue;
    }
    p = { ...p, ...fetched };
  }
  p.site = siteStatus(p.website);
  if (p.site === "ima sajt") {
    console.log(`  @${p.username}: ima sajt (${p.website}) — preskačem`);
    seen[key] = { ...p, reason: "već ima sajt" };
    continue;
  }
  try {
    const d = await draftMessage(p);
    seen[key] = { ...p, ...d, message: d.fit ? d.message : "" };
    console.log(`  @${p.username}: ${p.site}, ${d.business_type} → ${d.fit ? "poruka napisana" : "nije dobar lead"}`);
  } catch (err) {
    if (err instanceof Anthropic.APIError) console.log(`  @${p.username}: API greška ${err.status} — ${err.message}`);
    else console.log(`  @${p.username}: ${err.message}`);
    continue; // not marked seen, so it is retried next run
  }
  fs.writeFileSync(SEEN_FILE, JSON.stringify(seen, null, 2));
}
fs.writeFileSync(SEEN_FILE, JSON.stringify(seen, null, 2));

const n = writeOutputs(Object.values(seen));
console.log(`\nGotovo: ${n} poruka čeka pregled u ${OUT_DIR}/review.html (sve u ${OUT_DIR}/leads.csv).`);
