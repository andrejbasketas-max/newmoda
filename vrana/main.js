(() => {
  'use strict';
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => [...r.querySelectorAll(s)];
  const root = document.documentElement;
  const fmt = n => n.toLocaleString('sr-RS') + ' RSD';
  const clamp = (v, a = 0, b = 1) => Math.min(b, Math.max(a, v));
  const lerp = (a, b, t) => a + (b - a) * t;
  const reduce = matchMedia('(prefers-reduced-motion:reduce)').matches;
  const finePointer = matchMedia('(hover:hover) and (pointer:fine)').matches;
  const FREE_SHIP = 8000;
  const SIZES = ['S', 'M', 'L', 'XL'];

  /* ---------------------------------------------------------------- podaci */
  // boja: [ime, boja odeće, boja štampe, boja pločice]
  const PRODUCTS = [
    { id: 1, n: 'NOĆ 480 Duks', t: 'hoodie', price: 9900, print: 'NOĆ', py: 132, tag: 'Novo', cols: [['Ugalj', '#17171a', '#ebe6da', '#d9d2c0'], ['Krv', '#c0301f', '#ebe6da', '#8d977b']] },
    { id: 2, n: 'KROV Majica', t: 'tee', price: 3900, print: 'KROV', py: 112, cols: [['Kost', '#ebe6da', '#0d0d0c', '#ea3a1e'], ['Ugalj', '#17171a', '#ea3a1e', '#d9d2c0']] },
    { id: 3, n: 'TEREN Cargo', t: 'pants', price: 8400, cols: [['Maslina', '#4a4d33', '#fff', '#d9d2c0'], ['Ugalj', '#17171a', '#fff', '#8d977b']] },
    { id: 4, n: 'MRAK Coach Jakna', t: 'jacket', price: 12900, print: 'VRANA', py: 98, tag: 'Limitirano', cols: [['Noć', '#13233d', '#ebe6da', '#d9d2c0'], ['Ugalj', '#17171a', '#ea3a1e', '#1f3a8a']] },
    { id: 5, n: 'KANDŽA Kapa', t: 'cap', price: 2900, print: 'V', py: 108, cols: [['Ugalj', '#17171a', '#ebe6da', '#d9d2c0'], ['Krv', '#c0301f', '#ebe6da', '#1f3a8a']] },
    { id: 6, n: 'ŠAV Beanie', t: 'beanie', price: 2400, cols: [['Kost', '#ebe6da', '#0d0d0c', '#ea3a1e'], ['Ugalj', '#17171a', '#fff', '#d9d2c0']] }
  ];
  const ARCHIVE = [
    ['Garaža Duks', 'hoodie', 7900, 'Rasprodato', '#17171a'],
    ['Dorćol Majica', 'tee', 3200, 'Rasprodato', '#ebe6da'],
    ['Savamala Jakna', 'jacket', 10900, 'Pre-order', '#13233d'],
    ['Pop-up Kapa', 'cap', 2500, 'Rasprodato', '#c0301f'],
    ['Zemun Cargo', 'pants', 7600, 'Pre-order', '#4a4d33'],
    ['Kosančić Duks', 'hoodie', 8900, 'Rasprodato', '#c0301f'],
    ['Prvi Šav Majica', 'tee', 2900, 'Rasprodato', '#17171a'],
    ['Kalemegdan Beanie', 'beanie', 2200, 'Pre-order', '#ebe6da']
  ];
  const find = id => PRODUCTS.find(p => p.id === id);
  const garment = (t, color, print, ink, py) =>
    `<svg viewBox="0 0 200 220" style="--c:${color}" aria-hidden="true"><use href="#g-${t}"/>` +
    (print ? `<text x="100" y="${py}" text-anchor="middle" class="print" style="fill:${ink};font-size:${t === 'cap' ? 26 : 22}px">${print}</text>` : '') + `</svg>`;

  /* ---------------------------------------------------------------- toast */
  const toastEl = $('#toast');
  let toastT;
  function toast(msg, action) {
    toastEl.textContent = msg;
    toastEl.classList.toggle('is-act', !!action);
    toastEl.onclick = action || null;
    toastEl.classList.add('on');
    clearTimeout(toastT);
    toastT = setTimeout(() => toastEl.classList.remove('on'), 2600);
  }

  /* ---------------------------------------------------------------- torba */
  let cart = [];
  try { cart = JSON.parse(localStorage.getItem('vrana-cart') || '[]'); } catch (e) { cart = []; }
  const saveCart = () => { try { localStorage.setItem('vrana-cart', JSON.stringify(cart)); } catch (e) {} };
  const drawer = $('#drawer'), scrim = $('#scrim');

  function openDrawer() {
    toastEl.classList.remove('on');
    scrim.hidden = false;
    requestAnimationFrame(() => { scrim.classList.add('on'); drawer.classList.add('on'); });
    drawer.setAttribute('aria-hidden', 'false');
    $('#drawerClose').focus();
  }
  function closeDrawer() {
    scrim.classList.remove('on'); drawer.classList.remove('on');
    drawer.setAttribute('aria-hidden', 'true');
    setTimeout(() => { scrim.hidden = true; }, 400);
  }
  $('#bagBtn').addEventListener('click', openDrawer);
  $('#drawerClose').addEventListener('click', closeDrawer);
  scrim.addEventListener('click', closeDrawer);
  document.addEventListener('keydown', e => { if (e.key === 'Escape') { closeDrawer(); closeMenu(); } });

  function addToCart(item) {
    const hit = cart.find(c => c.id === item.id && c.color === item.color && c.size === item.size);
    if (hit) hit.qty++; else cart.push({ ...item, qty: 1 });
    renderCart();
    $('#hdr').classList.remove('is-hide');
    toast(`Dodato: ${item.name} — otvori torbu →`, openDrawer);
  }
  function renderCart() {
    saveCart();
    const count = cart.reduce((a, c) => a + c.qty, 0);
    const total = cart.reduce((a, c) => a + c.qty * c.price, 0);
    $('#bagCount').textContent = count;
    $('#drawerCount').textContent = count ? `(${count})` : '';
    $('#total').textContent = fmt(total);
    const left = FREE_SHIP - total;
    $('#shipMsg').textContent = total === 0 ? `Besplatna dostava preko ${fmt(FREE_SHIP)}`
      : left > 0 ? `Još ${fmt(left)} do besplatne dostave` : 'Besplatna dostava je tvoja';
    $('#shipFill').style.width = Math.min(100, total / FREE_SHIP * 100) + '%';
    const list = $('#items');
    if (!cart.length) { list.innerHTML = '<li class="empty">Torba je prazna.</li>'; return; }
    list.innerHTML = cart.map((c, i) => `
      <li class="item">
        <div class="item__img">${garment(c.type, c.hex, c.print, c.ink, c.py)}</div>
        <div><b>${c.name}</b><small class="f-mono">${c.colorName} · ${c.size}</small>
          <div class="qty"><button data-q="-1" data-i="${i}" aria-label="Manje">−</button><span>${c.qty}</span><button data-q="1" data-i="${i}" aria-label="Više">+</button></div></div>
        <div class="item__right">${fmt(c.price * c.qty)}<button data-rm="${i}">Ukloni</button></div>
      </li>`).join('');
  }
  $('#items').addEventListener('click', e => {
    const q = e.target.closest('[data-q]'), rm = e.target.closest('[data-rm]');
    if (q) { const it = cart[+q.dataset.i]; it.qty += +q.dataset.q; if (it.qty < 1) cart.splice(+q.dataset.i, 1); renderCart(); }
    if (rm) { cart.splice(+rm.dataset.rm, 1); renderCart(); }
  });
  $('#checkout').addEventListener('click', () => toast(cart.length ? 'Ovo je demo sajt, plaćanje nije aktivno' : 'Torba je prazna'));

  /* ---------------------------------------------------------------- drop mreža */
  $('#grid').innerHTML = PRODUCTS.map((p, i) => {
    const needSize = !['cap', 'beanie'].includes(p.t);
    const c = p.cols[0];
    return `
    <article class="card" data-id="${p.id}" data-ci="0" data-size="${needSize ? 'M' : 'Jedna'}" data-reveal="up">
      <div class="card__tile" style="--tile:${c[3]}">
        <span class="card__i f-mono">0${i + 1}/06</span>${p.tag ? `<span class="card__tag f-mono">${p.tag}</span>` : ''}
        <div class="art">${garment(p.t, c[1], p.print, c[2], p.py)}</div>
      </div>
      <div class="card__info">
        <div class="card__r1"><h3 class="card__n f-disp">${p.n}</h3><span class="card__p f-mono">${fmt(p.price)}</span></div>
        <div class="card__r2"><div class="sw" role="group" aria-label="Boja">${p.cols.map((x, k) => `<button style="background:${x[1]}" data-ci="${k}" aria-pressed="${k === 0}" aria-label="${x[0]}" title="${x[0]}"></button>`).join('')}</div><span class="colname f-mono">${c[0]}</span></div>
        ${needSize ? `<div class="sizes f-mono" role="group" aria-label="Veličina">${SIZES.map(s => `<button data-size="${s}" aria-pressed="${s === 'M'}">${s}</button>`).join('')}</div>` : ''}
        <button class="add" data-cursor="Dodaj"><span>Dodaj u torbu</span><b aria-hidden="true">+</b></button>
      </div>
    </article>`;
  }).join('') + '<a class="grid__more f-hand" href="#arhiva" data-reveal="fade">to je sve za ovaj drop.<b>ostalo je u arhivi →</b></a>';

  $('#grid').addEventListener('click', e => {
    const card = e.target.closest('.card'); if (!card) return;
    const p = find(+card.dataset.id);
    const sw = e.target.closest('.sw button'), sz = e.target.closest('.sizes button');
    if (sw) {
      const k = +sw.dataset.ci, c = p.cols[k];
      card.dataset.ci = k;
      $$('.sw button', card).forEach(b => b.setAttribute('aria-pressed', b === sw));
      $('.art', card).innerHTML = garment(p.t, c[1], p.print, c[2], p.py);
      $('.card__tile', card).style.setProperty('--tile', c[3]);
      $('.colname', card).textContent = c[0];
    }
    if (sz) {
      card.dataset.size = sz.dataset.size;
      $$('.sizes button', card).forEach(b => b.setAttribute('aria-pressed', b === sz));
    }
    if (e.target.closest('.add')) {
      const c = p.cols[+card.dataset.ci];
      addToCart({ id: p.id, name: p.n, price: p.price, type: p.t, hex: c[1], ink: c[2], print: p.print, py: p.py, color: c[0], colorName: c[0], size: card.dataset.size });
    }
  });

  $('#dealBtn').addEventListener('click', () => {
    [[1, 0, 'M'], [2, 0, 'M'], [5, 0, 'Jedna']].forEach(([id, ci, size]) => {
      const p = find(id), c = p.cols[ci];
      addToCart({ id: p.id, name: p.n, price: Math.round(p.price * 13900 / 16700), type: p.t, hex: c[1], ink: c[2], print: p.print, py: p.py, color: c[0], colorName: c[0], size });
    });
    openDrawer();
  });

  /* ---------------------------------------------------------------- arhiva + plutajući pregled */
  const alist = $('#alist'), af = $('#afloat'), afSvg = () => $('#afSvg');
  alist.innerHTML = ARCHIVE.map((a, i) =>
    `<li tabindex="0" data-i="${i}"><span class="n f-mono">0${i + 1}</span><span class="t f-disp">${a[0]}</span><span class="s f-mono ${a[3] === 'Pre-order' ? 'is-pre' : ''}">${a[3]}</span><span class="p f-mono">${fmt(a[2])}</span></li>`).join('');
  function showArchive(i) {
    const a = ARCHIVE[i];
    afSvg().outerHTML = garment(a[1], a[4], '', '', 0).replace('<svg ', '<svg id="afSvg" ');
    $('#afTag').textContent = `0${i + 1} — ${a[0]}`;
  }
  const af_ = { x: 0, y: 0, tx: 0, ty: 0, rot: 0, on: false, raf: 0 };
  function afLoop() {
    af_.x = lerp(af_.x, af_.tx, .14); af_.y = lerp(af_.y, af_.ty, .14);
    const vx = af_.tx - af_.x;
    af_.rot = lerp(af_.rot, clamp(vx * .06, -14, 14), .2);
    af.style.setProperty('--fx', `${af_.x + 28}px`);
    af.style.setProperty('--fy', `${af_.y - af.offsetHeight / 2}px`);
    af.style.setProperty('--fr', `${af_.rot}deg`);
    if (af_.on || Math.abs(vx) > .5) af_.raf = requestAnimationFrame(afLoop); else af_.raf = 0;
  }
  if (finePointer) {
    alist.addEventListener('mouseover', e => { const li = e.target.closest('li'); if (li) showArchive(+li.dataset.i); });
    alist.addEventListener('mousemove', e => {
      af_.tx = e.clientX; af_.ty = e.clientY;
      if (!af_.on) { af_.on = true; af_.x = af_.tx; af_.y = af_.ty; af.classList.add('on'); }
      if (!af_.raf) af_.raf = requestAnimationFrame(afLoop);
    });
    alist.addEventListener('mouseleave', () => { af_.on = false; af.classList.remove('on'); });
  }
  alist.addEventListener('click', e => { const li = e.target.closest('li'); if (li) toast(ARCHIVE[+li.dataset.i][3] === 'Pre-order' ? 'Pre-order se otvara sa sledećim dropom' : 'Ovaj komad je rasprodat'); });
  showArchive(0);

  /* ---------------------------------------------------------------- mere */
  const FITS = {
    regular: { note: 'Klasičan kroj, mera tvoje uobičajene veličine.', sx: 1, sy: 1, rows: [['S', 52, 69, 44], ['M', 55, 71, 46], ['L', 58, 73, 48], ['XL', 61, 75, 50]] },
    boxy: { note: 'Kraći i širi. Pada ravno, sa spuštenim ramenima.', sx: 1.14, sy: .93, rows: [['S', 56, 64, 50], ['M', 59, 66, 52], ['L', 62, 68, 54], ['XL', 65, 70, 56]] },
    over: { note: 'Prostrano i dugo. Uzmi svoju veličinu ili jednu manju.', sx: 1.28, sy: 1.05, rows: [['S', 60, 74, 56], ['M', 63, 76, 58], ['L', 66, 78, 60], ['XL', 69, 80, 62]] }
  };
  function setFit(k) {
    const f = FITS[k];
    $('#fitNote').textContent = f.note;
    $('#fitTee').style.transform = `scale(${f.sx}, ${f.sy})`;
    $('#fitBody').innerHTML = f.rows.map(r => `<tr><td>${r[0]}</td><td>${r[1]} cm</td><td>${r[2]} cm</td><td>${r[3]} cm</td></tr>`).join('');
    $$('.fit__tabs button').forEach(b => { const on = b.dataset.fit === k; b.classList.toggle('is-on', on); b.setAttribute('aria-selected', on); });
  }
  $$('.fit__tabs button').forEach(b => b.addEventListener('click', () => setFit(b.dataset.fit)));
  setFit('regular');

  /* ---------------------------------------------------------------- odbrojavanje + sat */
  function nextDrop() {
    const d = new Date(); d.setHours(18, 0, 0, 0);
    d.setDate(d.getDate() + ((6 - d.getDay() + 7) % 7));
    if (d <= new Date()) d.setDate(d.getDate() + 7);
    return d;
  }
  let target = nextDrop();
  const p2 = n => String(n).padStart(2, '0');
  function tick() {
    const s = Math.max(0, Math.floor((target - new Date()) / 1000));
    if (!s) target = nextDrop();
    $('#cd-d').textContent = p2(Math.floor(s / 86400));
    $('#cd-h').textContent = p2(Math.floor(s % 86400 / 3600));
    $('#cd-m').textContent = p2(Math.floor(s % 3600 / 60));
    $('#cd-s').textContent = p2(s % 60);
  }
  const clockFmt = new Intl.DateTimeFormat('sr-RS', { timeZone: 'Europe/Belgrade', hour: '2-digit', minute: '2-digit', hour12: false });
  const tickClock = () => { $('#clock').textContent = clockFmt.format(new Date()); };
  tick(); tickClock();
  let timers = [setInterval(tick, 1000), setInterval(tickClock, 15000)];
  document.addEventListener('visibilitychange', () => {
    timers.forEach(clearInterval);
    if (!document.hidden) { tick(); tickClock(); timers = [setInterval(tick, 1000), setInterval(tickClock, 15000)]; }
  });

  /* ---------------------------------------------------------------- termin, newsletter, meni */
  const modal = $('#bookModal'), bookDay = $('#bookDay');
  const days = ['Ned', 'Pon', 'Uto', 'Sre', 'Čet', 'Pet', 'Sub'];
  bookDay.innerHTML = Array.from({ length: 7 }, (_, i) => {
    const d = new Date(); d.setDate(d.getDate() + i + 1);
    return `<option>${days[d.getDay()]} ${d.getDate()}.${d.getMonth() + 1}.</option>`;
  }).join('');
  let city = '';
  $$('[data-book]').forEach(b => b.addEventListener('click', () => {
    city = b.dataset.book; $('#bookCity').textContent = city;
    if (modal.showModal) modal.showModal(); else toast('Termin: ' + city);
  }));
  modal.addEventListener('close', () => {
    if (modal.returnValue === 'ok') toast(`Termin potvrđen: ${city}, ${bookDay.value}`);
    modal.returnValue = '';
  });
  $('#newsForm').addEventListener('submit', e => {
    e.preventDefault();
    const v = $('#email').value.trim(), msg = $('#newsMsg');
    if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(v)) { msg.textContent = 'Upiši ispravan email.'; return; }
    msg.textContent = 'Upisan si. Vidimo se na dropu.'; $('#email').value = '';
  });

  const burger = $('#burger'), menu = $('#menu');
  function closeMenu() { menu.classList.remove('on'); burger.setAttribute('aria-expanded', 'false'); }
  burger.addEventListener('click', () => {
    const on = menu.classList.toggle('on');
    burger.setAttribute('aria-expanded', on);
  });
  $$('a', menu).forEach(a => a.addEventListener('click', closeMenu));

  /* ---------------------------------------------------------------- razdvajanje teksta */
  let chIndex = 0;
  $$('[data-split]').forEach(el => {
    const txt = el.textContent;
    el.textContent = '';
    for (const c of txt) {
      const s = document.createElement('span');
      s.className = 'ch'; s.style.setProperty('--i', chIndex++);
      s.textContent = c; el.appendChild(s);
    }
    el.classList.add('split-done');
  });
  const chars = $$('.f-disp .ch');

  // reči koje se otkrivaju skrolom
  const scrub = $('[data-scrub]');
  const scrubWords = [];
  (function wrap(node) {
    [...node.childNodes].forEach(n => {
      if (n.nodeType === 3) {
        const frag = document.createDocumentFragment();
        n.textContent.split(/(\s+)/).forEach(part => {
          if (!part) return;
          if (/^\s+$/.test(part)) { frag.appendChild(document.createTextNode(part)); return; }
          const w = document.createElement('span'); w.className = 'w'; w.textContent = part;
          frag.appendChild(w); scrubWords.push(w);
        });
        n.replaceWith(frag);
      } else if (n.nodeType === 1) wrap(n);
    });
  })(scrub);

  /* ---------------------------------------------------------------- otkrivanje pri skrolu + brojači */
  const countEls = $$('[data-count]');
  function countUp(el) {
    const end = +el.dataset.count, t0 = performance.now(), dur = 1500;
    (function step(t) {
      const k = clamp((t - t0) / dur);
      el.textContent = Math.round(end * (1 - Math.pow(1 - k, 4)));
      if (k < 1) requestAnimationFrame(step);
    })(t0);
  }
  const revealEls = $$('[data-reveal], .sh, .news__h, .draw, .stats, .story__l');
  if ('IntersectionObserver' in window && !reduce) {
    const io = new IntersectionObserver(es => es.forEach(en => {
      if (!en.isIntersecting) return;
      en.target.classList.add('in');
      if (en.target.classList.contains('stats')) $$('[data-count]', en.target).forEach(countUp);
      io.unobserve(en.target);
    }), { threshold: .15, rootMargin: '0px 0px -8% 0px' });
    revealEls.forEach(el => io.observe(el));
  } else revealEls.forEach(el => el.classList.add('in'));
  $$('.draw').forEach(svg => $$('path', svg).forEach(p => p.style.setProperty('--len', Math.ceil(p.getTotalLength()) + 4)));

  /* ---------------------------------------------------------------- preloader → hero */
  const hero = $('#hero'), pre = $('#pre');
  function heroIn() {
    hero.classList.add('is-in');
    setTimeout(() => $('.hero__arrow')?.classList.add('in'), 1400);
  }
  if (getComputedStyle(pre).display !== 'none') {
    const t0 = performance.now(), D = 1000;
    requestAnimationFrame(() => pre.classList.add('is-on'));
    (function step(t) {
      const k = clamp((t - t0) / D), e = 1 - Math.pow(1 - k, 2);
      $('#preN').textContent = String(Math.round(e * 100)).padStart(3, '0');
      $('#preBar').style.transform = `scaleX(${e})`;
      if (k < 1) requestAnimationFrame(step);
      else setTimeout(() => {
        pre.classList.add('is-out');
        try { sessionStorage.setItem('vrana-pre', '1'); } catch (e2) {}
        setTimeout(heroIn, 350);
        setTimeout(() => pre.remove(), 1000);
      }, 150);
    })(t0);
  } else heroIn();

  /* ---------------------------------------------------------------- kursor + magnetna dugmad */
  const ring = $('#ring');
  if (finePointer && !reduce) {
    root.classList.add('has-ring');
    let rx = 0, ry = 0, tx = 0, ty = 0, started = false;
    addEventListener('mousemove', e => { tx = e.clientX; ty = e.clientY; if (!started) { started = true; rx = tx; ry = ty; } }, { passive: true });
    (function loop() {
      rx = lerp(rx, tx, .22); ry = lerp(ry, ty, .22);
      ring.style.translate = `${rx}px ${ry}px`;
      requestAnimationFrame(loop);
    })();
    document.addEventListener('mouseover', e => {
      const lab = e.target.closest('[data-cursor]');
      if (lab) { ring.classList.add('is-label'); $('span', ring).textContent = lab.dataset.cursor; }
      else ring.classList.remove('is-label');
      ring.classList.toggle('is-link', !lab && !!e.target.closest('a,button,input,select,summary,li[tabindex]'));
    });
    addEventListener('mousedown', () => ring.classList.add('is-down'));
    addEventListener('mouseup', () => ring.classList.remove('is-down'));
    $$('[data-magnet]').forEach(el => {
      el.addEventListener('mousemove', e => {
        const r = el.getBoundingClientRect();
        el.style.translate = `${(e.clientX - r.left - r.width / 2) * .22}px ${(e.clientY - r.top - r.height / 2) * .35}px`;
      });
      el.addEventListener('mouseleave', () => { el.style.translate = ''; });
    });
  }

  /* ---------------------------------------------------------------- hero: slova se šire pod mišem */
  if (finePointer && !reduce) {
    let hx = -999, hy = -999, hraf = 0;
    const apply = () => {
      hraf = 0;
      const R = innerWidth * .26;
      chars.forEach(c => {
        const r = c.getBoundingClientRect();
        const d = Math.hypot(r.left + r.width / 2 - hx, r.top + r.height / 2 - hy);
        const k = clamp(1 - d / R);
        c.style.fontVariationSettings = `"wdth" ${(62 + k * k * 30).toFixed(1)}`;
      });
    };
    hero.addEventListener('mousemove', e => {
      hx = e.clientX; hy = e.clientY;
      if (!hraf) hraf = requestAnimationFrame(apply);
      const fig = $('#heroFig');
      fig.style.setProperty('--tx', `${(e.clientX / innerWidth - .5) * -26}px`);
      fig.style.setProperty('--ty', `${(e.clientY / innerHeight - .5) * -18}px`);
    });
    hero.addEventListener('mouseleave', () => {
      hx = hy = -999; if (!hraf) hraf = requestAnimationFrame(apply);
    });
  }

  /* ---------------------------------------------------------------- skrol: jedna petlja za sve */
  const progress = $('#progress'), hdr = $('#hdr');
  const tapeA = $('.tape__row--a .tape__t'), tapeB = $('.tape__row--b .tape__t');
  const look = $('#look'), track = $('#lookTrack'), lps = $$('.lp');
  const tl = $('#tl');
  let lastY = scrollY, vel = 0, skew = 0, posA = 0, posB = 0, halfA = 0, halfB = 0, ticking = false;
  const measure = () => { halfA = tapeA.scrollWidth / 2; halfB = tapeB.scrollWidth / 2; posB = -halfB; };
  measure(); addEventListener('resize', measure);
  document.fonts && document.fonts.ready.then(measure);

  function onScroll() {
    const y = scrollY, vh = innerHeight;
    vel = y - lastY;
    // traka napretka
    progress.style.transform = `scaleX(${clamp(y / (root.scrollHeight - vh))})`;
    // zaglavlje se krije pri skrolu nadole
    if (!menu.classList.contains('on')) { if (y > 240 && vel > 4) hdr.classList.add('is-hide'); else if (vel < -4 || y <= 240) hdr.classList.remove('is-hide'); }
    lastY = y;
    // reči u manifestu
    let r = scrub.getBoundingClientRect();
    if (r.top < vh && r.bottom > 0) {
      const p = clamp((vh * .82 - r.top) / (r.height + vh * .3));
      const n = Math.round(p * scrubWords.length * 1.12);
      scrubWords.forEach((w, i) => w.classList.toggle('on', i < n));
    }
    // lookbook: zakačen horizontalni skrol (samo na većim ekranima)
    if (innerWidth > 1000) {
      r = look.getBoundingClientRect();
      if (r.top < vh && r.bottom > 0) {
        const p = clamp(-r.top / (r.height - vh));
        const max = track.scrollWidth - innerWidth;
        look.style.setProperty('--lx', `${-p * max}px`);
        look.style.setProperty('--lp', p.toFixed(4));
        $('#lookN').textContent = p2(Math.min(5, Math.round(p * 4) + 1));
        lps.forEach(el => {
          const b = el.getBoundingClientRect();
          el.style.setProperty('--px', `${((b.left + b.width / 2) / innerWidth - .5) * -90}px`);
        });
      }
    }
    // vremenska linija
    r = tl.getBoundingClientRect();
    if (r.top < vh && r.bottom > 0) {
      const p = clamp((vh * .6 - r.top) / r.height);
      tl.style.setProperty('--tlp', p.toFixed(4));
      $$('li', tl).forEach(li => li.classList.toggle('on', li.getBoundingClientRect().top < vh * .6));
    }
    ticking = false;
  }
  addEventListener('scroll', () => { if (!ticking) { ticking = true; requestAnimationFrame(onScroll); } }, { passive: true });
  onScroll();

  // trake: stalno kretanje + ubrzanje i iskošenje prema brzini skrola
  if (!reduce) {
    (function tape() {
      const v = scrollY - (tape.y ?? scrollY); tape.y = scrollY;
      skew = lerp(skew, clamp(v * .22, -9, 9), .12);
      const boost = Math.min(Math.abs(v) * .5, 18);
      posA -= .9 + boost; if (posA <= -halfA) posA += halfA;
      posB += .7 + boost; if (posB >= 0) posB -= halfB;
      tapeA.style.setProperty('--tx', `${posA}px`); tapeA.style.setProperty('--sk', `${-skew}deg`);
      tapeB.style.setProperty('--tx', `${posB}px`); tapeB.style.setProperty('--sk', `${-skew}deg`);
      requestAnimationFrame(tape);
    })();
  }

  renderCart();
})();
