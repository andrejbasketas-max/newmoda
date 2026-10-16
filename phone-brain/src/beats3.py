"""Beats 89-132."""
from common import *
from beats1 import _place_phone


@scene(89)
def b89():
    cx, cy, s = 960, 520, 1.4
    o = [line(cx - 130, cy - 40, cx - 280, cy - 260, 12) + line(cx + 130, cy - 40, cx + 300, cy - 180, 12)]
    o.append(pline([(cx - 50, cy + 140), (cx - 150, cy + 260), (cx - 260, cy + 400)], INK, 12))
    o.append(pline([(cx + 50, cy + 140), (cx + 170, cy + 240), (cx + 180, cy + 400)], INK, 12))
    band = path('M-150 -42 Q0 -84 150 -42', 'none', INK, 40) + path('M-150 -42 Q0 -84 150 -42', 'none', RED, 26)
    o.append(brain(cx, cy, s, eyes='happy', mouth='smile', inner=band))
    o.append(shadow(cx, cy + 404, 520))
    return o


def savanna():
    return [sky(), ground_band(760, SAND)]


@scene(90)
def b90():
    o = savanna() + [acacia(1560, 800, 1.1)]
    for x in (700, 1040):
        o += [shadow(x, 904, 200), stand(x, 900, 1.3, pose='walk', hair='curly', necklace=True, look=(1, 0), mouth='small')]
    return o


@scene(91, DUSK)
def b91():
    o = [rect(0, 0, W, 500, '#F4A07F', None, 0), rect(0, 500, W, 260, DUSK2, None, 0), ground_band(760, '#E3C48C')]
    o.append(ell(1220, 820, 330, 170, ORANGE, None, 0, 0.22))
    pose = dict(base='sit', ka=(-82, 8), fa=(32, 24, 1), kb=(82, 8), fb=(-32, 24, -1), a=(-72, 2, 1), b=(72, 2, -1))
    o += [shadow(740, 834, 300), fig(740, 806, 1.4, pose, hair='curly', necklace=True, look=(1, 0.2), mouth='small')]
    o.append(campfire(1220, 840, 1.4))
    return o


@scene(92)
def b92():
    o = savanna() + [sun(1500, 200, 46), acacia(380, 860, 0.9)]
    o.append(path('M620 1090 Q900 960 820 880 Q740 800 1000 720 Q1150 680 1060 640 Q1000 610 1130 760 L1130 760 Z', 'none', 'none', 0))
    o.append(path('M560 1090 Q860 960 790 870 Q720 790 1010 710 Q1110 680 1080 640 L1100 640 Q1140 690 1050 730 Q850 800 920 880 Q990 970 860 1090Z', '#D9B57A', INK, 7))
    o.append(hills(760, '#D7C690', '#C9B87E'))
    o.append(stand(870, 930, 0.75, pose='walk', hair='curly', necklace=True, look=(0.6, -0.4)))
    return o


@scene(93)
def b93():
    o = savanna() + [hills(760), acacia(1650, 800, 0.8)]
    o += [bird(1250, 300, 1.4), bird(1340, 260, 1.1), bird(1400, 330, 1.2)]
    o.append(path(blob_d(560, 880, 220, 110, 8, 1.1), GRAY, INK, SW))
    o.append(fig(560, 790, 1.3, sit_pose(140), hair='curly', necklace=True, look=(1, -0.3), mouth='small'))
    return o


@scene(94)
def b94():
    o = savanna() + [acacia(480, 940, 1.1), acacia(1440, 940, 1.1)]
    o.append(line(476, 740, 640, 780, 6, BROWN) + line(1434, 740, 1280, 780, 6, BROWN))
    o.append(hammock(640, 780, 1280, 780, 90))
    f = fig(1000, 812, 1.2, dict(base='stand', a=(30, 20, -1), b=(-30, 20, 1)), rot=-90, eyes='closed', mouth='smile', hair='curly', necklace=True)
    o.append(f)
    o.append(path('M640 780 Q960 950 1280 780', 'none', INK, 8))
    return o


def laptop(x, y, s=1):
    o = rect(-170, -230, 340, 220, '#555', INK, SW, 14) + rect(-150, -212, 300, 184, SCREEN, None, 0, 6)
    o += poly([(-200, -10), (200, -10), (230, 30), (-230, 30)], LGRAY, INK, SW)
    return G(o, x, y, s)


@scene(95)
def b95():
    o = [couch(960, 980, 760)]
    for x, y, rx in ((1500, 400, 260), (430, 640, 220), (560, 300, 150), (1480, 760, 170)):
        o.append(glow(x, y, rx, rx * 0.8, SCREEN, 0.45))
    o.append(fig(960, 872, 1.5, sit_pose(110), eyes='wide', mouth='flat', look=(0.3, -0.2)))
    o += [tv(1500, 420, 1.25), laptop(430, 720, 0.9), phone(560, 300, 90, rot=-12), phone(1480, 760, 200, h=270, rot=10)]
    return o


@scene(96)
def b96():
    return [calendar(380, 220, 680, 660, crossed=14), txt(1460, 610, 'WEEK 2', 170)]


@scene(97)
def b97():
    f = stand(900, GROUND, 1.55, pose=dict(base='stand', b=(92, -206, 1), a=(-60, -150, -1)), hair='messy', glasses=True, coat=True,
              eyes='wide', brows='raised', mouth='big')
    hx, hy = f.J['b']
    return [shadow(900, GROUND + 4, 240), f, paper(hx + 40, hy - 90, 200, 260, 8, 6), sparkle(hx + 220, hy - 160, 0.9),
            sparkle(hx - 420, hy - 60, 0.7), sparkle(hx + 230, hy + 60, 0.6)]


@scene(98)
def b98():
    o = [header('2025')]
    for i, (x, c) in enumerate(zip((480, 800, 1120, 1440), (RED, BLUE, GREEN, YELLOW))):
        f = stand(x, GROUND, 1.25, pose=dict(base='stand', b=(58, -66, 1)), glasses=True, hat=c, mouth='small', look=(0.2, 0))
        hx, hy = f.J['b']
        o += [shadow(x, GROUND + 4, 200), f, clipboard(hx + 26, hy - 26, 0.85, 8)]
    return o


@scene(99)
def b99():
    o = [rect(-20, 120, W + 40, 1000, WOOD, INK, SW)]
    for y in (260, 420, 640, 860, 1000):
        o.append(path(f'M-10 {y} Q600 {y - 30} 1100 {y + 10} T1930 {y}', 'none', WOOD_D, 5, 0.6))
    o.append(ell(960, 820, 470, 50, INK, None, 0, 0.12))
    o.append(journal(960, 560, 1.35))
    return o


@scene(100)
def b100():
    return [phone(960, 470, 300, content=wifi(0, 30, 1.1)), padlock(960, 720, 1.6)]


@scene(101)
def b101():
    f = stand(620, GROUND, 1.5, pose=dict(base='stand', b=(62, -76, 1)), look=(0.6, 0.2), brows='tense', mouth='small')
    hx, hy = f.J['b']
    return [shadow(620, GROUND + 4, 230), calendar(1060, 260, 520, 560, crossed=14), f,
            phone(hx + 10, hy - 50, 80, rot=-6, content=padlock(0, 10, 0.25))]


@scene(102)
def b102():
    return [phone(960, 545, 480, h=900, content=call_icon(-110, -290, 1.0) + text_icon(40, -290, 1.0))]


@scene(103)
def b103():
    o = [txt(960, 230, '91%', 220)]
    for i, x in enumerate((330, 580, 830, 1090, 1340, 1590)):
        f = stand(x, 1000, 1.0, eyes='happy', mouth='smile',
                  hair=['short', None, 'curly', 'cap', 'shoulder', None][i], hair_c=[SKIN_HAIR['brown'], INK, INK, SKIN_HAIR['red'], INK, INK][i])
        hx, hy = f.J['head']
        o += [shadow(x, 1004, 150), f, arrow(hx, hy - 70, hx, hy - 170, 14, GREEN, 40)]
    return o


@scene(104)
def b104():
    return [heart(480, 560, 3.2), smiley(960, 540, 160), target(1440, 540, 165)]


@scene(105)
def b105():
    f = stand(520, GROUND, 1.5, pose=dict(base='stand', a=(-30, -40, 1), b=(30, -40, -1)), eyes='narrow', brows='tense', mouth='flat', look=(1, 0))
    o = [shadow(520, GROUND + 4, 230), f, target(1420, 540, 210)]
    o.append(line(1060, 540, 1420, 540, 12) + poly([(1060, 540), (1020, 510), (1000, 510), (1030, 540), (1000, 570), (1020, 570)], RED, INK, 6))
    o.append(motion(990, 540, 0, 3, 120, 36, 7))
    o.append(burst(1420, 540, 40, 70, 8, 6, INK, False))
    return o


@scene(106)
def b106():
    o = [clock(760, 560, 270, -40, 110)]
    o.append(curved_arrow(760, 560, 360, -30, -150, 14, INK, 44))
    o.append(curved_arrow(760, 560, 360, 150, 30, 14, INK, 44))
    o.append(txt(1490, 600, '-10 YEARS', 140))
    return o


@scene(107)
def b107():
    o = [line(960, 0, 960, H, 14)]
    o += [shadow(480, GROUND + 4, 220), stand(480, GROUND, 1.5, pose=dict(base='stand', neck=(12, -124)), hair='side', hair_c=SKIN_HAIR['gray'],
                                                 eyes='tired', brows='tired', mouth='frown')]
    o += [shadow(1440, GROUND + 4, 220), stand(1440, GROUND, 1.5, hair='short', eyes='bright', brows='raised', mouth='smile')]
    return o


@scene(108)
def b108():
    o = [stairs(260, 1000, 6, 230, 110)]
    s = 1.2
    sx, sy = 260 + 2 * 230 + 120, 1000 - 3 * 110
    f = fig(sx, sy - 150 * s, s, dict(base='walk', fa=(-30, 150, 1), fb=(80, 150 - 110 / s, -1)), eyes='happy', mouth='smile', look=(1, -0.2))
    return o + [f, arrow(1300, 380, 1560, 250, 10, INK, 34)]


@scene(109, NIGHT)
def b109():
    o = [rect(-20, 820, W + 40, 300, NIGHT2, INK, SW)]
    o.append(window(1380, 120, 360, 300, '#1F2850', NIGHT2) + moon(1560, 270, 60, '#F7F2D8'))
    o.append(rect(230, 640, 200, 200, WOOD, INK, SW, 8) + line(250, 720, 410, 720, 6))
    o.append(phone(330, 625, 100, rot=86, down=True))
    o.append(rect(520, 470, 40, 380, WOOD_D, INK, SW, 8) + rect(540, 660, 900, 130, WOOD, INK, SW, 10))
    o.append(ell(690, 650, 120, 50, '#fff', INK, SW))
    f = fig(940, 650, 1.25, dict(base='stand'), rot=-90, eyes='closed', mouth='small')
    o.append(f)
    o.append(path('M790 610 Q1100 560 1420 610 L1440 700 L780 700Z', BLUE, INK, SW))
    o.append(txt(820, 470, 'Z', 70, '#F7F2D8') + txt(880, 410, 'Z', 56, '#F7F2D8') + txt(930, 360, 'Z', 44, '#F7F2D8'))
    return o


@scene(110)
def b110():
    o = [rect(860, 620, 200, 24, WOOD, INK, SW, 6), rect(948, 644, 24, 260, WOOD_D, INK, 7), rect(880, 900, 160, 18, WOOD_D, INK, 7, 6)]
    side = dict(base='sit', ka=(76, 4), fa=(80, 112, 1), kb=(70, 10), fb=(74, 112, 1), a=(80, -30, 1), b=(64, -40, 1))
    for x, flip in ((600, False), (1320, True)):
        o.append(G(rect(-40, -10, 120, 20, WOOD, INK, 7, 4) + rect(-50, -230, 20, 360, WOOD_D, INK, 7, 4), x, 760, 1, sx=-1 if flip else 1, sy=1))
        o.append(fig(x, 744, 1.4, side, flip=flip, eyes='happy', mouth='big' if flip else 'smile', look=(0.8, 0),
                     hair='short' if flip else 'shoulder', hair_c=SKIN_HAIR['brown']))
    o.append(speech(700, 240, 200, 110, (790, 380)) + speech(1030, 160, 220, 110, (1120, 360)) + speech(780, 80, 170, 90, (850, 200)))
    for x, y, w_ in ((740, 285, 120), (1070, 205, 140), (815, 120, 100)):
        o.append(line(x, y, x + w_, y, 6, LGRAY) + line(x, y + 26, x + w_ * 0.7, y + 26, 6, LGRAY))
    return o


@scene(111, '#F49A86')
def b111():
    o = [rect(0, 330, W, 250, DUSK, None, 0), rect(0, 580, W, 260, DUSK2, None, 0)]
    o.append(circ(1460, 830, 110, '#FCD580', INK, SW))
    o.append(ground_band(820, '#E3C48C'))
    o.append(stand(760, 1050, 1.85, look=(0.4, -1), mouth='small', eyes='dot'))
    return o


@scene(112)
def b112():
    o = [shadow(420, GROUND + 4, 200), stand(420, GROUND, 1.3, look=(1, 0), mouth='small', brows='raised')]
    f1 = stand(1150, GROUND, 1.3, pose=dict(base='stand', b=(110, -120, 1)), eyes='happy', mouth='big', hair='curly')
    f2 = stand(1580, GROUND, 1.3, pose=dict(base='stand', a=(-104, -130, -1)), mouth='smile', look=(-1, 0), hair='shoulder', hair_c=SKIN_HAIR['red'])
    o += [shadow(1150, GROUND + 4, 200), shadow(1580, GROUND + 4, 200), f1, f2]
    o += [open_fingers(*f1.J['b'], -20, 1.2), open_fingers(*f2.J['a'], 200, 1.2)]
    o.append(speech(1160, 230, 160, 90, (1180, 380)) + speech(1420, 260, 160, 90, (1520, 400)))
    o.append(line(1190, 275, 1290, 275, 6, LGRAY) + line(1450, 305, 1550, 305, 6, LGRAY))
    return o


@scene(113)
def b113():
    inner = ''
    for (x, y, c, r) in ((-100, -40, YELLOW, -12), (-30, -76, '#9FD8F5', 8), (55, -64, '#FFB3C1', -6), (108, -10, '#B5E48C', 14),
                         (-112, 40, '#FFC37A', 10), (100, 60, YELLOW, -10), (-10, -40, '#C9A7F0', 4)):
        inner += sticky(x, y, 0.62, c, r)
    return [brain(960, 560, 1.75, eyes='happy', mouth='smile', inner=inner)]


@scene(114)
def b114():
    inner = rect(-110, -104, 220, 96, CREAM, INK, 7, 6) + line(-110, -70, 110, -70, 6) + line(-110, -38, 110, -38, 6)
    for x in (-92, -64, 40):
        inner += rect(x, -94, 22, 22, CARD, INK, 4, 2)
    for x in (-94, -40, -12, 60):
        inner += rect(x, -62, 22, 22, CARD, INK, 4, 2)
    inner += rect(70, -124, 26, 26, CARD, INK, 4, 2) + motion(83, -128, 90, 2, 16, 14, 3)
    return [brain(960, 560, 2.1, eyes='happy', mouth='smile', inner=inner)]


@scene(115)
def b115():
    o = [poly([(870, 330), (840, 230), (910, 310)], RED, INK, 8) + poly([(1050, 330), (1080, 230), (1010, 310)], RED, INK, 8)]
    o.append(phone(960, 590, 260))
    o.append(redx(960, 580, 520, 34))
    return o


@scene(116)
def b116():
    f = stand(700, GROUND, 1.5, pose=dict(base='stand', b=(82, -140, 1)), eyes='happy', mouth='big', look=(1, -0.2))
    g = fig(0, 95, 0.62, dict(base='stand', b=(70, -210, 1)), hair='curly', hair_c=SKIN_HAIR['gray'], eyes='happy', mouth='smile', glasses=True)
    o = [shadow(700, GROUND + 4, 230), f, phone(930, 520, 220, content=g)]
    o += [heart(1150, 300, 0.7), heart(1240, 400, 0.5), heart(1110, 190, 0.45)]
    return o


@scene(117)
def b117():
    sos = circ(0, -40, 95, RED, INK, 8) + txt(0, -16, 'SOS', 70, '#fff')
    return [shadow(1360, 940, 640), ambulance(1360, 940, 1.15), phone(700, 560, 270, content=sos)]


@scene(118)
def b118():
    o = [phone_in_hand(960, 760, 230, thumb='rest')]
    cols = [RED, BLUE, GREEN, YELLOW, PURPLE, ORANGE, BLUE, RED]
    for i in range(8):
        x, y = 960 + math.sin(i * 0.9) * 40 + i * 6, 520 - i * 58
        o.append(G(rect(-110, -24, 220, 48, cols[i], INK, 7, 6) + line(-90, 0, 90, 0, 5, '#fff', op=0.6), x, y, 1, (i % 3 - 1) * 6))
    o.append(motion(830, 300, -90, 2, 60, 30, 6) + motion(1110, 260, -90, 2, 60, 30, 6))
    return o


@scene(119)
def b119():
    o = [sky(), rect(-20, 540, W + 40, 260, '#5DA9DF', INK, SW), ground_band(780, SAND)]
    for x in (1200, 1450, 1700):
        o.append(path(f'M{x} 620 q30 -20 60 0 t60 0', 'none', '#fff', 6))
    f = stand(700, 980, 1.45, pose=dict(base='stand', neck=(-18, -132), b=(-60, -248, -1), a=(118, -100, 1), fa=(-40, 150, 1), fb=(52, 148, -1)),
              eyes='dot', brows='tense', mouth='grimace', look=(1, 0))
    hx, hy = f.J['b']
    o += [shadow(700, 984, 230), f, phone(hx - 10, hy - 40, 70, rot=-30), redx(960, 560, 820, 46)]
    return o


@scene(120)
def b120():
    f = fig(960, 1090, 2.7, dict(base='stand', neck=(12, -134), b=(80, -150, 1)), brows='one', mouth='small', tilt=-6)
    hx, hy = f.J['b']
    return [f, tube(hx, hy, hx + 4, hy - 90, 22, INK, INK, 0)]


@scene(121)
def b121():
    return [brain(760, 540, 1.5, eyes='happy', mouth='smile'), check(1380, 540, 320, GREEN)]


@scene(122)
def b122():
    f = at_desk(960, 1.45, 640, pose=dict(a=(-50, -60, 1), b=(76, -60, 1)), brows='tense', mouth='wavy', look=(0.4, 0.6))
    hx, hy = f.J['b']
    o = [f, desk_for(960), phone(1160, 680, 120, rot=84, down=True)]
    o.append(arcs(hx + 6, 676, 34, 200, 340, 2, 18, 5))
    for key, sg in (('ka', -1), ('kb', 1)):
        kx, ky = f.J[key]
        o.append(line(kx + sg * 40, ky - 10, kx + sg * 40, ky + 40, 6) + line(kx + sg * 62, ky, kx + sg * 62, ky + 30, 6))
    return o


@scene(123)
def b123():
    o = [mirror(1300, 500, 210, 320)]
    refl = fig(1300, 640, 1.25, 'stand', flip=True, eyes='closed', mouth='smile', look=(-0.5, 0))
    o.append(clip_group('mir', '<ellipse cx="1300" cy="500" rx="208" ry="318"/>', refl + line(1120, 330, 1180, 260, 8, '#fff', op=0.7)))
    o += [shadow(700, GROUND + 4, 230), stand(700, GROUND, 1.5, look=(1, 0), brows='worried', mouth='flat')]
    return o


@scene(124)
def b124():
    cx, cy, s = 720, 560, 1.35
    rx, ry = cx + 150 * s + 10, cy + 20
    o = [path(f'M1120 600 Q1500 760 1960 640', 'none', INK, 8)]
    o.append(circ(rx, ry, 22, 'none', DGRAY, 9))
    o.append(brain(cx, cy, s, eyes='happy', mouth='smile'))
    o.append(rect(1050, 580, 70, 40, LGRAY, INK, 7, 10))
    o.append(mitt(1150, 520, 0.9, 150, arm=420))
    o.append(sparkle(1010, 500, 0.6) + sparkle(1040, 680, 0.45))
    return o


@scene(125, CREAM)
def b125():
    inner = pigeon(960, 700, 1.1, eyes='sad', head=(48, -112))
    return [shadow(990, 935, 760), rect(620, 790, 760, 140, WOOD_D, INK, SW, 4), skinner_box(660, 330, 600, 460, inner)]


@scene(126, CREAM)
def b126():
    o = []
    for i in range(7):
        a = math.radians(-150 + i * 20)
        o.append(line(960 + 200 * math.cos(a), 470 + 120 * math.sin(a), 960 + 520 * math.cos(a), 470 + 300 * math.sin(a), 9, '#F2C94C'))
    o.append(poly([(560, 600), (700, 470), (1500, 470), (1360, 600)], CREAM_D, INK, SW))
    o.append(pigeon(990, 640, 1.0, eyes='wide', head=(30, -140), hrot=-30))
    o.append(rect(560, 600, 800, 400, WOOD, INK, SW))
    o.append(poly([(1360, 600), (1500, 470), (1500, 870), (1360, 1000)], WOOD_D, INK, SW))
    o.append(G(rect(-420, -24, 840, 48, WOOD, INK, SW, 6) + rect(-420, 24, 840, 30, WOOD_D, INK, SW, 4), 1150, 260, 1, -14))
    o.append(mitt(1420, 160, 1.3, 160, arm=600))
    return o


@scene(127)
def b127():
    o = []
    for i in range(9):
        a = math.radians(-170 + i * 20)
        o.append(line(960 + 380 * math.cos(a), 560 + 80 * math.sin(a), 960 + 700 * math.cos(a), 560 + 340 * math.sin(a), 9, '#F2C94C'))
    o.append(poly([(560, 560), (660, 480), (1460, 480), (1360, 560)], '#8D6A3E', INK, SW))
    o.append(poly([(560, 560), (760, 560), (840, 380), (620, 330)], CARD_D, INK, SW))
    o.append(poly([(1360, 560), (1160, 560), (1080, 380), (1300, 330)], CARD_D, INK, SW))
    s = 1.5
    o.append(fig(960, 700, s, dict(base='stand', a=(-84, -190, -1), b=(84, -190, 1)), eyes='bright', mouth='big', brows='raised'))
    o.append(rect(560, 560, 800, 460, CARD, INK, SW, 4) + line(960, 566, 960, 700, 6, CARD_D))
    o.append(poly([(1360, 560), (1460, 480), (1460, 940), (1360, 1020)], CARD_D, INK, SW))
    return o


@scene(128)
def b128():
    c = rect(-400, -200, 800, 330, '#3A3A3A', INK, 6, 12) + poly([(-40, -90), (-40, 10), (50, -40)], '#fff', INK, 5)
    c += line(-400, 175, 400, 175, 14, LGRAY) + line(-400, 175, 330, 175, 14, RED) + circ(330, 175, 18, RED, INK, 5)
    return [phone(960, 540, 520, h=980, rot=90, content=G(c, rot=-90))]


@scene(129)
def b129():
    w = 330
    h = w * 1.9
    return [phone_in_hand(960, 560, w, thumb='hover', content=circ(w * 0.22, -h * 0.16, 30, RED, INK, 7))]


@scene(130)
def b130():
    o = []
    pts_ = []
    for i in range(15):
        t = i * 0.62
        r = 170 + i * 32
        pts_.append((960 + r * math.cos(t - 1.2), 540 + r * 0.62 * math.sin(t - 1.2)))
    o.append(pline(pts_, INK, 5, '14 14'))
    o.append(phone(960, 540, 200))
    for i, (x, y) in enumerate(pts_[1:], 1):
        sc = 0.45 + i * 0.04
        o.append(thumb_tile(x, y, sc, (i * 17) % 30 - 15, [SCREEN, '#FFD6A5', '#B5E48C', '#FFB3C1'][i % 4]) if i % 3 else bell(x, y, sc * 0.6, YELLOW, dot=True))
    return o


@scene(131)
def b131():
    return _place_phone('left')


@scene(132, '#F1E3D3')
def b132():
    o = [rect(-20, 900, W + 40, 200, '#E2CFB8', INK, SW)]
    o.append(window(950, 130, 760, 520, DUSK2, '#fff'))
    o.append(f'<clipPath id="dw"><rect x="950" y="130" width="760" height="520"/></clipPath>')
    o.append('<g clip-path="url(#dw)">' + rect(950, 130, 760, 200, '#F4A07F', None, 0) + circ(1500, 560, 90, '#FCD580', INK, 7) +
             hills(600, '#C99A8A', '#B98C80') + '</g>')
    o.append(line(1330, 130, 1330, 650, 12, '#fff') + line(950, 390, 1710, 390, 12, '#fff') + rect(950, 130, 760, 520, 'none', INK, 7))
    o.append(rect(920, 650, 820, 40, '#fff', INK, SW, 6))
    o.append(phone(1560, 640, 100, rot=86, down=True))
    o.append(poly([(950, 900), (1710, 900), (1500, 1080), (700, 1080)], DUSK, None, 0, 0.35))
    o.append(rect(600, 760, 220, 26, WOOD, INK, SW, 6) + rect(620, 786, 22, 120, WOOD_D, INK, 7) + rect(778, 786, 22, 120, WOOD_D, INK, 7))
    o.append(fig(710, 752, 1.45, sit_pose((900 - 752) / 1.45), eyes='closed', mouth='smile', tilt=4))
    return o
