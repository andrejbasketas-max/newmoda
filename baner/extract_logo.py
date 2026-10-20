# Iseca ikonicu i natpis iz originalnog logoa i uklanja belu pozadinu (color-to-alpha).
import numpy as np
from PIL import Image

src = np.asarray(Image.open("logoforge-original.jpg").convert("RGB")).astype(np.float32) / 255


def to_alpha(rgb):
    # alpha = koliko piksel odstupa od bele; boja se "odmnozava" od bele
    alpha = np.clip((1 - rgb.min(axis=2)) * 1.08, 0, 1)
    alpha[alpha < 0.04] = 0
    safe = np.where(alpha > 0, alpha, 1)[..., None]
    col = np.clip((rgb - (1 - alpha[..., None])) / safe, 0, 1)
    return np.dstack([col, alpha])


def crop(rgba):
    ys, xs = np.where(rgba[..., 3] > 0.02)
    return rgba[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def save(rgba, path):
    Image.fromarray((rgba * 255).round().astype(np.uint8), "RGBA").save(path)


icon = crop(to_alpha(src[300:672, 430:810]))
save(icon, "logo-icon.png")

word = crop(to_alpha(src[725:900, 160:1110]))
save(word, "logo-wordmark.png")

# Varijanta za tamnu pozadinu: tamni, neobojeni pikseli ("Forge") postaju beli
dark = word.copy()
rgb = dark[..., :3]
sat = rgb.max(axis=2) - rgb.min(axis=2)
mask = (rgb.max(axis=2) < 0.35) & (sat < 0.18)
rgb[mask] = 1.0
save(dark, "logo-wordmark-light.png")
print(icon.shape, word.shape)
