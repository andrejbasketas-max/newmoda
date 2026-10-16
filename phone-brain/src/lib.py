"""Drawing kit for the flat, hand-drawn stick-figure style (1920x1080 SVG)."""
import math, base64, os

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 1920, 1080

INK = '#1c1c1c'
BG = '#F6F3EA'
CREAM = '#F2E3C6'
CREAM_D = '#E6D2AC'
SCREEN = '#BFE1F3'
RED = '#E2483D'
GREEN = '#45B058'
YELLOW = '#F6C83A'
PINK = '#F7AABD'
PINK_D = '#DC7E98'
GRAY = '#9C9C9C'
LGRAY = '#D4D4D4'
DGRAY = '#6E6E6E'
COUCH = '#A9ABAE'
COUCH_D = '#8E9094'
WOOD = '#C08A55'
WOOD_D = '#94603A'
JEANS = '#4F7EC2'
SKY = '#BDE2F4'
SAND = '#EBD49E'
GRASS = '#93C76B'
TREE = '#5FA351'
TREE_D = '#4A8840'
DUSK = '#F6B48F'
DUSK2 = '#F7C9A0'
NIGHT = '#2D3A68'
NIGHT2 = '#3C4B80'
BLUE = '#3E7CC9'
ORANGE = '#F28C28'
PURPLE = '#8E6CC4'
BROWN = '#7A4B26'
CARD = '#CFA36B'
CARD_D = '#B08350'
PIG = '#AEB4BC'
PIG_D = '#8C939C'
SKIN_HAIR = {'black': INK, 'gray': '#B9B9B9', 'brown': '#7B4A2A', 'red': '#D9582B', 'dark': '#2E2420'}

SW = 9

with open(os.path.join(HERE, 'marker.woff2'), 'rb') as fh:
    FONT = base64.b64encode(fh.read()).decode()


def F(v):
    s = f'{v:.1f}'
    return s[:-2] if s.endswith('.0') else s


def _st(fill, c, w, op=None, dash=None):
    a = f' fill="{fill}" stroke="{c if c else "none"}" stroke-width="{F(w)}"'
    if op is not None:
        a += f' opacity="{op}"'
    if dash:
        a += f' stroke-dasharray="{dash}"'
    return a


def line(x1, y1, x2, y2, w=SW, c=INK, dash=None, op=None):
    return f'<line x1="{F(x1)}" y1="{F(y1)}" x2="{F(x2)}" y2="{F(y2)}"{_st("none", c, w, op, dash)}/>'


def pts(p):
    return ' '.join(f'{F(x)},{F(y)}' for x, y in p)


def poly(p, fill='#fff', c=INK, w=SW, op=None, dash=None):
    return f'<polygon points="{pts(p)}"{_st(fill, c, w, op, dash)}/>'


def pline(p, c=INK, w=SW, dash=None, op=None, fill='none'):
    return f'<polyline points="{pts(p)}"{_st(fill, c, w, op, dash)}/>'


def circ(cx, cy, r, fill='#fff', c=INK, w=SW, op=None, dash=None):
    return f'<circle cx="{F(cx)}" cy="{F(cy)}" r="{F(r)}"{_st(fill, c, w, op, dash)}/>'


def ell(cx, cy, rx, ry, fill='#fff', c=INK, w=SW, op=None, rot=0, dash=None):
    t = f' transform="rotate({F(rot)} {F(cx)} {F(cy)})"' if rot else ''
    return f'<ellipse cx="{F(cx)}" cy="{F(cy)}" rx="{F(rx)}" ry="{F(ry)}"{_st(fill, c, w, op, dash)}{t}/>'


def rect(x, y, w, h, fill='#fff', c=INK, sw=SW, rx=0, op=None, dash=None, rot=0):
    t = f' transform="rotate({F(rot)} {F(x + w / 2)} {F(y + h / 2)})"' if rot else ''
    return f'<rect x="{F(x)}" y="{F(y)}" width="{F(w)}" height="{F(h)}" rx="{F(rx)}"{_st(fill, c, sw, op, dash)}{t}/>'


def path(d, fill='none', c=INK, w=SW, op=None, dash=None):
    return f'<path d="{d}"{_st(fill, c, w, op, dash)}/>'


def txt(x, y, s, size=110, fill=INK, anchor='middle', rot=0, op=None, outline=None, ow=10, spacing=None):
    t = f' transform="rotate({F(rot)} {F(x)} {F(y)})"' if rot else ''
    o = f' opacity="{op}"' if op is not None else ''
    sp = f' letter-spacing="{spacing}"' if spacing else ''
    st = ''
    if outline:
        st = f' stroke="{outline}" stroke-width="{ow}" paint-order="stroke"'
    s = s.replace('&', '&amp;').replace('<', '&lt;')
    return (f'<text x="{F(x)}" y="{F(y)}" font-size="{F(size)}" fill="{fill}" text-anchor="{anchor}"'
            f'{st}{t}{o}{sp}>{s}</text>')


def G(inner, x=0, y=0, s=1, rot=0, op=None, sx=None, sy=None):
    if isinstance(inner, (list, tuple)):
        inner = ''.join(map(str, inner))
    tr = []
    if x or y:
        tr.append(f'translate({F(x)} {F(y)})')
    if rot:
        tr.append(f'rotate({F(rot)})')
    sx = s if sx is None else sx
    sy = s if sy is None else sy
    if sx != 1 or sy != 1:
        tr.append(f'scale({sx:.4f} {sy:.4f})')
    t = f' transform="{" ".join(tr)}"' if tr else ''
    o = f' opacity="{op}"' if op is not None else ''
    return f'<g{t}{o}>{inner}</g>'


def tube(x1, y1, x2, y2, w, fill='#fff', c=INK, ow=SW):
    """Outlined capsule (thick line with an outline)."""
    return line(x1, y1, x2, y2, w + 2 * ow, c) + line(x1, y1, x2, y2, w, fill)


def doc(parts, bg=BG):
    body = ''.join(map(str, parts))
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">'
            f'<defs><style>@font-face{{font-family:"Marker";src:url(data:font/woff2;base64,{FONT}) format("woff2")}}'
            f'*{{stroke-linejoin:round;stroke-linecap:round}}text{{font-family:"Marker",sans-serif}}</style>'
            f'<filter id="rough" filterUnits="userSpaceOnUse" x="0" y="0" width="{W}" height="{H}">'
            f'<feTurbulence type="fractalNoise" baseFrequency="0.018" numOctaves="2" seed="4" result="n"/>'
            f'<feDisplacementMap in="SourceGraphic" in2="n" scale="5" xChannelSelector="R" yChannelSelector="G"/>'
            f'</filter></defs><rect width="{W}" height="{H}" fill="{bg}"/>'
            f'<g filter="url(#rough)">{body}</g></svg>')


# ---------------------------------------------------------------- small marks
def blob_d(cx, cy, rx, ry, n=10, bulge=1.2, phase=0.0):
    a = [phase + 2 * math.pi * i / n for i in range(n)]
    p = [(cx + rx * math.cos(t), cy + ry * math.sin(t)) for t in a]
    d = f'M{F(p[0][0])} {F(p[0][1])}'
    for i in range(n):
        t = phase + 2 * math.pi * (i + 0.5) / n
        q = p[(i + 1) % n]
        d += f' Q{F(cx + rx * bulge * math.cos(t))} {F(cy + ry * bulge * math.sin(t))} {F(q[0])} {F(q[1])}'
    return d + 'Z'


def cloud(cx, cy, rx, ry, fill='#fff', c=INK, w=SW, n=9, bulge=1.25, op=None):
    return path(blob_d(cx, cy, rx, ry, n, bulge, 0.3), fill, c, w, op)


def thought(cx, cy, rx, ry, tail=None, fill='#fff', w=SW, n=10):
    out = cloud(cx, cy, rx, ry, fill, INK, w, n, 1.22)
    if tail:
        tx, ty = tail
        for i, f in enumerate((0.55, 0.75, 0.9)):
            bx = cx + (tx - cx) * f
            by = cy + ry * 0.9 * (1 - f) + (ty) * f - cy * 0 - (cy + ry * 0.9) * 0
            by = (cy + ry) + (ty - (cy + ry)) * f
            r = [20, 14, 9][i] * (rx / 260 + 0.4)
            out += circ(bx, by, r, fill, INK, w * 0.8)
    return out


def speech(x, y, w, h, tail=None, fill='#fff', c=INK, sw=SW, rx=None):
    rx = h * 0.4 if rx is None else rx
    out = ''
    if tail:
        tx, ty = tail
        cx, cy = x + w / 2, y + h / 2
        bx = cx + (tx - cx) * 0.25
        out += poly([(bx - 28, cy), (bx + 28, cy), (tx, ty)], fill, c, sw)
    out += rect(x, y, w, h, fill, c, sw, rx)
    if tail:
        tx, ty = tail
        cx, cy = x + w / 2, y + h / 2
        bx = cx + (tx - cx) * 0.25
        out += poly([(bx - 22, cy), (bx + 22, cy), (cx + (tx - cx) * 0.8, cy + (ty - cy) * 0.8)], fill, 'none', 0)
    return out


def motion(x, y, ang, n=3, ln=60, gap=26, w=7, c=INK):
    """Parallel motion lines trailing behind (x,y), pointing along ang (deg)."""
    a = math.radians(ang)
    ux, uy = math.cos(a), math.sin(a)
    px, py = -uy, ux
    out = ''
    for i in range(n):
        o = (i - (n - 1) / 2) * gap
        l = ln * (1 - 0.25 * abs(i - (n - 1) / 2))
        sx, sy = x + px * o, y + py * o
        out += line(sx, sy, sx - ux * l, sy - uy * l, w, c)
    return out


def arcs(x, y, r0, a0, a1, n=3, gap=22, w=7, c=INK):
    """Concentric arc strokes (for motion / signal waves)."""
    out = ''
    for i in range(n):
        r = r0 + i * gap
        p0 = (x + r * math.cos(math.radians(a0)), y + r * math.sin(math.radians(a0)))
        p1 = (x + r * math.cos(math.radians(a1)), y + r * math.sin(math.radians(a1)))
        large = 1 if abs(a1 - a0) > 180 else 0
        out += path(f'M{F(p0[0])} {F(p0[1])} A{F(r)} {F(r)} 0 {large} 1 {F(p1[0])} {F(p1[1])}', 'none', c, w)
    return out


def zig(x1, y1, x2, y2, n=4, amp=10, w=6, c=INK):
    dx, dy = x2 - x1, y2 - y1
    L = math.hypot(dx, dy) or 1
    px, py = -dy / L, dx / L
    p = [(x1, y1)]
    for i in range(1, 2 * n):
        t = i / (2 * n)
        s = amp if i % 2 else -amp
        p.append((x1 + dx * t + px * s, y1 + dy * t + py * s))
    p.append((x2, y2))
    return pline(p, c, w)


def buzz(x, y, s=1, c=INK, w=6):
    out = ''
    for sg in (-1, 1):
        for i, dy in enumerate((-30, 0, 30)):
            l = 40 if i == 1 else 30
            out += zig(x + sg * 55 * s, y + dy * s, x + sg * (55 + l) * s, y + dy * s * 1.25, 3, 7 * s, w, c)
    return out


def drop(x, y, s=1, rot=0, fill='#8FD0F0'):
    d = 'M0 -24 Q14 -4 13 6 A13 13 0 1 1 -13 6 Q-14 -4 0 -24Z'
    return G(path(d, fill, INK, 5), x, y, s, rot)


def sparkle(x, y, s=1, fill=YELLOW, w=5):
    d = 'M0 -40 Q6 -6 40 0 Q6 6 0 40 Q-6 6 -40 0 Q-6 -6 0 -40Z'
    return G(path(d, fill, INK, w / s if s else w), x, y, s)


def burst(x, y, r0, r1, n=10, w=8, c=RED, jag=True, a0=0):
    out = ''
    for i in range(n):
        a = math.radians(a0 + 360 * i / n)
        x1, y1 = x + r0 * math.cos(a), y + r0 * math.sin(a)
        x2, y2 = x + r1 * math.cos(a), y + r1 * math.sin(a)
        out += zig(x1, y1, x2, y2, 2, 9, w, c) if jag else line(x1, y1, x2, y2, w, c)
    return out


def redx(x, y, size=200, w=26, c=RED):
    h = size / 2
    return line(x - h, y - h, x + h, y + h, w, c) + line(x + h, y - h, x - h, y + h, w, c)


def strike(x1, y1, x2, y2, w=18, c=RED):
    return line(x1, y1, x2, y2, w, c)


def check(x, y, size=100, c=GREEN, w=None):
    w = w or size * 0.18
    s = size / 100
    return pline([(x - 45 * s, y), (x - 12 * s, y + 35 * s), (x + 50 * s, y - 40 * s)], c, w)


def qmark(x, y, size=160, fill=INK, rot=0):
    return txt(x, y + size * 0.35, '?', size, fill, rot=rot)


def zzz(x, y, s=1):
    return (txt(x, y, 'Z', 70 * s) + txt(x + 55 * s, y - 60 * s, 'Z', 55 * s) +
            txt(x + 100 * s, y - 110 * s, 'Z', 42 * s))


def shadow(x, y, w, op=0.12):
    return ell(x, y, w / 2, w * 0.07, INK, None, 0, op)


def heart(x, y, s=1, fill=RED, w=7):
    d = 'M0 30 C-55 -5 -45 -55 -15 -50 C-5 -48 0 -40 0 -32 C0 -40 5 -48 15 -50 C45 -55 55 -5 0 30Z'
    return G(path(d, fill, INK, w / s), x, y, s)


def star(x, y, r=40, fill=YELLOW, w=6, rot=0):
    p = []
    for i in range(10):
        a = math.radians(-90 + rot + 36 * i)
        rr = r if i % 2 == 0 else r * 0.45
        p.append((x + rr * math.cos(a), y + rr * math.sin(a)))
    return poly(p, fill, INK, w)


def arrow(x1, y1, x2, y2, w=12, c=INK, head=36, fill=None):
    a = math.atan2(y2 - y1, x2 - x1)
    bx, by = x2 - head * 0.8 * math.cos(a), y2 - head * 0.8 * math.sin(a)
    p1 = (x2 - head * math.cos(a - 0.5), y2 - head * math.sin(a - 0.5))
    p2 = (x2 - head * math.cos(a + 0.5), y2 - head * math.sin(a + 0.5))
    return line(x1, y1, bx, by, w, c) + poly([p1, (x2, y2), p2], fill or c, c, w * 0.6)


def curved_arrow(cx, cy, r, a0, a1, w=12, c=INK, head=34):
    """Arc arrow from angle a0 to a1 (degrees, clockwise if a1>a0)."""
    p0 = (cx + r * math.cos(math.radians(a0)), cy + r * math.sin(math.radians(a0)))
    p1 = (cx + r * math.cos(math.radians(a1)), cy + r * math.sin(math.radians(a1)))
    sweep = 1 if a1 > a0 else 0
    large = 1 if abs(a1 - a0) > 180 else 0
    out = path(f'M{F(p0[0])} {F(p0[1])} A{F(r)} {F(r)} 0 {large} {sweep} {F(p1[0])} {F(p1[1])}', 'none', c, w)
    t = math.radians(a1)
    d = 1 if a1 > a0 else -1
    tx, ty = -math.sin(t) * d, math.cos(t) * d
    nx, ny = math.cos(t), math.sin(t)
    tip = (p1[0] + tx * head * 0.6, p1[1] + ty * head * 0.6)
    out += poly([tip, (p1[0] + nx * head * 0.55, p1[1] + ny * head * 0.55),
                 (p1[0] - nx * head * 0.55, p1[1] - ny * head * 0.55)], c, c, w * 0.5)
    return out


def tally(x, y, s=1, rot=0):
    out = ''.join(line(i * 16, 0, i * 16, 60, 7) for i in range(4))
    out += line(-8, 44, 58, 14, 7)
    return G(out, x, y, s, rot)


# ---------------------------------------------------------------- stick figure
R = 46
L_UA, L_FA, L_TH, L_SH = 70, 66, 80, 78

POSES = {
    'stand': dict(neck=(0, -135), a=(-46, 8, 1), b=(46, 8, -1), fa=(-34, 150, 1), fb=(34, 150, -1)),
    'sit': dict(neck=(0, -135), a=(-44, 18, 1), b=(44, 18, -1), ka=(-34, 24), fa=(-38, 110, 1), kb=(34, 24), fb=(38, 110, -1)),
    'walk': dict(neck=(8, -134), a=(-40, -12, 1), b=(62, -24, -1), fa=(-62, 142, 1), fb=(58, 144, -1)),
    'point_up': dict(neck=(0, -135), a=(-52, -4, 1), b=(110, -220, 1), fa=(-36, 150, 1), fb=(36, 150, -1)),
}


def ik(ax, ay, bx, by, l1, l2, bend):
    dx, dy = bx - ax, by - ay
    d = math.hypot(dx, dy) or 1e-6
    ux, uy = dx / d, dy / d
    d2 = min(max(d, abs(l1 - l2) + 0.5), l1 + l2 - 0.5)
    ex, ey = ax + ux * d2, ay + uy * d2
    ca = max(-1, min(1, (l1 * l1 + d2 * d2 - l2 * l2) / (2 * l1 * d2)))
    a = math.atan2(uy, ux) + bend * math.acos(ca)
    return (ax + l1 * math.cos(a), ay + l1 * math.sin(a)), (ex, ey)


class Fig(str):
    pass


def face(eyes='dot', brows=None, mouth=None, look=(0, 0), k=1.0, r=R, mouth_y=0.42):
    lx, ly = look
    ex, ey = 0.34 * r, -0.03 * r
    ox, oy = lx * 0.2 * r, ly * 0.14 * r
    w = 6 * k
    out = ''
    for sg in (-1, 1):
        cx, cy = sg * ex + ox, ey + oy
        if eyes == 'dot':
            out += circ(cx, cy, 0.11 * r, INK, None, 0)
        elif eyes in ('wide', 'huge'):
            rr = 0.21 * r if eyes == 'wide' else 0.28 * r
            out += circ(cx, cy, rr, '#fff', INK, w * 0.9)
            out += circ(cx + lx * rr * 0.4, cy + ly * rr * 0.4, rr * 0.42, INK, None, 0)
        elif eyes == 'crazy':
            rr = 0.26 * r
            out += circ(cx, cy, rr, '#fff', INK, w * 0.9)
            out += circ(cx + sg * rr * 0.35, cy - sg * rr * 0.3, rr * 0.25, INK, None, 0)
        elif eyes == 'closed':
            out += path(f'M{F(cx - .14 * r)} {F(cy)} Q{F(cx)} {F(cy + .13 * r)} {F(cx + .14 * r)} {F(cy)}', 'none', INK, w)
        elif eyes == 'happy':
            out += path(f'M{F(cx - .14 * r)} {F(cy + .05 * r)} Q{F(cx)} {F(cy - .13 * r)} {F(cx + .14 * r)} {F(cy + .05 * r)}', 'none', INK, w)
        elif eyes == 'half':
            out += path(f'M{F(cx - .13 * r)} {F(cy)} A{F(.13 * r)} {F(.13 * r)} 0 0 0 {F(cx + .13 * r)} {F(cy)}Z', INK, INK, w * 0.5)
            out += line(cx - .17 * r, cy, cx + .17 * r, cy, w)
        elif eyes == 'narrow':
            out += line(cx - .14 * r, cy, cx + .14 * r, cy + 0.0, w * 1.2)
        elif eyes == 'squeeze':
            out += pline([(cx - sg * .13 * r, cy - .11 * r), (cx + sg * .1 * r, cy), (cx - sg * .13 * r, cy + .11 * r)], INK, w)
        elif eyes == 'tired':
            out += circ(cx, cy + .03 * r, 0.1 * r, INK, None, 0)
            out += line(cx - .16 * r, cy - .06 * r, cx + .16 * r, cy - .06 * r, w * 0.8)
        elif eyes == 'bright':
            out += circ(cx, cy, 0.14 * r, INK, None, 0)
            out += circ(cx + .05 * r, cy - .05 * r, 0.045 * r, '#fff', None, 0)
        elif eyes == 'sad':
            out += circ(cx, cy + .03 * r, 0.1 * r, INK, None, 0)
    if brows:
        for sg in (-1, 1):
            bx, by = sg * ex + ox * 0.6, -0.36 * r + oy
            ox_, ix_ = bx + sg * 0.17 * r, bx - sg * 0.13 * r
            b = brows
            if b == 'one':
                b = 'raised' if sg < 0 else 'flat'
            if b in ('worried', 'sad'):
                out += line(ox_, by + .06 * r, ix_, by - .08 * r, w)
            elif b == 'tired':
                out += line(ox_, by + .1 * r, ix_, by - .02 * r, w)
            elif b == 'tense':
                out += line(ox_, by - .07 * r, ix_, by + .07 * r, w)
            elif b == 'flat':
                out += line(ox_, by + .12 * r, ix_, by + .12 * r, w)
            elif b == 'raised':
                out += path(f'M{F(ox_)} {F(by - .08 * r)} Q{F(bx)} {F(by - .28 * r)} {F(ix_)} {F(by - .1 * r)}', 'none', INK, w)
    if mouth:
        mx, my = ox * 0.7, mouth_y * r + oy
        R_ = r
        if mouth == 'smile':
            out += path(f'M{F(mx - .22 * R_)} {F(my - .03 * R_)} Q{F(mx)} {F(my + .2 * R_)} {F(mx + .22 * R_)} {F(my - .03 * R_)}', 'none', INK, w)
        elif mouth == 'small':
            out += path(f'M{F(mx - .13 * R_)} {F(my)} Q{F(mx)} {F(my + .1 * R_)} {F(mx + .13 * R_)} {F(my)}', 'none', INK, w)
        elif mouth in ('big', 'eager'):
            s = 1 if mouth == 'big' else 0.8
            out += path(f'M{F(mx - .25 * R_ * s)} {F(my - .04 * R_)} Q{F(mx)} {F(my + .4 * R_ * s)} {F(mx + .25 * R_ * s)} {F(my - .04 * R_)}Z', INK, INK, w * 0.6)
        elif mouth == 'frown':
            out += path(f'M{F(mx - .2 * R_)} {F(my + .08 * R_)} Q{F(mx)} {F(my - .1 * R_)} {F(mx + .2 * R_)} {F(my + .08 * R_)}', 'none', INK, w)
        elif mouth == 'o':
            out += circ(mx, my + .03 * R_, .08 * R_, '#fff', INK, w * 0.8)
        elif mouth == 'O':
            out += ell(mx, my + .05 * R_, .11 * R_, .15 * R_, INK, None, 0)
        elif mouth == 'flat':
            out += line(mx - .16 * R_, my + .02 * R_, mx + .16 * R_, my + .02 * R_, w)
        elif mouth == 'grimace':
            out += rect(mx - .23 * R_, my - .07 * R_, .46 * R_, .16 * R_, '#fff', INK, w * 0.7, .05 * R_)
            out += line(mx - .21 * R_, my + .01 * R_, mx + .21 * R_, my + .01 * R_, w * 0.5)
            for t in (-.08, .08):
                out += line(mx + t * R_, my - .06 * R_, mx + t * R_, my + .08 * R_, w * 0.5)
        elif mouth == 'yawn':
            out += ell(mx, my + .06 * R_, .15 * R_, .24 * R_, INK, None, 0)
        elif mouth == 'wavy':
            out += path(f'M{F(mx - .22 * R_)} {F(my)} q{F(.055 * R_)} {F(-.07 * R_)} {F(.11 * R_)} 0 t{F(.11 * R_)} 0 t{F(.11 * R_)} 0 t{F(.11 * R_)} 0', 'none', INK, w * 0.8)
    return out


def hair_parts(style, col, k):
    """Returns (back, front) svg in head-local units."""
    w = 7 * k
    r = R
    back = front = ''
    if not style:
        return back, front
    if style == 'messy':
        p = []
        n = 9
        for i in range(n + 1):
            a = math.radians(192 + (348 - 192) * i / n)
            rr = r * (1.0 if i in (0, n) else (1.3 if i % 2 else 1.08))
            p.append((rr * math.cos(a), rr * math.sin(a)))
        p += [(0.62 * r, -0.62 * r), (0.2 * r, -0.74 * r), (-0.3 * r, -0.72 * r), (-0.7 * r, -0.55 * r)]
        front = poly(p, col, INK, w)
    elif style == 'side':
        front = path(f'M{-1.03 * r} {-0.12 * r} A{1.05 * r} {1.05 * r} 0 0 1 {1.03 * r} {-0.16 * r} '
                     f'Q{0.62 * r} {-0.74 * r} {-0.18 * r} {-0.74 * r} Q{-0.62 * r} {-0.62 * r} {-1.03 * r} {-0.12 * r}Z', col, INK, w)
        front += path(f'M{-0.18 * r} {-0.74 * r} Q{-0.22 * r} {-0.9 * r} {-0.3 * r} {-1.02 * r}', 'none', INK, w * 0.7)
    elif style in ('cap', 'short'):
        front = path(f'M{-1.02 * r} {-0.18 * r} A{1.05 * r} {1.05 * r} 0 0 1 {1.02 * r} {-0.18 * r} '
                     f'Q{0.55 * r} {-0.66 * r} 0 {-0.68 * r} Q{-0.55 * r} {-0.66 * r} {-1.02 * r} {-0.18 * r}Z', col, INK, w)
    elif style in ('shoulder', 'long'):
        L = 1.35 if style == 'shoulder' else 2.1
        back = path(f'M{-1.12 * r} {-0.2 * r} Q{-1.3 * r} {L * 0.7 * r} {-1.15 * r} {L * r} L{1.15 * r} {L * r} '
                    f'Q{1.3 * r} {L * 0.7 * r} {1.12 * r} {-0.2 * r}Z', col, INK, w)
        front = path(f'M{-1.04 * r} {-0.05 * r} A{1.06 * r} {1.06 * r} 0 0 1 {1.04 * r} {-0.05 * r} '
                     f'Q{0.7 * r} {-0.55 * r} {0.05 * r} {-0.68 * r} Q{-0.45 * r} {-0.45 * r} {-1.04 * r} {-0.05 * r}Z', col, INK, w)
    elif style == 'curly':
        front = path(f'M{-1.0 * r} {-0.2 * r} A{1.02 * r} {1.02 * r} 0 0 1 {1.0 * r} {-0.2 * r} Q0 {-0.75 * r} {-1.0 * r} {-0.2 * r}Z', col, 'none', 0)
        for i in range(8):
            a = math.radians(196 + 148 * i / 7)
            front += circ(1.0 * r * math.cos(a), 1.0 * r * math.sin(a), 0.3 * r, col, INK, w * 0.8)
        front += circ(0, -0.85 * r, 0.3 * r, col, INK, w * 0.8)
    return back, front


def fig(x, y, s=1.0, pose='stand', eyes='dot', brows=None, mouth=None, look=(0, 0), hair=None, hair_c=INK,
        glasses=False, coat=False, jeans=False, hat=None, necklace=False, flip=False, tilt=0, lw=12,
        rot=0, op=None, sleeves=None, head_fill='#fff', mouth_y=0.42):
    """Stick figure; (x, y) is the hip. Returns Fig (a str) with .J joint dict (world coords)."""
    if isinstance(pose, str):
        P = dict(POSES[pose])
    else:
        P = dict(POSES[pose.get('base', 'stand')])
        P.update({k: v for k, v in pose.items() if k != 'base'})
        P = {k: v for k, v in P.items() if v is not None}
    nx, ny = P['neck']
    sh = (nx * 0.88, ny * 0.88)
    J = {'hip': (0, 0), 'neck': (nx, ny), 'sh': sh}
    for key, root, l1, l2 in (('a', sh, L_UA, L_FA), ('b', sh, L_UA, L_FA), ('fa', (0, 0), L_TH, L_SH), ('fb', (0, 0), L_TH, L_SH)):
        tx, ty, bend = P[key]
        mid_key = {'a': 'ea', 'b': 'eb', 'fa': 'ka', 'fb': 'kb'}[key]
        if mid_key in P:
            mid, end = P[mid_key], (tx, ty)
        else:
            mid, end = ik(root[0], root[1], tx, ty, l1, l2, bend)
        J[mid_key] = mid
        J[key] = end
    L = math.hypot(nx, ny) or 1
    hc = (nx + nx / L * (R + 3), ny + ny / L * (R + 3))
    J['head'] = hc
    mx = -1 if flip else 1
    ca, sa = math.cos(math.radians(rot)), math.sin(math.radians(rot))

    def T(p):
        px, py = p[0] * mx * s, p[1] * s
        return (x + px * ca - py * sa, y + px * sa + py * ca)

    W_ = J_world = {k: T(v) for k, v in J.items()}
    lwW = lw * s ** 0.75
    k = s ** -0.25
    out = []
    hb, hf = hair_parts(hair, hair_c, k)
    head_rot = rot + tilt * mx + math.degrees(math.atan2(nx, -ny)) * mx

    def head_group(inner):
        hx, hy = W_['head']
        return G(inner, hx, hy, 1, head_rot) if False else (
            f'<g transform="translate({F(hx)} {F(hy)}) rotate({F(head_rot)}) scale({mx * s:.4f} {s:.4f})">{inner}</g>')

    if hb:
        out.append(head_group(hb))
    # legs
    legs = [(W_['hip'], W_['ka'], W_['fa']), (W_['hip'], W_['kb'], W_['fb'])]
    if jeans:
        hl = (T((-16, 0)), T((16, 0)))
        for a, b, c in legs:
            out.append(pline([a, b, c], INK, lwW + 14 * s ** 0.75))
        out.append(line(*hl[0], *hl[1], lwW + 14 * s ** 0.75))
        for a, b, c in legs:
            out.append(pline([a, b, c], JEANS, lwW + 1))
        out.append(line(*hl[0], *hl[1], lwW + 1, JEANS))
    else:
        for a, b, c in legs:
            out.append(pline([a, b, c], INK, lwW))
    # torso
    if coat:
        cp = [T((nx - 30, ny + 10)), T((nx + 30, ny + 10)), T((56, 48)), T((-56, 48))]
        out.append(poly(cp, coat if isinstance(coat, str) else '#fff', INK, 7 * s ** 0.75))
        out.append(pline([T((nx - 15, ny + 10)), T((nx, ny + 52)), T((nx + 15, ny + 10))], INK, 6 * s ** 0.75))
        out.append(line(*T((nx * 0.6, ny * 0.6 + 20)), *T((0, 40)), 4 * s ** 0.75, INK))
    else:
        out.append(line(*W_['hip'], *W_['neck'], lwW))
    # arms
    sleeve = sleeves or ('#fff' if coat else None)
    for e, h in (('ea', 'a'), ('eb', 'b')):
        p = [W_['sh'], W_[e], W_[h]]
        if sleeve:
            out.append(pline(p, INK, lwW + 12 * s ** 0.75))
            out.append(pline(p, sleeve, lwW))
            out.append(circ(*W_[h], lwW * 0.7, INK, None, 0))
        else:
            out.append(pline(p, INK, lwW))
    # head
    inner = circ(0, 0, R, head_fill, INK, 8 * k)
    inner += hf
    inner += face(eyes, brows, mouth, look, k, R, mouth_y)
    if glasses:
        ex = 0.34 * R + look[0] * 0.2 * R
        for sg in (-1, 1):
            inner += circ(sg * 0.34 * R + look[0] * 0.2 * R, -0.03 * R + look[1] * 0.14 * R, 0.25 * R, 'none', INK, 5.5 * k)
        inner += line(-0.09 * R + look[0] * 0.2 * R, -0.03 * R, 0.09 * R + look[0] * 0.2 * R, -0.03 * R, 5 * k)
    if hat:
        inner += ell(0, -0.55 * R, 1.3 * R, 0.22 * R, hat, INK, 6 * k)
        inner += path(f'M{-0.78 * R} {-0.58 * R} L{-0.62 * R} {-1.28 * R} Q0 {-1.45 * R} {0.62 * R} {-1.28 * R} L{0.78 * R} {-0.58 * R}Z', hat, INK, 6 * k)
        inner += line(-0.74 * R, -0.75 * R, 0.74 * R, -0.75 * R, 5 * k, INK, op=0.5)
    if necklace:
        cols = [RED, YELLOW, BLUE, GREEN, ORANGE, PURPLE]
        for i, a in enumerate(range(30, 151, 20)):
            t = math.radians(a)
            inner += circ(0.55 * R * math.cos(t), R * 1.05 + 0.32 * R * math.sin(t), 0.11 * R, cols[i % 6], INK, 3 * k)
    out.append(head_group(inner))
    svg = ''.join(out)
    if op is not None:
        svg = f'<g opacity="{op}">{svg}</g>'
    f = Fig(svg)
    f.J = W_
    f.s = s
    f.R = R * s
    return f


# ---------------------------------------------------------------- characters
def brain(cx, cy, s=1.0, eyes='dot', mouth='smile', brows=None, look=(0, 0), fill=PINK, inner=''):
    out = path(blob_d(0, 0, 150, 112, 12, 1.12, 0.1), fill, INK, 9)
    for d in ('M0 -118 Q-14 -80 4 -48 Q16 -20 -4 0', 'M-118 -28 Q-90 -62 -58 -38', 'M-102 42 Q-72 60 -48 32',
              'M44 -82 Q80 -92 100 -58', 'M70 20 Q96 46 128 18', 'M-64 -92 Q-48 -70 -72 -52', 'M38 64 Q60 84 88 70'):
        out += path(d, 'none', PINK_D, 7)
    out += inner
    out += G(face(eyes, brows, mouth, look, 1.15, 92, 0.42), 0, 22)
    return G(out, cx, cy, s)


def pigeon(x, y, s=1.0, facing=1, eyes='dot', peck=False, brows=None, head=None, hrot=None):
    out = ''
    out += poly([(-55, -58), (-128, -44), (-124, -18), (-50, -30)], PIG_D, INK, 7)
    for fx in (-14, 16):
        out += line(fx, -20, fx - 4, -2, 7, ORANGE)
        out += line(fx - 4, -2, fx + 14, -2, 6, ORANGE) + line(fx - 4, -2, fx - 16, 0, 6, ORANGE)
    hx, hy = (88, -52) if peck else (head or (46, -128))
    out += line(18, -86, hx, hy, 66, INK)
    out += ell(0, -62, 74, 52, PIG, INK, 8)
    out += line(18, -86, hx, hy, 50, PIG)
    out += line(18 + (hx - 18) * 0.35, -86 + (hy + 86) * 0.35, 18 + (hx - 18) * 0.6, -86 + (hy + 86) * 0.6, 40, '#86BBA6', op=0.85)
    out += path('M-46 -72 Q0 -98 42 -62 Q4 -44 -46 -72Z', PIG_D, INK, 6)
    if hrot is None:
        hrot = 50 if peck else 0
    h = circ(0, 0, 33, PIG, INK, 8)
    h += poly([(27, -8), (54, 4), (27, 12)], ORANGE, INK, 5)
    h += circ(24, -10, 5, '#fff', INK, 3)
    ex, ey = 8, -8
    if eyes == 'dot':
        h += circ(ex, ey, 5.5, INK, None, 0)
    elif eyes in ('wide', 'eager'):
        h += circ(ex, ey, 12, '#fff', INK, 4) + circ(ex + 3, ey, 6, INK, None, 0)
        if eyes == 'eager':
            h += circ(ex + 5, ey - 3, 2, '#fff', None, 0)
    elif eyes == 'crazy':
        h += circ(ex, ey, 14, '#fff', INK, 4) + circ(ex + 6, ey - 5, 3.5, INK, None, 0)
    elif eyes == 'sad':
        h += circ(ex, ey + 2, 5, INK, None, 0) + line(ex - 9, ey - 8, ex + 8, ey - 3, 4)
    if brows == 'up':
        h += path(f'M{ex - 10} {ey - 18} Q{ex} {ey - 26} {ex + 10} {ey - 18}', 'none', INK, 4)
    out += G(h, hx, hy, 1, hrot)
    return G(out, x, y, s, sx=s * facing, sy=s)


# ---------------------------------------------------------------- phone & hands
def phone(cx, cy, w=120, rot=0, screen=SCREEN, down=False, content='', h=None, dashed=False, op=None, lw=None, fill='none'):
    h = h or w * 1.9
    lw = lw or max(4, w * 0.045)
    if dashed:
        g = rect(-w / 2, -h / 2, w, h, fill, INK, lw, w * 0.15, dash=f'{F(w * 0.12)} {F(w * 0.1)}')
        return G(g, cx, cy, 1, rot, op)
    if down:
        g = rect(-w / 2, -h / 2, w, h, '#2A2A2A', INK, lw, w * 0.15)
        g += rect(-w * 0.36, -h * 0.44, w * 0.3, w * 0.42, '#3a3a3a', '#111', lw * 0.6, w * 0.08)
        g += circ(-w * 0.21, -h * 0.44 + w * 0.12, w * 0.07, '#555', '#111', lw * 0.4)
        g += circ(-w * 0.21, -h * 0.44 + w * 0.3, w * 0.07, '#555', '#111', lw * 0.4)
        g += line(-w * 0.32, h * 0.38, w * 0.32, h * 0.38, lw * 0.4, '#444')
    else:
        g = rect(-w / 2, -h / 2, w, h, INK, INK, lw, w * 0.15)
        g += rect(-w * 0.42, -h / 2 + w * 0.13, w * 0.84, h - w * 0.26, screen, None, 0, w * 0.05)
        g += line(-w * 0.1, -h / 2 + w * 0.065, w * 0.1, -h / 2 + w * 0.065, w * 0.035, '#444')
        g += content
    return G(g, cx, cy, 1, rot, op)


def screen_size(w=120, h=None):
    h = h or w * 1.9
    return w * 0.84, h - w * 0.26


def glow(cx, cy, rx, ry, col=SCREEN, op=0.45):
    return ell(cx, cy, rx, ry, col, None, 0, op)


def phone_in_hand(cx, cy, w=260, rot=0, thumb='rest', content='', screen=SCREEN, down=False, arm=True):
    """Close-up cartoon hand holding a phone. (cx,cy) = phone centre."""
    h = w * 1.9
    o = []
    if arm:
        o.append(tube(w * 0.3, h * 1.3, w * 0.1, h * 0.42, w * 0.58))
    o.append(ell(w * 0.04, h * 0.3, w * 0.58, w * 0.5, '#fff', INK, SW))
    o.append(phone(0, 0, w, 0, screen, down, content))
    for i, yy in enumerate((0.02, 0.14, 0.26)):
        o.append(tube(-w * 0.64, h * yy, -w * 0.44, h * yy + 6, w * 0.13, '#fff', INK, SW * 0.9))
    if thumb == 'rest':
        tip = (w * 0.36, h * 0.06)
    elif thumb == 'press':
        tip = (w * 0.06, -h * 0.02)
    elif thumb == 'drag':
        tip = (w * 0.0, -h * 0.18)
    elif thumb == 'hover':
        tip = (w * 0.04, -h * 0.03)
    else:
        tip = None
    if tip:
        base = (w * 0.6, h * 0.34)
        if thumb == 'hover':
            o.append(ell(tip[0] - 4, tip[1] + 30, w * 0.08, w * 0.04, INK, None, 0, 0.15))
            o.append(tube(base[0], base[1], tip[0], tip[1] - 18, w * 0.16, '#fff', INK, SW))
        else:
            o.append(tube(base[0], base[1], tip[0], tip[1], w * 0.16, '#fff', INK, SW))
            o.append(path(f'M{F(tip[0] - w * 0.04)} {F(tip[1] - w * 0.05)} q{F(w * 0.04)} {F(-w * 0.03)} {F(w * 0.08)} 0', 'none', INK, 4))
    return G(o, cx, cy, 1, rot)


def mitt(x, y, s=1.0, ang=0, arm=360, flipy=False, point=False, open_=False, sleeve='#fff'):
    """Cartoon hand; wrist at (x,y), fingers pointing along ang (deg)."""
    fy = -1 if flipy else 1
    o = []
    if arm:
        o.append(tube(-arm, 0, -10, 0, 54, sleeve, INK, SW))
    if open_:
        for i, yy in enumerate((-30, -10, 10, 30)):
            o.append(tube(60, yy * 1.0, 118 - abs(yy) * 0.6, yy * 1.25, 22, '#fff', INK, 7))
        o.append(rect(-6, -42, 92, 84, '#fff', INK, SW, 38))
    else:
        o.append(rect(-6, -42, 100, 84, '#fff', INK, SW, 38))
        for yy in (-14, 12):
            o.append(line(62, yy, 92, yy, 5))
    if point:
        o.append(tube(70, -26, 150, -26, 22, '#fff', INK, 7))
    o.append(tube(24, -34 * fy, 58, -64 * fy, 24, '#fff', INK, 7))
    return G(o, x, y, s, ang, sx=s, sy=s * fy) if flipy else G(o, x, y, s, ang)


# ---------------------------------------------------------------- furniture & places
def couch(x, y, w=560, col=COUCH, col_d=COUCH_D):
    """(x, y) = floor centre. Seat top at y-100."""
    h = w / 2
    o = ''
    o += rect(x - h + 30, y - 270, w - 60, 190, col_d, INK, SW, 26)
    o += rect(x - h + 40, y - 112, w - 80, 92, col, INK, SW, 18)
    o += line(x, y - 108, x, y - 26, 6, INK, op=0.5)
    for sx in (-1, 1):
        o += rect(x + sx * (h - 35) - 38, y - 175, 76, 160, col, INK, SW, 30)
        o += rect(x + sx * (h - 70) - 9, y - 18, 18, 18, INK, INK, 3)
    return o


def table(x, y, w=520, col=WOOD, legs=180, depth=70):
    """Table seen slightly from above; (x, y) = top surface back edge centre."""
    h = w / 2
    o = rect(x - h, y, w, depth, col, INK, SW, 8)
    o += rect(x - h, y + depth, w, 26, WOOD_D, INK, SW, 6)
    for sx in (-1, 1):
        o += rect(x + sx * (h - 40) - 12, y + depth + 26, 24, legs, WOOD_D, INK, SW, 4)
    return o


def desk(x, y, w=620, depth=110, legs=200, col=WOOD):
    return table(x, y, w, col, legs, depth)


def chair(x, y, s=1, facing=1):
    o = rect(-70, -100, 140, 22, WOOD, INK, SW, 6)
    o += rect(facing * -70 - 11, -280, 22, 190, WOOD, INK, SW, 6)
    o += rect(-62, -80, 18, 80, WOOD_D, INK, 7) + rect(44, -80, 18, 80, WOOD_D, INK, 7)
    return G(o, x, y, s)


def calendar(x, y, w=420, h=440, crossed=0, circled=None, cols=7, rows=5, title=None, xcol=RED):
    o = rect(x, y, w, h, '#fff', INK, SW, 14)
    o += rect(x, y, w, h * 0.17, RED, INK, SW, 14)
    o += rect(x + 3, y + h * 0.1, w - 6, h * 0.07 + 2, RED, None, 0)
    for rx_ in (0.25, 0.75):
        o += rect(x + w * rx_ - 8, y - 24, 16, 48, LGRAY, INK, 6, 8)
    if title:
        o += txt(x + w / 2, y + h * 0.135, title, h * 0.09, '#fff')
    gx, gy = x + w * 0.06, y + h * 0.23
    cw, ch = w * 0.88 / cols, h * 0.72 / rows
    n = 0
    marks = ''
    for r_ in range(rows):
        for c_ in range(cols):
            cx, cy = gx + c_ * cw + cw / 2, gy + r_ * ch + ch / 2
            o += rect(gx + c_ * cw + 3, gy + r_ * ch + 3, cw - 6, ch - 6, '#fff', LGRAY, 3, 4)
            if n < crossed:
                marks += redx(cx, cy, min(cw, ch) * 0.6, max(5, w * 0.012), xcol)
            if circled is not None and n == circled:
                marks += ell(cx, cy, cw * 0.7, ch * 0.66, 'none', RED, max(9, w * 0.022))
            n += 1
    return o + marks


def clipboard(x, y, s=1, rot=0, content='check'):
    o = rect(-75, -100, 150, 200, WOOD, INK, SW, 12)
    o += rect(-60, -78, 120, 166, '#fff', INK, 5, 4)
    o += rect(-32, -112, 64, 30, LGRAY, INK, 6, 8)
    if content == 'check':
        o += ''.join(line(-42, yy, 42, yy, 5, LGRAY) for yy in (-50, -30, -10))
        o += check(4, 40, 60, GREEN)
    elif content == 'graph':
        o += line(-45, 70, -45, -55, 5) + line(-45, 70, 48, 70, 5)
        o += pline([(-40, 50), (-18, 28), (2, 36), (20, -4), (44, -40)], RED, 6)
    elif content == 'lines':
        o += ''.join(line(-42, yy, 42, yy, 5, LGRAY) for yy in (-50, -25, 0, 25, 50))
    elif content == 'paper':
        o += ''.join(line(-42, yy, 30, yy, 5, LGRAY) for yy in (-50, -25, 0))
        o += pline([(-40, 60), (-15, 30), (5, 45), (40, 0)], GREEN, 6)
    return G(o, x, y, s, rot)


def paper(x, y, w=170, h=120, rot=0, lines=4, star_=False, fill='#fff'):
    o = rect(-w / 2, -h / 2, w, h, fill, INK, 6, 4)
    for i in range(lines):
        yy = -h / 2 + h * (i + 1) / (lines + 1)
        o += line(-w * 0.38, yy, w * 0.3, yy, 4, LGRAY)
    if star_:
        o += star(w * 0.25, -h * 0.15, h * 0.32)
    return G(o, x, y, 1, rot)


def bulb(x, y, s=1, on=True, col=YELLOW, rays=True, op=None, dim=False):
    o = ''
    if on and rays:
        o += circ(0, -10, 78, col, None, 0, 0.25)
        for i in range(8):
            a = math.radians(-90 + i * 45)
            if i in (3, 4, 5):
                continue
            o += line(66 * math.cos(a), -10 + 66 * math.sin(a), 92 * math.cos(a), -10 + 92 * math.sin(a), 7)
    fill = col if on else (LGRAY if dim else '#fff')
    o += path('M-26 30 Q-28 14 -38 2 A50 50 0 1 1 38 2 Q28 14 26 30Z', fill, INK, 7)
    o += rect(-24, 30, 48, 30, LGRAY, INK, 6, 6)
    o += line(-22, 42, 22, 42, 4) + line(-14, 66, 14, 66, 8)
    if on:
        o += path('M-14 6 Q0 -16 14 6', 'none', INK, 4, 0.5)
    return G(o, x, y, s, op=op)


def box3d(x, y, w, h, d=60, front=WOOD, top=None, side=None, sw=SW):
    """Box: (x,y) top-left of front face; depth offset up-right."""
    top = top or front
    side = side or front
    o = poly([(x, y), (x + d, y - d * 0.7), (x + w + d, y - d * 0.7), (x + w, y)], top, INK, sw)
    o += poly([(x + w, y), (x + w + d, y - d * 0.7), (x + w + d, y + h - d * 0.7), (x + w, y + h)], side, INK, sw)
    o += rect(x, y, w, h, front, INK, sw)
    return o


def skinner_box(x, y, w=460, h=340, inner='', lid=True, glass=True, d=70):
    """Wooden box with a front window; inner drawn inside the window (behind glass)."""
    o = ''
    if lid:
        o += poly([(x, y), (x + d, y - d * 0.7), (x + w + d, y - d * 0.7), (x + w, y)], WOOD, INK, SW)
    o += poly([(x + w, y), (x + w + d, y - d * 0.7), (x + w + d, y + h - d * 0.7), (x + w, y + h)], WOOD_D, INK, SW)
    wx, wy, ww, wh = x + w * 0.12, y + h * 0.14, w * 0.76, h * 0.7
    o += rect(x, y, w, h, WOOD, INK, SW)
    o += rect(wx, wy, ww, wh, CREAM, INK, SW)
    o += f'<svg x="{F(wx)}" y="{F(wy)}" width="{F(ww)}" height="{F(wh)}" viewBox="{F(wx)} {F(wy)} {F(ww)} {F(wh)}" overflow="hidden">{inner}</svg>'
    if glass:
        o += rect(wx, wy, ww, wh, '#DDF1FA', None, 0, 0, 0.25)
        o += line(wx + ww * 0.72, wy + 18, wx + ww * 0.55, wy + wh * 0.4, 7, '#fff', op=0.9)
        o += line(wx + ww * 0.86, wy + 22, wx + ww * 0.68, wy + wh * 0.55, 7, '#fff', op=0.9)
    o += rect(wx, wy, ww, wh, 'none', INK, SW)
    for t in (0.06, 0.94):
        o += line(x + w * t, y + h * 0.05, x + w * t, y + h * 0.95, 4, WOOD_D)
    return o


def box_interior(fill_back=CREAM, wall=CREAM_D, floor='#E0C79A'):
    """Full-frame view inside a box."""
    bx0, by0, bx1, by1 = 460, 200, 1460, 760
    o = poly([(0, 0), (W, 0), (bx1, by0), (bx0, by0)], '#EBD9B6', INK, SW)
    o += poly([(0, 0), (bx0, by0), (bx0, by1), (0, H)], wall, INK, SW)
    o += poly([(W, 0), (bx1, by0), (bx1, by1), (W, H)], wall, INK, SW)
    o += poly([(0, H), (bx0, by1), (bx1, by1), (W, H)], floor, INK, SW)
    o += rect(bx0, by0, bx1 - bx0, by1 - by0, fill_back, INK, SW)
    return o


def red_key(x, y, r=60):
    return circ(x, y, r + 16, LGRAY, INK, SW) + circ(x, y, r, RED, INK, SW) + circ(x - r * 0.3, y - r * 0.3, r * 0.18, '#fff', None, 0, 0.6)


def tray(x, y, w=200, grain=False, empty=False):
    o = ''
    if grain:
        for i in range(14):
            o += ell(x - w * 0.32 + (i * 37) % (w * 0.64), y - 14 - (i % 3) * 8, 9, 6, YELLOW, INK, 3, rot=(i * 40) % 180)
    o += path(f'M{F(x - w / 2)} {F(y - 30)} L{F(x - w * 0.42)} {F(y + 10)} L{F(x + w * 0.42)} {F(y + 10)} L{F(x + w / 2)} {F(y - 30)}Z', LGRAY, INK, SW)
    o += line(x - w / 2 - 6, y - 30, x + w / 2 + 6, y - 30, 12, DGRAY)
    return o


def dice(x, y, s=1, rot=0, n=5):
    o = rect(-50, -50, 100, 100, '#fff', INK, SW, 20)
    P = {1: [(0, 0)], 2: [(-22, -22), (22, 22)], 3: [(-24, -24), (0, 0), (24, 24)], 4: [(-22, -22), (22, -22), (-22, 22), (22, 22)],
         5: [(-24, -24), (24, -24), (0, 0), (-24, 24), (24, 24)], 6: [(-22, -26), (22, -26), (-22, 0), (22, 0), (-22, 26), (22, 26)]}
    for px, py in P[n]:
        o += circ(px, py, 9, INK, None, 0)
    return G(o, x, y, s, rot)


def bell(x, y, s=1, fill=RED, dot=True):
    o = path('M-60 40 Q-50 30 -48 -10 Q-46 -60 0 -64 Q46 -60 48 -10 Q50 30 60 40Z', fill, INK, 9)
    o += line(-70, 42, 70, 42, 14) + circ(0, 56, 16, fill, INK, 8) + circ(0, -70, 10, fill, INK, 7)
    if dot:
        o += circ(52, -50, 24, RED, INK, 7)
    return G(o, x, y, s)


def msg_icon(x, y, s=1, fill=GREEN, empty=False):
    o = path('M-80 -55 Q-80 -70 -65 -70 L65 -70 Q80 -70 80 -55 L80 30 Q80 45 65 45 L-20 45 L-55 80 L-50 45 L-65 45 Q-80 45 -80 30Z', fill, INK, 9)
    if not empty:
        for yy in (-35, -10, 15):
            o += line(-50, yy, 50 if yy < 15 else 10, yy, 9, '#fff')
    return G(o, x, y, s)


def app_grid(x, y, s=1):
    cols = [[RED, YELLOW], [BLUE, GREEN]]
    o = ''
    for i in range(2):
        for j in range(2):
            o += rect(-80 + j * 85, -80 + i * 85, 75, 75, cols[i][j], INK, 8, 18)
    return G(o, x, y, s)


def wifi(x, y, s=1, c=INK, w=14):
    o = circ(0, 0, 12, c, None, 0)
    for r in (40, 75, 110):
        o += path(f'M{F(-r * 0.75)} {F(-r * 0.66)} A{r} {r} 0 0 1 {F(r * 0.75)} {F(-r * 0.66)}', 'none', c, w)
    return G(o, x, y, s)


def tv(x, y, s=1, screen=SCREEN):
    o = line(-30, -150, 0, -105, 7) + line(30, -150, 0, -105, 7)
    o += rect(-130, -105, 260, 180, '#555', INK, SW, 18) + rect(-108, -86, 190, 142, screen, INK, 6, 10)
    o += circ(106, -60, 8, LGRAY, INK, 4) + circ(106, -30, 8, LGRAY, INK, 4)
    o += line(-80, 75, -100, 105, 9) + line(80, 75, 100, 105, 9)
    return G(o, x, y, s)


def battery(x, y, w=240, h=120, level=0.0, col=RED, s=1):
    o = rect(-w / 2, -h / 2, w, h, '#fff', INK, 12, 18)
    o += rect(w / 2, -h * 0.2, 24, h * 0.4, INK, INK, 6, 6)
    if level > 0:
        o += rect(-w / 2 + 14, -h / 2 + 14, (w - 28) * level, h - 28, col, None, 0, 8)
    return G(o, x, y, s)


def signal_bars(x, y, s=1, col=INK):
    o = ''
    for i in range(4):
        hh = 40 + i * 35
        o += rect(-90 + i * 50, 60 - hh, 34, hh, col, INK, 6, 6)
    return G(o, x, y, s)


def mute_icon(x, y, s=1, c=INK):
    o = poly([(-40, -14), (-20, -14), (4, -36), (4, 36), (-20, 14), (-40, 14)], c, c, 5)
    o += line(18, -18, 46, 18, 7, RED) + line(46, -18, 18, 18, 7, RED)
    return G(o, x, y, s)


def gift(x, y, s=1, fill=RED, q=True):
    o = rect(-110, -80, 220, 170, fill, INK, SW, 8)
    o += rect(-125, -125, 250, 55, fill, INK, SW, 8)
    o += rect(-18, -125, 36, 215, YELLOW, INK, 7)
    o += path('M0 -125 Q-70 -200 -60 -135 Q-50 -120 0 -125Z', YELLOW, INK, 7)
    o += path('M0 -125 Q70 -200 60 -135 Q50 -120 0 -125Z', YELLOW, INK, 7)
    if q:
        o += txt(-62, 50, '?', 110, INK) + txt(62, 50, '?', 110, INK)
    return G(o, x, y, s)


def coin(x, y, s=1, rot=0):
    return G(ell(0, 0, 30, 30, YELLOW, INK, 6) + ell(0, 0, 16, 16, 'none', '#D9A21B', 5), x, y, s, rot, sx=s * 0.75, sy=s)


def sun(x, y, r=60):
    o = ''
    for i in range(10):
        a = math.radians(i * 36)
        o += line(x + (r + 16) * math.cos(a), y + (r + 16) * math.sin(a), x + (r + 40) * math.cos(a), y + (r + 40) * math.sin(a), 8, '#E9A92A')
    return o + circ(x, y, r, YELLOW, INK, SW)


def moon(x, y, r=60, fill='#fff'):
    return path(f'M{F(x)} {F(y - r)} A{r} {r} 0 1 0 {F(x + r * 0.2)} {F(y + r * 0.98)} A{r * 0.78} {r * 0.78} 0 1 1 {F(x)} {F(y - r)}Z', fill, INK, SW)


def acacia(x, y, s=1):
    o = path('M-10 0 L-6 -150 Q-40 -200 -90 -220 M-6 -150 Q20 -200 70 -225 M-6 -150 L4 -230', 'none', BROWN, 18)
    o += line(-10, 0, -6, -150, 22, BROWN)
    o += path('M-210 -230 Q-200 -300 -60 -300 Q40 -330 140 -295 Q230 -280 215 -235 Q100 -205 0 -215 Q-110 -205 -210 -230Z', TREE, INK, SW)
    return G(o, x, y, s)


def palm(x, y, s=1, lean=1):
    o = path(f'M0 0 Q{20 * lean} -120 {50 * lean} -260', 'none', INK, 34) + path(f'M0 0 Q{20 * lean} -120 {50 * lean} -260', 'none', '#B07A44', 22)
    tx, ty = 50 * lean, -260
    for a in (-160, -120, -60, -20, -90):
        r_ = math.radians(a)
        ex, ey = tx + 120 * math.cos(r_), ty + 110 * math.sin(r_) + 40
        o += path(f'M{F(tx)} {F(ty)} Q{F((tx + ex) / 2)} {F(min(ty, ey) - 50)} {F(ex)} {F(ey)} Q{F((tx + ex) / 2)} {F(min(ty, ey) - 10)} {F(tx)} {F(ty)}Z', TREE, INK, 7)
    return G(o, x, y, s)


def round_tree(x, y, s=1):
    return G(rect(-14, -120, 28, 120, BROWN, INK, 7) + circ(0, -170, 85, TREE, INK, SW), x, y, s)


def bird(x, y, s=1):
    return G(path('M-20 0 Q-10 -12 0 0 Q10 -12 20 0', 'none', INK, 5), x, y, s)


def hills(y, col='#C9D9A0', col2='#B5CC8A'):
    o = path(f'M0 {y} Q300 {y - 120} 640 {y - 40} Q960 {y - 150} 1300 {y - 50} Q1620 {y - 130} 1920 {y - 30} L1920 {y + 40} L0 {y + 40}Z', col2, INK, 7)
    return o


def campfire(x, y, s=1):
    o = rect(-90, -16, 180, 30, BROWN, INK, 7, 14, rot=-12) + rect(-90, -16, 180, 30, WOOD_D, INK, 7, 14, rot=12)
    o += path('M-50 -10 Q-70 -80 -20 -120 Q-30 -80 0 -70 Q-5 -140 30 -180 Q40 -110 60 -90 Q75 -60 50 -10Z', ORANGE, INK, 7)
    o += path('M-20 -10 Q-30 -50 0 -80 Q5 -55 20 -50 Q35 -30 20 -10Z', YELLOW, INK, 5)
    return G(o, x, y, s)


def hammock(x1, y1, x2, y2, sag=110, col='#D9B98A'):
    mx = (x1 + x2) / 2
    my = (y1 + y2) / 2 + sag
    o = path(f'M{x1} {y1} Q{mx} {my + 40} {x2} {y2} Q{mx} {my - 10} {x1} {y1}Z', col, INK, 8)
    for t in (0.3, 0.45, 0.6, 0.75):
        pass
    return o


def university(x, y, s=1):
    o = poly([(-360, -330), (0, -470), (360, -330)], '#F4F1E8', INK, SW)
    o += rect(-380, -340, 760, 40, '#ECE7DA', INK, SW)
    for i in range(6):
        cx = -300 + i * 120
        o += rect(cx - 26, -300, 52, 250, '#fff', INK, 8)
        o += line(cx - 8, -290, cx - 8, -60, 4, LGRAY) + line(cx + 8, -290, cx + 8, -60, 4, LGRAY)
    o += rect(-400, -50, 800, 22, '#ECE7DA', INK, 8) + rect(-430, -28, 860, 28, '#E3DDCC', INK, 8)
    o += circ(0, -385, 30, '#fff', INK, 7)
    return G(o, x, y, s)


def tower(x, y, s=1):
    o = rect(-90, -560, 180, 560, '#F1E6CC', INK, SW)
    o += rect(-110, -600, 220, 60, '#E8DAB8', INK, SW)
    o += poly([(-100, -600), (0, -700), (100, -600)], '#D9A35E', INK, SW)
    o += circ(0, -480, 42, '#fff', INK, 8) + line(0, -480, 0, -505, 6) + line(0, -480, 18, -470, 6)
    for i in range(4):
        o += rect(-50, -400 + i * 90, 36, 56, SKY, INK, 6, 4) + rect(14, -400 + i * 90, 36, 56, SKY, INK, 6, 4)
    o += rect(-260, -200, 170, 200, '#F1E6CC', INK, SW) + rect(90, -200, 170, 200, '#F1E6CC', INK, SW)
    for xx in (-230, -160, 120, 190):
        o += rect(xx, -160, 40, 60, SKY, INK, 6, 4)
    o += path('M-30 0 L-30 -70 A30 30 0 0 1 30 -70 L30 0Z', WOOD_D, INK, 7)
    return G(o, x, y, s)


def dd_bus(x, y, s=1):
    o = rect(-300, -330, 600, 310, RED, INK, SW, 30)
    o += line(-300, -175, 300, -175, 7)
    for i in range(5):
        o += rect(-270 + i * 112, -305, 90, 90, SKY, INK, 7, 8)
        o += rect(-270 + i * 112, -150, 90, 80, SKY, INK, 7, 8)
    o += circ(-180, -20, 46, INK, INK, 4) + circ(-180, -20, 18, LGRAY, None, 0)
    o += circ(180, -20, 46, INK, INK, 4) + circ(180, -20, 18, LGRAY, None, 0)
    return G(o, x, y, s)


def ambulance(x, y, s=1):
    o = rect(-260, -260, 360, 220, '#fff', INK, SW, 18)
    o += path('M100 -200 L200 -200 L260 -120 L260 -40 L100 -40Z', '#fff', INK, SW)
    o += path('M120 -185 L190 -185 L232 -125 L120 -125Z', SKY, INK, 7)
    o += rect(-130, -200, 30, 100, RED, None, 0) + rect(-165, -165, 100, 30, RED, None, 0)
    o += line(-260, -70, 260, -70, 12, RED)
    o += rect(-30, -290, 60, 30, RED, INK, 7, 8)
    o += circ(-160, -30, 44, INK, INK, 4) + circ(-160, -30, 16, LGRAY, None, 0)
    o += circ(170, -30, 44, INK, INK, 4) + circ(170, -30, 16, LGRAY, None, 0)
    return G(o, x, y, s)


def pie(x, y, r, frac, col=RED, rest=LGRAY):
    a = 2 * math.pi * frac
    ex, ey = x + r * math.sin(a), y - r * math.cos(a)
    large = 1 if frac > 0.5 else 0
    o = circ(x, y, r, rest, INK, SW)
    o += path(f'M{x} {y} L{x} {y - r} A{r} {r} 0 {large} 1 {F(ex)} {F(ey)}Z', col, INK, SW)
    return o


def mirror(x, y, rx=170, ry=250, fill='#DDEFF6'):
    return ell(x, y, rx + 22, ry + 22, WOOD, INK, SW) + ell(x, y, rx, ry, fill, INK, 7)


def clock(x, y, r=220, h_ang=-60, m_ang=40):
    o = circ(x, y, r + 20, GRAY, INK, SW) + circ(x, y, r, '#fff', INK, 7)
    for i in range(12):
        a = math.radians(i * 30)
        o += line(x + r * 0.82 * math.cos(a), y + r * 0.82 * math.sin(a), x + r * 0.95 * math.cos(a), y + r * 0.95 * math.sin(a), 8 if i % 3 == 0 else 5)
    for ang, L, w in ((h_ang, 0.5, 16), (m_ang, 0.78, 11)):
        a = math.radians(ang - 90)
        o += line(x, y, x + r * L * math.cos(a), y + r * L * math.sin(a), w)
    return o + circ(x, y, 14, INK, None, 0)


def target(x, y, r=170):
    o = ''
    for i, c in enumerate((RED, '#fff', RED, '#fff', RED)):
        o += circ(x, y, r * (1 - i * 0.19), c, INK, 7)
    return o


def smiley(x, y, r=110, fill=YELLOW):
    return circ(x, y, r, fill, INK, SW) + G(face('dot', None, 'smile', (0, 0), 1.6, r / 1.05, 0.38), x, y)


def padlock(x, y, s=1, col=RED):
    o = path('M-60 -20 L-60 -80 A60 60 0 0 1 60 -80 L60 -20', 'none', INK, 34) + path('M-60 -20 L-60 -80 A60 60 0 0 1 60 -80 L60 -20', 'none', LGRAY, 20)
    o += rect(-95, -30, 190, 160, col, INK, SW, 22)
    o += circ(0, 35, 20, INK, None, 0) + rect(-8, 40, 16, 45, INK, None, 0, 6)
    return G(o, x, y, s)


def rocket(x, y, s=1, rot=0):
    o = path('M0 -110 Q50 -60 40 40 L-40 40 Q-50 -60 0 -110Z', RED, INK, 8)
    o += circ(0, -30, 20, SKY, INK, 6)
    o += poly([(-40, 0), (-75, 60), (-40, 40)], '#fff', INK, 7) + poly([(40, 0), (75, 60), (40, 40)], '#fff', INK, 7)
    o += path('M-25 45 Q0 110 25 45Z', ORANGE, INK, 6)
    return G(o, x, y, s, rot)


def puzzle(x, y, s=1, fill=BLUE, rot=0):
    d = 'M-50 -50 L-12 -50 A14 14 0 1 1 12 -50 L50 -50 L50 -12 A14 14 0 1 1 50 12 L50 50 L-50 50Z'
    return G(path(d, fill, INK, 7 / s), x, y, s, rot)


def photo(x, y, s=1, rot=0, sky=SKY):
    o = rect(-70, -55, 140, 110, '#fff', INK, 7, 4) + rect(-56, -42, 112, 72, sky, INK, 4)
    o += path('M-56 30 L-20 -6 L6 18 L26 0 L56 30Z', GRASS, INK, 4) + circ(30, -22, 10, YELLOW, INK, 3)
    return G(o, x, y, s, rot)


def sticky(x, y, s=1, fill=YELLOW, rot=0):
    o = rect(-40, -40, 80, 80, fill, INK, 6, 3) + line(-24, -12, 24, -12, 4, INK, op=0.4) + line(-24, 8, 16, 8, 4, INK, op=0.4)
    return G(o, x, y, s, rot)


def book(x, y, w=60, h=200, fill=BLUE, rot=0):
    o = rect(-w / 2, -h / 2, w, h, fill, INK, 7, 6) + line(-w / 2 + 8, -h * 0.3, w / 2 - 8, -h * 0.3, 5, '#fff', op=0.7)
    o += line(-w / 2 + 8, h * 0.3, w / 2 - 8, h * 0.3, 5, '#fff', op=0.7)
    return G(o, x, y, 1, rot)


def doorway(x, y, w=300, h=560, inside='#FFF6D6', door=WOOD, open_=True):
    o = rect(x - w / 2 - 20, y - h - 20, w + 40, h + 20, WOOD_D, INK, SW)
    o += rect(x - w / 2, y - h, w, h, inside if open_ else door, INK, SW)
    if open_:
        o += poly([(x - w / 2, y - h), (x - w / 2 - w * 0.45, y - h + 50), (x - w / 2 - w * 0.45, y + 30), (x - w / 2, y)], door, INK, SW)
        o += circ(x - w / 2 - w * 0.36, y - h / 2 + 30, 12, YELLOW, INK, 5)
    else:
        o += circ(x + w * 0.35, y - h / 2, 14, YELLOW, INK, 6)
    return o


def window(x, y, w, h, sky=SKY, frame='#fff', cross=True):
    o = rect(x - 14, y - 14, w + 28, h + 28, frame, INK, SW, 6) + rect(x, y, w, h, sky, INK, 7)
    if cross:
        o += line(x + w / 2, y, x + w / 2, y + h, 12, frame) + line(x, y + h / 2, x + w, y + h / 2, 12, frame)
        o += rect(x, y, w, h, 'none', INK, 7)
    return o


def cardboard(x, y, w=420, h=300, flaps=True, label=None, fill=CARD):
    o = ''
    if flaps:
        o += poly([(x, y), (x - 70, y - 90), (x + w * 0.45, y - 90), (x + w * 0.5, y)], CARD_D, INK, SW)
        o += poly([(x + w, y), (x + w + 70, y - 90), (x + w * 0.55, y - 90), (x + w * 0.5, y)], CARD_D, INK, SW)
    o += rect(x, y, w, h, fill, INK, SW, 4)
    o += line(x + w * 0.5, y + 6, x + w * 0.5, y + h * 0.3, 6, CARD_D)
    if label:
        o += txt(x + w / 2, y + h * 0.65, label, h * 0.2)
    return o


def glass_case(x, y, w=360, h=380):
    o = rect(x - w / 2 - 30, y, w + 60, 260, '#E8E3D6', INK, SW, 6)
    o += rect(x - w / 2, y - h, w, h, '#DDF1FA', INK, SW, 4, op=None)
    return o


def stairs(x, y, n=6, sw_=160, sh=90, fill='#E6E0D2'):
    p = [(x, y)]
    for i in range(n):
        p += [(x + i * sw_, y - (i + 1) * sh), (x + (i + 1) * sw_, y - (i + 1) * sh)]
    p += [(x + n * sw_, y)]
    return poly(p, fill, INK, SW)


def bag(x, y, s=1, fill=BROWN):
    o = path('M-50 -70 Q-50 -130 0 -130 Q50 -130 50 -70', 'none', INK, 12)
    o += rect(-95, -75, 190, 160, fill, INK, SW, 22)
    o += rect(-70, -40, 140, 40, '#8E5B33', INK, 6, 10)
    return G(o, x, y, s)


def journal(x, y, s=1):
    o = path('M-330 -170 Q-170 -200 0 -165 Q170 -200 330 -170 L330 170 Q170 140 0 175 Q-170 140 -330 170Z', '#FFFDF6', INK, SW)
    o += line(0, -165, 0, 175, 7)
    o += txt(-165, -100, 'JOURNAL', 52)
    o += line(-270, -60, -60, -60, 5, LGRAY) + line(-270, -35, -80, -35, 5, LGRAY)
    o += line(-260, 120, -260, -10, 6) + line(-260, 120, -70, 120, 6)
    for i, hh in enumerate((50, 90, 70, 120)):
        o += rect(-240 + i * 42, 120 - hh, 30, hh, [BLUE, RED, GREEN, YELLOW][i], INK, 5)
    o += line(60, 120, 60, -130, 6) + line(60, 120, 290, 120, 6)
    o += pline([(70, 100), (120, 60), (170, 80), (220, 0), (280, -80)], RED, 7)
    o += line(60, 150, 280, 150, 5, LGRAY)
    return G(o, x, y, s)


def couch_simple(x, y, w=560):
    return couch(x, y, w)
