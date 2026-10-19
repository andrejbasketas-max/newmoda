// "Uhvati 50 kapi" — catch honey drops in the jar, dodge the bees.
(() => {
  const dlg = document.getElementById('game');
  const cv = document.getElementById('gameCanvas');
  const ctx = cv.getContext('2d');
  const scoreEl = document.getElementById('gScore');
  const livesEl = document.getElementById('gLives');
  const over = document.getElementById('gOver');
  const msg = document.getElementById('gMsg');
  const startBtn = document.getElementById('gStart');
  const W = cv.width, H = cv.height, GOAL = 50;
  const C = window.MED.C;

  let jarX = W / 2, items = [], score = 0, lives = 3, running = false, last = 0, spawn = 0, keys = {};

  function reset() {
    items = []; score = 0; lives = 3; jarX = W / 2; spawn = 0;
    scoreEl.textContent = score; livesEl.textContent = lives;
  }

  function start() {
    reset();
    over.classList.add('hidden');
    running = true;
    last = performance.now();
    requestAnimationFrame(loop);
    cv.focus();
  }

  function end(won) {
    running = false;
    msg.innerHTML = won ? 'Pobeda! Kod: <b>MEDVED10</b>' : `Skupio si ${score} kapi`;
    startBtn.textContent = 'Opet';
    over.classList.remove('hidden');
  }

  function loop(t) {
    if (!running) return;
    const dt = Math.min(0.05, (t - last) / 1000);
    last = t;
    const speed = 1 + score / 40;

    if (keys.ArrowLeft) jarX -= 420 * dt;
    if (keys.ArrowRight) jarX += 420 * dt;
    jarX = Math.max(40, Math.min(W - 40, jarX));

    spawn -= dt;
    if (spawn <= 0) {
      const isBee = Math.random() < 0.22;
      items.push({ x: 30 + Math.random() * (W - 60), y: -20, v: (150 + Math.random() * 90) * speed, bee: isBee, w: Math.random() * 6 });
      spawn = 0.55 / speed;
    }

    for (const it of items) {
      it.y += it.v * dt;
      if (it.bee) it.x += Math.sin(t / 200 + it.w) * 1.4;
      if (it.y > H - 92 && it.y < H - 40 && Math.abs(it.x - jarX) < 42) {
        it.dead = true;
        if (it.bee) { lives--; livesEl.textContent = lives; }
        else { score++; scoreEl.textContent = score; }
      } else if (it.y > H + 20) it.dead = true;
    }
    items = items.filter((i) => !i.dead);

    draw(t);
    if (score >= GOAL) return end(true);
    if (lives <= 0) return end(false);
    requestAnimationFrame(loop);
  }

  function drawDrop(x, y) {
    ctx.fillStyle = C.gold;
    ctx.beginPath();
    ctx.moveTo(x, y - 14);
    ctx.bezierCurveTo(x + 4, y - 6, x + 10, y, x + 10, y + 5);
    ctx.arc(x, y + 5, 10, 0, Math.PI);
    ctx.bezierCurveTo(x - 10, y, x - 4, y - 6, x, y - 14);
    ctx.fill();
  }

  function drawBee(x, y, t) {
    ctx.strokeStyle = C.gold; ctx.lineWidth = 2;
    const flap = Math.sin(t / 40) * 2;
    ctx.beginPath(); ctx.ellipse(x - 6, y - 10, 7, 5 + flap, 0, 0, Math.PI * 2); ctx.stroke();
    ctx.beginPath(); ctx.ellipse(x + 6, y - 10, 7, 5 + flap, 0, 0, Math.PI * 2); ctx.stroke();
    ctx.fillStyle = C.chili;
    ctx.beginPath(); ctx.ellipse(x, y, 13, 9, 0, 0, Math.PI * 2); ctx.fill();
    ctx.fillStyle = C.clove;
    ctx.fillRect(x - 4, y - 8, 3, 16); ctx.fillRect(x + 3, y - 8, 3, 16);
  }

  function drawJar(x) {
    const y = H - 92;
    ctx.fillStyle = C.clove;
    ctx.fillRect(x - 30, y - 6, 60, 10);
    ctx.fillStyle = C.amber;
    ctx.beginPath(); ctx.roundRect(x - 40, y + 4, 80, 76, 14); ctx.fill();
    ctx.fillStyle = C.clove;
    ctx.fillRect(x - 40, y + 26, 80, 30);
    ctx.fillStyle = C.gold;
    ctx.font = '600 14px "Clash Display", sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText('MED', x, y + 46);
  }

  function draw(t) {
    ctx.fillStyle = C.rust;
    ctx.fillRect(0, 0, W, H);
    ctx.fillStyle = C.spice;
    ctx.fillRect(0, H - 14, W, 14);
    for (const it of items) it.bee ? drawBee(it.x, it.y, t) : drawDrop(it.x, it.y);
    drawJar(jarX);
  }

  const toCanvasX = (clientX) => {
    const r = cv.getBoundingClientRect();
    return ((clientX - r.left) / r.width) * W;
  };
  cv.addEventListener('pointermove', (e) => { jarX = toCanvasX(e.clientX); });
  cv.addEventListener('pointerdown', (e) => { jarX = toCanvasX(e.clientX); });
  cv.tabIndex = 0;
  addEventListener('keydown', (e) => {
    if (!dlg.open || !['ArrowLeft', 'ArrowRight'].includes(e.key)) return;
    keys[e.key] = true;
    e.preventDefault();
  });
  addEventListener('keyup', (e) => { keys[e.key] = false; });

  startBtn.addEventListener('click', start);
  dlg.addEventListener('close', () => { running = false; over.classList.remove('hidden'); });
  reset();
  draw(0);
})();
