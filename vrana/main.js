(() => {
  'use strict';
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => [...r.querySelectorAll(s)];
  const fmt = n => n.toLocaleString('sr-RS') + ' RSD';
  const FREE_SHIP = 8000;
  const SIZES = ['S', 'M', 'L', 'XL'];

  const PRODUCTS = [
    { id: 1, n: 'NOĆ 480 Duks', t: 'hoodie', price: 9900, print: 'NOĆ', py: 128, tag: 'Novo', cols: [['Ugalj', '#1b1b1d', '#f3efe6', '#3a1810'], ['Krv', '#b3261e', '#f3efe6', '#4a0f0b']] },
    { id: 2, n: 'KROV Majica', t: 'tee', price: 3900, print: 'KROV', py: 112, cols: [['Kost', '#e9e2d1', '#111', '#3a2a16'], ['Ugalj', '#1b1b1d', '#ff4a2b', '#3a1810']] },
    { id: 3, n: 'TEREN Cargo', t: 'pants', price: 8400, cols: [['Maslina', '#4a4d33', '#fff', '#262a10'], ['Ugalj', '#1b1b1d', '#fff', '#1c1c24']] },
    { id: 4, n: 'MRAK Coach Jakna', t: 'jacket', price: 12900, print: 'VRANA', py: 92, tag: 'Limitirano', cols: [['Noć', '#13233d', '#f3efe6', '#0a1a3a'], ['Ugalj', '#1b1b1d', '#d6ff3f', '#1c2410']] },
    { id: 5, n: 'KANDŽA Kapa', t: 'cap', price: 2900, print: 'V', py: 108, cols: [['Ugalj', '#1b1b1d', '#f3efe6', '#3a1810'], ['Krv', '#b3261e', '#f3efe6', '#4a0f0b']] },
    { id: 6, n: 'ŠAV Beanie', t: 'beanie', price: 2400, cols: [['Kost', '#e9e2d1', '#111', '#3a2a16'], ['Ugalj', '#1b1b1d', '#fff', '#1c1c24']] }
  ];
  const ARCHIVE = [
    ['Garaža Duks', 'hoodie', 7900, 'Rasprodato', '#1b1b1d'],
    ['Dorćol Majica', 'tee', 3200, 'Rasprodato', '#e9e2d1'],
    ['Savamala Jakna', 'jacket', 10900, 'Pre-order', '#13233d'],
    ['Pop-up Kapa', 'cap', 2500, 'Rasprodato', '#b3261e'],
    ['Zemun Cargo', 'pants', 7600, 'Pre-order', '#4a4d33'],
    ['Kosančić Duks', 'hoodie', 8900, 'Rasprodato', '#b3261e'],
    ['Prvi Šav Majica', 'tee', 2900, 'Rasprodato', '#1b1b1d'],
    ['Kalemegdan Beanie', 'beanie', 2200, 'Pre-order', '#e9e2d1']
  ];
  const find = id => PRODUCTS.find(p => p.id === id);

  const garment = (t, color, print, ink, py) =>
    `<svg viewBox="0 0 200 220" style="--c:${color}" aria-hidden="true"><use href="#g-${t}"/>` +
    (print ? `<text x="100" y="${py}" text-anchor="middle" class="print" style="fill:${ink};font-size:${t === 'cap' ? 24 : 20}px">${print}</text>` : '') + `</svg>`;

  /* ---------- toast ---------- */
  const toastEl = $('#toast');
  let toastT;
  function toast(msg) {
    toastEl.textContent = msg;
    toastEl.classList.add('on');
    clearTimeout(toastT);
    toastT = setTimeout(() => toastEl.classList.remove('on'), 2600);
  }

  /* ---------- cart ---------- */
  let cart = [];
  try { cart = JSON.parse(localStorage.getItem('vrana-cart') || '[]'); } catch (e) { cart = []; }
  const save = () => { try { localStorage.setItem('vrana-cart', JSON.stringify(cart)); } catch (e) {} };
  const drawer = $('#drawer'), scrim = $('#scrim');

  function openDrawer() {
    scrim.hidden = false;
    requestAnimationFrame(() => { scrim.classList.add('on'); drawer.classList.add('on'); });
    drawer.setAttribute('aria-hidden', 'false');
    $('#drawerClose').focus();
  }
  function closeDrawer() {
    scrim.classList.remove('on'); drawer.classList.remove('on');
    drawer.setAttribute('aria-hidden', 'true');
    setTimeout(() => { scrim.hidden = true; }, 300);
  }
  $('#bagBtn').addEventListener('click', openDrawer);
  $('#drawerClose').addEventListener('click', closeDrawer);
  scrim.addEventListener('click', closeDrawer);
  document.addEventListener('keydown', e => { if (e.key === 'Escape') closeDrawer(); });

  function addToCart(item) {
    const hit = cart.find(c => c.id === item.id && c.color === item.color && c.size === item.size);
    if (hit) hit.qty++; else cart.push({ ...item, qty: 1 });
    renderCart();
    toast(`Dodato: ${item.name}`);
  }

  function renderCart() {
    save();
    const count = cart.reduce((a, c) => a + c.qty, 0);
    const total = cart.reduce((a, c) => a + c.qty * c.price, 0);
    $('#bagCount').textContent = count;
    $('#drawerCount').textContent = count ? `(${count})` : '';
    $('#total').textContent = fmt(total);
    const left = FREE_SHIP - total;
    $('#shipMsg').textContent = total === 0 ? `Besplatna dostava preko ${fmt(FREE_SHIP)}`
      : left > 0 ? `Još ${fmt(left)} do besplatne dostave` : 'Besplatna dostava je tvoja ✦';
    $('#shipFill').style.width = Math.min(100, total / FREE_SHIP * 100) + '%';
    const list = $('#items');
    if (!cart.length) { list.innerHTML = '<li class="empty">Torba je prazna.</li>'; return; }
    list.innerHTML = cart.map((c, i) => `
      <li class="item">
        <div class="item__img">${garment(c.type, c.hex, c.print, c.ink, c.py)}</div>
        <div><b>${c.name}</b><small>${c.colorName} · ${c.size}</small>
          <div class="qty"><button data-q="-1" data-i="${i}" aria-label="Manje">−</button><span>${c.qty}</span><button data-q="1" data-i="${i}" aria-label="Više">+</button></div></div>
        <div class="item__right">${fmt(c.price * c.qty)}<button data-rm="${i}">Ukloni</button></div>
      </li>`).join('');
  }
  $('#items').addEventListener('click', e => {
    const q = e.target.closest('[data-q]'), rm = e.target.closest('[data-rm]');
    if (q) { const it = cart[+q.dataset.i]; it.qty += +q.dataset.q; if (it.qty < 1) cart.splice(+q.dataset.i, 1); renderCart(); }
    if (rm) { cart.splice(+rm.dataset.rm, 1); renderCart(); }
  });
  $('#checkout').addEventListener('click', () => {
    if (!cart.length) return toast('Torba je prazna');
    toast('Ovo je demo sajt, plaćanje nije aktivno');
  });

  /* ---------- product grid ---------- */
  $('#grid').innerHTML = PRODUCTS.map((p, i) => {
    const needSize = !['cap', 'beanie'].includes(p.t);
    const c = p.cols[0];
    return `
    <article class="card reveal" data-id="${p.id}" data-ci="0" data-size="${needSize ? 'M' : 'Jedna'}">
      <div class="card__stage" style="--glow:${c[3]}">
        <span class="card__no">0${i + 1}</span>${p.tag ? `<span class="card__tag">${p.tag}</span>` : ''}
        <div class="art">${garment(p.t, c[1], p.print, c[2], p.py)}</div>
      </div>
      <div class="card__body">
        <div class="card__row"><h3 class="card__name">${p.n}</h3><span class="card__price">${fmt(p.price)}</span></div>
        <div class="card__ctl"><div class="sw" role="group" aria-label="Boja">${p.cols.map((x, k) => `<button style="background:${x[1]}" data-ci="${k}" aria-pressed="${k === 0}" aria-label="${x[0]}" title="${x[0]}"></button>`).join('')}</div>
        <span class="colname" style="font:500 11px var(--mono);color:var(--mut);letter-spacing:.1em;text-transform:uppercase">${c[0]}</span></div>
        ${needSize ? `<div class="sizes" role="group" aria-label="Veličina">${SIZES.map(s => `<button data-size="${s}" aria-pressed="${s === 'M'}">${s}</button>`).join('')}</div>` : ''}
        <button class="btn btn--solid add">Dodaj u torbu</button>
      </div>
    </article>`;
  }).join('');

  $('#grid').addEventListener('click', e => {
    const card = e.target.closest('.card'); if (!card) return;
    const p = find(+card.dataset.id);
    const sw = e.target.closest('.sw button'), sz = e.target.closest('.sizes button');
    if (sw) {
      const k = +sw.dataset.ci, c = p.cols[k];
      card.dataset.ci = k;
      $$('.sw button', card).forEach(b => b.setAttribute('aria-pressed', b === sw));
      $('.art', card).innerHTML = garment(p.t, c[1], p.print, c[2], p.py);
      $('.card__stage', card).style.setProperty('--glow', c[3]);
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

  /* paket */
  $('#dealBtn').addEventListener('click', () => {
    [[1, 0, 'M'], [2, 0, 'M'], [5, 0, 'Jedna']].forEach(([id, ci, size]) => {
      const p = find(id), c = p.cols[ci];
      addToCart({ id: p.id, name: p.n, price: Math.round(p.price * 13900 / 16700), type: p.t, hex: c[1], ink: c[2], print: p.print, py: p.py, color: c[0], colorName: c[0], size });
    });
    openDrawer();
  });

  /* ---------- arhiva ---------- */
  const alist = $('#alist');
  alist.innerHTML = ARCHIVE.map((a, i) =>
    `<li tabindex="0" data-i="${i}"><span class="n">0${i + 1}</span><span class="t">${a[0]}</span><span class="s ${a[3] === 'Pre-order' ? 'pre' : ''}">${a[3]}</span><span class="p">${fmt(a[2])}</span></li>`).join('');
  function showArchive(i) {
    const a = ARCHIVE[i];
    $$('li', alist).forEach((li, k) => li.classList.toggle('is-on', k === i));
    $('#apSvg').outerHTML = garment(a[1], a[4], '', '', 0).replace('<svg ', '<svg id="apSvg" ');
    $('#apNo').textContent = '0' + (i + 1);
    $('#apName').textContent = a[0];
    $('#apPrice').textContent = fmt(a[2]);
  }
  alist.addEventListener('mouseover', e => { const li = e.target.closest('li'); if (li) showArchive(+li.dataset.i); });
  alist.addEventListener('focusin', e => { const li = e.target.closest('li'); if (li) showArchive(+li.dataset.i); });
  alist.addEventListener('click', e => { const li = e.target.closest('li'); if (li) toast(ARCHIVE[+li.dataset.i][3] === 'Pre-order' ? 'Pre-order se otvara sa sledećim dropom' : 'Ovaj komad je rasprodat'); });
  showArchive(0);

  /* ---------- fit finder ---------- */
  const FITS = {
    regular: { note: 'Klasičan kroj, mera tvoje uobičajene veličine.', scale: 1, rows: [['S', 52, 69, 44], ['M', 55, 71, 46], ['L', 58, 73, 48], ['XL', 61, 75, 50]] },
    boxy: { note: 'Kraći i širi. Pada ravno, sa spuštenim ramenima.', scale: 1.12, rows: [['S', 56, 64, 50], ['M', 59, 66, 52], ['L', 62, 68, 54], ['XL', 65, 70, 56]] },
    over: { note: 'Prostrano i dugo. Uzmi svoju veličinu za pun efekat ili jednu manju.', scale: 1.26, rows: [['S', 60, 74, 56], ['M', 63, 76, 58], ['L', 66, 78, 60], ['XL', 69, 80, 62]] }
  };
  function setFit(k) {
    const f = FITS[k];
    $('#fitNote').textContent = f.note;
    $('#fitTee').style.transform = `scale(${f.scale}, ${k === 'boxy' ? .94 : k === 'over' ? 1.04 : 1})`;
    $('#fitBody').innerHTML = f.rows.map(r => `<tr><td>${r[0]}</td><td>${r[1]} cm</td><td>${r[2]} cm</td><td>${r[3]} cm</td></tr>`).join('');
    $$('.fit__tabs button').forEach(b => { const on = b.dataset.fit === k; b.classList.toggle('is-on', on); b.setAttribute('aria-selected', on); });
  }
  $$('.fit__tabs button').forEach(b => b.addEventListener('click', () => setFit(b.dataset.fit)));
  setFit('regular');

  /* ---------- odbrojavanje do subote 18:00 ---------- */
  function nextDrop() {
    const d = new Date(); d.setHours(18, 0, 0, 0);
    d.setDate(d.getDate() + ((6 - d.getDay() + 7) % 7));
    if (d <= new Date()) d.setDate(d.getDate() + 7);
    return d;
  }
  let target = nextDrop();
  const pad2 = n => String(n).padStart(2, '0');
  function tick() {
    let s = Math.max(0, Math.floor((target - new Date()) / 1000));
    if (!s) target = nextDrop();
    $('#cd-d').textContent = pad2(Math.floor(s / 86400));
    $('#cd-h').textContent = pad2(Math.floor(s % 86400 / 3600));
    $('#cd-m').textContent = pad2(Math.floor(s % 3600 / 60));
    $('#cd-s').textContent = pad2(s % 60);
  }
  tick();
  let cdTimer = setInterval(tick, 1000);
  document.addEventListener('visibilitychange', () => {
    clearInterval(cdTimer);
    if (!document.hidden) { tick(); cdTimer = setInterval(tick, 1000); }
  });

  /* ---------- zakazivanje ---------- */
  const modal = $('#bookModal'), bookDay = $('#bookDay');
  const days = ['Ned', 'Pon', 'Uto', 'Sre', 'Čet', 'Pet', 'Sub'];
  bookDay.innerHTML = Array.from({ length: 7 }, (_, i) => {
    const d = new Date(); d.setDate(d.getDate() + i + 1);
    return `<option>${days[d.getDay()]} ${d.getDate()}.${d.getMonth() + 1}.</option>`;
  }).join('');
  let city = '';
  $$('[data-book]').forEach(b => b.addEventListener('click', () => {
    city = b.dataset.book; $('#bookCity').textContent = ' · ' + city;
    if (modal.showModal) modal.showModal(); else toast('Termin: ' + city);
  }));
  modal.addEventListener('close', () => {
    if (modal.returnValue === 'ok') toast(`Termin potvrđen: ${city}, ${bookDay.value}`);
    modal.returnValue = '';
  });

  /* ---------- newsletter ---------- */
  $('#newsForm').addEventListener('submit', e => {
    e.preventDefault();
    const v = $('#email').value.trim(), msg = $('#newsMsg');
    if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(v)) { msg.textContent = 'Upiši ispravan email.'; return; }
    msg.textContent = 'Upisan si. Vidimo se na dropu ✦'; $('#email').value = '';
  });

  /* ---------- meni ---------- */
  const burger = $('#burger'), menu = $('#menu');
  burger.addEventListener('click', () => {
    const on = menu.classList.toggle('on');
    burger.setAttribute('aria-expanded', on);
  });
  $$('a', menu).forEach(a => a.addEventListener('click', () => { menu.classList.remove('on'); burger.setAttribute('aria-expanded', 'false'); }));

  /* ---------- otkrivanje pri skrolu ---------- */
  const revealEls = $$('.reveal');
  if ('IntersectionObserver' in window) {
    const io = new IntersectionObserver(es => es.forEach(en => {
      if (en.isIntersecting) { en.target.classList.add('in'); io.unobserve(en.target); }
    }), { threshold: .12, rootMargin: '0px 0px -6% 0px' });
    revealEls.forEach((el, i) => { el.style.transitionDelay = (i % 3) * 70 + 'ms'; io.observe(el); });
  } else revealEls.forEach(el => el.classList.add('in'));

  renderCart();
})();
