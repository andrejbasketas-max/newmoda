/* Vektor Auto — inventory, filters, detail dialog, loan calculator, contact form and the Motion layer.
   Without Motion or with reduced motion everything still works; only the animation is skipped. */
(() => {
  const root = document.documentElement;
  const M = window.Motion;
  const motionOK = Boolean(M) && root.classList.contains('motion-ok');
  if (!motionOK) root.classList.remove('motion-ok');
  const $ = (s, el = document) => el.querySelector(s);
  const $$ = (s, el = document) => [...el.querySelectorAll(s)];
  const ease = [0.16, 1, 0.3, 1];

  /* ---------- Settings ---------- */
  const APR = 7.9;              // informative yearly interest rate, %
  const DEFAULT_DOWN = 20;      // % used for the "rata ≈" figure on cards
  const DEFAULT_MONTHS = 60;
  const EMAIL = 'prodaja@vektorauto.rs';
  // Set to a form backend URL (e.g. Formspree) to receive inquiries directly; empty opens the visitor's e-mail app.
  const FORM_ENDPOINT = '';

  /* ---------- Inventory ----------
     Order = "Preporučeno" sort. `photo` (optional) replaces the illustration, e.g. photo: 'img/m4.jpg'. */
  const CARS = [
    { id: 'm4', make: 'BMW', model: 'M4 Competition', year: 2021, km: 32000, fuel: 'Benzin', gearbox: 'Automatik', hp: 510, body: 'coupe', color: '#0f6b4f', colorName: 'Isle of Man zelena', price: 74900, badge: ['Auto meseca', 'red'],
      features: ['Karbonski paket', 'Adaptivno vešanje', 'Head-up displej', 'Harman Kardon ozvučenje', 'Prvi vlasnik'] },
    { id: '320d', make: 'BMW', model: '320d M Sport', year: 2021, km: 68000, fuel: 'Dizel', gearbox: 'Automatik', hp: 190, body: 'sedan', color: '#1d4ed8', colorName: 'Portimao plava', price: 29900, badge: ['Izdvojeno', 'dark'],
      features: ['M Sport paket', 'LED farovi', 'Navigacija', 'Grejanje sedišta', 'Servisna knjiga'] },
    { id: 'rav4', make: 'Toyota', model: 'RAV4 2.5 Hybrid', year: 2021, km: 52000, fuel: 'Hibrid', gearbox: 'Automatik', hp: 218, body: 'suv', color: '#7c8a74', colorName: 'Urban Khaki', price: 31400, badge: ['Hibrid', 'green'],
      features: ['Potrošnja 5,6 l/100 km', 'Adaptivni tempomat', 'Kamera 360°', 'Apple CarPlay', 'Garancija baterije'] },
    { id: 'golf', make: 'Volkswagen', model: 'Golf 8 1.5 eTSI', year: 2022, km: 34000, fuel: 'Benzin', gearbox: 'Automatik', hp: 150, body: 'hatch', color: '#e7e9ee', colorName: 'Pure White', price: 22400,
      features: ['DSG menjač', 'Digitalni kokpit', 'LED farovi', 'Parking senzori', 'Prvi vlasnik'] },
    { id: 'q5', make: 'Audi', model: 'Q5 40 TDI quattro', year: 2020, km: 96000, fuel: 'Dizel', gearbox: 'Automatik', hp: 204, body: 'suv', color: '#16191f', colorName: 'Mythos crna', price: 36500,
      features: ['Quattro 4x4', 'Virtual Cockpit', 'Panorama krov', 'Električna peta vrata', 'Kožna sedišta'] },
    { id: 'model3', make: 'Tesla', model: 'Model 3 Long Range', year: 2022, km: 39000, fuel: 'Električni', gearbox: 'Automatik', hp: 440, body: 'sedan', color: '#f1f2f4', colorName: 'Pearl White', price: 37900, badge: ['Električni', 'green'],
      features: ['Domet 560 km (WLTP)', 'Autopilot', 'Dual Motor AWD', 'Staklen krov', 'Garancija baterije'] },
    { id: 'c220', make: 'Mercedes-Benz', model: 'C 220 d Avantgarde', year: 2022, km: 41000, fuel: 'Dizel', gearbox: 'Automatik', hp: 200, body: 'sedan', color: '#a3abb5', colorName: 'Hightech srebrna', price: 41900,
      features: ['MBUX navigacija', 'Ambijentalno svetlo', 'Kamera za vožnju unazad', 'Grejanje sedišta', 'Servis u ovlašćenom servisu'] },
    { id: 'mustang', make: 'Ford', model: 'Mustang 5.0 V8 GT', year: 2019, km: 45000, fuel: 'Benzin', gearbox: 'Automatik', hp: 450, body: 'coupe', color: '#f2a900', colorName: 'Grabber žuta', price: 44900, badge: ['Novo u ponudi', 'red'],
      features: ['V8 5.0 Coyote', 'Aktivni auspuh', 'Recaro sedišta', 'Brembo kočnice', 'Digitalni kokpit'] },
    { id: 'octavia', make: 'Škoda', model: 'Octavia Combi 2.0 TDI', year: 2021, km: 89000, fuel: 'Dizel', gearbox: 'Automatik', hp: 150, body: 'wagon', color: '#2e3a30', colorName: 'Tamnozelena', price: 19800,
      features: ['Prtljažnik 640 l', 'Navigacija', 'Kuka za vuču', 'Grejanje sedišta', 'Servisna knjiga'] },
    { id: 'v60', make: 'Volvo', model: 'V60 B4 Momentum', year: 2021, km: 71000, fuel: 'Dizel', gearbox: 'Automatik', hp: 197, body: 'wagon', color: '#1f2a3a', colorName: 'Denim plava', price: 32500,
      features: ['Blagi hibrid', 'Pilot Assist', 'Kožna sedišta', 'Električna peta vrata', 'LED farovi'] },
    { id: '3008', make: 'Peugeot', model: '3008 1.5 BlueHDi GT', year: 2020, km: 78000, fuel: 'Dizel', gearbox: 'Automatik', hp: 130, body: 'suv', color: '#4a4f57', colorName: 'Platinum siva', price: 21900,
      features: ['i-Cockpit', 'Full LED', 'Masažna sedišta', 'Kamera za vožnju unazad'] },
    { id: 'clio', make: 'Renault', model: 'Clio 1.0 TCe', year: 2022, km: 28000, fuel: 'Benzin', gearbox: 'Manuelni', hp: 91, body: 'hatch', color: '#c8102e', colorName: 'Flame crvena', price: 13900,
      features: ['Potrošnja 5,1 l/100 km', 'Apple CarPlay', 'LED farovi', 'Parking senzori'] },
  ];
  const BODY_NAMES = { sedan: 'Limuzina', hatch: 'Hečbek', wagon: 'Karavan', suv: 'SUV', coupe: 'Kupe' };
  const byId = Object.fromEntries(CARS.map((c) => [c.id, c]));

  /* ---------- Formatting & math ---------- */
  const nf = new Intl.NumberFormat('sr-Latn-RS', { maximumFractionDigits: 0 });
  const nf1 = new Intl.NumberFormat('sr-Latn-RS', { minimumFractionDigits: 1, maximumFractionDigits: 1 });
  const eur = (n) => `${nf.format(n)} €`;
  const km = (n) => `${nf.format(n)} km`;
  const plural = (n, one, many) => (n % 10 === 1 && n % 100 !== 11 ? one : many);
  const monthly = (price, downPct, months) => {
    const principal = price * (1 - downPct / 100);
    const r = APR / 12 / 100;
    return (principal * r) / (1 - (1 + r) ** -months);
  };
  const rateFor = (car) => Math.round(monthly(car.price, DEFAULT_DOWN, DEFAULT_MONTHS));
  const media = (car, size = 'card') => car.photo
    ? `<img src="${car.photo}" alt="${car.make} ${car.model}" loading="lazy" decoding="async">`
    : window.carSVG({ body: car.body, color: car.color, id: `${size}-${car.id}` });

  /* ---------- Hero numbers ---------- */
  $('[data-count-cars]').textContent = CARS.length;
  $('[data-min-rate]').textContent = nf.format(Math.min(...CARS.map(rateFor)));

  /* ---------- Inventory grid ---------- */
  const grid = $('[data-car-grid]');
  const countEl = $('[data-result-count]');
  const emptyEl = $('[data-empty]');
  const state = { body: 'all', fuel: 'all', sort: 'featured' };
  const sorters = {
    featured: () => 0,
    'price-asc': (a, b) => a.price - b.price,
    'price-desc': (a, b) => b.price - a.price,
    'km-asc': (a, b) => a.km - b.km,
    'year-desc': (a, b) => b.year - a.year || a.km - b.km,
  };

  const cardHTML = (car) => `
    <li data-card>
      <article class="card">
        <div class="card-media">
          ${car.badge ? `<span class="badge badge-${car.badge[1]}">${car.badge[0]}</span>` : ''}
          ${media(car)}
        </div>
        <div class="card-body">
          <div>
            <p class="card-make">${car.make}</p>
            <h3 class="card-title">${car.model}</h3>
          </div>
          <ul class="card-specs" aria-label="Osnovni podaci">
            <li>${car.year}.</li><li>${km(car.km)}</li><li>${car.fuel}</li><li>${car.gearbox}</li>
          </ul>
          <div class="card-foot">
            <p><span class="card-price">${eur(car.price)}</span><span class="card-rate">rata ≈ ${nf.format(rateFor(car))} €/mes</span></p>
            <button type="button" class="card-btn" data-open-car="${car.id}" aria-label="Detalji: ${car.make} ${car.model}">Detalji <svg class="ic"><use href="#i-arrow"/></svg></button>
          </div>
        </div>
      </article>
    </li>`;

  let gridAnim;
  function renderGrid({ animate = true } = {}) {
    const list = CARS
      .filter((c) => (state.body === 'all' || c.body === state.body) && (state.fuel === 'all' || c.fuel === state.fuel))
      .sort(sorters[state.sort]);
    grid.innerHTML = list.map(cardHTML).join('');
    emptyEl.hidden = list.length > 0;
    countEl.textContent = `${list.length} ${plural(list.length, 'vozilo', 'vozila')} u ponudi`;
    if (motionOK && animate && list.length) {
      gridAnim?.stop();
      gridAnim = M.animate($$('[data-card]', grid), { opacity: [0, 1], transform: ['translateY(18px)', 'translateY(0px)'] },
        { duration: 0.55, ease, delay: M.stagger(0.045) });
    }
  }

  $('[data-body-filter]').addEventListener('click', (e) => {
    const chip = e.target.closest('[data-body]');
    if (!chip) return;
    state.body = chip.dataset.body;
    $$('[data-body]').forEach((c) => c.setAttribute('aria-pressed', String(c === chip)));
    renderGrid();
  });
  $('[data-fuel-filter]').addEventListener('change', (e) => { state.fuel = e.target.value; renderGrid(); });
  $('[data-sort]').addEventListener('change', (e) => { state.sort = e.target.value; renderGrid(); });
  $('[data-reset]').addEventListener('click', () => {
    Object.assign(state, { body: 'all', fuel: 'all' });
    $('[data-fuel-filter]').value = 'all';
    $$('[data-body]').forEach((c) => c.setAttribute('aria-pressed', String(c.dataset.body === 'all')));
    renderGrid();
  });
  renderGrid({ animate: false });

  // The grid enters with the rest of the page the first time it scrolls into view.
  if (motionOK) {
    $$('[data-card]', grid).forEach((li) => { li.style.opacity = 0; });
    const stopGridView = M.inView(grid, () => { stopGridView(); renderGrid(); }, { margin: '0px 0px -15% 0px' });
  }

  /* ---------- Detail dialog ---------- */
  const modal = $('[data-modal]');
  let current = null;

  function openCar(id) {
    const car = byId[id];
    if (!car) return;
    current = car;
    $('[data-modal-media]', modal).innerHTML = media(car, 'modal');
    $('[data-modal-make]', modal).textContent = `${car.make} · ${BODY_NAMES[car.body]}`;
    $('[data-modal-title]', modal).textContent = car.model;
    $('[data-modal-price]', modal).textContent = eur(car.price);
    $('[data-modal-rate]', modal).textContent = `rata ≈ ${nf.format(rateFor(car))} €/mes uz ${DEFAULT_DOWN}% učešća i ${DEFAULT_MONTHS} meseci`;
    const specs = [
      ['Godište', `${car.year}.`], ['Kilometraža', km(car.km)], ['Gorivo', car.fuel], ['Menjač', car.gearbox],
      ['Snaga', `${car.hp} KS`], ['Boja', car.colorName],
    ];
    $('[data-modal-specs]', modal).innerHTML = specs.map(([k, v]) => `<div><dt>${k}</dt><dd>${v}</dd></div>`).join('');
    $('[data-modal-features]', modal).innerHTML = car.features.map((f) => `<li><svg class="ic"><use href="#i-check"/></svg>${f}</li>`).join('');
    modal.showModal();
    $('.modal-inner', modal).scrollTop = 0;
    if (motionOK) {
      const svg = $('[data-modal-media] svg', modal);
      if (svg) {
        M.animate(svg, { transform: ['translateX(60px)', 'translateX(0px)'], opacity: [0, 1] }, { duration: 0.7, ease });
        M.animate($$('.wheel', svg), { transform: ['rotate(160deg)', 'rotate(0deg)'] }, { duration: 0.7, ease });
      }
      M.animate($('.modal-body', modal).children, { opacity: [0, 1], transform: ['translateY(10px)', 'translateY(0px)'] },
        { duration: 0.5, ease, delay: M.stagger(0.04, { startDelay: 0.1 }) });
    }
  }

  document.addEventListener('click', (e) => {
    const opener = e.target.closest('[data-open-car]');
    if (opener) openCar(opener.dataset.openCar);
  });
  $('[data-modal-close]', modal).addEventListener('click', () => modal.close());
  modal.addEventListener('click', (e) => { if (e.target === modal) modal.close(); });

  /* ---------- Jumping to the form / calculator ---------- */
  const form = $('[data-form]');
  const interest = $('#f-interest');
  const carSelect = $('[data-car-select]');
  carSelect.insertAdjacentHTML('beforeend', CARS.map((c) => `<option value="${c.id}">${c.make} ${c.model}</option>`).join(''));

  function goTo(id, focusEl) {
    $(id).scrollIntoView({ behavior: motionOK ? 'smooth' : 'auto' });
    if (focusEl) setTimeout(() => focusEl.focus({ preventScroll: true }), motionOK ? 700 : 0);
  }
  document.addEventListener('click', (e) => {
    const link = e.target.closest('[data-interest]');
    if (link) interest.value = link.dataset.interest;
  });
  $('[data-modal-drive]', modal).addEventListener('click', () => {
    modal.close();
    interest.value = 'Probna vožnja';
    carSelect.value = current.id;
    goTo('#kontakt', $('#f-name'));
  });
  $('[data-modal-calc]', modal).addEventListener('click', () => {
    modal.close();
    calc.price.value = Math.min(Math.max(current.price, +calc.price.min), +calc.price.max);
    updateCalc();
    goTo('#finansiranje', calc.price);
  });

  /* ---------- Loan calculator ---------- */
  const calc = $('[data-calc]').elements;
  const out = (k) => $(`[data-out="${k}"]`);
  const rateEl = $('[data-rate]');
  let shownRate = 0;
  let rateAnim;
  $('[data-apr]').textContent = nf1.format(APR);

  function updateCalc() {
    const price = +calc.price.value, down = +calc.down.value, months = +calc.months.value;
    for (const input of [calc.price, calc.down, calc.months]) {
      input.style.setProperty('--p', `${((input.value - input.min) / (input.max - input.min)) * 100}%`);
    }
    out('price').textContent = eur(price);
    out('down').textContent = `${down}% · ${eur(Math.round(price * down / 100))}`;
    out('months').textContent = `${months} ${plural(months, 'mesec', 'meseci')}`;
    const rate = monthly(price, down, months);
    $('[data-loan]').textContent = eur(Math.round(price * (1 - down / 100)));
    $('[data-downpay]').textContent = eur(Math.round(price * down / 100));
    $('[data-total]').textContent = eur(Math.round(rate * months + price * down / 100));
    rateAnim?.stop();
    if (motionOK && shownRate) {
      rateAnim = M.animate(shownRate, rate, { duration: 0.45, ease, onUpdate: (v) => { shownRate = v; rateEl.textContent = nf.format(v); } });
    } else {
      shownRate = rate;
      rateEl.textContent = nf.format(rate);
    }
  }
  $('[data-calc]').addEventListener('input', updateCalc);
  $('[data-calc]').addEventListener('submit', (e) => e.preventDefault());
  updateCalc();

  /* ---------- Contact form ---------- */
  const status = $('[data-form-status]');
  const checks = {
    name: (v) => v.trim().length >= 2,
    phone: (v) => v.replace(/\D/g, '').length >= 8,
  };
  let tried = false;
  function validate(name) {
    const input = form.elements[name];
    const ok = checks[name](input.value);
    input.setAttribute('aria-invalid', String(!ok));
    $(`#f-${name}-err`).hidden = ok;
    return ok;
  }
  form.addEventListener('input', (e) => { if (tried && checks[e.target.name]) validate(e.target.name); });
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    tried = true;
    const bad = Object.keys(checks).filter((n) => !validate(n));
    if (bad.length) { form.elements[bad[0]].focus(); return; }

    const data = Object.fromEntries(new FormData(form));
    const car = byId[data.car];
    const firstName = data.name.trim().split(/\s+/)[0];
    const lines = [
      `Ime: ${data.name}`, `Telefon: ${data.phone}`, `Interesuje me: ${data.interest}`,
      `Vozilo: ${car ? `${car.make} ${car.model} (${eur(car.price)})` : 'nije izabrano'}`,
      data.message ? `\n${data.message}` : '',
    ];
    const btn = $('[type="submit"]', form);

    if (FORM_ENDPOINT) {
      btn.disabled = true;
      btn.textContent = 'Šaljem…';
      try {
        const res = await fetch(FORM_ENDPOINT, { method: 'POST', headers: { 'Content-Type': 'application/json', Accept: 'application/json' }, body: JSON.stringify(data) });
        if (!res.ok) throw new Error(res.status);
        status.textContent = `Hvala, ${firstName}! Javljamo se u toku radnog dana.`;
        form.reset();
        tried = false;
      } catch {
        status.textContent = 'Slanje nije uspelo. Pozovite nas na 011 123 4567 ili pokušajte ponovo.';
      } finally {
        btn.disabled = false;
        btn.textContent = 'Pošalji upit';
      }
      return;
    }
    const subject = `${data.interest}${car ? ` — ${car.make} ${car.model}` : ''}`;
    window.location.href = `mailto:${EMAIL}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(lines.join('\n'))}`;
    status.textContent = `Hvala, ${firstName}! Otvorili smo vaš e-mail sa pripremljenom porukom — samo je pošaljite. Ako se nije otvorio, pozovite 011 123 4567.`;
  });

  /* ---------- Opening hours (Belgrade time) ---------- */
  const HOURS = { 1: [9, 19], 2: [9, 19], 3: [9, 19], 4: [9, 19], 5: [9, 19], 6: [9, 15] };
  function updateOpen() {
    const parts = Object.fromEntries(new Intl.DateTimeFormat('en-GB', { timeZone: 'Europe/Belgrade', weekday: 'short', hour: 'numeric', minute: 'numeric', hourCycle: 'h23' })
      .formatToParts(new Date()).map((p) => [p.type, p.value]));
    const day = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].indexOf(parts.weekday);
    const h = +parts.hour + parts.minute / 60;
    const today = HOURS[day];
    const el = $('[data-open-status]');
    const open = today && h >= today[0] && h < today[1];
    el.classList.toggle('is-open', Boolean(open));
    if (open) { el.textContent = `Otvoreno sada · do ${today[1]}h`; return; }
    if (today && h < today[0]) { el.textContent = `Zatvoreno · otvaramo danas u ${today[0]}h`; return; }
    let next = (day + 1) % 7;
    while (!HOURS[next]) next = (next + 1) % 7;
    el.textContent = `Zatvoreno · otvaramo ${next === (day + 1) % 7 ? 'sutra' : 'u ponedeljak'} u ${HOURS[next][0]}h`;
  }
  updateOpen();
  setInterval(updateOpen, 60000);

  /* ---------- Nav ---------- */
  const nav = $('[data-nav]');
  const burger = $('[data-burger]');
  const setMenu = (open) => {
    nav.classList.toggle('is-open', open);
    burger.setAttribute('aria-expanded', String(open));
    burger.setAttribute('aria-label', open ? 'Zatvori meni' : 'Otvori meni');
    $('use', burger).setAttribute('href', open ? '#i-x' : '#i-menu');
  };
  burger.addEventListener('click', () => setMenu(!nav.classList.contains('is-open')));
  $('#navLinks').addEventListener('click', (e) => { if (e.target.closest('a')) setMenu(false); });
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && nav.classList.contains('is-open')) { setMenu(false); burger.focus(); }
  });
  let lastY = scrollY;
  addEventListener('scroll', () => {
    const y = scrollY;
    nav.classList.toggle('is-solid', y > 40);
    nav.classList.toggle('is-hidden', y > 400 && y > lastY && !nav.classList.contains('is-open') && !nav.contains(document.activeElement));
    lastY = y;
  }, { passive: true });

  const links = $$('#navLinks a');
  const io = new IntersectionObserver((entries) => {
    for (const en of entries) {
      if (!en.isIntersecting) continue;
      links.forEach((a) => (a.getAttribute('href') === `#${en.target.id}` ? a.setAttribute('aria-current', 'true') : a.removeAttribute('aria-current')));
    }
  }, { rootMargin: '-45% 0px -50% 0px' });
  links.forEach((a) => { const s = $(a.getAttribute('href')); if (s) io.observe(s); });

  /* ---------- Static illustrations ---------- */
  const heroCar = $('[data-hero-car]');
  heroCar.innerHTML = window.carSVG({ body: 'coupe', color: '#c8102e', id: 'hero' });
  const featureCar = $('[data-feature-car]');
  featureCar.innerHTML = window.carSVG({ body: byId.m4.body, color: byId.m4.color, id: 'feature' });

  window.vektorReady = true;
  if (!motionOK) return;

  /* ---------- Motion: hero intro ---------- */
  M.animate($$('[data-hero-line]'), { transform: ['translateY(110%)', 'translateY(0%)'] }, { duration: 1.1, ease, delay: M.stagger(0.12, { startDelay: 0.15 }) });
  M.animate($$('[data-hero]'), { opacity: [0, 1], transform: ['translateY(16px)', 'translateY(0px)'] }, { duration: 0.9, ease, delay: M.stagger(0.1, { startDelay: 0.45 }) });
  M.animate(heroCar, { transform: ['translateX(110vw)', 'translateX(0vw)'] }, { duration: 1.6, ease: [0.22, 1, 0.36, 1], delay: 0.3 });
  M.animate($$('.wheel', heroCar), { transform: ['rotate(0deg)', 'rotate(-1440deg)'] }, { duration: 1.6, ease: [0.22, 1, 0.36, 1], delay: 0.3 });
  M.animate($('.streaks'), { opacity: [0, 1, 0], transform: ['translateX(40%)', 'translateX(-10%)'] }, { duration: 1.5, delay: 0.35, ease: 'easeOut' });
  M.animate($('.headlight', heroCar), { opacity: [1, 0.25, 1, 0.25, 1] }, { duration: 0.6, delay: 1.9 });

  /* ---------- Motion: reveals ---------- */
  $$('[data-reveal]').forEach((el) => {
    const siblings = [...el.parentElement.children].filter((c) => c.hasAttribute('data-reveal'));
    const i = siblings.indexOf(el);
    const stop = M.inView(el, () => {
      stop();
      M.animate(el, { opacity: [0, 1], transform: ['translateY(28px)', 'translateY(0px)'] }, { duration: 0.9, ease, delay: Math.min(i, 4) * 0.08 });
    }, { margin: '0px 0px -12% 0px' });
  });

  /* ---------- Motion: car of the month ---------- */
  const feature = $('[data-feature]');
  const word = $('[data-feature-word]');
  const featureWheels = $$('.wheel', featureCar);
  const counters = $$('[data-to]', feature);
  let counted = false;
  const countUp = () => {
    if (counted) return;
    counted = true;
    counters.forEach((el, i) => {
      const to = +el.dataset.to, fmt = el.dataset.dec ? nf1 : nf;
      M.animate(0, to, { duration: 1.4, delay: i * 0.12, ease, onUpdate: (v) => { el.textContent = fmt.format(v); } });
    });
  };
  const wide = matchMedia('(min-width: 900px)');
  if (wide.matches) {
    M.scroll((p) => {
      const drive = Math.min(p / 0.6, 1);
      const eased = 1 - (1 - drive) ** 3;
      featureCar.style.transform = `translateX(${(1 - eased) * 75}vw)`;
      featureWheels.forEach((w) => { w.style.transform = `rotate(${-(1 - eased) * 1800}deg)`; });
      word.style.transform = `translate(calc(-50% + ${(0.5 - p) * 30}vw), -50%)`;
      if (p > 0.3) countUp();
    }, { target: feature, offset: ['start start', 'end end'] });
  } else {
    const stop = M.inView(feature, () => { stop(); countUp(); }, { amount: 0.4 });
  }
})();
