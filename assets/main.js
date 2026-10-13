(() => {
  const root = document.documentElement;
  root.classList.add('js');
  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* Header: solid background after leaving the top */
  const header = document.querySelector('[data-header]');
  const onScroll = () => header.classList.toggle('is-scrolled', window.scrollY > 24);
  onScroll();
  window.addEventListener('scroll', onScroll, { passive: true });

  /* Mobile menu */
  const menuBtn = document.querySelector('[data-menu-btn]');
  const navLinks = document.getElementById('nav-links');
  const setMenu = (open) => {
    menuBtn.setAttribute('aria-expanded', String(open));
    menuBtn.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
    navLinks.classList.toggle('is-open', open);
  };
  menuBtn.addEventListener('click', () => setMenu(menuBtn.getAttribute('aria-expanded') !== 'true'));
  navLinks.addEventListener('click', (e) => { if (e.target.closest('a')) setMenu(false); });
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && navLinks.classList.contains('is-open')) { setMenu(false); menuBtn.focus(); }
  });

  /* Reveal on scroll, staggered within each parent */
  const reveals = document.querySelectorAll('.reveal');
  if (reduceMotion || !('IntersectionObserver' in window)) {
    reveals.forEach((el) => el.classList.add('is-in'));
  } else {
    const groups = new Map();
    reveals.forEach((el) => {
      const i = groups.get(el.parentElement) || 0;
      el.style.setProperty('--d', `${Math.min(i, 5) * 0.09}s`);
      groups.set(el.parentElement, i + 1);
    });
    const io = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        entry.target.classList.add('is-in');
        io.unobserve(entry.target);
      });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.12 });
    reveals.forEach((el) => io.observe(el));
  }

  /* Notes: active chapter drives bottle colour and background */
  const notes = document.querySelector('[data-notes]');
  if (notes) {
    const chapters = [...notes.querySelectorAll('.chapter')];
    const bottle = notes.querySelector('.notes-bottle');
    const ring = notes.querySelector('.notes-ring');
    const dots = [...notes.querySelectorAll('.notes-progress li')];
    const activate = (ch) => {
      const i = Number(ch.dataset.chapter);
      chapters.forEach((c) => c.classList.toggle('is-active', c === ch));
      dots.forEach((d, j) => d.classList.toggle('is-active', j === i));
      bottle.style.setProperty('--liquid', ch.dataset.liquid);
      ring.style.setProperty('--liquid', ch.dataset.liquid);
      notes.style.setProperty('--bg', ch.dataset.bg);
    };
    activate(chapters[0]);
    if ('IntersectionObserver' in window) {
      const cio = new IntersectionObserver((entries) => {
        entries.forEach((entry) => { if (entry.isIntersecting) activate(entry.target); });
      }, { rootMargin: '-45% 0px -45% 0px' });
      chapters.forEach((c) => cio.observe(c));
    }
  }

  /* Count-up stats */
  const counters = document.querySelectorAll('[data-count]');
  if (!reduceMotion && 'IntersectionObserver' in window) {
    const run = (el) => {
      const target = Number(el.dataset.count);
      const suffix = el.dataset.suffix || '';
      const start = performance.now();
      const dur = 1400;
      const tick = (now) => {
        const t = Math.min((now - start) / dur, 1);
        const eased = 1 - Math.pow(1 - t, 4);
        el.textContent = Math.round(target * eased) + suffix;
        if (t < 1) requestAnimationFrame(tick);
      };
      requestAnimationFrame(tick);
    };
    const sio = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        run(entry.target);
        sio.unobserve(entry.target);
      });
    }, { threshold: 0.6 });
    counters.forEach((el) => sio.observe(el));
  }

  /* Bag + toast */
  const bagBtn = document.querySelector('[data-bag-btn]');
  const bagCount = document.querySelector('[data-bag-count]');
  const toast = document.querySelector('[data-toast]');
  let count = 0;
  let toastTimer;
  const showToast = (msg) => {
    toast.textContent = msg;
    toast.classList.add('is-visible');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => toast.classList.remove('is-visible'), 2800);
  };
  const addToBag = (name, btn) => {
    count += 1;
    bagCount.textContent = count;
    bagCount.classList.add('has-items');
    bagCount.classList.remove('bump');
    void bagCount.offsetWidth;
    bagCount.classList.add('bump');
    bagBtn.setAttribute('aria-label', `Shopping bag, ${count} item${count === 1 ? '' : 's'}`);
    showToast(`${name} added to your bag`);
    if (btn && btn.classList.contains('btn-add')) {
      const label = btn.textContent;
      btn.classList.add('is-added');
      btn.textContent = 'Added';
      setTimeout(() => { btn.classList.remove('is-added'); btn.textContent = label; }, 1600);
    }
  };
  document.addEventListener('click', (e) => {
    const btn = e.target.closest('[data-add]');
    if (btn) addToBag(btn.dataset.add, btn);
  });
  bagBtn.addEventListener('click', () => {
    showToast(count ? `${count} item${count === 1 ? '' : 's'} in your bag` : 'Your bag is empty');
  });

  /* Scent finder */
  const scents = {
    nuit: { name: 'Nuit d’Ambre', liquid: '#B4651E', desc: 'Amber resin, smoked oud and vanilla. Warm and close to the skin, for people who like to be remembered after they leave the room.' },
    fleur: { name: 'Fleur de Sel', liquid: '#7FA3B8', desc: 'Sea salt, powdery iris and white musk. It smells like clean skin after a swim, and it’s easy to wear every day.' },
    rose: { name: 'Rose Noire', liquid: '#7A1E35', desc: 'Black rose sharpened with saffron over dark patchouli. Bold and theatrical, made for evenings out.' },
    vert: { name: 'Vert Silence', liquid: '#5E7350', desc: 'Green fig leaf, vetiver and cedar. Quiet and grounded, like an afternoon in the shade.' },
  };
  const finder = document.querySelector('[data-finder]');
  const result = document.querySelector('[data-finder-result]');
  const finderError = document.querySelector('[data-finder-error]');
  let chosen = null;
  finder.addEventListener('submit', (e) => {
    e.preventDefault();
    const data = new FormData(finder);
    const answers = ['time', 'place', 'feel'].map((k) => data.get(k));
    const missing = answers.findIndex((a) => !a);
    if (missing !== -1) {
      finderError.textContent = `Please answer question ${missing + 1} to see your scent.`;
      finder.querySelectorAll('fieldset')[missing].querySelector('input').focus();
      return;
    }
    finderError.textContent = '';
    const tally = {};
    answers.forEach((a) => { tally[a] = (tally[a] || 0) + 1; });
    // Ties go to the "feel" answer, the strongest signal.
    const best = Object.keys(tally).sort((a, b) => tally[b] - tally[a] || (b === answers[2]) - (a === answers[2]))[0];
    chosen = scents[best];
    result.querySelector('[data-result-name]').textContent = chosen.name;
    result.querySelector('[data-result-desc]').textContent = chosen.desc;
    result.querySelector('svg').style.setProperty('--liquid', chosen.liquid);
    finder.hidden = true;
    result.hidden = false;
    result.focus();
  });
  result.querySelector('[data-result-add]').addEventListener('click', () => chosen && addToBag(chosen.name));
  result.querySelector('[data-finder-reset]').addEventListener('click', () => {
    finder.reset();
    result.hidden = true;
    finder.hidden = false;
    finder.querySelector('input').focus();
  });

  /* Newsletter */
  const letter = document.querySelector('[data-letter]');
  const email = letter.querySelector('#email');
  const field = letter.querySelector('.field');
  const emailMsg = letter.querySelector('#email-error');
  const setEmailError = (msg) => {
    field.classList.toggle('has-error', Boolean(msg));
    email.setAttribute('aria-invalid', msg ? 'true' : 'false');
    emailMsg.classList.remove('is-success');
    emailMsg.textContent = msg;
  };
  const validateEmail = () => {
    const v = email.value.trim();
    if (!v) return 'Please enter your email address.';
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(v)) return 'That email doesn’t look right. Check for typos, e.g. name@example.com.';
    return '';
  };
  email.addEventListener('blur', () => { if (email.value) setEmailError(validateEmail()); });
  email.addEventListener('input', () => { if (field.classList.contains('has-error')) setEmailError(validateEmail()); });
  letter.addEventListener('submit', (e) => {
    e.preventDefault();
    const err = validateEmail();
    setEmailError(err);
    if (err) { email.focus(); return; }
    emailMsg.textContent = 'Thank you. Your first letter arrives next month.';
    emailMsg.classList.add('is-success');
    letter.reset();
  });

  const year = document.querySelector('[data-year]');
  if (year) year.textContent = new Date().getFullYear();
})();
