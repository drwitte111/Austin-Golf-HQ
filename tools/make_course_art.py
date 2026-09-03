"""Generate the course artwork used behind the menu and the course buttons.

Original stylized illustrations rather than photographs, so nothing in the repo
is someone else's copyrighted image. To use real photos instead, drop your own
files at the same paths and sizes and skip running this.

Everything is drawn at 2x and downsampled, which is how you get clean edges out
of PIL primitives. Output is WebP because these are large flat-colour gradients
that WebP encodes far smaller than JPEG at the same quality.
"""
from PIL import Image, ImageDraw, ImageFilter
import math, os, random

OUT = r"C:\Users\DavidWitte\Documents\GitHub\Austin-Golf-HQ"
SS = 2  # supersample


def lerp(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def vgrad(img, box, top, bottom):
    """Vertical gradient inside box, drawn a scanline at a time."""
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = box
    span = max(1, y1 - y0)
    for y in range(y0, y1):
        d.line([(x0, y), (x1, y)], fill=lerp(top, bottom, (y - y0) / span))


def treeline(d, y, w, base_h, colour, seed, spacing=26):
    """Silhouetted conifers along a baseline."""
    rnd = random.Random(seed)
    x = -spacing
    while x < w + spacing:
        h = base_h * rnd.uniform(0.62, 1.38)
        half = spacing * rnd.uniform(0.42, 0.78)
        d.polygon([(x, y), (x + half, y - h), (x + half * 2, y)], fill=colour)
        x += spacing * rnd.uniform(0.5, 0.95)


def scene(w, h, *, sky_top, sky_low, sun, far, mid, fairway_a, fairway_b,
          rough, sand, water=None, horizon=0.42, seed=7, stripes=True):
    W, H = w * SS, h * SS
    img = Image.new("RGB", (W, H), sky_top)
    d = ImageDraw.Draw(img, "RGBA")
    hz = int(H * horizon)

    # Sky, warming toward the horizon.
    vgrad(img, (0, 0, W, hz), sky_top, sky_low)

    # Low sun haze.
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    r = int(W * 0.34)
    gd.ellipse([int(W * 0.63) - r, hz - int(r * 1.15), int(W * 0.63) + r, hz + int(r * 0.5)],
               fill=sun + (120,))
    img = Image.alpha_composite(img.convert("RGBA"), glow.filter(ImageFilter.GaussianBlur(W // 14))).convert("RGB")
    d = ImageDraw.Draw(img, "RGBA")

    # Ground goes down FIRST. Drawing it after the trees clipped their bases
    # and left a row of floating triangle tips along the horizon.
    vgrad(img, (0, hz, W, H), rough, lerp(rough, (10, 30, 18), 0.45))
    d = ImageDraw.Draw(img, "RGBA")

    # Two treelines standing on the horizon, the nearer one darker for depth.
    treeline(d, hz + 1, W, H * 0.055, far, seed, spacing=int(W * 0.030))
    treeline(d, hz + int(H * 0.014), W, H * 0.048, mid, seed + 1, spacing=int(W * 0.044))

    # Fairway: a trapezoid narrowing toward the horizon.
    top_y = hz + int(H * 0.035)
    d.polygon([(int(W * 0.30), top_y), (int(W * 0.70), top_y),
               (int(W * 1.28), H), (int(W * -0.28), H)], fill=fairway_a)

    if stripes:
        # Mowing stripes, converging with the fairway edges.
        for i in range(9):
            if i % 2:
                continue
            t0, t1 = i / 9, (i + 1) / 9
            d.polygon([
                (int(W * (0.30 + 0.40 * t0)), top_y), (int(W * (0.30 + 0.40 * t1)), top_y),
                (int(W * (-0.28 + 1.56 * t1)), H), (int(W * (-0.28 + 1.56 * t0)), H),
            ], fill=fairway_b)

    if water:
        d.ellipse([int(W * -0.18), int(H * 0.60), int(W * 0.62), int(H * 0.92)], fill=water)
        d.ellipse([int(W * -0.10), int(H * 0.635), int(W * 0.52), int(H * 0.86)],
                  fill=lerp(water, (255, 255, 255), 0.13))

    # Bunkers.
    d.ellipse([int(W * 0.60), int(H * 0.545), int(W * 0.95), int(H * 0.625)], fill=sand)
    d.ellipse([int(W * 0.10), int(H * 0.485), int(W * 0.34), int(H * 0.532)], fill=sand)

    # Putting surface and flag, set back near the horizon.
    gx, gy = int(W * 0.50), int(H * 0.475)
    gw, gh = int(W * 0.20), int(H * 0.038)
    d.ellipse([gx - gw, gy - gh, gx + gw, gy + gh], fill=lerp(fairway_b, (255, 255, 255), 0.22))
    cup = int(W * 0.006)
    d.ellipse([gx - cup, gy - cup // 2, gx + cup, gy + cup // 2], fill=(18, 34, 22))
    stick = max(2, int(W * 0.004))
    top = gy - int(H * 0.075)
    d.rectangle([gx - stick, top, gx + stick, gy], fill=(248, 246, 238))
    d.polygon([(gx - stick, top), (gx - int(W * 0.062), top + int(H * 0.017)),
               (gx - stick, top + int(H * 0.034))], fill=(168, 29, 56))

    return img.resize((w, h), Image.LANCZOS)


def save(img, name, quality):
    p = os.path.join(OUT, name)
    img.save(p, "WEBP", quality=quality, method=6)
    print(f"{name:26} {os.path.getsize(p)/1024:6.1f} KB  {img.size[0]}x{img.size[1]}")


# Menu background - portrait, since this is used almost entirely on a phone
# held vertically. Deliberately dim and low-contrast: menu text sits on top.
save(scene(
    720, 1280,
    sky_top=(16, 40, 62), sky_low=(196, 168, 122), sun=(255, 214, 150),
    far=(24, 54, 40), mid=(18, 42, 31),
    fairway_a=(46, 104, 62), fairway_b=(56, 122, 72),
    rough=(30, 68, 45), sand=(214, 198, 158),
    horizon=0.40, seed=11,
), "bg-course.webp", 72)

# World Tour Golf - the card leans on TPC Sawgrass #17, so: water.
save(scene(
    720, 320,
    sky_top=(20, 58, 84), sky_low=(214, 196, 156), sun=(255, 226, 170),
    far=(22, 56, 42), mid=(16, 44, 33),
    fairway_a=(52, 116, 68), fairway_b=(64, 134, 80),
    rough=(32, 74, 48), sand=(224, 208, 168),
    water=(38, 96, 132), horizon=0.40, seed=3,
), "course-world-tour.webp", 76)

# New Kings North - pines and a warmer, later light, to read differently.
save(scene(
    720, 320,
    sky_top=(38, 44, 78), sky_low=(236, 174, 120), sun=(255, 190, 128),
    far=(28, 48, 36), mid=(19, 36, 28),
    fairway_a=(44, 100, 60), fairway_b=(54, 116, 70),
    rough=(28, 64, 42), sand=(226, 206, 162),
    horizon=0.44, seed=23,
), "course-kings-north.webp", 76)
