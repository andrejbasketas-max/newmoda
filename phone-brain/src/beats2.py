"""Beats 45-88."""
from common import *


@scene(45)
def b45():
    s = 2.6
    f = fig(960, 1090, s, dict(base='stand', a=(-70, -60, -1), b=(70, -60, 1)), eyes='wide', brows='worried', mouth='wavy', look=(0, 0.5))
    hx, hy = f.J['head']
    nb = rect(700, 800, 520, 300, '#fff', INK, SW, 8, rot=-3) + line(960, 805, 958, 1095, 6)
    for i in range(5):
        y = 850 + i * 42
        nb += zig(730, y, 930, y + 4, 7, 7, 4) + zig(990, y, 1180, y - 2, 7, 7, 4)
    o = [f, nb]
    for key in ('a', 'b'):
        o.append(circ(*f.J[key], 16, INK, None, 0))
    for sg in (-1, 1):
        o.append(arcs(hx, hy, 150, 180 + sg * 0 - 20 if sg < 0 else -20, 200 if sg < 0 else 20, 2, 26, 6))
    for dx, dy, r in ((-190, -80, -30), (180, -110, 30), (-150, -170, -15), (210, -10, 40)):
        o.append(drop(hx + dx, hy + dy, 1.4, r))
    return o


@scene(46)
def b46():
    s = 1.5
    f = stand(620, GROUND, s, pose=dict(base='stand', neck=(14, -133), b=(118, -170, 1), a=(-40, 10, 1)),
              eyes='wide', brows='worried', mouth='frown', look=(1, -0.6))
    hx, hy = f.J['head']
    o = [shadow(620, GROUND + 4, 230), f, phone(1300, 360, 120, rot=14), glow(1300, 360, 120, 150, SCREEN, 0.35)]
    for a in (-150, -110, -60, -20):
        r = math.radians(a)
        o.append(zig(hx + 95 * math.cos(r), hy + 95 * math.sin(r), hx + 140 * math.cos(r), hy + 140 * math.sin(r), 2, 7, 6))
    return o


@scene(47)
def b47():
    o = [poly([(0, 1080), (0, 760), (960, 470), (1920, 760), (1920, 1080)], '#E9E3D5', None, 0)]
    o.append(line(960, -10, 960, 470, 8) + line(960, 470, -10, 763, 8) + line(960, 470, 1930, 763, 8))
    s = 0.95
    pose = dict(base='stand', neck=(0, -122), ka=(-24, -72), fa=(-30, 10, 1), kb=(24, -72), fb=(30, 10, -1),
                ea=(-52, -84), a=(-8, -60, 1), eb=(52, -84), b=(8, -60, -1))
    f = fig(960, 600, s, pose, brows='worried', mouth='frown', look=(0, 0.5))
    o += [shadow(960, 612, 200), f]
    hx, hy = f.J['hip']
    for sg in (-1, 1):
        o.append(arcs(hx, hy - 90, 115, 160 if sg < 0 else -20, 200 if sg < 0 else 20, 2, 18, 5))
    return o


@scene(48)
def b48():
    o = [shadow(1150, 905, 500), glass_case(1150, 640, 360, 380)]
    o.append(rect(1100, 560, 100, 80, '#E8E3D6', INK, 7))
    o.append(phone(1150, 480, 90))
    s = 1.5
    f = fig(820, 900 - 150 * s, s, dict(base='stand', neck=(58, -122), a=(118, -148, 1), b=(122, -100, 1), fa=(-40, 150, 1), fb=(20, 150, -1)),
            eyes='wide', brows='worried', mouth='o', look=(1, 0))
    o += [shadow(800, 905, 220), f]
    o.append(rect(970, 260, 360, 380, '#DDF1FA', None, 0, op=0.35))
    o.append(line(1240, 290, 1180, 420, 8, '#fff') + line(1290, 300, 1220, 460, 8, '#fff'))
    o.append(rect(970, 260, 360, 380, 'none', INK, SW, 4))
    for key in ('a', 'b'):
        o.append(ell(f.J[key][0] + 6, f.J[key][1], 14, 22, '#fff', INK, 5, 0.9))
    return o


@scene(49)
def b49():
    return [calendar(380, 220, 680, 660, circled=10), txt(1450, 610, '1 DAY', 190)]


@scene(50)
def b50():
    return [txt(1000, 520, 'NOMOPHOBIA', 230), shadow(330, 1004, 170),
            stand(330, 1000, 1.15, pose='point_up', look=(0.7, -0.7), mouth='small')]


@scene(51)
def b51():
    s = 2.6
    f = fig(960, 1090, s, dict(base='stand', a=(-74, -66, -1), b=(74, -66, 1)), eyes='huge', brows='worried', mouth='grimace')
    bx, by = f.J['b']
    o = [f, phone(bx + 10, by - 120, 130, rot=10, dashed=True)]
    for key, sg in (('a', -1), ('b', 1)):
        hx, hy = f.J[key]
        o.append(open_fingers(hx, hy, -90 + sg * 30, 2.0, 7))
    return o


@scene(52)
def b52():
    o = [sky(), rect(-20, 860, W + 40, 240, '#B9B9B9', INK, SW), line(0, 980, W, 980, 10, '#fff', dash='60 50')]
    o += [dd_bus(1320, 900, 1.0), header('2008')]
    f = stand(520, 960, 1.25, pose=dict(base='stand', b=(58, -66, 1)), hair='messy', glasses=True, coat=True, look=(0.6, 0.2), mouth='small')
    hx, hy = f.J['b']
    return o + [f, clipboard(hx + 30, hy - 30, 0.85, 8)]


@scene(53)
def b53():
    o = [pie(720, 540, 320, 0.56)]
    for i, x in enumerate((1260, 1490, 1720)):
        o += [shadow(x, GROUND + 4, 150), stand(x, GROUND, 1.05, brows='worried', mouth='wavy', look=(-0.6, 0),
                                                 hair=[None, 'cap', 'curly'][i], hair_c=[INK, SKIN_HAIR['brown'], INK][i])]
    return o


@scene(54)
def b54():
    o = [path('M150 160 L490 160 L470 920 L170 920Z', JEANS, INK, SW)]
    o.append(path('M150 300 Q300 320 400 160', 'none', INK, 8))
    o.append(path('M150 330 Q315 350 430 160', 'none', '#DCE6F4', 4, dash='12 10'))
    o.append(battery(960, 540, 340, 170, 0.12, RED))
    o.append(signal_bars(1600, 560, 1.35, LGRAY) + redx(1600, 540, 300, 26))
    o.append(line(640, 0, 640, H, 14) + line(1280, 0, 1280, H, 14))
    return o


@scene(55)
def b55():
    s = 2.8
    f = fig(960, 1090, s, dict(base='stand', neck=(10, -134), a=(-56, 30, 1), b=(56, 30, -1)), brows='one', mouth='small', tilt=-8)
    hx, hy = f.J['head']
    return [f, sparkle(hx + 230, hy - 120, 1.4), sparkle(hx + 300, hy - 20, 0.7)]


@scene(56)
def b56():
    s = 1.5
    f = stand(560, GROUND, s, pose=dict(base='stand', neck=(-14, -133), b=(150, -88, 1), fa=(-44, 150, 1), fb=(30, 150, -1)),
              eyes='wide', brows='worried', mouth='o', look=(1, 0), sleeves=BLUE)
    hx, hy = f.J['b']
    o = [shadow(560, GROUND + 4, 230), f]
    o.append(phone(1380, 520, 300, content=mute_icon(0, -180, 1.4)))
    o.append(mitt(hx + 80, hy - 4, 1.05, 180, arm=420))
    return o


@scene(57)
def b57():
    o = [sky(), ground_band(900, GRASS), tower(1250, 900, 1.05), header('2017')]
    f = stand(560, 960, 1.3, hair='short', hair_c=SKIN_HAIR['brown'], glasses=True, mouth='small', look=(0.5, 0))
    return o + [f]


@scene(58)
def b58():
    o = [txt(960, 160, '800', 170)]
    rows = ((330, 0.36, 9), (500, 0.44, 8), (690, 0.53, 7), (900, 0.63, 6))
    for y, s, n in rows:
        span = 1700 * (0.75 + s * 0.4)
        for i in range(n):
            x = 960 - span / 2 + span * (i + 0.5) / n
            hip = y - 10 * s
            f = fig(x, hip, s, sit_pose(110, a=(-40, -40, 1), b=(40, -40, -1)), look=(0, 0.7),
                    hair=[None, 'short', 'curly', 'cap', None, 'shoulder'][(i + int(y)) % 6],
                    hair_c=[INK, SKIN_HAIR['brown'], INK, SKIN_HAIR['red'], INK, SKIN_HAIR['brown']][(i + int(y)) % 6])
            o.append(f)
            o.append(rect(x - 95 * s * 1.6, y - 60 * s, 190 * s * 1.6, 60 * s, WOOD, INK, 6 * s ** 0.5, 4))
            o.append(rect(x - 95 * s * 1.6, y, 190 * s * 1.6, 22 * s, WOOD_D, INK, 6 * s ** 0.5, 3))
            o.append(rect(x - 30 * s, y - 50 * s, 60 * s, 34 * s, '#fff', INK, 3, 2))
    return o


def _test_desk(**kw):
    s = 1.45
    pose = kw.pop('pose', dict(b=(36, -60, 1), a=(-56, -60, 1)))
    f = at_desk(960, s, 640, pose=pose, **kw)
    return f, [paper(960, 690, 190, 70, -4, 3, kw.get('_star', False))]


@scene(59)
def b59():
    f, p = _test_desk(look=(0, 0.7), brows='tense', mouth='flat')
    hx, hy = f.J['head']
    o = [f, desk_for(960)] + p + [pencil(f.J['b'][0] + 10, 650, 0.55, 20)]
    o += [puzzle(hx - 260, hy - 150, 1.0, BLUE, -15), puzzle(hx + 250, hy - 190, 0.9, RED, 20), puzzle(hx + 20, hy - 290, 0.8, YELLOW, 5)]
    o += [txt(hx - 140, hy - 270, '7', 90), txt(hx + 150, hy - 330, '+', 90), txt(hx + 360, hy - 40, '3', 90), txt(hx - 360, hy - 10, '9', 90)]
    return o


@scene(60)
def b60():
    f, p = _test_desk(look=(0, 0.7), mouth='flat')
    return [f, desk_for(960)] + p + [pencil(f.J['b'][0] + 10, 650, 0.55, 20), phone(1210, 680, 120, rot=84, down=True)]


@scene(61)
def b61():
    f, p = _test_desk(look=(0, 0.7), mouth='flat')
    o = [rect(560, 400, 26, 420, WOOD_D, INK, 7, 4), rect(500, 680, 140, 24, WOOD, INK, 7, 4)]
    o.append(phone(560, 560, 70, rot=-10))
    o.append(bag(560, 680, 1.0))
    o.append(line(560, 410, 560, 560, 6))
    return o + [f, desk_for(1020, 640, 700)] + p + [pencil(f.J['b'][0] + 10, 650, 0.55, 20)]


@scene(62)
def b62():
    o = [rect(-20, 880, W + 40, 220, '#E9E3D5', INK, SW)]
    o.append(rect(860, -20, 200, 1120, '#DCD5C4', INK, SW))
    o.append(rect(880, 330, 160, 560, WOOD, INK, SW, 4) + circ(1010, 620, 12, YELLOW, INK, 5))
    o.append(rect(240, 520, 420, 26, WOOD_D, INK, 7, 4) + line(300, 546, 330, 600, 7) + line(600, 546, 570, 600, 7))
    o.append(phone(450, 450, 70))
    s = 1.2
    top = 700
    f = fig(1450, top + 76, s, dict(base='sit', fa=(-40, (880 - top - 76) / s, 1), fb=(40, (880 - top - 76) / s, -1), ka=(-34, 26), kb=(34, 26),
                                     a=(-50, -40, 1), b=(50, -40, -1)), look=(0, 0.7), mouth='small')
    o += [f, table(1450, top, 520, WOOD, 160, 64), paper(1450, top + 32, 150, 46, -4, 2)]
    return o


@scene(63)
def b63():
    return [phone(x, 540, 220, content=mute_icon(0, 0, 1.6)) for x in (520, 960, 1400)]


@scene(64)
def b64():
    s = 1.45
    f = at_desk(960, s, 640, pose=dict(b=(60, -60, 1), a=(-56, -60, 1)), eyes='happy', mouth='big', brows='raised')
    return [f, desk_for(960), paper(960, 685, 220, 80, -4, 3, True), sparkle(1240, 380, 0.8), sparkle(680, 420, 0.6)]


@scene(65)
def b65():
    o = [line(420, 900, 1500, 900, 12) + line(420, 900, 420, 180, 12)]
    o.append(rect(560, 300, 300, 600, GREEN, INK, SW, 6) + rect(1060, 640, 300, 260, GRAY, INK, SW, 6))
    o.append(txt(710, 990, 'OTHER ROOM', 72) + txt(1210, 990, 'DESK', 72))
    return o


@scene(66)
def b66():
    s = 1.45
    f = at_desk(860, s, 640, pose=dict(b=(60, -60, 1), a=(-56, -60, 1)), eyes='tired', brows='tired', mouth='flat', look=(0.3, 0.4))
    hx, hy = f.J['head']
    bx, by = hx, hy - 210
    bat = G(rect(-130, -60, 260, 120, '#fff', INK, 12, 18) + rect(130, -24, 22, 48, INK, INK, 6, 6) +
            rect(-116, -46, 60, 92, RED, None, 0, 8) + rect(-50, -46, 52, 92, GREEN, None, 0, 8, op=0.25) +
            rect(8, -46, 52, 92, GREEN, None, 0, 8, op=0.12), bx, by)
    o = [f, desk_for(960), paper(820, 690, 190, 70, -4, 3), phone(1150, 680, 120, rot=84, down=True), bat]
    o.append(path(f'M{F(bx + 150)} {F(by)} Q{F(1260)} {F(by + 40)} {F(1170)} {F(640)}', 'none', RED, 6, dash='14 12'))
    o.append(arrow(1190, 600, 1168, 646, 6, RED, 22))
    return o


@scene(67)
def b67():
    o = [txt(960, 190, 'BRAIN DRAIN', 150), sink_drain(960, 880, 1.2)]
    o.append(swirl(960, 870, 260, 2.4, 8, BLUE, 0.32))
    o.append(brain(960, 520, 1.15, eyes='wide', brows='worried', mouth='wavy', look=(0, 0.8)))
    return o


@scene(68)
def b68():
    o = [phone(1560, 560, 160)]
    o.append(mitt(1280, 600, 1.1, 0, arm=900))
    bx, by = 620, 420
    o.append(line(bx + 40, by + 100, 900, 600, 11) + line(bx + 130, by + 40, 1000, 590, 11))
    o.append(circ(900, 600, 13, INK, None, 0) + circ(1000, 590, 13, INK, None, 0))
    o.append(brain(bx, by, 1.15, eyes='squeeze', mouth='grimace', brows='tense'))
    o.append(drop(bx - 190, by - 90, 1.2, -30) + drop(bx + 200, by - 120, 1.1, 30))
    o.append(motion(870, 500, 180, 3, 60, 26, 6))
    return o


@scene(69)
def b69():
    o = [sun(260, 170, 52), moon(470, 170, 46), phone(1380, 560, 420, rot=-4)]
    s = 1.5
    f = stand(880, GROUND, s, pose=dict(base='stand', neck=(70, -110), a=(150, -150, 1), b=(152, -104, 1), fa=(-110, 140, 1), fb=(30, 150, -1)),
              eyes='squeeze', mouth='grimace', look=(1, 0))
    hx, hy = f.J['head']
    o += [shadow(880, GROUND + 4, 300), f, drop(hx - 100, hy - 90, 1.2, -30), drop(hx - 140, hy - 10, 1.0, -50), drop(hx + 20, hy - 130, 1.0, 10)]
    return o


@scene(70)
def b70():
    s = 1.55
    f = stand(1180, GROUND, s, pose='walk', jeans=True, eyes='happy', mouth='smile', look=(1, 0))
    hx, hy = f.J['hip']
    o = [shadow(1180, GROUND + 4, 240), f, jeans_pocket(f, 'a')]
    for x, y, r in ((hx - 90, hy + 70, 20), (hx - 170, hy + 160, -30), (900, GROUND - 6, 80), (780, GROUND - 4, 90), (640, GROUND - 8, 70)):
        o.append(coin(x, y, 1.0, r))
    o.append(line(hx - 70, hy + 30, hx - 60, hy + 50, 6) + line(hx - 60, hy + 50, hx - 80, hy + 55, 6))
    return o


@scene(71)
def b71():
    o = [rect(-20, 880, W + 40, 220, '#E9E3D5', INK, SW)]
    o.append(doorway(1280, 900, 360, 640))
    for i in range(6):
        a = math.radians(200 + i * 28)
        o.append(line(1280 + 60 * math.cos(a), 600 + 60 * math.sin(a), 1280 + 140 * math.cos(a), 600 + 140 * math.sin(a), 7, '#F2C94C'))
    o.append(phone(520, 900, 110, rot=84, down=True))
    s = 1.45
    o += [stand(1150, 900, s, pose='walk', look=(1, -0.2), mouth='small', brows='raised')]
    return o


@scene(72)
def b72():
    o = [couch(960, 960, 760), header('DAY 3')]
    f = fig(960, 852, 1.5, sit_pose(110), eyes='closed', mouth='small')
    hx, hy = f.J['head']
    return o + [f, phone(hx, hy - 260, 110, dashed=True, op=0.35), phone(hx, hy - 260, 110, op=0.12)]


@scene(73)
def b73():
    o = [path('M380 260 Q960 210 1480 260 L1440 1100 L460 1100Z', JEANS, INK, 12)]
    o.append(path('M820 250 Q860 470 1150 520 L1150 250', 'none', INK, 9))
    o.append(path('M790 250 Q840 500 1150 555', 'none', '#DCE6F4', 4, dash='14 10'))
    o.append(line(500, 250, 1440, 250, 22, BROWN) + rect(860, 232, 70, 36, '#C9C9C9', INK, 6, 6))
    o.append(mitt(1480, 520, 1.7, 92, arm=700))
    return o


@scene(74)
def b74():
    o = [couch(960, 960, 760), txt(960, 190, 'BORED', 150)]
    s = 1.5
    f = fig(960, 880, s, dict(base='sit', neck=(14, -112), ka=(-44, 0), kb=(44, 0), fa=(-74, 56, 1), fb=(74, 56, -1),
                               a=(-72, 0, 1), b=(72, 0, -1)), eyes='half', mouth='flat', tilt=14)
    return o + [f]


@scene(75)
def b75():
    s = 1.5
    f = stand(560, GROUND, s, pose=dict(base='stand', neck=(20, -132), a=(136, -64, 1), b=(144, -92, 1)), eyes='wide', mouth='o', look=(1, 0.3))
    o = [shadow(1150, GROUND + 4, 600), shadow(560, GROUND + 4, 220)]
    o.append(cardboard(900, 600, 520, 360, flaps=False, label='BOREDOM'))
    o.append(poly([(900, 600), (840, 470), (1150, 470), (1160, 600)], CARD_D, INK, SW))
    o.append(poly([(1420, 600), (1500, 500), (1260, 520), (1160, 600)], CARD_D, INK, SW))
    o.append(cobweb(905, 605, 1.0, 0) + cobweb(1415, 605, 1.0, 90) + cobweb(1415, 955, 0.8, 180))
    o += [f]
    for x, y, sc in ((1130, 420, 1.2), (1260, 380, 0.9), (1000, 380, 0.8), (1370, 430, 0.7)):
        o.append(dust(x, y, sc))
    return o


@scene(76)
def b76():
    o = []
    for i, x in enumerate((300, 560, 820, 1100, 1360, 1620)):
        main = x == 1100
        o.append(shadow(x, GROUND + 4, 150))
        o.append(stand(x, GROUND, 1.15, look=(1, 0) if not main else (0, 0), mouth='flat' if main else None,
                       hair=['short', 'curly', 'cap', None, 'shoulder', 'short'][i],
                       hair_c=[SKIN_HAIR['brown'], INK, SKIN_HAIR['red'], INK, INK, SKIN_HAIR['gray']][i]))
    return o


@scene(77, '#C9CDD2')
def b77():
    o = [rect(180, 120, 1400, 520, SKY, INK, SW, 30)]
    o.append(f'<clipPath id="bw"><rect x="180" y="120" width="1400" height="520" rx="30"/></clipPath>')
    inner = rect(150, 520, 1500, 200, GRASS, INK, 7) + round_tree(420, 560, 0.9) + round_tree(900, 560, 1.1) + round_tree(1350, 560, 0.85)
    inner += motion(700, 330, 180, 3, 120, 40, 6) + motion(1200, 300, 180, 2, 120, 40, 6)
    o.append(f'<g clip-path="url(#bw)">{inner}</g>')
    o.append(rect(180, 120, 1400, 520, 'none', INK, SW, 30) + line(880, 120, 880, 640, 16, '#E8E8E8') + line(880, 120, 880, 640, 6))
    o.append(rect(-20, 900, W + 40, 200, '#9EA4AB', INK, SW))
    s = 1.45
    hip = (1250, 840)
    o.append(rect(1080, 520, 380, 280, BLUE, INK, SW, 30))
    f = fig(*hip, s, sit_pose((900 - 840) / s + 40, a=(-40, 10, 1), b=(40, 10, -1)), look=(-1, -0.4), mouth='small')
    o.append(f)
    o.append(rect(1060, 790, 420, 70, BLUE, INK, SW, 20))
    return o


@scene(78)
def b78():
    f = stand(960, GROUND, 1.55, pose=dict(base='stand', neck=(8, -122), a=(-30, 20, 1), b=(30, 20, -1)), brows='worried', mouth='grimace', tilt=10)
    hx, hy = f.J['head']
    return [shadow(960, GROUND + 4, 230), f, rain_cloud(hx, hy - 260, 1.2)]


@scene(79)
def b79():
    s = 2.8
    f = fig(960, 1200, s, dict(base='stand'), look=(0, -1), mouth='small')
    hx, hy = f.J['head']
    return [f, circ(hx, hy - 330, 130, YELLOW, None, 0, 0.16), bulb(hx, hy - 330, 1.4, True, YELLOW, True)]


@scene(80)
def b80():
    o = [rect(1130, 520, 120, 150, LGRAY, INK, SW, 14), line(1190, 600, 1300, 440, 18), circ(1300, 440, 34, RED, INK, 8)]
    o.append(curved_arrow(1190, 600, 230, -110, -55, 8, INK, 26))
    o.append(brain(900, 580, 1.4, eyes='wide', mouth='o', look=(0.8, -0.3)))
    for x, y, c, sc in ((1390, 340, YELLOW, 0.8), (1430, 520, BLUE, 0.6), (1300, 290, PINK_D, 0.6), (1050, 330, GREEN, 0.6), (1440, 420, ORANGE, 0.5)):
        o.append(sparkle(x, y, sc, c))
    return o


@scene(81)
def b81():
    o = [txt(960, 180, 'DEFAULT MODE NETWORK', 110)]
    s = 1.6
    pts_ = [(-95, -55), (-30, -85), (45, -70), (100, -25), (-110, 10), (-45, -20), (30, -15), (85, 35), (-60, 60), (10, 75)]
    pts_ = [(960 + x * s, 600 + y * s) for x, y in pts_]
    edges = [(0, 1), (1, 2), (2, 3), (0, 4), (4, 5), (5, 1), (5, 6), (6, 2), (6, 3), (6, 7), (4, 8), (8, 9), (9, 7), (5, 8), (6, 9)]
    o.append(brain(960, 600, s, eyes='wide', mouth='small'))
    o.append(network_dots(pts_, edges, 11))
    return o


@scene(82)
def b82():
    o = [sky(), ground_band(760, SAND), ell(900, 860, 560, 80, GRASS, INK, SW), acacia(1600, 800, 1.1)]
    f = fig(900, 840, 1.3, dict(base='stand', a=(-60, -150, -1), b=(60, -150, 1)), rot=-90, eyes='closed', mouth='small')
    hx, hy = f.J['head']
    o += [f, thought(780, 330, 300, 170, tail=(hx + 20, hy - 70))]
    return o


@scene(83)
def b83():
    o = [thought(960, 350, 600, 240, tail=(1010, 610), n=12)]
    a, b_, c, d = (640, 330), (900, 260), (1130, 420), (1320, 300)
    o.append(pline([a, b_, c, d], INK, 5, '12 12'))
    o.append(line(*a, 760, 470, 5, INK, '12 12') + line(760, 470, *c, 5, INK, '12 12'))
    o += [photo(*a, 1.0, -8), photo(760, 470, 0.8, 10), rocket(*b_, 0.8, 30), puzzle(*c, 0.8, BLUE, -10), puzzle(*d, 0.75, GREEN, 15)]
    o += [shadow(960, 1044, 150), stand(960, 1040, 0.95, look=(0, -0.8), mouth='small')]
    return o


@scene(84)
def b84():
    o = [header('2014')]
    for x, h, c in ((720, 'long', SKIN_HAIR['dark']), (1200, 'short', SKIN_HAIR['red'])):
        f = stand(x, GROUND, 1.4, pose=dict(base='stand', b=(58, -66, 1)), hair=h, hair_c=c, mouth='small', look=(0.3, 0))
        hx, hy = f.J['b']
        o += [shadow(x, GROUND + 4, 220), f, clipboard(hx + 30, hy - 30, 0.95, 8)]
    return o


@scene(85)
def b85():
    f = at_desk(960, 1.45, 640, pose=dict(neck=(0, -138)), eyes='squeeze', mouth='yawn', tilt=-6)
    hx, hy = f.J['head']
    return [f, desk_for(960), paper(960, 690, 200, 70, -4, 3), zzz(hx + 130, hy - 60, 1.0)]


@scene(86)
def b86():
    f = at_desk(960, 1.45, 640, pose=dict(b=(70, -60, 1), a=(-70, -60, 1)), eyes='half', mouth='flat', look=(0.2, 0.7))
    pb = rect(700, 650, 320, 64, YELLOW, INK, 7, 6) + rect(712, 646, 148, 56, '#FFFBEA', INK, 5, 3) + rect(862, 646, 146, 56, '#FFFBEA', INK, 5, 3)
    for yy in (656, 670, 684):
        pb += line(724, yy, 846, yy, 3, GRAY) + line(874, yy, 996, yy, 3, GRAY)
    pr = paper(1170, 686, 200, 70, -4, 0) + txt(1170, 702, '555-0192', 30, rot=-4)
    hx, hy = f.J['b']
    return [f, desk_for(960), pb, pr, pencil(hx + 14, 650, 0.55, 20)]


def _bulbs_around(hx, hy, n=7, r=260):
    cols = [YELLOW, '#FF9AA2', '#8FD0F0', '#B5E48C', '#FFC37A', '#C9A7F0', YELLOW]
    o = ''
    for i in range(n):
        a = math.radians(-180 + i * 180 / (n - 1))
        o += bulb(hx + r * math.cos(a), hy - 30 + r * 0.9 * math.sin(a), 0.62, True, cols[i % len(cols)], True)
    return o


@scene(87)
def b87():
    f = stand(960, 1000, 1.5, eyes='happy', mouth='big')
    hx, hy = f.J['head']
    return [shadow(960, 1004, 230), f, _bulbs_around(hx, hy, 7, 290)]


@scene(88)
def b88():
    f1 = stand(560, 1000, 1.3, eyes='happy', mouth='big')
    f2 = stand(1380, 1000, 1.3, mouth='flat', brows='flat')
    h1, h2 = f1.J['head'], f2.J['head']
    return [shadow(560, 1004, 200), shadow(1380, 1004, 200), f1, f2, _bulbs_around(*h1, 6, 230),
            bulb(h2[0], h2[1] - 210, 0.75, False, LGRAY, False, dim=True)]
