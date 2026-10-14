# Contact sheet of preview frames: python3 sheet.py out.jpg frame...
import sys
from PIL import Image
out, frames = sys.argv[1], sys.argv[2:]
cols = min(4, len(frames)); rows = (len(frames) + cols - 1) // cols
S = Image.new('RGB', (cols * 360, rows * 640))
for i, f in enumerate(frames):
    S.paste(Image.open(f'preview/film-{f}.jpg').resize((360, 640)), ((i % cols) * 360, (i // cols) * 640))
S.save(out, quality=88)
