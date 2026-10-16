"""Build all beats: python3 build.py [beat numbers...]  ->  ../svg/*.svg and ../png/*.png"""
import os, sys, subprocess, importlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import SCENES
from lib import doc
for m in ('beats1', 'beats2', 'beats3'):
    try:
        importlib.import_module(m)
    except ModuleNotFoundError as e:
        if e.name != m:
            raise

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SVG = os.path.join(ROOT, 'svg')
PNG = os.path.join(ROOT, 'png')
os.makedirs(SVG, exist_ok=True)
want = [int(a) for a in sys.argv[1:]] or sorted(SCENES)
for n in want:
    fn, bg = SCENES[n]
    with open(os.path.join(SVG, f'beat_{n:03d}.svg'), 'w') as fh:
        fh.write(doc(fn(), bg))
flt = '^beat_(' + '|'.join(f'{n:03d}' for n in want) + r')\.svg$'
subprocess.run(['node', os.path.join(ROOT, 'src', 'render.mjs'), SVG, PNG, flt], check=True)
print('built', len(want))
