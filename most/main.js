// Most — calculator, tabs, country grid, reveals, QR badge.
(() => {
  const root = document.documentElement;
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (!reduced && 'IntersectionObserver' in window) root.classList.add('js');

  /* ---------- EU flag stars ---------- */
  const euStars = (() => {
    let dots = '';
    for (let i = 0; i < 12; i++) {
      const a = (i / 12) * Math.PI * 2;
      dots += `<circle cx="${(50 + Math.cos(a) * 30).toFixed(2)}" cy="${(50 + Math.sin(a) * 30).toFixed(2)}" r="4.2" fill="%23ffcc00"/>`;
    }
    return `url("data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'>${dots.replace(/"/g, "'")}</svg>")`;
  })();
  const paintFlags = (scope = document) => {
    scope.querySelectorAll('[data-flag="eu"]').forEach((el) => {
      el.style.backgroundImage = euStars;
      el.style.backgroundSize = 'cover';
    });
  };
  paintFlags();

  /* ---------- Data (illustrative rates, per 1 EUR) ---------- */
  const currencies = {
    RSD: { name: 'Srpski dinar', flag: 'rs', rate: 117.2, dec: 0 },
    EUR: { name: 'Evro', flag: 'eu', rate: 1, dec: 2 },
    USD: { name: 'Američki dolar', flag: 'us', rate: 1.09, dec: 2 },
    CHF: { name: 'Švajcarski franak', flag: 'ch', rate: 0.94, dec: 2 },
    SEK: { name: 'Švedska kruna', flag: 'se', rate: 11.35, dec: 2 },
    HUF: { name: 'Mađarska forinta', flag: 'hu', rate: 392, dec: 0 },
    PLN: { name: 'Poljski zlot', flag: 'pl', rate: 4.27, dec: 2 },
    RON: { name: 'Rumunski lej', flag: 'ro', rate: 4.98, dec: 2 },
    UAH: { name: 'Ukrajinska hrivnja', flag: 'ua', rate: 45.6, dec: 2 },
  };

  // [flag, name, accusative ("Šalješ u …"), currency]
  const countries = [
    ['de', 'Nemačka', 'Nemačku', 'EUR'],
    ['at', 'Austrija', 'Austriju', 'EUR'],
    ['ch', 'Švajcarska', 'Švajcarsku', 'CHF'],
    ['us', 'SAD', 'SAD', 'USD'],
    ['fr', 'Francuska', 'Francusku', 'EUR'],
    ['it', 'Italija', 'Italiju', 'EUR'],
    ['nl', 'Holandija', 'Holandiju', 'EUR'],
    ['be', 'Belgija', 'Belgiju', 'EUR'],
    ['se', 'Švedska', 'Švedsku', 'SEK'],
    ['ie', 'Irska', 'Irsku', 'EUR'],
    ['hu', 'Mađarska', 'Mađarsku', 'HUF'],
    ['ro', 'Rumunija', 'Rumuniju', 'RON'],
    ['bg', 'Bugarska', 'Bugarsku', 'EUR'],
    ['pl', 'Poljska', 'Poljsku', 'PLN'],
    ['ua', 'Ukrajina', 'Ukrajinu', 'UAH'],
    ['lu', 'Luksemburg', 'Luksemburg', 'EUR'],
    ['ee', 'Estonija', 'Estoniju', 'EUR'],
    ['lt', 'Litvanija', 'Litvaniju', 'EUR'],
    ['lv', 'Letonija', 'Letoniju', 'EUR'],
    ['mc', 'Monako', 'Monako', 'EUR'],
  ];
  const defaultCountry = { EUR: 'de', USD: 'us', CHF: 'ch', SEK: 'se', HUF: 'hu', PLN: 'pl', RON: 'ro', UAH: 'ua', RSD: null };

  /* ---------- Calculator ---------- */
  const calc = document.getElementById('calc');
  const amountEl = document.getElementById('amount');
  const resultEl = document.getElementById('result');
  const list = document.getElementById('curList');
  const recFlag = document.getElementById('recFlag');
  const recName = document.getElementById('recName');
  const state = { from: 'RSD', to: 'EUR', country: 'de' };

  const fmt = (n, dec) => new Intl.NumberFormat('sr-Latn-RS', { minimumFractionDigits: dec, maximumFractionDigits: dec }).format(n);
  const parse = (s) => {
    const n = parseFloat(String(s).replace(/\s/g, '').replace(/\./g, '').replace(',', '.'));
    return Number.isFinite(n) ? n : 0;
  };

  const update = () => {
    const from = currencies[state.from];
    const to = currencies[state.to];
    const amount = parse(amountEl.value);
    const fixed = 0.6 * from.rate;                 // fixed part, in source currency
    const fee = amount > 0 ? amount * 0.0045 + fixed : 0;
    const converted = Math.max(amount - fee, 0);
    const rate = to.rate / from.rate;
    const bankFee = amount > 0 ? amount * 0.032 + 4 * from.rate : 0;

    document.getElementById('feeVal').textContent = `${fmt(fee, 2)} ${state.from}`;
    document.getElementById('convVal').textContent = `${fmt(converted, 2)} ${state.from}`;
    document.getElementById('rateVal').textContent = fmt(rate, rate < 0.1 ? 6 : 4);
    document.getElementById('saveVal').textContent = `${fmt(Math.max(bankFee - fee, 0), from.dec)} ${state.from}`;
    resultEl.value = fmt(converted * rate, to.dec);
  };

  const setCur = (side, code) => {
    state[side] = code;
    const btn = calc.querySelector(`.cur[data-side="${side}"]`);
    btn.querySelector('b').textContent = code;
    const flag = btn.querySelector('.flag');
    flag.dataset.flag = currencies[code].flag;
    flag.style.backgroundImage = '';
    paintFlags(btn);
    if (side === 'to') {
      const match = countries.find((c) => c[0] === state.country && c[3] === code);
      if (!match && defaultCountry[code]) setCountry(defaultCountry[code], false);
      if (code === 'RSD') { recFlag.dataset.flag = 'rs'; recFlag.style.backgroundImage = ''; recName.textContent = 'Srbiju'; }
    }
    update();
  };

  function setCountry(flag, syncCur = true) {
    const c = countries.find((x) => x[0] === flag);
    if (!c) return;
    state.country = flag;
    recFlag.dataset.flag = flag;
    recFlag.style.backgroundImage = '';
    recName.textContent = c[2];
    if (syncCur && state.to !== c[3]) setCur('to', c[3]);
  }

  // Dropdown (currencies or countries)
  let open = null; // { trigger, kind, side }
  const closeList = () => {
    if (!open) return;
    open.trigger.setAttribute('aria-expanded', 'false');
    list.hidden = true;
    open = null;
  };
  const openList = (trigger, kind, side) => {
    if (open && open.trigger === trigger) return closeList();
    closeList();
    const items = kind === 'country'
      ? countries.map((c) => ({ id: c[0], flag: c[0], label: c[1], meta: c[3], selected: c[0] === state.country }))
      : Object.entries(currencies).map(([code, c]) => ({ id: code, flag: c.flag, label: code, meta: c.name, selected: code === state[side] }));
    list.innerHTML = items.map((it) => `<li role="option" data-id="${it.id}" aria-selected="${it.selected}" tabindex="-1"><span class="flag flag-sm" data-flag="${it.flag}"></span>${it.label}<small>${it.meta}</small></li>`).join('');
    paintFlags(list);
    const top = trigger.getBoundingClientRect().bottom - calc.getBoundingClientRect().top + 8;
    list.style.top = `${top}px`;
    list.hidden = false;
    trigger.setAttribute('aria-expanded', 'true');
    open = { trigger, kind, side };
    const sel = list.querySelector('[aria-selected="true"]') || list.firstElementChild;
    sel.focus();
  };

  calc.querySelectorAll('.cur').forEach((btn) => {
    btn.addEventListener('click', (e) => { e.stopPropagation(); openList(btn, 'currency', btn.dataset.side); });
  });
  const recChange = document.getElementById('recChange');
  recChange.addEventListener('click', (e) => { e.stopPropagation(); openList(recChange, 'country'); });

  const choose = (li) => {
    if (!open || !li) return;
    const { kind, side, trigger } = open;
    closeList();
    if (kind === 'country') setCountry(li.dataset.id);
    else setCur(side, li.dataset.id);
    trigger.focus();
  };
  list.addEventListener('click', (e) => { e.stopPropagation(); choose(e.target.closest('li')); });
  list.addEventListener('keydown', (e) => {
    const cur = document.activeElement.closest('li');
    if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
      e.preventDefault();
      const next = e.key === 'ArrowDown' ? cur?.nextElementSibling : cur?.previousElementSibling;
      next?.focus();
    } else if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault(); choose(cur);
    } else if (e.key === 'Escape') {
      const t = open?.trigger; closeList(); t?.focus();
    }
  });
  document.addEventListener('click', closeList);

  amountEl.addEventListener('input', () => {
    const raw = amountEl.value.replace(/[^\d,]/g, '');
    const [int = '', dec] = raw.split(',');
    const grouped = int.replace(/^0+(?=\d)/, '').replace(/\B(?=(\d{3})+(?!\d))/g, '.');
    amountEl.value = dec !== undefined ? `${grouped},${dec.slice(0, 2)}` : grouped;
    update();
  });
  update();

  /* ---------- Country grid ---------- */
  const grid = document.getElementById('countries');
  grid.innerHTML = countries.map((c) => `<li><a href="#kalkulator" data-country="${c[0]}"><span class="flag" data-flag="${c[0]}"></span><span>${c[1]}</span></a></li>`).join('');
  paintFlags(grid);
  grid.addEventListener('click', (e) => {
    const a = e.target.closest('a[data-country]');
    if (a) setCountry(a.dataset.country);
  });

  /* ---------- Tabs ---------- */
  const tabs = [...document.querySelectorAll('.seg-tabs [role="tab"]')];
  const selectTab = (tab, focus) => {
    tabs.forEach((t) => {
      const on = t === tab;
      t.setAttribute('aria-selected', on);
      t.tabIndex = on ? 0 : -1;
      const p = document.getElementById(t.getAttribute('aria-controls'));
      p.hidden = !on;
      p.classList.toggle('is-in', on);
    });
    if (focus) tab.focus();
  };
  tabs.forEach((t, i) => {
    t.addEventListener('click', () => selectTab(t));
    t.addEventListener('keydown', (e) => {
      const dir = e.key === 'ArrowRight' ? 1 : e.key === 'ArrowLeft' ? -1 : 0;
      if (dir) { e.preventDefault(); selectTab(tabs[(i + dir + tabs.length) % tabs.length], true); }
    });
  });

  /* ---------- Nav ---------- */
  const nav = document.getElementById('nav');
  const burger = document.getElementById('burger');
  const navRight = document.getElementById('navRight');
  window.addEventListener('scroll', () => nav.classList.toggle('is-scrolled', window.scrollY > 8), { passive: true });
  burger.addEventListener('click', () => {
    const on = burger.getAttribute('aria-expanded') !== 'true';
    burger.setAttribute('aria-expanded', on);
    burger.setAttribute('aria-label', on ? 'Zatvori meni' : 'Otvori meni');
    navRight.classList.toggle('is-open', on);
  });
  navRight.addEventListener('click', (e) => {
    if (e.target.closest('a')) { burger.setAttribute('aria-expanded', 'false'); navRight.classList.remove('is-open'); }
  });

  /* ---------- Signup ---------- */
  const form = document.getElementById('signup');
  const email = document.getElementById('email');
  const msg = document.getElementById('formMsg');
  form.addEventListener('submit', (e) => {
    e.preventDefault();
    const ok = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(email.value.trim());
    email.classList.toggle('is-error', !ok);
    msg.classList.toggle('is-error', !ok);
    msg.textContent = ok ? `Poslali smo link na ${email.value.trim()}. Proveri inbox.` : 'Unesi ispravnu email adresu.';
    if (ok) form.reset();
  });

  /* ---------- QR (decorative) ---------- */
  const qr = document.getElementById('qr');
  if (qr) {
    const N = 25;
    let seed = 7;
    const rnd = () => ((seed = (seed * 16807) % 2147483647) / 2147483647);
    const inFinder = (x, y) => [[0, 0], [N - 7, 0], [0, N - 7]].some(([fx, fy]) => x >= fx - 1 && x < fx + 8 && y >= fy - 1 && y < fy + 8);
    let cells = '';
    for (let y = 0; y < N; y++) for (let x = 0; x < N; x++) if (!inFinder(x, y) && rnd() > 0.52) cells += `M${x} ${y}h1v1h-1z`;
    const finder = (fx, fy) => `M${fx} ${fy}h7v7h-7zM${fx + 1} ${fy + 1}v5h5v-5zM${fx + 2} ${fy + 2}h3v3h-3z`;
    qr.innerHTML = `<path fill="#163300" fill-rule="evenodd" d="${finder(0, 0)}${finder(N - 7, 0)}${finder(0, N - 7)}${cells}"/>`;
  }

  /* ---------- Reveals + counters ---------- */
  if (!root.classList.contains('js')) {
    document.querySelectorAll('[data-count]').forEach((el) => { el.textContent = el.dataset.count + (el.dataset.suffix || ''); });
    return;
  }
  const countUp = (el) => {
    const end = +el.dataset.count;
    const suffix = el.dataset.suffix || '';
    const t0 = performance.now();
    const step = (t) => {
      const p = Math.min((t - t0) / 1200, 1);
      el.textContent = Math.round(end * (1 - Math.pow(1 - p, 3))) + suffix;
      if (p < 1) requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
  };
  const io = new IntersectionObserver((entries) => {
    entries.forEach((en) => {
      if (!en.isIntersecting) return;
      en.target.classList.add('is-in');
      en.target.querySelectorAll('[data-count]').forEach(countUp);
      io.unobserve(en.target);
    });
  }, { threshold: 0.2, rootMargin: '0px 0px -40px 0px' });
  document.querySelectorAll('.reveal, .display').forEach((el) => io.observe(el));
})();
