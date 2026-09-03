"""Turn full-size course photographs into the WebP files the app ships.

Usage:  python tools/prepare_photos.py <source-dir>

Expects these files in <source-dir>:
    main-bg.jpg      -> bg-course.webp          (portrait, menu/login backdrop)
    world-tour.jpg   -> course-world-tour.webp  (wide tile)
    kings-north.png  -> course-kings-north.webp (wide tile)

Originals are not committed: they are multi-megabyte and only the derived
files are ever served. Re-run this against new sources to replace the artwork.

Everything is centre-cropped to the target aspect and resized down, so the
phone never downloads pixels it cannot show, and EXIF is dropped on save.
"""
from PIL import Image, ImageOps
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def render(src, dest, w, h, quality):
    im = Image.open(src)
    im = ImageOps.exif_transpose(im)   # honour camera rotation before cropping
    im = im.convert("RGB")
    # Centre-crop to the target aspect, then scale. ImageOps.fit does both and
    # picks the crop box for us.
    im = ImageOps.fit(im, (w, h), method=Image.LANCZOS, centering=(0.5, 0.5))
    out = os.path.join(REPO, dest)
    im.save(out, "WEBP", quality=quality, method=6)
    print(f"{dest:26} {os.path.getsize(out)/1024:6.1f} KB  {w}x{h}")


def main(src_dir):
    # Portrait: this backs the menu on a phone held upright, so it is cropped
    # tall rather than letting CSS cover crop an arbitrary slice out of a
    # landscape frame.
    render(os.path.join(src_dir, "main-bg.jpg"), "bg-course.webp", 720, 960, 70)

    # Wide tiles behind the two course buttons.
    render(os.path.join(src_dir, "world-tour.jpg"), "course-world-tour.webp", 720, 320, 76)
    render(os.path.join(src_dir, "kings-north.png"), "course-kings-north.webp", 720, 320, 76)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("usage: python tools/prepare_photos.py <source-dir>")
    main(sys.argv[1])
