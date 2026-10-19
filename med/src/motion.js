// Page motion for Gladni Medved, built on Motion (motion.dev).
import { animate, scroll, inView, stagger, press, hover } from 'motion';

const $ = (s, el = document) => el.querySelector(s);
const $$ = (s, el = document) => [...el.querySelectorAll(s)];
const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
const root = document.documentElement;
const spring = (stiffness = 260, damping = 22, extra = {}) => ({ type: 'spring', stiffness, damping, ...extra });

// Split a heading into words (and optionally characters), keeping <em> and <br>.
// Each word sits in a clipping wrapper so it can rise from below its own baseline.
function split(el, chars = false) {
  const words = [];
  const letters = [];
  const makeWord = (content) => {
    const mask = document.createElement('span');
    mask.className = 'w';
    const inner = document.createElement('span');
    inner.className = 'wi';
    if (chars) {
      for (const node of content) {
        const target = node.nodeType === 3 ? inner : inner.appendChild(node.cloneNode(false));
        for (const ch of node.textContent) {
          const c = document.createElement('span');
          c.className = 'ch';
          c.textContent = ch;
          target.appendChild(c);
          letters.push(c);
        }
      }
    } else {
      content.forEach((n) => inner.appendChild(n));
    }
    mask.appendChild(inner);
    words.push(inner);
    return mask;
  };
  const out = document.createDocumentFragment();
  for (const node of [...el.childNodes]) {
    if (node.nodeType === 3) {
      node.textContent.split(/(\s+)/).forEach((part) => {
        if (!part) return;
        out.appendChild(/\s/.test(part) ? document.createTextNode(' ') : makeWord([document.createTextNode(part)]));
      });
    } else if (node.nodeName === 'BR') {
      out.appendChild(node);
    } else {
      out.appendChild(makeWord([node]));
    }
  }
  el.textContent = '';
  el.appendChild(out);
  el.setAttribute('aria-label', el.textContent.replace(/\s+/g, ' ').trim());
  [...el.children].forEach((c) => c.setAttribute('aria-hidden', 'true'));
  return { words, letters };
}

const css = (el, name) => getComputedStyle(el).getPropertyValue(name).trim();

// ---------- Headlines: rise in, then fill with honey colour as they scroll through ----------
$$('.fill').forEach((h) => {
  const on = css(h, '--on'), off = css(h, '--off');
  const { words } = split(h);
  if (reduce) { h.style.color = on; return; }
  words.forEach((w) => { w.style.color = off; });
  inView(h, () => {
    animate(words, { y: ['108%', '0%'], rotate: [4, 0] }, { ...spring(170, 20), delay: stagger(0.06) });
  }, { amount: 0.3 });
  scroll(animate(words, { color: [off, on] }, { delay: stagger(0.12), ease: 'linear' }), {
    target: h, offset: ['start 92%', 'end 45%'],
  });
});

// ---------- Hero intro ----------
const heroTitle = $('.hero-title');
if (heroTitle) {
  const { letters } = split(heroTitle, true);
  if (!reduce) {
    animate(letters, { y: ['110%', '0%'], rotate: [10, 0] }, { ...spring(200, 18), delay: stagger(0.035, { startDelay: 0.15 }) });
    animate('.hero .eyebrow', { opacity: [0, 1], y: [12, 0] }, { duration: 0.6, delay: 0.1 });
    animate('.hero-product', { opacity: [0, 1], y: [30, 0] }, { ...spring(160, 20), delay: 0.55 });
    animate('.hero-jar', { opacity: [0, 1], scale: [0.6, 1], y: [80, 0] }, { ...spring(120, 14), delay: 0.45 });
    animate('.hero-foot > *', { opacity: [0, 1], y: [20, 0] }, { delay: stagger(0.08, { startDelay: 0.9 }) });
    animate('.nav .pill, .brand', { opacity: [0, 1], y: [-24, 0] }, { ...spring(300, 24), delay: stagger(0.04, { startDelay: 0.2 }) });
    animate('.hero .rule', { scaleX: [0, 1] }, { duration: 1.1, ease: [0.22, 1, 0.36, 1], delay: stagger(0.15) });
  }
}
root.classList.remove('mo-wait');

if (!reduce) {
  // ---------- Staggered entrances ----------
  const reveal = (sel, opts = {}) => {
    $$(sel).forEach((group) => {
      const items = opts.children ? $$(opts.children, group) : [group];
      items.forEach((i) => { i.style.opacity = 0; });
      inView(group, () => {
        animate(items, { opacity: [0, 1], y: [opts.y ?? 50, 0] }, { ...spring(140, 20), delay: stagger(opts.stagger ?? 0.08) });
      }, { amount: opts.amount ?? 0.2 });
    });
  };
  reveal('.products', { children: '.product', y: 70, stagger: 0.1, amount: 0.05 });
  reveal('.recipe-cards', { children: 'li', y: 80, stagger: 0.12, amount: 0.1 });
  reveal('.why-cols', { children: 'article', y: 60, stagger: 0.12, amount: 0.1 });
  reveal('.facts', { children: 'li', y: 30, stagger: 0.1 });
  reveal('.icon-row', { children: 'li', y: 30, stagger: 0.1 });
  reveal('.foot-grid', { children: ':scope > *', y: 30, stagger: 0.06 });
  $$('.micro:not(.hero-foot .micro)').forEach((m) => {
    if (m.closest('.product, .r-card, .why-cols, .cart, dialog')) return;
    m.style.opacity = 0;
    inView(m, () => { animate(m, { opacity: [0, 1], y: [16, 0] }, { duration: 0.7, ease: [0.22, 1, 0.36, 1] }); }, { amount: 0.5 });
  });

  // Dotted rules draw themselves across the page
  $$('.rule:not(.hero .rule)').forEach((el) => {
    el.style.transform = 'scaleX(0)';
    inView(el, () => { animate(el, { scaleX: [0, 1] }, { duration: 1.2, ease: [0.22, 1, 0.36, 1] }); });
  });

  // Footer wordmark: letters spring up
  const wm = $('.wordmark');
  if (wm) {
    const { letters } = split(wm, true);
    inView(wm, () => {
      animate(letters, { y: ['105%', '0%'] }, { ...spring(180, 18), delay: stagger(0.03) });
    }, { amount: 0.4 });
  }

  // ---------- Scroll-linked parallax ----------
  $$('.step').forEach((s, i) => {
    const r = [5, -4, 3][i] ?? 0;
    scroll(animate(s, { y: [120, -120], rotate: [r - 4, r + 3] }, { ease: 'linear' }), { target: s, offset: ['start end', 'end start'] });
  });
  const unlockRot = [-58, -18, 32];
  $$('.unlock-jars .jar').forEach((j, i) => {
    const base = unlockRot[i];
    scroll(animate(j, { y: [160 - i * 40, -140 + i * 30], rotate: [base - 10, base + 10] }, { ease: 'linear' }), {
      target: $('.unlock'), offset: ['start end', 'end start'],
    });
  });
  $$('.inside-jar').forEach((j, i) => {
    scroll(animate(j, { '--py': [`${i ? 70 : -50}px`, `${i ? -70 : 50}px`] }, { ease: 'linear' }), {
      target: $('.inside'), offset: ['start end', 'end start'],
    });
  });
  $$('.sticker').forEach((s, i) => {
    const base = [14, -12, 26][i];
    s.style.opacity = 0;
    inView(s, () => {
      animate(s, { opacity: [0, 1], scale: [0.2, 1], rotate: [base - 40, base] }, { ...spring(300, 12), delay: 0.3 + i * 0.15 });
    }, { amount: 1 });
  });
  const seal = $('.seal');
  if (seal) scroll(animate(seal, { rotate: [0, 540] }, { ease: 'linear' }), { target: $('.news') });

  // ---------- Recipe cards: 3D tilt toward the pointer ----------
  $$('.r-card').forEach((card) => {
    card.style.transformPerspective = '900px';
    hover(card, () => {
      const move = (e) => {
        const r = card.getBoundingClientRect();
        const x = (e.clientX - r.left) / r.width - 0.5;
        const y = (e.clientY - r.top) / r.height - 0.5;
        animate(card, { rotateY: x * 14, rotateX: -y * 12, y: -6 }, spring(300, 24));
      };
      card.addEventListener('pointermove', move);
      return () => {
        card.removeEventListener('pointermove', move);
        animate(card, { rotateY: 0, rotateX: 0, y: 0 }, spring(200, 18));
      };
    });
  });

  // ---------- Springy presses ----------
  $$('.btn, .pill, .dock-btn, .r-card').forEach((el) => {
    press(el, () => {
      animate(el, { scale: 0.93 }, spring(600, 30));
      return () => animate(el, { scale: 1 }, spring(500, 12));
    });
  });
}

// ---------- Hooks used by main.js ----------
function fly(fromEl) {
  const target = $$('[data-open-cart]').find((b) => b.offsetParent && b.closest('.dock')) || $('[data-open-cart]');
  if (!fromEl || !target || reduce) return;
  const a = fromEl.getBoundingClientRect();
  const b = target.getBoundingClientRect();
  const drop = document.createElement('span');
  drop.className = 'fly-drop';
  drop.style.left = a.left + a.width / 2 - 11 + 'px';
  drop.style.top = a.top + a.height / 2 - 14 + 'px';
  document.body.appendChild(drop);
  const dx = b.left + b.width / 2 - (a.left + a.width / 2);
  const dy = b.top + b.height / 2 - (a.top + a.height / 2);
  animate(drop, {
    x: [0, dx * 0.5, dx], y: [0, Math.min(dy, 0) - 140, dy], scale: [0.4, 1.3, 0.5], rotate: [0, -20, 0],
  }, { duration: 0.85, ease: [0.45, 0, 0.25, 1] }).then(() => {
    drop.remove();
    animate(target, { scale: [1, 1.25, 1] }, { duration: 0.45 });
  });
}

function price(el, from, to, fmt) {
  if (reduce) { el.textContent = fmt(to); return; }
  animate(from, to, { duration: 0.6, ease: [0.22, 1, 0.36, 1], onUpdate: (v) => { el.textContent = fmt(Math.round(v / 10) * 10); } });
  animate(el, { scale: [1, 1.12, 1] }, { duration: 0.4 });
}

function drawer(dlg) {
  if (reduce) return;
  animate($$('.c-item, .cart-sum, .cart-empty', dlg).filter((e) => !e.hidden), { opacity: [0, 1], x: [40, 0] }, {
    ...spring(220, 24), delay: stagger(0.05, { startDelay: 0.12 }),
  });
}

window.GMFX = { fly, price, drawer };
