(() => {
  const $ = (s, el = document) => el.querySelector(s);
  const $$ = (s, el = document) => [...el.querySelectorAll(s)];
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;

  // Nav: background on scroll + call button
  const nav = $('#nav');
  const fab = $('.fab');
  const onScroll = () => {
    const y = scrollY;
    nav.classList.toggle('scrolled', y > 20);
    fab.classList.toggle('show', y > innerHeight * 0.6);
  };
  addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  // Mobile menu
  const burger = $('#burger');
  const links = $('#navLinks');
  const setMenu = (open) => {
    burger.setAttribute('aria-expanded', open);
    burger.setAttribute('aria-label', open ? 'Zatvori meni' : 'Otvori meni');
    links.classList.toggle('open', open);
    document.body.classList.toggle('menu-open', open);
  };
  burger.addEventListener('click', () => setMenu(burger.getAttribute('aria-expanded') !== 'true'));
  $$('a', links).forEach((a) => a.addEventListener('click', () => setMenu(false)));
  addEventListener('keydown', (e) => e.key === 'Escape' && setMenu(false));

  // Reveal on scroll + count-up
  const countUp = (el) => {
    const end = +el.dataset.count;
    const suffix = el.dataset.suffix || '';
    if (reduce) { el.textContent = end + suffix; return; }
    const start = performance.now();
    const dur = 1600;
    const tick = (t) => {
      const p = Math.min((t - start) / dur, 1);
      el.textContent = Math.round(end * (1 - Math.pow(1 - p, 3))) + suffix;
      if (p < 1) requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
  };

  const io = new IntersectionObserver((entries) => {
    entries.forEach((e) => {
      if (!e.isIntersecting) return;
      e.target.classList.remove('pending');
      const n = $('[data-count]', e.target);
      if (n) countUp(n);
      io.unobserve(e.target);
    });
  }, { threshold: 0.15, rootMargin: '0px 0px -40px 0px' });
  // Only elements below the first screen animate in; everything else is visible at rest
  if (!reduce) {
    $$('.reveal').forEach((el) => {
      if (el.closest('.hero') || el.getBoundingClientRect().top < innerHeight) return;
      el.classList.add('pending');
      io.observe(el);
    });
  }

  // Menu tabs with sliding pill
  const tabs = $$('[role="tab"]');
  const pill = $('.tab-pill');
  const movePill = (tab) => {
    pill.style.width = tab.offsetWidth + 'px';
    pill.style.transform = `translateX(${tab.offsetLeft}px)`;
  };
  const select = (tab) => {
    tabs.forEach((t) => {
      const on = t === tab;
      t.setAttribute('aria-selected', on);
      t.tabIndex = on ? 0 : -1;
      const panel = $('#' + t.getAttribute('aria-controls'));
      panel.hidden = !on;
      panel.classList.toggle('is-active', on);
    });
    movePill(tab);
  };
  tabs.forEach((t, i) => {
    t.addEventListener('click', () => select(t));
    t.addEventListener('keydown', (e) => {
      const dir = e.key === 'ArrowRight' ? 1 : e.key === 'ArrowLeft' ? -1 : 0;
      if (!dir) return;
      const next = tabs[(i + dir + tabs.length) % tabs.length];
      next.focus();
      select(next);
    });
  });
  const current = () => tabs.find((t) => t.getAttribute('aria-selected') === 'true');
  addEventListener('resize', () => movePill(current()));
  document.fonts?.ready.then(() => movePill(current()));
  movePill(current());

  // Open / closed status + highlight today's hours
  const hours = { 0: [9, 22], 6: [8.5, 24] }; // Sun, Sat; weekdays default
  const now = new Date();
  const day = now.getDay();
  const [open, close] = hours[day] || [7.5, 23];
  const h = now.getHours() + now.getMinutes() / 60;
  const isOpen = h >= open && h < close;
  const fmt = (v) => `${String(Math.floor(v) % 24).padStart(2, '0')}:${v % 1 ? '30' : '00'}`;
  $('#openText').textContent = isOpen
    ? `Otvoreno sada · do ${fmt(close)}`
    : `Trenutno zatvoreno · otvaramo u ${fmt(open)}`;
  $('#openDot').classList.toggle('closed', !isOpen);
  const rows = $$('.hours div');
  rows[day === 0 ? 2 : day === 6 ? 1 : 0].classList.add('today');

  $('#year').textContent = now.getFullYear();
})();
