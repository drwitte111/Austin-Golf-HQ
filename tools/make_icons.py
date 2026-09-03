"""Generate the Austin Golf HQ PWA icon set.

Draws a flagstick on a green at 4x then downsamples, which is the cheapest way
to get clean anti-aliased edges out of PIL. Maskable variants keep the artwork
inside the inner ~62% so Android can crop them to any shape without clipping.
"""
from PIL import Image, ImageDraw
import os

OUT = r"C:\Users\DavidWitte\Documents\GitHub\Austin-Golf-HQ"

BG      = (20, 48, 31)     # --fairway
GREEN   = (46, 125, 79)    # --green
LIGHT   = (76, 175, 109)   # --light
CREAM   = (243, 239, 226)  # --cream
RED     = (168, 29, 56)    # --par-red
SAND    = (217, 200, 154)  # --sand

S = 4  # supersample factor


def draw_icon(size, inset=0.0, rounded=False):
    """inset: fraction of the canvas to keep clear around the artwork."""
    c = size * S
    img = Image.new("RGBA", (c, c), BG + (255,))
    d = ImageDraw.Draw(img)

    if rounded:
        # Plain square; the launcher applies its own mask.
        pass

    # Artwork box, shrunk for maskable icons.
    pad = c * inset
    x0, y0, x1, y1 = pad, pad, c - pad, c - pad
    w = x1 - x0

    # Rolling green: a wide ellipse cropped by the bottom of the art box.
    green_top = y0 + w * 0.60
    d.ellipse([x0 - w * 0.30, green_top, x1 + w * 0.30, y0 + w * 1.55],
              fill=GREEN + (255,))
    # A lighter band to suggest a putting surface.
    d.ellipse([x0 + w * 0.06, green_top + w * 0.06, x1 - w * 0.06, y0 + w * 1.05],
              fill=LIGHT + (255,))

    # The cup.
    cup_cx, cup_cy = x0 + w * 0.56, green_top + w * 0.135
    cup_rx, cup_ry = w * 0.075, w * 0.030
    d.ellipse([cup_cx - cup_rx, cup_cy - cup_ry, cup_cx + cup_rx, cup_cy + cup_ry],
              fill=(12, 30, 19, 255))

    # Flagstick.
    stick_w = max(2, int(w * 0.030))
    stick_top = y0 + w * 0.135
    d.rectangle([cup_cx - stick_w / 2, stick_top, cup_cx + stick_w / 2, cup_cy],
                fill=CREAM + (255,))

    # Pennant flying left off the stick.
    d.polygon([
        (cup_cx - stick_w / 2, stick_top),
        (cup_cx - w * 0.32, stick_top + w * 0.085),
        (cup_cx - stick_w / 2, stick_top + w * 0.175),
    ], fill=RED + (255,))

    # Ball sitting on the green, left of the cup.
    ball_r = w * 0.072
    ball_cx, ball_cy = x0 + w * 0.235, green_top + w * 0.20
    d.ellipse([ball_cx - ball_r, ball_cy - ball_r, ball_cx + ball_r, ball_cy + ball_r],
              fill=CREAM + (255,))

    return img.resize((size, size), Image.LANCZOS)


def save(img, name):
    path = os.path.join(OUT, name)
    img.convert("RGB").save(path, "PNG", optimize=True)
    print(name, os.path.getsize(path), "bytes")


save(draw_icon(192), "icon-192.png")
save(draw_icon(512), "icon-512.png")
save(draw_icon(180), "icon-180.png")
save(draw_icon(32),  "favicon-32.png")
# Maskable: artwork pulled well inside so any crop shape still works.
save(draw_icon(192, inset=0.19), "icon-192-maskable.png")
save(draw_icon(512, inset=0.19), "icon-512-maskable.png")
