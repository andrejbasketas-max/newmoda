"""Synthesizes the 15 s soundtrack from scratch with NumPy. No samples.

128 BPM, A minor, 8 bars (1 bar = 1.875 s), locked to the cuts in reel.js.
Output: music.wav (48 kHz, 16-bit stereo).
"""
import wave
import numpy as np

SR = 48000
DUR = 15.0
BPM = 128
BEAT = 60 / BPM
BAR = BEAT * 4
N = int(SR * DUR)
rng = np.random.default_rng(26)


def mtof(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def buf():
    return np.zeros((N, 2))


def place(bus, sig, t, gain=1.0, pan=0.0):
    """Add a mono or stereo signal into a stereo bus at time t (equal-power pan)."""
    i = int(round(t * SR))
    if i >= N:
        return
    if sig.ndim == 1:
        l, r = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
        sig = np.stack([sig * l, sig * r], axis=1) * np.sqrt(2)
    n = min(len(sig), N - i)
    bus[i:i + n] += sig[:n] * gain


def tt(d):
    return np.arange(int(d * SR)) / SR


# ---------- oscillators ----------
def saw(f, d, maxf=9000.0, phase=0.0):
    t = tt(d)
    out = np.zeros_like(t)
    for k in range(1, int(maxf / f) + 1):
        out += np.sin(2 * np.pi * k * f * t + phase * k) / k
    return out * (2 / np.pi)


def square(f, d, maxf=8000.0):
    t = tt(d)
    out = np.zeros_like(t)
    for k in range(1, int(maxf / f) + 1, 2):
        out += np.sin(2 * np.pi * k * f * t) / k
    return out * (4 / np.pi)


def noise(d):
    return rng.uniform(-1, 1, int(d * SR))


# ---------- filters (frequency domain) ----------
def fft_filter(x, lo=None, hi=None, order=4):
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR) + 1e-9
    m = np.ones_like(f)
    if hi is not None:
        m *= 1 / np.sqrt(1 + (f / hi) ** (2 * order))
    if lo is not None:
        m *= 1 / np.sqrt(1 + (lo / f) ** (2 * order))
    return np.fft.irfft(X * m, len(x))


def tv_lowpass(x, fc, res=0.0, n=2048, hop=512):
    """Time-varying low-pass via STFT overlap-add. fc: function of time (s) -> Hz."""
    win = np.hanning(n)
    pad = np.concatenate([np.zeros(n), x, np.zeros(n)])
    out = np.zeros_like(pad)
    norm = np.zeros_like(pad)
    f = np.fft.rfftfreq(n, 1 / SR)
    for s in range(0, len(pad) - n, hop):
        c = max(fc(max((s + n / 2 - n) / SR, 0.0)), 20.0)
        m = 1 / np.sqrt(1 + (f / c) ** 8) + res * np.exp(-(((f - c) / (0.18 * c)) ** 2))
        out[s:s + n] += np.fft.irfft(np.fft.rfft(pad[s:s + n] * win) * m, n) * win
        norm[s:s + n] += win ** 2
    return (out / np.maximum(norm, 1e-6))[n:n + len(x)]


def env_adsr(d, a=0.005, dec=0.1, s=0.6, r=0.05):
    t = tt(d)
    e = np.where(t < a, t / a, s + (1 - s) * np.exp(-(t - a) / max(dec, 1e-4)))
    rel = int(r * SR)
    if rel and rel < len(e):
        e[-rel:] *= np.linspace(1, 0, rel)
    return e


# ---------- drums ----------
def kick(big=False):
    d = 1.4 if big else 0.5
    t = tt(d)
    f = 44 + 120 * np.exp(-t * 28) + (20 * np.exp(-t * 4) if big else 0)
    ph = 2 * np.pi * np.cumsum(f) / SR
    body = np.sin(ph) * np.exp(-t * (2.2 if big else 6.5))
    click = fft_filter(noise(0.006), lo=2000) * np.linspace(1, 0, int(0.006 * SR))
    body[:len(click)] += click * 0.5
    return np.tanh(body * 1.6) * 0.95


def clap():
    d = 0.35
    t = tt(d)
    n = fft_filter(noise(d), lo=900, hi=5000, order=2)
    e = np.zeros_like(t)
    for o in (0.0, 0.011, 0.022):
        e += np.where(t >= o, np.exp(-(t - o) * 90), 0)
    e += np.where(t >= 0.03, 0.55 * np.exp(-(t - 0.03) * 14), 0)
    tone = np.sin(2 * np.pi * 185 * t) * np.exp(-t * 30) * 0.35
    return n * e * 0.8 + tone


def hat(open_=False):
    d = 0.25 if open_ else 0.06
    t = tt(d)
    return fft_filter(noise(d), lo=7500, order=3) * np.exp(-t * (14 if open_ else 70))


def crash():
    d = 2.2
    t = tt(d)
    return fft_filter(noise(d), lo=2500, order=2) * np.exp(-t * 2.2)


def snare_roll_hit(pitch):
    d = 0.09
    t = tt(d)
    n = fft_filter(noise(d), lo=1200 * pitch, hi=9000, order=2)
    return (n * 0.7 + np.sin(2 * np.pi * 200 * pitch * t) * 0.4) * np.exp(-t * 38)


# ---------- FX ----------
def riser(d, f0=200, f1=9000):
    t = tt(d)
    x = noise(d)
    y = tv_lowpass(x, lambda s: f0 * (f1 / f0) ** min(max(s / d, 0), 1), res=1.6)
    sweep = np.sin(2 * np.pi * np.cumsum(220 * 2 ** (t / d * 2.5)) / SR) * 0.25
    return (y + sweep) * (t / d) ** 2.2


def whoosh(d):
    t = tt(d)
    peak = 0.8
    e = np.where(t / d < peak, (t / d / peak) ** 2, np.exp(-(t / d - peak) * 25))
    y = tv_lowpass(noise(d), lambda s: 400 + 7000 * min(s / d, 1) ** 1.5, res=1.2)
    return y * e


def blip(f, d=0.12, glide=1.0):
    t = tt(d)
    ph = 2 * np.pi * np.cumsum(f * glide ** (t / d)) / SR
    return (np.sin(ph) + 0.25 * np.sin(2 * ph)) * np.exp(-t * 28)


def zap(d=0.14):
    t = tt(d)
    ph = 2 * np.pi * np.cumsum(2400 * (0.08 ** (t / d))) / SR
    return np.sign(np.sin(ph)) * 0.3 * np.exp(-t * 18)


def sub_boom():
    t = tt(2.0)
    ph = 2 * np.pi * np.cumsum(52 * 0.72 ** (t / 2.0)) / SR
    return np.sin(ph) * np.exp(-t * 1.6)


# ---------- harmony ----------
# chords per beat-slot (bar, beat) -> midi notes; bass root
CHORDS = {
    0: [57, 60, 64], 1: [57, 60, 64], 2: [53, 57, 60], 3: [55, 60, 64],
    4: [55, 59, 62], 5: [57, 60, 64], 6: [53, 57, 60], 7: [57, 60, 64, 71],
}
ROOTS = {0: 33, 1: 33, 2: 29, 3: 36, 4: 31, 5: 33, 6: 29, 7: 33}
E_MAJ = [56, 59, 64]  # dominant at the end of bar 6, pulls back to Am


def chord_at(bar, beat):
    if bar == 6 and beat >= 2:
        return E_MAJ, 28
    return CHORDS[bar], ROOTS[bar]


def kick_times():
    ts = []
    for b in range(1, 7):
        for k in range(4):
            if b == 6 and k == 3:
                continue
            ts.append(b * BAR + k * BEAT)
    return ts


def sidechain():
    g = np.ones(N)
    t = np.arange(N) / SR
    for tk in kick_times() + [7 * BAR]:
        m = (t >= tk) & (t < tk + 0.3)
        g[m] = np.minimum(g[m], 1 - 0.72 * (1 - (t[m] - tk) / 0.3) ** 2)
    return g


def build():
    drums, bass, pad, lead, fx, send = buf(), buf(), buf(), buf(), buf(), buf()

    # ---- pad: detuned saws, filter opens through the intro
    padraw = np.zeros(N)
    segs = [(b * BAR, BAR, CHORDS[b]) for b in range(6)] + [(6 * BAR, BEAT * 2, CHORDS[6]), (6 * BAR + 2 * BEAT, BEAT * 2, E_MAJ)]
    for start, d, notes in segs:
        dd = d + 0.02
        x = np.zeros(int(dd * SR))
        for m in notes:
            for cents in (-9, 0, 9):
                x += saw(mtof(m) * 2 ** (cents / 1200), dd, maxf=7000, phase=rng.uniform(0, 6.28))
        x *= np.minimum(1, np.arange(len(x)) / (0.01 * SR))
        i = int(start * SR)
        padraw[i:i + len(x)] += x[:N - i]

    def pad_fc(s):
        if s < BAR:
            return 250 + 2200 * (s / BAR) ** 2
        if s < 6 * BAR:
            return 1900 + 700 * np.sin(s * 1.3)
        return 1600 + 3000 * ((s - 6 * BAR) / BAR) ** 2
    padf = tv_lowpass(padraw, pad_fc, res=0.6) * 0.085
    padf *= sidechain()
    place(pad, padf, 0, pan=-0.15)
    place(pad, np.roll(padf, int(0.013 * SR)), 0, gain=0.8, pan=0.6)

    # ---- drums
    for tk in kick_times():
        place(drums, kick(), tk, 0.9)
    for b in range(1, 6):
        for k in (1, 3):
            place(drums, clap(), b * BAR + k * BEAT, 0.42, pan=0.05)
            place(send, clap(), b * BAR + k * BEAT, 0.25)
    place(drums, clap(), 6 * BAR + BEAT, 0.42)
    for b in range(1, 7):
        for k in range(4):
            if b == 6 and k == 3:
                continue
            place(drums, hat(True), b * BAR + k * BEAT + BEAT / 2, 0.16, pan=0.3)
            if b >= 3:
                for s in (1, 3):
                    place(drums, hat(), b * BAR + k * BEAT + s * BEAT / 4, 0.12, pan=-0.35)

    # ---- bass: off-beat 8ths with a sub layer
    for b in range(1, 7):
        for k in range(4):
            if b == 6 and k == 3:
                continue
            _, root = chord_at(b, k)
            for off, oct_ in ((0.5, 0), (0.75, 12)) if b >= 3 else ((0.5, 0),):
                d = BEAT * 0.42
                f = mtof(root + 12 + oct_)
                x = saw(f, d, maxf=1400) * 0.6 + np.sin(2 * np.pi * f / 2 * tt(d)) * (0.7 if oct_ == 0 else 0)
                x *= env_adsr(d, 0.004, 0.08, 0.5, 0.03)
                place(bass, x, b * BAR + k * BEAT + off * BEAT, 0.5)

    # ---- arp: 16th plucks from bar 3, ping-pong delay
    pattern = [0, 1, 2, 1, 2, 3, 2, 1]
    for b in range(3, 7):
        for k in range(4):
            if b == 6 and k == 3:
                continue
            notes, _ = chord_at(b, k)
            tones = [n + 12 for n in notes] + [notes[0] + 24]
            for s in range(4):
                idx = pattern[(k * 4 + s) % 8]
                f = mtof(tones[idx % len(tones)])
                d = 0.16
                x = square(f, d, 6000) * 0.5 + saw(f * 2, d, 6000) * 0.2
                x = fft_filter(x, hi=2600 + 1800 * (b - 3) / 3, order=2) * np.exp(-tt(d) * 22)
                t0 = b * BAR + k * BEAT + s * BEAT / 4
                place(lead, x, t0, 0.17, pan=-0.2)
                place(lead, x, t0 + BEAT * 0.75, 0.07, pan=0.7)
                place(lead, x, t0 + BEAT * 1.5, 0.035, pan=-0.7)
                place(send, x, t0, 0.08)

    # ---- intro sound design (synced to the visuals in reel.js)
    place(fx, blip(1320, 0.18, 0.7), 0.06, 0.35)                     # dot pops in
    place(fx, whoosh(0.5)[::-1] * 0.6, BEAT - 0.02, 0.5)               # line stretches
    for i in range(18):                                                # typed characters
        x = fft_filter(noise(0.012), lo=3000, hi=9000) * np.exp(-tt(0.012) * 400)
        place(fx, x, 0.62 + 0.034 * (i + 1), 0.35, pan=rng.uniform(-0.3, 0.3))
    place(fx, blip(660, 0.25, 1.5), BEAT * 2, 0.22)                    # line splits
    place(fx, riser(BAR - 0.35), 0.35, 0.3)                            # build into the drop
    place(drums, crash(), BAR, 0.32)

    # ---- transitions between scenes (whooshes into each cut)
    for b in (2, 3, 4, 5):
        place(fx, whoosh(0.45), b * BAR - 0.45, 0.35, pan=0.4 if b % 2 else -0.4)
    # shape morphs: rising blips on each beat of bar 2
    for k, m in enumerate([76, 79, 83, 88]):
        place(fx, blip(mtof(m), 0.2, 1.02), 2 * BAR + k * BEAT, 0.16, pan=(k - 1.5) * 0.4)
        place(send, blip(mtof(m), 0.2), 2 * BAR + k * BEAT, 0.12)
    # particles gather into the word
    place(fx, whoosh(0.7)[::-1] * 0.8, 3 * BAR + BEAT * 1.15, 0.3)
    place(fx, blip(1760, 0.3, 0.5), 3 * BAR + 1.56, 0.18)             # explosion
    # montage stings
    place(fx, zap(), 6 * BAR + BEAT, 0.3, pan=-0.3)
    place(fx, zap(), 6 * BAR + 2 * BEAT, 0.3, pan=0.3)
    # 32nd-note snare roll matching the word flashes, plus a riser
    for i in range(8):
        place(drums, snare_roll_hit(1 + i * 0.09), 6 * BAR + 3 * BEAT + i * BEAT / 8, 0.28 + i * 0.03)
    place(fx, riser(BEAT * 1.6, 600, 12000), 7 * BAR - BEAT * 1.6, 0.3)

    # ---- the drop: end card
    T = 7 * BAR
    place(drums, kick(big=True), T, 1.0)
    place(drums, sub_boom(), T, 0.75)
    place(drums, crash(), T, 0.45)
    place(send, crash(), T, 0.3)
    stab = np.zeros(int(1.9 * SR))
    for m in CHORDS[7] + [45]:
        for cents in (-7, 7):
            stab += saw(mtof(m) * 2 ** (cents / 1200), 1.9, maxf=6000)
    stab = tv_lowpass(stab, lambda s: 5000 * np.exp(-s * 1.6) + 300) * np.exp(-tt(1.9) * 1.1) * 0.09
    place(pad, stab, T, 1.0)
    place(send, stab, T, 0.6)
    place(fx, blip(mtof(88), 0.3, 1.0), T + 0.48, 0.2)                # the dot returns
    place(send, blip(mtof(88), 0.3), T + 0.48, 0.2)
    place(fx, blip(mtof(76), 0.4, 0.5), T + 1.72, 0.2)                # the dot vanishes

    # ---- reverb: stereo convolution with a decaying noise impulse
    ir_len = int(2.4 * SR)
    t = np.arange(ir_len) / SR
    irL = fft_filter(rng.standard_normal(ir_len), hi=6000) * np.exp(-t * 2.6)
    irR = fft_filter(rng.standard_normal(ir_len), hi=6000) * np.exp(-t * 2.6)
    irL /= np.sqrt(np.sum(irL ** 2)); irR /= np.sqrt(np.sum(irR ** 2))
    send = send + pad * 0.35 + lead * 0.5
    L = N + ir_len
    nfft = 1 << (L - 1).bit_length()
    wet = np.stack([np.fft.irfft(np.fft.rfft(send[:, 0], nfft) * np.fft.rfft(irL, nfft), nfft)[:N],
                    np.fft.irfft(np.fft.rfft(send[:, 1], nfft) * np.fft.rfft(irR, nfft), nfft)[:N]], axis=1)
    wet *= 0.55

    for nm, st in (("drums", drums), ("bass", bass), ("pad", pad), ("lead", lead), ("fx", fx), ("wet", wet)):
        print(nm, "peak %.2f rms %.3f" % (np.max(np.abs(st)), np.sqrt(np.mean(st ** 2))))
    mix = drums * 1.0 + bass * 1.0 + pad * 1.0 + lead * 1.0 + fx * 1.0 + wet
    # master: gentle saturation, normalize, short fade at the very end
    mix = np.tanh(mix * 0.75) / 0.75
    mix /= np.max(np.abs(mix)) / 0.89
    fade = int(0.15 * SR)
    mix[-fade:] *= np.linspace(1, 0, fade)[:, None] ** 2
    return mix


if __name__ == '__main__':
    out = build()
    pcm = (np.clip(out, -1, 1) * 32767).astype('<i2')
    with wave.open('music.wav', 'wb') as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    print('music.wav', out.shape, 'peak', float(np.max(np.abs(out))))
