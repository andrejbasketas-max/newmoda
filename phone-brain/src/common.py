"""Scene registry and helpers shared by the beat files."""
import math
from lib import *

SCENES = {}


def scene(n, bg=BG):
    def deco(fn):
        SCENES[n] = (fn, bg)
        return fn
    return deco


GROUND = 960


def stand(x, ground=GROUND, s=1.0, **kw):
    return fig(x, ground - 150 * s, s, **kw)


def header(t, size=140, x=80, y=190):
    return txt(x, y, t, size, anchor='start')


def sit_pose(foot_y=110, **over):
    p = dict(base='sit', fa=(-38, foot_y, 1), fb=(38, foot_y, -1))
    p.update(over)
    return p


def at_desk(x, s=1.45, top=640, **kw):
    """Figure seated behind a table whose top surface starts at y=top (draw the table after it)."""
    hip_y = top + 92
    foot = (top + 92 + 26 + 200 - hip_y) / s
    pose = kw.pop('pose', {})
    p = dict(base='sit', fa=(-40, foot, 1), fb=(40, foot, -1), ka=(-34, 26), kb=(34, 26),
             a=(-60, (top + 50 - hip_y) / s, 1), b=(60, (top + 50 - hip_y) / s, -1))
    p.update(pose)
    return fig(x, hip_y, s, pose=p, **kw)


def desk_for(x, top=640, w=820):
    return table(x, top, w, WOOD, 200, 80)


def at_hand(f, key='b'):
    return f.J[key]


def open_fingers(x, y, ang, s=1.0, w=6):
    out = ''
    for d in (-35, 0, 35):
        a = math.radians(ang + d)
        out += line(x, y, x + 26 * s * math.cos(a), y + 26 * s * math.sin(a), w * s ** 0.5)
    return out


def pencil(x, y, s=1.0, rot=0):
    o = rect(-12, -90, 24, 150, YELLOW, INK, 6, 3)
    o += poly([(-12, 60), (12, 60), (0, 92)], '#F2D3A2', INK, 6) + poly([(-4, 80), (4, 80), (0, 92)], INK, INK, 3)
    o += rect(-12, -110, 24, 22, '#F49AB0', INK, 6, 6)
    return G(o, x, y, s, rot)


def rain_cloud(x, y, s=1.0):
    o = cloud(0, 0, 150, 70, '#B8BCC4', INK, SW, 8, 1.3)
    for i, xx in enumerate((-90, -40, 10, 60, 105)):
        o += line(xx, 95 + (i % 2) * 20, xx - 14, 140 + (i % 2) * 20, 7, BLUE)
    return G(o, x, y, s)


def dust(x, y, s=1.0, op=0.85):
    return cloud(x, y, 46 * s, 30 * s, '#D9D5CC', INK, 5, 7, 1.35, op)


def cobweb(x, y, s=1.0, rot=0):
    o = ''
    for a in (0, 22, 45, 68, 90):
        r = math.radians(a)
        o += line(0, 0, 130 * math.cos(r), 130 * math.sin(r), 3, DGRAY)
    for rr in (40, 75, 110):
        p = [(rr * math.cos(math.radians(a)), rr * math.sin(math.radians(a))) for a in (0, 22, 45, 68, 90)]
        o += pline(p, DGRAY, 3)
    return G(o, x, y, s, rot)


def sink_drain(x, y, s=1.0):
    o = ell(0, 0, 260, 90, LGRAY, INK, SW) + ell(0, 0, 90, 34, DGRAY, INK, 7)
    for a in (0, 60, 120):
        o += line(-70, 0, 70, 0, 6, INK, op=0.5) if a == 0 else ''
    o += line(0, -30, 0, 30, 6, INK, op=0.5)
    return G(o, x, y, s)


def swirl(x, y, r=140, turns=2.2, w=8, c=BLUE, squash=0.4):
    p = []
    n = 60
    for i in range(n + 1):
        t = i / n
        a = t * turns * 2 * math.pi
        rr = r * (1 - t * 0.85)
        p.append((x + rr * math.cos(a), y + rr * math.sin(a) * squash))
    return pline(p, c, w)


def grains_fall(x, y, n=6):
    o = ''
    for i in range(n):
        o += ell(x + ((i * 23) % 50) - 25, y + i * 26, 8, 5, YELLOW, INK, 3, rot=i * 30)
    return o


def call_icon(x, y, s=1.0, fill=GREEN):
    o = rect(-60, -60, 120, 120, fill, INK, 7, 28)
    o += path('M-30 -34 Q-38 -10 -16 16 Q8 40 32 32 L34 18 L16 8 L6 18 Q-8 10 -16 -4 L-6 -14 L-16 -32Z', '#fff', 'none', 0)
    return G(o, x, y, s)


def text_icon(x, y, s=1.0, fill=GREEN):
    o = rect(-60, -60, 120, 120, fill, INK, 7, 28)
    o += path('M-34 -26 L34 -26 Q42 -26 42 -18 L42 12 Q42 20 34 20 L-6 20 L-24 36 L-22 20 L-34 20 Q-42 20 -42 12 L-42 -18 Q-42 -26 -34 -26Z', '#fff', 'none', 0)
    return G(o, x, y, s)


def thumb_tile(x, y, s=1.0, rot=0, col=SCREEN):
    o = rect(-70, -45, 140, 90, col, INK, 7, 10) + poly([(-16, -20), (-16, 20), (20, 0)], RED, INK, 5)
    return G(o, x, y, s, rot)


def ground_band(y, col=SAND, top=None):
    return rect(-20, y, W + 40, H - y + 20, col, INK, SW)


def sky(col=SKY):
    return rect(0, 0, W, H, col, None, 0)


def jeans_pocket(f, side='b', s=None):
    """Front pocket line on the jeans of figure f."""
    s = s or f.s
    hx, hy = f.J['hip']
    sg = 1 if side == 'b' else -1
    return path(f'M{F(hx + sg * 8 * s)} {F(hy + 2 * s)} Q{F(hx + sg * 30 * s)} {F(hy + 26 * s)} {F(hx + sg * 44 * s)} {F(hy + 44 * s)}', 'none', INK, 5 * s ** 0.75)


def network_dots(pts_, edges, r=11):
    o = ''
    for i, j in edges:
        o += line(*pts_[i], *pts_[j], 3.5, INK)
    for x, y in pts_:
        o += circ(x, y, r * 1.9, YELLOW, None, 0, 0.35) + circ(x, y, r, YELLOW, INK, 4)
    return o


def clip_group(cid, shape, inner):
    return f'<clipPath id="{cid}">{shape}</clipPath><g clip-path="url(#{cid})">{inner}</g>'
