/* Motion layer: preloader, smooth scroll, text reveals, scroll scenes, tilt, cursor.
   Everything here is optional — without GSAP or with reduced motion the page is complete. */
(() => {
  const { gsap, ScrollTrigger, SplitText, Lenis } = window;
  const root = document.documentElement;
  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const fine = window.matchMedia('(hover: hover) and (pointer: fine)').matches;
  const preloader = document.querySelector('[data-preloader]');
  const startIntro = () => window.dispatchEvent(new Event('newmoda:intro'));

  if (!gsap || !ScrollTrigger || reduce) {
    preloader?.remove();
    startIntro();
    return;
  }
  gsap.registerPlugin(ScrollTrigger, SplitText);
  const $ = (s, el = document) => el.querySelector(s);
  const $$ = (s, el = document) => [...el.querySelectorAll(s)];

  /* ---------- Smooth scroll ---------- */
  let lenis = null;
  if (Lenis) {
    lenis = new Lenis({ lerp: 0.085, smoothWheel: true });
    lenis.on('scroll', ScrollTrigger.update);
    gsap.ticker.add((t) => lenis.raf(t * 1000));
    gsap.ticker.lagSmoothing(0);
    document.addEventListener('click', (e) => {
      const a = e.target.closest('a[href^="#"]');
      if (!a || a.classList.contains('skip-link')) return;
      const id = a.getAttribute('href');
      const target = id.length > 1 && document.querySelector(id);
      if (!target) return;
      e.preventDefault();
      const offset = id === '#top' ? 0 : -parseFloat(getComputedStyle(root).getPropertyValue('--header-h'));
      lenis.scrollTo(target, { offset, duration: 1.6 });
      history.replaceState(null, '', id);
    });
  }

  /* ---------- Header hides on scroll down ---------- */
  const header = $('[data-header]');
  ScrollTrigger.create({
    start: 0, end: 'max',
    onUpdate: (self) => {
      const menuOpen = $('#nav-links').classList.contains('is-open');
      header.classList.toggle('is-hidden', !menuOpen && self.direction === 1 && self.scroll() > 600);
    },
  });

  const fontsReady = Promise.race([document.fonts ? document.fonts.ready : Promise.resolve(), new Promise((r) => setTimeout(r, 1500))]);

  fontsReady.then(() => {
    root.classList.add('gsap-ready');
    buildHero();
    buildReveals();
    buildScenes();
    ScrollTrigger.refresh();
  });

  /* ---------- Preloader + hero intro ---------- */
  function buildHero() {
    const h1 = $('.hero h1');
    const split = SplitText.create(h1, { type: 'lines,chars', linesClass: 'split-line', mask: 'lines' });
    const others = ['.hero .eyebrow', '.hero-lede', '.hero-cta', '.hero-meta'].map((s) => $(s));

    const tl = gsap.timeline({ defaults: { ease: 'expo.out' } });
    if (preloader) {
      tl.to('[data-preloader-bar]', { scaleX: 1, duration: 0.9, ease: 'power2.inOut' })
        .to('.preloader-inner', { yPercent: -40, autoAlpha: 0, duration: 0.6, ease: 'power3.in' })
        .to(preloader, { clipPath: 'inset(0% 0% 100% 0%)', duration: 1, ease: 'expo.inOut' }, '-=0.15')
        .set(preloader, { display: 'none' });
    }
    tl.add(startIntro, preloader ? '-=0.7' : 0)
      .from(split.chars, { yPercent: 115, rotate: 6, duration: 1.4, stagger: 0.035 }, '<')
      .from(others, { y: 30, autoAlpha: 0, duration: 1.2, stagger: 0.1 }, '<0.35')
      .from('.halo', { scale: 0.6, autoAlpha: 0, duration: 2 }, '<');

    // Hero drifts away on scroll.
    gsap.to('.hero-copy', {
      yPercent: -18, opacity: 0.15, ease: 'none',
      scrollTrigger: { trigger: '.hero', start: 'top top', end: 'bottom top', scrub: true },
    });
    gsap.to('.halo', {
      scale: 1.35, rotate: 25, opacity: 0, ease: 'none',
      scrollTrigger: { trigger: '.hero', start: 'top top', end: 'bottom top', scrub: true },
    });
  }

  /* ---------- Reveals ---------- */
  function buildReveals() {
    $$('main h2').forEach((h2) => {
      const split = SplitText.create(h2, { type: 'lines', linesClass: 'split-line', mask: 'lines' });
      gsap.from(split.lines, {
        yPercent: 110, duration: 1.3, stagger: 0.12, ease: 'expo.out',
        scrollTrigger: { trigger: h2, start: 'top 88%' },
      });
    });

    const fades = $$('.reveal').filter((el) => !el.closest('.hero') && el.tagName !== 'H2' && !el.classList.contains('product'));
    gsap.set(fades, { autoAlpha: 0, y: 40 });
    ScrollTrigger.batch(fades, {
      start: 'top 90%',
      onEnter: (batch) => gsap.to(batch, { autoAlpha: 1, y: 0, duration: 1.1, stagger: 0.1, ease: 'power3.out', overwrite: true }),
    });

    // Product cards rise in with a 3D swing, then become tiltable.
    const cards = $$('.product');
    gsap.set(cards, { transformPerspective: 1200 });
    gsap.from(cards, {
      y: 90, rotateX: -24, autoAlpha: 0, duration: 1.4, stagger: 0.12, ease: 'expo.out',
      scrollTrigger: { trigger: '.products', start: 'top 82%' },
      onComplete: () => cards.forEach(enableTilt),
    });
  }

  function enableTilt(card) {
    if (!fine || card.dataset.tilt) return;
    card.dataset.tilt = '1';
    const rx = gsap.quickTo(card, 'rotateX', { duration: 0.6, ease: 'power3.out' });
    const ry = gsap.quickTo(card, 'rotateY', { duration: 0.6, ease: 'power3.out' });
    const y = gsap.quickTo(card, 'y', { duration: 0.6, ease: 'power3.out' });
    const bottle = $('.product-stage svg', card);
    const bx = gsap.quickTo(bottle, 'x', { duration: 0.8, ease: 'power3.out' });
    card.addEventListener('pointermove', (e) => {
      const r = card.getBoundingClientRect();
      const px = (e.clientX - r.left) / r.width;
      const py = (e.clientY - r.top) / r.height;
      rx((0.5 - py) * 14);
      ry((px - 0.5) * 16);
      y(-10);
      bx((px - 0.5) * 18);
      card.style.setProperty('--gx', `${px * 100}%`);
      card.style.setProperty('--gy', `${py * 100}%`);
    });
    card.addEventListener('pointerleave', () => { rx(0); ry(0); y(0); bx(0); });
  }

  /* ---------- Scroll scenes ---------- */
  function buildScenes() {
    // Marquee: constant drift that speeds up and skews with scroll velocity.
    const track = $('.marquee-track');
    const loop = gsap.to(track, { xPercent: -50, duration: 38, ease: 'none', repeat: -1 });
    const skew = gsap.quickTo(track, 'skewX', { duration: 0.5, ease: 'power3.out' });
    ScrollTrigger.create({
      trigger: '.marquee', start: 'top bottom', end: 'bottom top',
      onUpdate: (self) => {
        const v = self.getVelocity();
        gsap.to(loop, { timeScale: 1 + Math.min(Math.abs(v) / 300, 6), duration: 0.3, overwrite: true });
        gsap.to(loop, { timeScale: 1, duration: 1.2, delay: 0.3 });
        skew(gsap.utils.clamp(-8, 8, v / -250));
      },
      onLeave: () => skew(0), onLeaveBack: () => skew(0),
    });

    // Notes: chips settle in per chapter.
    $$('.chapter').forEach((ch) => {
      gsap.from($$('.chips li', ch), {
        y: 16, autoAlpha: 0, stagger: 0.06, duration: 0.8, ease: 'power3.out',
        scrollTrigger: { trigger: ch, start: 'top 65%' },
      });
    });
    gsap.fromTo('.notes-ring', { scale: 0.85 }, {
      scale: 1.15, ease: 'none',
      scrollTrigger: { trigger: '.notes', start: 'top bottom', end: 'bottom top', scrub: true },
    });

    // Origins: pinned horizontal journey on wide screens; swipeable row on small ones.
    const mm = gsap.matchMedia();
    mm.add('(min-width: 861px)', () => {
      const section = $('[data-origins]');
      const rail = $('[data-origins-track]');
      section.classList.add('is-pinned');
      const distance = () => rail.scrollWidth - window.innerWidth + Math.max(32, (window.innerWidth - 1240) / 2 + 48);
      const scroll = gsap.to(rail, {
        x: () => -distance(), ease: 'none',
        scrollTrigger: {
          trigger: section, start: 'top top', end: () => `+=${distance()}`,
          pin: true, scrub: 1, invalidateOnRefresh: true, anticipatePin: 1,
        },
      });
      $$('.origin', rail).forEach((card) => {
        gsap.from($('.origin-orb', card), {
          scale: 0.4, rotate: -90, ease: 'none',
          scrollTrigger: { trigger: card, containerAnimation: scroll, start: 'left right', end: 'center center', scrub: true },
        });
        gsap.from($$('h3, .origin-place, p:not(.origin-num)', card), {
          x: 60, autoAlpha: 0, stagger: 0.05, ease: 'none',
          scrollTrigger: { trigger: card, containerAnimation: scroll, start: 'left 90%', end: 'left 45%', scrub: true },
        });
      });
      return () => section.classList.remove('is-pinned');
    });

    // Atelier ghost word glides across.
    gsap.fromTo('[data-ghost]', { xPercent: 8 }, {
      xPercent: -38, ease: 'none',
      scrollTrigger: { trigger: '.atelier', start: 'top bottom', end: 'bottom top', scrub: true },
    });

    // Discovery: bottles fan out from a stack.
    const fan = $$('.discovery-bottles svg');
    gsap.from(fan, {
      x: (i) => (1.5 - i) * 70, y: 80, rotate: 0, autoAlpha: 0, ease: 'none',
      scrollTrigger: { trigger: '.discovery', start: 'top 85%', end: 'center 60%', scrub: 1 },
    });
    gsap.to(fan, {
      y: (i) => (i % 2 ? -30 : -12), ease: 'none',
      scrollTrigger: { trigger: '.discovery', start: 'center 60%', end: 'bottom top', scrub: true },
    });

    if (fine) { magnetic(); cursor(); }
  }

  /* ---------- Pointer niceties ---------- */
  function magnetic() {
    $$('.btn, .bag-btn').forEach((btn) => {
      const x = gsap.quickTo(btn, 'x', { duration: 0.5, ease: 'power3.out' });
      const y = gsap.quickTo(btn, 'y', { duration: 0.5, ease: 'power3.out' });
      btn.addEventListener('pointermove', (e) => {
        const r = btn.getBoundingClientRect();
        x((e.clientX - r.left - r.width / 2) * 0.22);
        y((e.clientY - r.top - r.height / 2) * 0.35);
      });
      btn.addEventListener('pointerleave', () => {
        gsap.to(btn, { x: 0, y: 0, duration: 0.9, ease: 'elastic.out(1, 0.4)', overwrite: true });
      });
    });
  }

  function cursor() {
    const el = $('[data-cursor]');
    if (!el) return;
    root.classList.add('has-cursor');
    const dot = $('.cursor-dot', el);
    const ring = $('.cursor-ring', el);
    const dx = gsap.quickTo(dot, 'x', { duration: 0.12, ease: 'power3.out' });
    const dy = gsap.quickTo(dot, 'y', { duration: 0.12, ease: 'power3.out' });
    const rx = gsap.quickTo(ring, 'x', { duration: 0.55, ease: 'power3.out' });
    const ry = gsap.quickTo(ring, 'y', { duration: 0.55, ease: 'power3.out' });
    window.addEventListener('pointermove', (e) => {
      el.classList.add('is-on');
      dx(e.clientX); dy(e.clientY); rx(e.clientX); ry(e.clientY);
      const hot = e.target.closest('a, button, label, input, .product');
      el.classList.toggle('is-hot', Boolean(hot));
    }, { passive: true });
    document.addEventListener('pointerleave', () => el.classList.remove('is-on'));
  }

  window.addEventListener('load', () => ScrollTrigger.refresh());
})();
