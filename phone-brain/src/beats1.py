"""Beats 1-44."""
from common import *


@scene(1)
def b1():
    o = [couch(960, 960, 780)]
    s = 1.5
    pose = sit_pose(110, neck=(14, -126), a=(66, -118, 1), b=(92, -122, 1))
    hip = (960, 852)
    px, py = hip[0] + 84 * s, hip[1] - 168 * s
    o.append(glow(px, py, 150, 170, SCREEN, 0.45))
    o.append(fig(*hip, s, pose, look=(0.9, 0.3), mouth='flat'))
    o.append(phone(px, py, 62 * s, rot=-8))
    return o


@scene(2)
def b2():
    s = 2.8
    f = fig(860, 1000, s, dict(base='stand', b=(78, -118, 1), a=(-46, 30, 1)), look=(1, -0.2), brows='worried', mouth='flat')
    hx, hy = f.J['b']
    o = [f, phone(hx + 10, hy - 95, 150, rot=-6), circ(hx + 190, hy - 250, 34, RED, INK, 8)]
    o.append(thought(560, 190, 130, 90, tail=(700, 330)))
    o.append(qmark(560, 175, 150))
    return o


@scene(3)
def b3():
    o = [bell(500, 330, 1.35), msg_icon(960, 330, 1.35), app_grid(1420, 330, 1.35)]
    o.append(shadow(960, GROUND + 4, 160))
    o.append(stand(960, GROUND, 1.0, eyes='wide', look=(0, -1)))
    return o


@scene(4)
def b4():
    o = [phone_in_hand(960, 520, 380, thumb='press')]
    tx, ty = 960 + 380 * 0.06, 520 - 0.02 * 722
    o.append(arcs(tx, ty - 10, 70, 200, 340, 3, 26, 7))
    return o


def _tallies(seed=3, n=46, avoid=(620, 180, 1300, 1000)):
    o = ''
    import random
    rnd = random.Random(seed)
    placed = 0
    while placed < n:
        x, y = rnd.uniform(80, 1820), rnd.uniform(260, 1010)
        if avoid[0] < x < avoid[2] and avoid[1] < y < avoid[3]:
            continue
        o += tally(x, y, rnd.uniform(0.7, 1.1), rnd.uniform(-15, 15))
        placed += 1
    return o


@scene(5)
def b5():
    s = 1.55
    f = stand(960, GROUND, s, pose=dict(base='stand', b=(62, -76, 1)), brows='tired', eyes='tired', look=(0.5, 0.4), mouth='flat')
    hx, hy = f.J['b']
    return [_tallies(), header('100–150'), shadow(960, GROUND + 4, 240), f, phone(hx + 6, hy - 50, 64, rot=-6)]


@scene(6)
def b6():
    s = 1.6
    f = stand(880, GROUND, s, pose=dict(base='stand', b=(104, -196, 1)), brows='flat', mouth='flat', look=(0.6, -0.2))
    hx, hy = f.J['b']
    return [shadow(880, GROUND + 4, 240), f, phone(hx + 10, hy - 70, 92, rot=8), txt(hx + 10, hy - 230, '0', 150, GRAY)]


@scene(7)
def b7():
    s = 1.5
    f = stand(880, GROUND, s, pose=dict(base='stand', b=(98, -150, 1)), mouth='flat', look=(0.4, 0))
    hx, hy = f.J['b']
    bx, by = 880, 190
    o = [shadow(880, GROUND + 4, 230)]
    o.append(line(bx + 40, by + 100, hx, hy, 5, INK, dash='16 14'))
    o.append(line(bx + 90, by + 70, hx + 20, hy + 40, 5, INK, dash='16 14'))
    o += [f, phone(hx + 18, hy + 60, 70, rot=12), brain(bx, by, 0.62, mouth='small', look=(0.4, 0.6))]
    return o


@scene(8)
def b8():
    s = 1.5
    f = stand(640, GROUND, s, pose=dict(base='stand', neck=(24, -130), a=(132, -112, 1), b=(140, -88, 1),
                                         fa=(-50, 150, 1), fb=(30, 150, -1)),
              eyes='wide', brows='worried', mouth='o', look=(1, 0))
    o = [shadow(640, GROUND + 4, 240), f]
    o.append(motion(1340, 470, -12, 3, 140, 46, 8))
    o.append(phone(1450, 450, 110, rot=18))
    return o


@scene(9)
def b9():
    s = 1.5
    f = stand(620, GROUND, s, pose=dict(base='stand', b=(58, -66, 1)), hair='messy', glasses=True, coat=True, look=(0.6, 0.2), mouth='small')
    hx, hy = f.J['b']
    o = [shadow(620, GROUND + 4, 240), calendar(1020, 250, 520, 560, crossed=19), f, clipboard(hx + 30, hy - 30, 1.0, 8)]
    return o


@scene(10)
def b10():
    s = 2.8
    f = fig(820, 1010, s, dict(base='stand', b=(52, -40, 1), a=(-50, 30, 1)), hair='messy', glasses=True, coat=True,
            eyes='wide', brows='raised', mouth='o', look=(0.3, 0.5))
    hx, hy = f.J['b']
    return [f, clipboard(hx + 90, hy - 70, 1.7, 10), qmark(1480, 330, 320)]


@scene(11)
def b11():
    o = [couch(860, 960, 760)]
    s = 1.5
    f = fig(860, 852, s, sit_pose(110, a=(-30, -52, -1), b=(30, -52, 1)), look=(0, 0.9), brows='tense', mouth='flat')
    o.append(f)
    for key, sg in (('a', -1), ('b', 1)):
        hx, hy = f.J[key]
        o.append(open_fingers(hx, hy, -90 + sg * 25, 1.2))
    o.append(rect(1400, 330, 380, 170, '#fff', INK, SW, 8, rot=-4))
    o.append(txt(1590, 455, 'RELAX', 110, rot=-4))
    o.append(strike(1410, 470, 1770, 355, 20))
    o.append(line(1590, 330, 1590, 300, 6) + circ(1590, 292, 10, RED, INK, 4))
    return o


@scene(12)
def b12():
    s = 2.6
    hip = (960, 1080)
    f = fig(*hip, s, dict(base='stand', a=(-46, -164, -1), b=(46, -164, 1)), eyes='huge', brows='worried', mouth='O')
    hx, hy = f.J['head']
    return [burst(hx, hy, 210, 330, 12, 10), f, txt(960, 175, 'PANIC', 150)]


@scene(13)
def b13():
    return [txt(860, 640, 'WHY?', 360), shadow(1530, GROUND + 4, 170),
            stand(1530, GROUND, 1.15, pose=dict(base='point_up', b=(-118, -210, -1), a=(46, 8, -1)), look=(-0.7, -0.6), mouth='small')]


@scene(14, CREAM)
def b14():
    s = 1.5
    f = stand(470, GROUND, s, pose=dict(base='stand', b=(128, -96, 1)), hair='side', hair_c=SKIN_HAIR['gray'], coat=True,
              look=(0.8, 0), mouth='small')
    hx, hy = f.J['b']
    inner = pigeon(1170, 755, 0.95, eyes='dot', facing=-1)
    o = [header('1950s'), shadow(470, GROUND + 4, 240), shadow(1180, GROUND + 4, 600, 0.1)]
    o.append(skinner_box(900, 440, 520, 380, inner))
    o.append(rect(860, 820, 640, 140, WOOD_D, INK, SW, 4))
    o += [f, open_fingers(hx, hy, -10, 1.3)]
    return o


@scene(15, CREAM)
def b15():
    o = [box_interior(), red_key(1010, 430, 58), tray(1010, 640, 240)]
    o.append(pigeon(640, 960, 1.7, eyes='wide', head=(50, -128)))
    return o


def _peck_panel(x0, grain):
    o = rect(x0, 0, 960, H, CREAM, None, 0)
    o += line(x0 + 30, 900, x0 + 930, 900, 7, INK, op=0.4)
    o += red_key(x0 + 480, 640, 44)
    o += tray(x0 + 670, 890, 200, grain=grain)
    o += pigeon(x0 + 270, 900, 1.35, eyes='wide', head=(64, -122), hrot=8)
    o += motion(x0 + 440, 640, 0, 2, 40, 40, 6)
    if grain:
        o += grains_fall(x0 + 670, 720, 5)
        o += rect(x0 + 640, 560, 60, 120, LGRAY, INK, 7, 6)
    else:
        o += rect(x0 + 640, 560, 60, 120, LGRAY, INK, 7, 6)
        o += qmark(x0 + 680, 790, 110)
    return o


@scene(16, CREAM)
def b16():
    return [_peck_panel(0, True), _peck_panel(960, False), line(960, 0, 960, H, 14)]


@scene(17, CREAM)
def b17():
    s = 1.5
    f = stand(460, GROUND, s, pose=dict(base='stand', b=(64, -70, 1), a=(30, -60, 1)), hair='side', hair_c=SKIN_HAIR['gray'], coat=True,
              look=(1, 0.2), mouth='flat')
    hx, hy = f.J['b']
    inner = pigeon(1150, 760, 0.95, eyes='dot', head=(64, -122), hrot=8) + red_key(1290, 630, 30)
    return [shadow(460, GROUND + 4, 240), skinner_box(900, 440, 520, 380, inner), rect(860, 820, 640, 140, WOOD_D, INK, SW, 4),
            f, clipboard(hx + 40, hy - 40, 1.25, 6, 'graph')]


@scene(18, CREAM)
def b18():
    o = [box_interior(), tray(1250, 860, 260)]
    o.append(pigeon(620, 980, 1.6, eyes='wide', head=(50, -128)))
    o.append(motion(1080, 520, 30, 3, 80, 36, 7) + motion(1290, 470, -20, 3, 80, 36, 7))
    o.append(dice(1150, 560, 1.4, 22, 5) + dice(1360, 500, 1.25, -18, 3))
    return o


@scene(19, CREAM)
def b19():
    o = [box_interior(), red_key(1110, 680, 72), tray(1110, 960, 240)]
    o.append(pigeon(700, 1050, 2.2, eyes='crazy', head=(70, -118), hrot=10))
    hx, hy = 700 + 70 * 2.2, 1050 - 118 * 2.2
    o.append(arcs(hx, hy, 110, 190, 260, 3, 26, 8))
    o.append(motion(1020, 690, 0, 3, 60, 32, 7))
    for i, (dx, dy, r) in enumerate(((-150, -120, -30), (-40, -190, 10), (60, -170, 40), (-190, -10, -60))):
        o.append(drop(hx + dx, hy + dy, 1.1, r))
    return o


@scene(20, CREAM)
def b20():
    o = [box_interior(), red_key(1150, 660, 56), tray(1150, 900, 220)]
    o.append(rect(720, 250, 480, 170, '#fff', INK, SW, 20))
    o.append(txt(960, 370, '1000s', 120))
    o.append(pigeon(800, 1000, 1.8, eyes='wide', head=(70, -118), hrot=10))
    o.append(motion(1080, 670, 0, 3, 60, 30, 7))
    o.append(arcs(800 + 70 * 1.8, 1000 - 118 * 1.8, 90, 200, 260, 2, 24, 7))
    return o


@scene(21)
def b21():
    return [phone_in_hand(960, 500, 320, thumb='rest')]


@scene(22)
def b22():
    w = 330
    h = w * 1.9
    content = curved_arrow(0, -h * 0.36, 34, -60, 230, 9, INK, 26)
    content += arrow(-w * 0.2, -h * 0.25, -w * 0.2, -h * 0.07, 9, INK, 26)
    return [phone_in_hand(960, 560, w, thumb='drag', content=content)]


@scene(23)
def b23():
    o = [phone(960, 580, 230)]
    o.append(line(820, 470, 700, 330, 5, INK, dash='12 14') + heart(650, 290, 1.3))
    o.append(line(1100, 470, 1220, 380, 5, INK, dash='12 14'))
    o.append(speech(1220, 270, 230, 150, (1210, 400), LGRAY))
    return o


@scene(24)
def b24():
    o = [rect(0, 0, 960, H, CREAM, None, 0), line(60, 900, 900, 900, 7, INK, op=0.4)]
    o.append(red_key(680, 640, 46))
    o.append(pigeon(400, 900, 1.5, eyes='wide', head=(70, -118), hrot=10))
    s = 1.45
    f = fig(1300, 900 - 150 * s, s, dict(base='stand', neck=(46, -126), a=(110, -88, 1), b=(124, -70, 1),
                                           fa=(-40, 150, 1), fb=(30, 150, -1)), look=(1, 0.4), eyes='wide')
    hx, hy = f.J['b']
    o += [line(1000, 900, 1880, 900, 7, INK, op=0.4), f, phone(hx + 30, hy - 40, 80, rot=20), line(960, 0, 960, H, 14)]
    return o


@scene(25)
def b25():
    return [shadow(1320, 830, 300), brain(680, 520, 1.25, eyes='wide', mouth='eager', look=(0.3, 0)),
            pigeon(1300, 830, 2.0, eyes='eager', facing=-1)]


@scene(26)
def b26():
    o = [txt(960, 200, 'DOPAMINE', 140), brain(960, 620, 1.45, eyes='happy', mouth='smile')]
    import random
    rnd = random.Random(5)
    for i in range(16):
        a = i / 16 * 2 * math.pi
        r = rnd.uniform(300, 400)
        x, y = 960 + r * math.cos(a), 620 + r * 0.72 * math.sin(a)
        o.append(sparkle(x, y, rnd.uniform(0.5, 0.9)) if i % 2 else drop(x, y, 1.0, rnd.uniform(-30, 30), YELLOW))
    return o


@scene(27)
def b27():
    s = 1.5
    f = stand(640, GROUND, s, pose=dict(base='stand', neck=(44, -126), a=(118, -60, 1), b=(130, -44, 1),
                                         fa=(-44, 150, 1), fb=(32, 150, -1)), eyes='wide', mouth='eager', look=(1, 0.3))
    return [shadow(640, GROUND + 4, 240), shadow(1300, GROUND + 4, 330), f, gift(1300, GROUND - 90, 1.45)]


@scene(28)
def b28():
    w = 420
    h = w * 1.9
    content = ''
    for i, sym in enumerate(('heart', 'q', 'bell')):
        cx = (i - 1) * 118
        content += rect(cx - 52, -95, 104, 190, '#fff', INK, 7, 10)
        if sym == 'heart':
            content += heart(cx, 0, 0.75)
        elif sym == 'q':
            content += qmark(cx, -10, 120)
        else:
            content += bell(cx, 0, 0.42, YELLOW, dot=False)
    content += rect(-170, 140, 340, 70, YELLOW, INK, 7, 12) + txt(0, 192, 'SPIN', 50)
    o = [phone(900, 560, w, content=content)]
    o.append(line(1110, 600, 1190, 600, 22) + line(1190, 610, 1190, 310, 20, DGRAY) + circ(1190, 290, 40, RED, INK, 8))
    o.append(arcs(1190, 290, 70, -60, 20, 2, 24, 6))
    return o


@scene(29)
def b29():
    s = 1.75
    f = stand(900, 1000, s, pose=dict(base='stand', b=(34, -6, -1)), jeans=True, look=(0.5, 0.9), brows='one', mouth='small')
    hx, hy = f.J['hip']
    px, py = hx + 34 * s, hy - 24 * s
    ph = phone(px, py, 60 * s, rot=-12) + line(px + 34 * s, py - 20 * s, px + 50 * s, py - 20 * s, 7) + line(px + 50 * s, py - 20 * s, px + 50 * s, py - 50 * s, 6) + circ(px + 50 * s, py - 56 * s, 9, RED, INK, 4)
    pocket = path(f'M{F(hx + 4 * s)} {F(hy + 2 * s)} L{F(hx + 66 * s)} {F(hy + 2 * s)} L{F(hx + 62 * s)} {F(hy + 40 * s)} Q{F(hx + 34 * s)} {F(hy + 56 * s)} {F(hx + 8 * s)} {F(hy + 36 * s)}Z', JEANS, INK, 6)
    return [shadow(900, 1004, 260), f, ph, pocket, circ(*f.J['b'], 12, INK, None, 0)]


def _place_phone(hand_from, flip=False):
    o = [rect(-20, 600, W + 40, 500, WOOD, INK, SW), line(-20, 600, W + 40, 600, 10)]
    o.append(ell(960, 820, 230, 30, INK, None, 0, 0.12))
    o.append(phone(960, 770, 190, rot=90, down=True))
    if hand_from == 'right':
        o.append(mitt(1080, 640, 1.55, 160, arm=700))
    else:
        o.append(mitt(820, 640, 1.55, 20, arm=700, flipy=True))
    return o


@scene(30)
def b30():
    return _place_phone('right')


@scene(31)
def b31():
    s = 1.45
    f = at_desk(820, s, 640, pose=dict(neck=(18, -132), b=(112, -36, 1)), look=(1, 0.6), brows='worried', mouth='flat')
    hx, hy = f.J['b']
    return [f, desk_for(960), phone(hx + 120, 690, 120, rot=80, down=True),
            circ(hx + 4, 680, 13, INK, None, 0), motion(hx - 40, 670, 0, 2, 50, 26, 6), header('HOUR 1')]


@scene(32)
def b32():
    s = 1.7
    f = stand(1020, 1000, s, pose=dict(base='stand', b=(34, 8, -1)), jeans=True, look=(-0.4, 0), mouth='flat')
    hx, hy = f.J['head']
    bx, by = hx - 330, hy - 210
    legs = pline([(bx - 30, by + 50), (bx - 60, by + 100), (bx - 110, by + 115)], INK, 9)
    legs += pline([(bx + 30, by + 50), (bx + 60, by + 100), (bx + 70, by + 150)], INK, 9)
    return [shadow(1020, 1004, 260), f, jeans_pocket(f), legs, motion(bx - 110, by - 10, 0, 3, 120, 34, 8),
            brain(bx, by, 0.6, eyes='wide', brows='worried', mouth='O', look=(1, 0.4))]


@scene(33)
def b33():
    s = 1.7
    f = stand(880, 1000, s, jeans=True, eyes='wide', brows='raised', mouth='o', look=(0.6, 0.6))
    hx, hy = f.J['hip']
    px, py = hx + 46 * s, hy + 36 * s
    return [shadow(880, 1004, 260), f, jeans_pocket(f), phone(px, py, 48 * s, rot=-10, dashed=True), buzz(px, py, 1.4)]


@scene(34)
def b34():
    s = 1.4
    f = stand(420, GROUND, s, pose=dict(base='stand', b=(58, -66, 1)), hair='shoulder', hair_c=SKIN_HAIR['brown'], glasses=True,
              look=(1, 0), mouth='small')
    hx, hy = f.J['b']
    o = [header('2012'), shadow(420, GROUND + 4, 220), f, clipboard(hx + 30, hy - 30, 0.95, 8, 'lines')]
    for i, x in enumerate((900, 1140, 1380, 1620)):
        o.append(shadow(x, GROUND + 4, 150))
        o.append(stand(x, GROUND, 1.0, look=(-0.8, 0), mouth='small' if i % 2 else None,
                       hair=['short', 'curly', None, 'cap'][i], hair_c=[SKIN_HAIR['brown'], INK, INK, SKIN_HAIR['red']][i]))
    return o


@scene(35)
def b35():
    o = [txt(960, 300, '89%', 230)]
    for i, x in enumerate((360, 660, 960, 1260, 1560)):
        f = stand(x, 1000, 1.05, eyes='wide', brows='raised', mouth='o', look=((i - 2) * 0.25, 0.4),
                  hair=['short', None, 'curly', 'cap', None][i], hair_c=[SKIN_HAIR['brown'], INK, INK, SKIN_HAIR['red'], INK][i])
        hx, hy = f.J['hip']
        o += [shadow(x, 1004, 150), f, buzz(hx, hy + 60, 0.75, INK, 5)]
    return o


@scene(36)
def b36():
    o = [path('M700 -20 L1240 -20 L1180 1100 L760 1100Z', JEANS, INK, 12)]
    o.append(path('M700 120 Q900 140 1080 -20', 'none', INK, 9))
    o.append(path('M700 150 Q910 170 1110 -20', 'none', '#DCE6F4', 4, dash='14 10'))
    o.append(line(980, 300, 960, 1100, 5, '#DCE6F4', dash='16 12'))
    o.append(phone(900, 330, 170, rot=-8, dashed=True))
    o.append(buzz(900, 330, 2.2, INK, 9))
    return o


@scene(37)
def b37():
    o = [line(960, 470, 960, 300, 12), circ(960, 285, 22, RED, INK, 8)]
    o.append(arcs(960, 285, 60, -150, -30, 3, 40, 9))
    o.append(arcs(960, 285, 60, 150, 210, 3, 40, 9))
    o.append(arcs(960, 285, 60, -30, 30, 3, 40, 9))
    o.append(brain(960, 650, 1.45, eyes='wide', brows='raised', mouth='o', look=(0, -0.8)))
    return o


@scene(38)
def b38():
    o = [line(1000, 600, 1110, 480, 11), circ(1110, 480, 12, INK, None, 0)]
    o.append(brain(800, 620, 1.4, eyes='happy', mouth='smile', look=(0.6, -0.3)))
    o.append(pencil(1135, 440, 1.0, 35))
    o.append(arcs(1300, 360, 50, -60, 60, 3, 44, 10))
    o.append(arcs(1300, 360, 50, 120, 200, 2, 44, 10, INK))
    o.append(line(1230, 410, 1190, 450, 5, INK, dash='6 10'))
    return o


@scene(39)
def b39():
    o = [couch(960, 960, 760)]
    s = 1.5
    f = fig(960, 852, s, sit_pose(110, neck=(0, -138), a=(-30, 6, 1), b=(30, 6, -1)), brows='tense', mouth='grimace')
    for key, sg in (('ka', -1), ('kb', 1)):
        kx, ky = f.J[key]
        o.append(line(kx + sg * 30, ky - 30, kx + sg * 30, ky + 10, 6) + line(kx + sg * 50, ky - 22, kx + sg * 50, ky + 2, 6))
    o += [f, header('DAY 1')]
    return o


@scene(40)
def b40():
    o = [sky(), ground_band(900, GRASS), university(960, 900, 1.0), header('2010')]
    for x in (360, 1560):
        f = stand(x, 960, 1.15, pose=dict(base='stand', b=(58, -66, 1)), glasses=True, look=(0.2, 0), mouth='small',
                  hair='short' if x < 960 else 'shoulder', hair_c=SKIN_HAIR['brown'] if x < 960 else INK)
        hx, hy = f.J['b']
        o += [f, clipboard(hx + 26, hy - 26, 0.8, 8)]
    return o


@scene(41)
def b41():
    o = [txt(960, 190, '24 HOURS', 150), shadow(1530, 984, 520)]
    o.append(cardboard(1300, 640, 460, 340))
    for i, x in enumerate((260, 520, 780)):
        f = stand(x, 980, 1.05, pose=dict(base='stand', b=(58, -66, 1)), brows='worried', mouth='frown', look=(1, 0),
                  hair=[None, 'short', 'curly'][i], hair_c=SKIN_HAIR['brown'] if i == 1 else INK)
        hx, hy = f.J['b']
        o += [shadow(x, 984, 150), f, phone(hx + 6, hy - 40, 44, rot=-8)]
    f = stand(1110, 980, 1.05, pose=dict(base='stand', neck=(20, -132), b=(132, -104, 1)), brows='worried', mouth='frown', look=(1, 0.5),
              hair='cap', hair_c=SKIN_HAIR['red'])
    hx, hy = f.J['b']
    o += [shadow(1110, 984, 150), f, phone(hx + 30, hy + 50, 44, rot=20)]
    o += [motion(1430, 580, 90, 2, 40, 30, 6), phone(1430, 610, 44, rot=-30)]
    return o


@scene(42)
def b42():
    return [phone(460, 540, 200), redx(460, 540, 330, 30), wifi(960, 640, 1.9), redx(960, 540, 330, 30),
            tv(1460, 590, 1.25), redx(1460, 540, 330, 30)]


def _writer(look=(0.2, 0.9)):
    s = 1.45
    f = at_desk(960, s, 640, pose=dict(b=(30, -40, 1), a=(-50, -40, 1)), look=look, mouth='small')
    hx, hy = f.J['b']
    nb = rect(800, 662, 160, 46, '#fff', INK, 6, 4) + rect(960, 662, 160, 46, '#fff', INK, 6, 4)
    nb += ''.join(line(820, yy, 940, yy, 3, LGRAY) + line(980, yy, 1080, yy, 3, LGRAY) for yy in (676, 692))
    return f, nb


@scene(43)
def b43():
    f, nb = _writer()
    hx, hy = f.J['b']
    return [f, desk_for(960), nb, pencil(hx + 14, 640, 0.6, 20), circ(hx, 680, 13, INK, None, 0)]


@scene(44)
def b44():
    f, nb = _writer()
    hx, hy = f.J['b']
    th = thought(1380, 240, 290, 160, tail=(1080, 380))
    scene_ = palm(1230, 330, 0.55, 1) + palm(1530, 330, 0.55, -1) + path('M1270 230 Q1380 300 1490 230', 'none', INK, 8)
    scene_ += path('M1270 230 Q1380 300 1490 230 Q1380 270 1270 230Z', '#D9B98A', INK, 6)
    return [f, desk_for(960), nb, pencil(hx + 14, 640, 0.6, 20), circ(hx, 680, 13, INK, None, 0), th, scene_, redx(1380, 240, 230, 22)]
