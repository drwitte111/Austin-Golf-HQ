"""Generate the menu tile artwork for Live Scorecard and Stats.

Original illustrations rather than stock photography, so nothing here belongs to
anyone else, and drawn from the app's own palette so the tiles sit alongside the
course photos rather than fighting them.

Both are designed to read under a heavy left-to-right scrim: bold shapes, high
contrast, nothing important in the left third where the label sits.

    python tools/make_tile_art.py
"""
from PIL import Image, ImageDraw
import os

OUT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H, SS = 720, 320, 3          # supersample, then downsample for clean edges

FAIRWAY = (20, 48, 31)
GREEN   = (46, 125, 79)
LIGHT   = (76, 175, 109)
PAPER   = (247, 244, 234)
INK     = (26, 26, 26)
GOLD    = (210, 169, 63)
RED     = (168, 29, 56)
SAND    = (217, 200, 154)


def canvas():
    img = Image.new("RGB", (W * SS, H * SS), FAIRWAY)
    return img, ImageDraw.Draw(img, "RGBA")


def save(img, name, quality=80):
    path = os.path.join(OUT, name)
    img.resize((W, H), Image.LANCZOS).save(path, "WEBP", quality=quality, method=6)
    print(f"{name:22} {os.path.getsize(path)/1024:6.1f} KB  {W}x{H}")


def scorecard_tile():
    """A scorecard sheet, angled, echoing the card the app already draws."""
    img, _ = canvas()

    # Build the sheet on its own transparent layer so it can be rotated whole.
    sw, sh = int(W * SS * 0.92), int(H * SS * 0.95)
    sheet = Image.new("RGBA", (sw, sh), (0, 0, 0, 0))
    d = ImageDraw.Draw(sheet, "RGBA")

    d.rectangle([0, 0, sw, sh], fill=PAPER + (255,), outline=INK + (255,), width=6 * SS)

    cols, rows = 11, 6
    cw = sw / cols
    top = sh * 0.14
    rh = (sh - top) / rows

    # Header band, then the tee/par/handicap rows in the printed card's colours.
    d.rectangle([0, 0, sw, top], fill=INK + (255,))
    band = {2: GOLD, 4: RED}
    for r in range(rows):
        y0 = top + r * rh
        if r in band:
            d.rectangle([0, y0, sw, y0 + rh], fill=band[r] + (255,))

    for c in range(1, cols):
        x = c * cw
        d.line([(x, 0), (x, sh)], fill=(150, 145, 132, 255), width=2 * SS)
    for r in range(rows + 1):
        y = top + r * rh
        d.line([(0, y), (sw, y)], fill=(150, 145, 132, 255), width=2 * SS)

    # Numbers sit inside their own bands: holes in the header, yardages on the
    # gold row, par on the red one. Anything else reads as a misprint.
    def text_row(values, y, colour, size):
        for i, value in enumerate(values):
            d.text(((i + 1) * cw + cw / 2, y), value,
                   fill=colour + (255,), anchor="mm", font_size=int(size))

    holes = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "OUT"]
    text_row(holes, top / 2, PAPER, top * 0.46)
    text_row(["360", "531", "132", "401", "542", "344", "170", "391", "354", "3026"],
             top + 2 * rh + rh / 2, INK, rh * 0.44)
    text_row(["4", "5", "3", "4", "5", "4", "3", "4", "4", "36"],
             top + 4 * rh + rh / 2, PAPER, rh * 0.50)

    sheet = sheet.rotate(-7, resample=Image.BICUBIC, expand=True)
    img.paste(sheet, (int(W * SS * 0.10), int(-H * SS * 0.06)), sheet)
    return img


def stats_tile():
    """A rising leaderboard of bars with a flag over the leader."""
    img, d = canvas()

    base = H * SS * 0.86
    n = 9
    gap = W * SS * 0.012
    bw = (W * SS - gap * (n + 1)) / n
    heights = [0.30, 0.44, 0.38, 0.58, 0.50, 0.72, 0.64, 0.88, 0.80]

    for i, frac in enumerate(heights):
        x0 = gap + i * (bw + gap)
        top = base - H * SS * frac * 0.78
        # Tallest bars pick up the gold so the eye lands on the leader.
        colour = GOLD if frac >= 0.85 else LIGHT if frac >= 0.6 else GREEN
        d.rounded_rectangle([x0, top, x0 + bw, base],
                            radius=int(bw * 0.14), fill=colour + (255,))

    d.line([(0, base), (W * SS, base)], fill=SAND + (170,), width=3 * SS)

    # Flagstick planted on the leader.
    lead = heights.index(max(heights))
    cx = gap + lead * (bw + gap) + bw / 2
    top = base - H * SS * max(heights) * 0.78
    stick_top = top - H * SS * 0.20
    d.rectangle([cx - 2 * SS, stick_top, cx + 2 * SS, top], fill=PAPER + (255,))
    d.polygon([(cx - 2 * SS, stick_top),
               (cx - W * SS * 0.075, stick_top + H * SS * 0.055),
               (cx - 2 * SS, stick_top + H * SS * 0.11)], fill=RED + (255,))
    return img


save(scorecard_tile(), "tile-scorecard.webp")
save(stats_tile(), "tile-stats.webp")
