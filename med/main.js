(() => {
  const { PRODUCTS, LEVELS, byId, jarSVG, artSVG } = window.MED;
  const $ = (s, el = document) => el.querySelector(s);
  const $$ = (s, el = document) => [...el.querySelectorAll(s)];
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const rsd = (n) => n.toLocaleString('sr-RS') + ' RSD';
  const FREE_SHIP = 3000;
  const SHIP = 390;

  // ---------- Render products ----------
  $('#products').innerHTML = PRODUCTS.map((p) => `
    <li class="product" data-id="${p.id}">
      <div class="jar" data-jar="${p.id}"></div>
      <div class="p-tags">
        <span class="badge heat" title="Jačina ukusa">Jačina · ${LEVELS[p.level]} <i aria-hidden="true">${'●'.repeat(p.level)}${'○'.repeat(3 - p.level)}</i></span>
      </div>
      <h3 class="p-name">${p.name}</h3>
      <p class="micro">${p.notes}</p>
      <div class="sizes" role="radiogroup" aria-label="Veličina tegle">
        ${p.sizes.map(([s], i) => `<button class="pill size" role="radio" aria-checked="${i === 0}" data-size="${i}">${s}</button>`).join('')}
      </div>
      <div class="p-buy">
        <span class="price">${rsd(p.sizes[0][1])}</span>
        <button class="btn" data-add="${p.id}">Dodaj u korpu</button>
      </div>
    </li>`).join('');

  // Jars + illustrations
  $$('[data-jar]').forEach((el) => { el.innerHTML = jarSVG(byId(el.dataset.jar)); });
  $$('.art[data-art]').forEach((el) => { el.innerHTML = artSVG(el.dataset.art); });

  // ---------- Size selection ----------
  $('#products').addEventListener('click', (e) => {
    const btn = e.target.closest('.size');
    if (!btn) return;
    const card = btn.closest('.product');
    const p = byId(card.dataset.id);
    const prev = $('.size[aria-checked="true"]', card);
    $$('.size', card).forEach((b) => b.setAttribute('aria-checked', b === btn));
    const el = $('.price', card);
    const from = p.sizes[+prev.dataset.size][1], to = p.sizes[+btn.dataset.size][1];
    if (window.GMFX) window.GMFX.price(el, from, to, rsd);
    else el.textContent = rsd(to);
  });

  // ---------- Cart ----------
  let cart = [];
  try { cart = JSON.parse(localStorage.getItem('gm-cart')) || []; } catch { cart = []; }
  const save = () => { try { localStorage.setItem('gm-cart', JSON.stringify(cart)); } catch {} };

  const cartDlg = $('#cart');
  const line = (it) => byId(it.id).sizes[it.size];

  function renderCart() {
    const count = cart.reduce((n, it) => n + it.qty, 0);
    $$('[data-cart-count]').forEach((el) => { el.textContent = count; el.hidden = !count; });

    $('#cartItems').innerHTML = cart.map((it, i) => {
      const p = byId(it.id);
      const [size, price] = line(it);
      return `<li class="c-item">
        <div class="c-jar">${jarSVG(p)}</div>
        <div class="c-info">
          <p class="c-name">${p.name}</p>
          <p class="micro">${size} · ${rsd(price)}</p>
          <div class="qty">
            <button class="pill pill-sq" data-dec="${i}" aria-label="Smanji količinu"><svg viewBox="0 0 256 256" aria-hidden="true"><use href="#i-minus"/></svg></button>
            <span aria-live="polite">${it.qty}</span>
            <button class="pill pill-sq" data-inc="${i}" aria-label="Povećaj količinu"><svg viewBox="0 0 256 256" aria-hidden="true"><use href="#i-plus"/></svg></button>
          </div>
        </div>
        <button class="c-remove" data-rm="${i}">Ukloni</button>
      </li>`;
    }).join('');

    const sub = cart.reduce((s, it) => s + line(it)[1] * it.qty, 0);
    const ship = !sub || sub >= FREE_SHIP ? 0 : SHIP;
    $('#cartEmpty').hidden = !!cart.length;
    $('#cartSum').hidden = !cart.length;
    $('#sumSub').textContent = rsd(sub);
    $('#sumShip').textContent = ship ? rsd(ship) : 'Besplatna';
    $('#sumTotal').textContent = rsd(sub + ship);
    $('#shipHint').textContent = ship
      ? `Još ${rsd(FREE_SHIP - sub)} do besplatne dostave.`
      : 'Dostava je besplatna.';
  }

  function add(id, size = 0) {
    const hit = cart.find((it) => it.id === id && it.size === size);
    hit ? hit.qty++ : cart.push({ id, size, qty: 1 });
    save();
    renderCart();
    const p = byId(id);
    toast(`${p.name} · ${p.sizes[size][0]} je u korpi`);
    bump();
  }

  $('#cartItems').addEventListener('click', (e) => {
    const t = e.target.closest('button');
    if (!t) return;
    const i = +(t.dataset.inc ?? t.dataset.dec ?? t.dataset.rm);
    if (t.dataset.inc) cart[i].qty++;
    if (t.dataset.dec) cart[i].qty--;
    if (t.dataset.rm || cart[i].qty < 1) cart.splice(i, 1);
    save();
    renderCart();
  });

  document.addEventListener('click', (e) => {
    const addBtn = e.target.closest('[data-add]');
    if (addBtn) {
      const card = addBtn.closest('.product');
      const size = card ? +$('.size[aria-checked="true"]', card).dataset.size : 0;
      add(addBtn.dataset.add, size);
      window.GMFX?.fly(addBtn);
      if (!card) openDialog(cartDlg);
    }
    if (e.target.closest('[data-open-cart]')) openDialog(cartDlg);
    if (e.target.closest('[data-open-game]')) { setMenu(false); openDialog($('#game')); }
  });

  $('#orderForm').addEventListener('submit', (e) => {
    e.preventDefault();
    const f = e.target;
    if (!f.reportValidity()) return;
    // No backend yet: confirm locally and clear the cart.
    cart = [];
    save();
    renderCart();
    $('#cartSum').hidden = true;
    $('#cartEmpty').hidden = true;
    $('#cartDone').hidden = false;
    f.reset();
  });

  // ---------- Dialogs ----------
  function openDialog(d) {
    if (d === cartDlg) { $('#cartDone').hidden = true; renderCart(); }
    if (!d.open) d.showModal();
    if (d === cartDlg) window.GMFX?.drawer(d);
    document.body.classList.add('locked');
  }
  $$('dialog').forEach((d) => {
    d.addEventListener('click', (e) => {
      if (e.target === d || e.target.closest('[data-close]')) d.close();
    });
    d.addEventListener('close', () => {
      if (!$$('dialog').some((x) => x.open)) document.body.classList.remove('locked');
    });
  });

  // ---------- Nav / mobile menu ----------
  const menuBtn = $('#menuBtn');
  const menu = $('#mobileMenu');
  let menuT;
  function setMenu(open) {
    if (open === !menu.hidden && open === menu.classList.contains('is-open')) return;
    menuBtn.setAttribute('aria-expanded', open);
    menuBtn.setAttribute('aria-label', open ? 'Zatvori meni' : 'Otvori meni');
    $('.mb-label', menuBtn).textContent = open ? 'Zatvori' : 'Meni';
    document.body.classList.toggle('menu-open', open);
    clearTimeout(menuT);
    if (open) {
      menu.hidden = false;
      requestAnimationFrame(() => requestAnimationFrame(() => menu.classList.add('is-open')));
    } else {
      menu.classList.remove('is-open');
      menuT = setTimeout(() => { menu.hidden = true; }, reduce ? 0 : 450);
    }
  }
  menuBtn.addEventListener('click', () => setMenu(menu.hidden));
  $$('a', menu).forEach((a) => a.addEventListener('click', () => setMenu(false)));
  addEventListener('keydown', (e) => { if (e.key === 'Escape') setMenu(false); });

  // Desktop links: a honey "ink" pill slides to the hovered link, resting on the section in view
  const navLinks = $('#navLinks');
  const ink = $('.nav-ink', navLinks);
  let activeLink = null;
  function moveInk(link) {
    if (!link) { ink.style.opacity = 0; return; }
    ink.style.opacity = 1;
    ink.style.width = link.offsetWidth + 'px';
    ink.style.transform = `translateX(${link.offsetLeft}px)`;
  }
  $$('.nav-link', navLinks).forEach((l) => {
    l.addEventListener('pointerenter', () => moveInk(l));
    l.addEventListener('focus', () => moveInk(l));
  });
  navLinks.addEventListener('pointerleave', () => moveInk(activeLink));
  const spyLinks = $$('[data-spy]');
  const spy = new IntersectionObserver((entries) => {
    entries.forEach((e) => {
      if (!e.isIntersecting) return;
      spyLinks.forEach((l) => l.classList.toggle('is-active', l.dataset.spy === e.target.id));
      activeLink = $(`.nav-link[data-spy="${e.target.id}"]`, navLinks);
      if (!navLinks.matches(':hover')) moveInk(activeLink);
    });
  }, { rootMargin: '-45% 0px -50% 0px' });
  spyLinks.forEach((l) => { const s = document.getElementById(l.dataset.spy); if (s) spy.observe(s); });
  document.fonts?.ready.then(() => moveInk(activeLink));

  // ---------- Toast ----------
  const toastEl = $('#toast');
  let toastT;
  function toast(msg) {
    toastEl.textContent = msg;
    toastEl.classList.add('show');
    clearTimeout(toastT);
    toastT = setTimeout(() => toastEl.classList.remove('show'), 2200);
  }
  function bump() {
    $$('[data-cart-count]').forEach((el) => {
      el.classList.remove('bump');
      void el.offsetWidth;
      el.classList.add('bump');
    });
  }

  // ---------- Newsletter ----------
  $('#newsForm').addEventListener('submit', (e) => {
    e.preventDefault();
    const f = e.target;
    if (!f.reportValidity()) return;
    $('#newsMsg').textContent = 'Hvala! Tvoj kod za 10% popusta: MEDVED10';
    f.reset();
  });

  // ---------- Scroll: travelling jar ----------
  const journey = $('#journey');
  const jjar = $('#journeyJar');
  const nav = $('#nav');
  const lerp = (a, b, t) => a + (b - a) * t;
  // Keyframes along the journey: x offset (vw), rotation (deg), scale, lid lift (px)
  const KEYS = [
    [0, 24, -14, 0.9, 0],
    [0.33, 22, -6, 1, 0],
    [0.52, -22, 0, 1, 1],
    [0.75, -22, 4, 1, 1],
    [1, 24, 16, 0.95, 0],
  ];
  const at = (p) => {
    let i = 0;
    while (i < KEYS.length - 2 && p > KEYS[i + 1][0]) i++;
    const [p0, ...a] = KEYS[i];
    const [p1, ...b] = KEYS[i + 1];
    const t = Math.min(1, Math.max(0, (p - p0) / (p1 - p0)));
    const e = t * t * (3 - 2 * t);
    return a.map((v, k) => lerp(v, b[k], e));
  };

  // The bar tucks away while scrolling down and comes back as soon as you scroll up
  let lastY = scrollY;
  function navState() {
    const y = scrollY;
    nav.classList.toggle('scrolled', y > 10);
    if (!document.body.classList.contains('menu-open')) {
      if (y > lastY + 6 && y > 240) nav.classList.add('nav-hidden');
      else if (y < lastY - 6 || y < 240) nav.classList.remove('nav-hidden');
    }
    lastY = y;
  }

  function frame() {
    const vh = innerHeight;
    navState();
    const jr = journey.getBoundingClientRect();
    const p = Math.min(1, Math.max(0, -jr.top / (jr.height - vh)));
    const mobile = innerWidth < 760;
    const [x, rot, s, lid] = at(p);
    jjar.style.transform = `translate(${mobile ? x * 0.9 : x}vw, ${lid * 9}vh) rotate(${rot}deg) scale(${s})`;
    jjar.style.setProperty('--lid', lid);
    jjar.j3d = { spin: p, lid };
  }

  if (reduce) {
    addEventListener('scroll', navState, { passive: true });
  } else {
    let ticking = false;
    const onScroll = () => {
      if (ticking) return;
      ticking = true;
      requestAnimationFrame(() => { frame(); ticking = false; });
    };
    addEventListener('scroll', onScroll, { passive: true });
    addEventListener('resize', onScroll);
    frame();
  }

  renderCart();
  $('#year').textContent = new Date().getFullYear();
})();
