"""Soundtrack for the film: comedic march score, synthesized SFX and gibberish voices.
Everything is generated here from timeline.js (same timings as the picture) → audio.wav (48 kHz stereo)."""
import json, re
import numpy as np
from scipy import signal

SR = 48000
src = open('timeline.js').read()
TL = json.loads(src[src.index('{'):src.rindex('}') + 1])
DUR = TL['duration']
N = int(SR * (DUR + 0.5))
rng = np.random.default_rng(7)

def T(d): return np.arange(int(SR * d)) / SR
def env_adsr(n, a=0.005, d=0.1, s=0.6, r=0.1):
    e = np.ones(n) * s
    na, nd, nr = int(a * SR), int(d * SR), int(r * SR)
    na = min(na, n); e[:na] = np.linspace(0, 1, na)
    nd = min(nd, n - na); e[na:na + nd] = np.linspace(1, s, nd)
    nr = min(nr, n); e[n - nr:] *= np.linspace(1, 0, nr)
    return e
def bp(x, lo, hi, order=2):
    sos = signal.butter(order, [lo, hi], btype='band', fs=SR, output='sos'); return signal.sosfilt(sos, x)
def lp(x, f, order=2):
    sos = signal.butter(order, f, btype='low', fs=SR, output='sos'); return signal.sosfilt(sos, x)
def hp(x, f, order=2):
    sos = signal.butter(order, f, btype='high', fs=SR, output='sos'); return signal.sosfilt(sos, x)
def noise(d): return rng.standard_normal(int(SR * d))
def sweep(f0, f1, d, kind='exp'):
    t = T(d); f = f0 * (f1 / f0) ** (t / d) if kind == 'exp' else np.linspace(f0, f1, len(t))
    return np.sin(2 * np.pi * np.cumsum(f) / SR), f
def saw(f, d, harm=12):
    t = T(d); return sum(np.sin(2 * np.pi * f * k * t) / k for k in range(1, harm + 1) if f * k < SR / 2)
def place(buf, x, at, gain=1.0, pan=0.0):
    i = int(at * SR); x = x[: max(0, buf.shape[1] - i)]
    if i < 0 or len(x) == 0: return
    l, r = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
    buf[0, i:i + len(x)] += x * gain * l * 1.414; buf[1, i:i + len(x)] += x * gain * r * 1.414

mus = np.zeros((2, N)); sfx = np.zeros((2, N)); vox = np.zeros((2, N))
def m2f(m): return 440 * 2 ** ((m - 69) / 12)

# ---------------- MUSIC ----------------
BPM = 120; BEAT = 60 / BPM
def tuba(f, d):
    t = T(d); x = np.sin(2 * np.pi * f * t) + 0.5 * np.sin(4 * np.pi * f * t) + 0.25 * np.sin(6 * np.pi * f * t)
    return lp(x * env_adsr(len(t), 0.01, 0.12, 0.5, 0.08), 900)
def pizz(f, d=0.3):
    t = T(d); x = saw(f, d, 8) * np.exp(-t * 14); return lp(x, 3500) * 0.6
def glock(f, d=0.6):
    t = T(d); return (np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * f * 2.76 * t)) * np.exp(-t * 6)
def brass(f, d):
    t = T(d); x = saw(f, d, 14); x = lp(x, 1800 + 0 * t[0]); return x * env_adsr(len(t), 0.04, 0.2, 0.7, 0.15) * 0.4
def snare(d=0.18):
    t = T(d); return hp(noise(d), 1500) * np.exp(-t * 25) * 0.5 + np.sin(2 * np.pi * 190 * t) * np.exp(-t * 30) * 0.4
def kick(d=0.25):
    t = T(d); f = 50 + 90 * np.exp(-t * 30); return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 12)
def hat(d=0.05):
    t = T(d); return hp(noise(d), 7000) * np.exp(-t * 80) * 0.3

# Epic Roman intro (0–3.2): brass fanfare in D minor → cut at the portal flash
for (m, st, d) in [(62, 0.0, 0.5), (69, 0.5, 0.5), (67, 1.0, 0.25), (69, 1.25, 0.25), (74, 1.5, 1.2)]:
    place(mus, brass(m2f(m), d), st, 0.5); place(mus, brass(m2f(m - 12), d), st, 0.35)
for b in [0.0, 1.0, 1.5]: place(mus, kick(0.6) * 1.2, b, 0.8)
place(mus, lp(noise(2.6), 300) * np.linspace(0, 1, int(SR * 2.6)) * 0.25, 0.4)

# Comedic march (3.4 → 59.3) in F major: oom-pah tuba, pizzicato tune, glockenspiel accents
PROG = [(53, 'F'), (48, 'C'), (50, 'Dm'), (46, 'Bb'), (53, 'F'), (48, 'C'), (46, 'Bb'), (48, 'C')]
TRIAD = {'F': [65, 69, 72], 'C': [60, 64, 67], 'Dm': [62, 65, 69], 'Bb': [58, 62, 65]}
MELODY = [72, None, 74, 72, 69, None, 67, 65, 64, None, 65, 67, 69, 72, 70, 69,
          74, None, 72, 69, 70, None, 69, 67, 65, 67, 69, 65, 67, None, 72, None]
start, end = 3.45, 59.25
t0 = start; bar = 0
while t0 < end:
    root, ch = PROG[bar % 8]
    sec = 'scoot' if 42 < t0 < 49 else 'museum' if t0 > 50 else 'norm'
    for b in range(4):
        tb = t0 + b * BEAT
        if tb >= end: break
        if b % 2 == 0: place(mus, tuba(m2f(root - 12 + (7 if b == 2 else 0)), BEAT * 0.8), tb, 0.55)
        else:
            for n in TRIAD[ch]: place(mus, pizz(m2f(n), 0.25), tb, 0.12, pan=0.3)
        if sec != 'museum':
            place(mus, snare(), tb + BEAT * 0.5, 0.18 if b % 2 else 0.08, pan=-0.2)
            if sec == 'scoot':
                for h in range(4): place(mus, hat(), tb + h * BEAT / 4, 0.5, pan=0.4)
                if b % 2 == 0: place(mus, kick(), tb, 0.5)
        for half in range(2):
            mi = (bar * 8 + b * 2 + half) % len(MELODY); n = MELODY[mi]
            if n is not None and tb + half * BEAT / 2 < end:
                place(mus, pizz(m2f(n), 0.32) * 1.3, tb + half * BEAT / 2, 0.28, pan=-0.25)
                if sec == 'museum': place(mus, glock(m2f(n + 12)), tb + half * BEAT / 2, 0.08, pan=0.4)
    t0 += 4 * BEAT; bar += 1

# ---------------- VOICES (formant gibberish) ----------------
VOWELS = {'a': (800, 1200, 2500), 'e': (500, 1900, 2600), 'i': (320, 2300, 3000), 'o': (500, 900, 2400), 'u': (350, 750, 2300), 'ae': (680, 1700, 2500)}
VOICE = {'marcus': (105, 1.0), 'girl': (215, 1.17), 'worker': (150, 1.08), 'visitor': (180, 1.12)}
def glottal(f0curve):
    ph = np.cumsum(f0curve) / SR; frac = ph % 1.0
    x = (frac * 2 - 1) - (np.roll(frac, 1) * 2 - 1) * 0.0  # bright saw
    return lp(x, 4000)
def formant_filter(x, fs3, scale, bw=(90, 120, 160)):
    y = np.zeros_like(x)
    for (f, b, g) in zip(fs3, bw, (1.0, 0.6, 0.3)):
        f = min(f * scale, SR / 2 - 500)
        y += bp(x, max(60, f - b), f + b, 2) * g
    return y
def say(who, line, idx):
    f0, fs = VOICE[who]; loud = line.get('loud', 0)
    d = line['t1'] - line['t0']; n = int(d * SR); syl = line['syl']
    t = np.arange(n) / SR; u = t / d * syl; k = np.floor(u).astype(int); f = u - k
    # pitch contour: declination + per-syllable jitter + question/exclamation lift
    text = line['text']
    lift = 1.25 if text.rstrip().endswith('?') else 1.0
    contour = f0 * (1.12 - 0.18 * t / d) * (1 + 0.08 * np.sin(2 * np.pi * 0.7 * t)) * np.where(t / d > 0.82, lift, 1.0)
    contour *= (1 + 0.06 * np.array([np.sin(i * 12.9898 + idx) for i in range(syl + 1)])[np.minimum(k, syl)])
    if loud: contour *= 1.35
    src_ = glottal(contour) + 0.04 * noise(d)[:n]
    keys = list(VOWELS)
    out = np.zeros(n)
    for s in range(syl):
        a, b = int(s * n / syl), int((s + 1) * n / syl)
        v = VOWELS[keys[(s * 7 + idx * 3) % len(keys)]]
        seg_ = formant_filter(src_[a:b], v, fs)
        e = np.sin(np.pi * np.linspace(0, 1, b - a)) ** 0.6
        out[a:b] += seg_ * e
        # consonant burst at syllable start
        cb = min(int(0.03 * SR), b - a)
        out[a:a + cb] += hp(noise(0.03)[:cb], 2500) * np.linspace(1, 0, cb) * 0.25
    out *= env_adsr(n, 0.02, 0.05, 1.0, 0.06)
    out /= (np.abs(out).max() + 1e-9)
    return out * (1.0 if loud else 0.75)
for i, line in enumerate(TL['lines']):
    pan = {'marcus': 0.0, 'girl': 0.25, 'worker': -0.25, 'visitor': -0.2}[line['who']]
    place(vox, say(line['who'], line, i), line['t0'], 0.7, pan)

# ---------------- SFX ----------------
def s_portal():
    x, f = sweep(80, 900, 1.4); w = (x + 0.5 * np.sin(2 * np.pi * np.cumsum(f * 1.5) / SR)) * env_adsr(len(x), 0.05, 0.3, 0.7, 0.5)
    sh = bp(noise(1.4), 2000, 8000) * np.sin(np.linspace(0, np.pi, len(x))) * 0.3
    return (w * 0.5 + sh) * (1 + 0.5 * np.sin(2 * np.pi * 9 * T(1.4)))
def s_whoosh(d=0.6, lo=300, hi=3000):
    # crossfade between band-passed noise layers from low to high (smooth, click-free sweep)
    x = noise(d); t = T(d); u = t / d
    bands = np.geomspace(lo, hi, 5); y = np.zeros_like(x)
    for i, c in enumerate(bands):
        w = np.clip(1 - np.abs(u * 4 - i), 0, 1)
        y += bp(x, max(60, c * 0.6), min(c * 1.6, SR / 2 - 100), 1) * w
    return y * np.sin(np.pi * u) ** 2
def s_boom():
    t = T(1.6); f = 35 + 80 * np.exp(-t * 8); x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 2.5)
    return x + lp(noise(1.6), 400) * np.exp(-t * 4) * 0.5
def s_zip():
    x, f = sweep(220, 420, 0.5, 'lin'); x = (saw(1, 0.5, 1) * 0) + np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * 0.3
    return lp(x, 1200) * np.sin(np.pi * T(0.5) / 0.5) ** 2 + s_whoosh(0.5, 800, 4000) * 0.4
def s_carpass():
    d = 2.2; t = T(d); doppler = 1 + 0.15 * np.tanh((1.1 - t) * 3)
    eng = saw(1, d, 1) * 0
    f = 70 * doppler; x = np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * 0.2 + lp(noise(d), 500) * 0.6
    return lp(x, 900) * np.exp(-((t - 1.1) ** 2) / 0.25)
def s_horn():
    t = T(0.55); x = (np.sign(np.sin(2 * np.pi * 415 * t)) + np.sign(np.sin(2 * np.pi * 330 * t))) * 0.25
    return lp(x, 2500) * env_adsr(len(t), 0.01, 0.05, 0.9, 0.05)
def s_boing():
    t = T(0.5); f = 180 + 260 * np.exp(-t * 6) * (1 + 0.3 * np.sin(2 * np.pi * 14 * t))
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 6)
def s_shutter():
    t = T(0.12); c = hp(noise(0.12), 1500) * (np.exp(-t * 90) + 0.6 * np.exp(-np.maximum(0, t - 0.06) * 90) * (t > 0.06))
    return c
def s_gasp():
    t = T(0.45); return bp(noise(0.45), 600, 2500) * np.sin(np.pi * t / 0.45) * np.linspace(0.4, 1, len(t)) * 0.6
def s_draw():
    t = T(0.7); x = bp(noise(0.7), 3000, 9000) * np.exp(-t * 3) * 0.4
    ring = sum(np.sin(2 * np.pi * f * t) * np.exp(-t * 3) for f in (2100, 3170, 4420)) * 0.15
    return x + ring
def s_swish(): return s_whoosh(0.28, 600, 5000)
def s_record():
    t = T(0.45); f = 600 * (1 - t / 0.45) ** 2 + 60; x = np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * 0.2 + bp(noise(0.45), 500, 3000) * 0.3
    return x * np.exp(-t * 3)
def s_ev(d=3.5):
    t = T(d); f = 300 + 500 * np.minimum(1, t / d * 1.4); x = np.sin(2 * np.pi * np.cumsum(f) / SR) + 0.3 * np.sin(2 * np.pi * np.cumsum(f * 2.01) / SR)
    return x * np.minimum(1, t / 1.5) * np.minimum(1, (d - t) / 0.5) * 0.25 + lp(noise(d), 300) * 0.15
def s_clang():
    t = T(1.2); return sum(np.sin(2 * np.pi * f * t) * np.exp(-t * k) for f, k in ((520, 4), (1240, 6), (1913, 7), (2780, 9))) * 0.3 + hp(noise(1.2), 2000) * np.exp(-t * 40) * 0.5
def s_brake():
    t = T(0.6); f = 2600 + 300 * np.sin(2 * np.pi * 7 * t); x = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.25 + bp(noise(0.6), 1500, 4000) * 0.3
    return x * env_adsr(len(t), 0.02, 0.1, 0.8, 0.2)
def s_beep():
    out = np.zeros(int(SR * 0.5))
    for i, (f, a) in enumerate(((1320, 0), (990, 0.18))):
        t = T(0.14); b = np.sin(2 * np.pi * f * t) * env_adsr(len(t), 0.005, 0.02, 0.8, 0.03); s = int(a * SR); out[s:s + len(b)] += b * 0.5
    return out
def s_fanfare():
    out = np.zeros(int(SR * 2.4))
    for m, st, d in [(65, 0, 0.18), (65, 0.2, 0.18), (65, 0.4, 0.18), (70, 0.6, 1.4)]:
        for o in (0, -12, 4 if d > 1 else 0):
            x = brass(m2f(m + o), d); s = int(st * SR); out[s:s + len(x)] += x * (0.8 if o == 0 else 0.5)
    return out
def s_door():
    t = T(0.9); return (np.sin(2 * np.pi * 1318 * t) * np.exp(-t * 4) + np.sin(2 * np.pi * 1046 * np.maximum(0, t - 0.25)) * np.exp(-np.maximum(0, t - 0.25) * 4) * (t > 0.25)) * 0.3
def s_tap():
    t = T(0.08); return np.sin(2 * np.pi * 1760 * t) * np.exp(-t * 60) * 0.4
def s_chime():
    out = np.zeros(int(SR * 1.2))
    for i, m in enumerate((72, 76, 79, 84)):
        x = glock(m2f(m), 0.9); s = int(i * 0.09 * SR); out[s:s + len(x)] += x * 0.4
    return out
def s_bag():
    t = T(0.12); return lp(noise(0.12), 900) * np.exp(-t * 40) * 0.7 + np.sin(2 * np.pi * 110 * t) * np.exp(-t * 35) * 0.4
def s_ooh():
    t = T(1.4); f0 = 130 * (1 + 0.4 * np.sin(np.pi * t / 1.4)); x = glottal(f0)
    return formant_filter(x, VOWELS['o'], 1.0) * np.sin(np.pi * t / 1.4) * 0.8
def s_click():
    t = T(0.05); return hp(noise(0.05), 3000) * np.exp(-t * 120)
def s_scooter():
    d = 5.9; t = T(d); f = 220 + 520 * np.minimum(1, t / 1.0) + 60 * np.sin(2 * np.pi * 1.3 * t)
    f = np.where(t > 5.4, f * (1 - (t - 5.4) / 0.5 * 0.7), f)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) + 0.4 * np.sign(np.sin(2 * np.pi * np.cumsum(f * 0.5) / SR))
    return lp(x, 2500) * np.minimum(1, t / 0.1) * np.minimum(1, (d - t) / 0.3) * 0.22
def s_flutter():
    d = 1.4; t = T(d); am = (np.sin(2 * np.pi * 18 * t) > 0).astype(float)
    return bp(noise(d), 300, 1800) * am * np.exp(-t * 1.5) * 0.6
def s_pings():
    out = np.zeros(int(SR * 4.6))
    for i in range(11):
        st = i * 0.4 + (i % 3) * 0.05; t = T(0.25); x = (np.sin(2 * np.pi * 1568 * t) + np.sin(2 * np.pi * 2093 * t) * (t > 0.06)) * np.exp(-t * 18) * 0.25
        s = int(st * SR); out[s:s + len(x)] += x
    return out
def s_skid():
    t = T(0.6); return bp(noise(0.6), 1200, 3800) * env_adsr(len(t), 0.01, 0.1, 0.8, 0.3) * 0.6
def s_cheer():
    d = 2.6; t = T(d); claps = np.zeros(len(t))
    for i in range(140):
        s = int(rng.uniform(0, d - 0.05) * SR); c = hp(noise(0.03), 1200) * np.exp(-T(0.03) * 120); claps[s:s + len(c)] += c * rng.uniform(0.2, 0.6)
    crowd = bp(noise(d), 300, 2500) * 0.4 * (1 + 0.3 * np.sin(2 * np.pi * 3.3 * t))
    return (claps + crowd) * np.minimum(1, t / 0.2) * np.minimum(1, (d - t) / 0.8)
def s_steps():
    out = np.zeros(int(SR * 1.6))
    for i in range(4):
        t = T(0.25); x = lp(noise(0.25), 1500) * np.exp(-t * 30); s = int(i * 0.36 * SR); out[s:s + len(x)] += x * 0.5
    # reverb tail feel
    return out + np.convolve(out, np.exp(-T(0.4) * 9) * hp(noise(0.4), 300) * 0.05)[:len(out)]
def choir(d, chord, gain=1.0):
    t = T(d); out = np.zeros(len(t))
    for n in chord:
        for det in (-0.004, 0.004):
            f0 = m2f(n) * (1 + det) * (1 + 0.004 * np.sin(2 * np.pi * 5 * t)); out += formant_filter(glottal(f0), VOWELS['a'], 1.1)
    return out / len(chord) * env_adsr(len(t), 0.25, 0.3, 0.8, 0.8) * gain
def s_laugh():
    out = np.zeros(int(SR * 1.5))
    for i in range(6):
        t = T(0.16); f0 = 260 * (1 - i * 0.04) * (1 + 0.1 * np.sin(np.pi * t / 0.16)); x = formant_filter(glottal(f0), VOWELS['a'], 1.15) * np.sin(np.pi * t / 0.16)
        x += bp(noise(0.16), 1000, 4000) * 0.15 * np.exp(-t * 30); s = int(i * 0.2 * SR); out[s:s + len(x)] += x
    return out / (np.abs(out).max() + 1e-9) * 0.7
def s_zoom(): return s_whoosh(0.4, 400, 6000) * 1.2
def s_sting():
    out = np.zeros(int(SR * 1.3))
    for m in (65, 69, 72, 77):
        x = brass(m2f(m), 1.1); out[:len(x)] += x * 0.6
    t = T(1.3); out += np.sin(2 * np.pi * 43.65 * t) * np.exp(-t * 3) * 0.6
    return out
def s_beeps():
    # 38 taps accelerating between 33.0 and 35.3 (matches the kiosk counter)
    d = 2.4; out = np.zeros(int(SR * d)); last = 2
    for i in range(int(2.3 * SR)):
        u = i / SR / 2.3; q = min(40, 2 + int(u ** 0.7 * 38.99))
        if q != last:
            x = np.sin(2 * np.pi * (1500 + q * 12) * T(0.05)) * np.exp(-T(0.05) * 50) * 0.35
            out[i:i + len(x)] += x[:len(out) - i]; last = q
    return out
def s_bags():
    out = np.zeros(int(SR * 2.8))
    for i in range(40):
        x = s_bag(); s = int(i * 0.06 * SR); out[s:s + len(x)] += x * (0.6 + 0.4 * (i % 3 == 0))
    return out

SFX = {'portal': (s_portal, 0.55), 'whoosh': (lambda: s_whoosh(0.7), 0.7), 'boom': (s_boom, 0.9), 'zip': (s_zip, 0.5), 'carpass': (s_carpass, 0.6),
       'horn': (s_horn, 0.45), 'boing': (s_boing, 0.45), 'shutter': (s_shutter, 0.8), 'gasp': (s_gasp, 0.6), 'draw': (s_draw, 0.6), 'swish': (s_swish, 0.6),
       'record': (s_record, 0.6), 'ev': (s_ev, 0.5), 'clang': (s_clang, 0.6), 'brake': (s_brake, 0.4), 'beep': (s_beep, 0.6), 'fanfare': (s_fanfare, 0.55),
       'door': (s_door, 0.6), 'tap': (s_tap, 0.7), 'beeps': (s_beeps, 0.7), 'chime': (s_chime, 0.6), 'bags': (s_bags, 0.8), 'ooh': (s_ooh, 0.5),
       'click': (s_click, 0.6), 'scooter': (s_scooter, 0.7), 'flutter': (s_flutter, 0.6), 'pings': (s_pings, 0.5), 'skid': (s_skid, 0.6), 'cheer': (s_cheer, 0.55),
       'steps': (s_steps, 0.6), 'choir': (lambda: choir(1.8, [57, 64, 69], 0.7), 0.5), 'laugh': (s_laugh, 0.6), 'zoom': (s_zoom, 0.6),
       'choirbig': (lambda: choir(2.6, [53, 60, 65, 69, 72], 1.0), 0.6), 'sting': (s_sting, 0.8)}
for name, at in TL['sfx']:
    fn, g = SFX[name]; x = fn(); x = x / (np.abs(x).max() + 1e-9)
    pan = {'zip': -0.4, 'carpass': 0.3, 'horn': 0.4, 'ev': -0.3, 'pings': 0.35, 'flutter': 0.3}.get(name, 0.0)
    place(sfx, x, at, g * 0.8, pan)
# city ambience under the street scenes, restaurant murmur
amb = lp(noise(DUR), 600) * 0.05 + bp(noise(DUR), 800, 3000) * 0.012
envamb = np.zeros(int(SR * DUR))
for a, b in ((3.2, 28.0), (40.0, 50.0)): envamb[int(a * SR):int(b * SR)] = 1
envamb = np.convolve(envamb, np.ones(4800) / 4800, 'same')
sfx[0, :len(amb)] += amb * envamb; sfx[1, :len(amb)] += np.roll(amb, 911) * envamb

# ---------------- MIX ----------------
# duck music under dialogue
duck = np.ones(N)
for l in TL['lines']: duck[int((l['t0'] - 0.1) * SR):int((l['t1'] + 0.15) * SR)] = 0.45
duck = np.convolve(duck, np.ones(9600) / 9600, 'same')
# small room reverb on everything
def reverb(x, d=1.6, mix=0.18):
    ir = noise(d) * np.exp(-T(d) * 4.5); ir = lp(ir, 5000); ir /= np.abs(ir).sum() ** 0.5 * 8
    return x + signal.fftconvolve(x, ir)[:len(x)] * mix
mix = np.zeros((2, N))
for c in range(2):
    mix[c] = reverb(mus[c] * duck * 0.55, 1.8, 0.25) + reverb(sfx[c], 1.0, 0.12) + reverb(vox[c] * 1.0, 0.8, 0.1)
mix = np.tanh(mix * 1.3) / np.tanh(1.3)
mix *= 0.89 / np.abs(mix).max()
fade = np.ones(N); fe = int(59.75 * SR); fade[fe:] = np.linspace(1, 0, N - fe).clip(0)
mix *= fade
mix = mix[:, :int(SR * DUR)]
import wave
with wave.open('audio.wav', 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((mix.T * 32767).astype('<i2').tobytes())
print('audio.wav', mix.shape[1] / SR, 's')
