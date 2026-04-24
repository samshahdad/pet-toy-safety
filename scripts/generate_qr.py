#!/usr/bin/env python3
"""Generate branded QR codes for 3DPawsnToys pet-toy safety page.

Produces three files in qr/:
  - qr_code.png         High-resolution PNG with logo embedded (print-ready, ~2000x2000)
  - qr_code_plain.png   High-resolution PNG without logo (maximum scannability, fallback)
  - qr_code.svg         Scalable vector QR (no logo) for clean print at any size

The branded PNG uses high error-correction (H, ~30%) so embedding the logo
in the centre does not break scanning.
"""
from pathlib import Path

import qrcode
from qrcode.constants import ERROR_CORRECT_H
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers.pil import RoundedModuleDrawer
from qrcode.image.styles.colormasks import SolidFillColorMask
from qrcode.image.svg import SvgPathImage
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
OUT = ROOT / "qr"
OUT.mkdir(exist_ok=True)

URL = "https://samshahdad.github.io/pet-toy-safety/"
LOGO_PATH = ASSETS / "logo.png"

# Brand colours (matching logo gradient)
BRAND_DARK = (31, 78, 161)      # deep blue from logo
BACKGROUND = (255, 255, 255)    # white

TARGET_SIZE_PX = 2000           # final pixel size for branded + plain PNGs


def build_qr():
    qr = qrcode.QRCode(
        version=None,
        error_correction=ERROR_CORRECT_H,
        box_size=20,
        border=4,
    )
    qr.add_data(URL)
    qr.make(fit=True)
    return qr


def prepare_logo(qr_size_px: int) -> Image.Image:
    logo = Image.open(LOGO_PATH).convert("RGBA")

    logo_target = int(qr_size_px * 0.20)
    logo.thumbnail((logo_target, logo_target), Image.LANCZOS)

    pad = int(logo_target * 0.12)
    bg_size = (logo.size[0] + pad * 2, logo.size[1] + pad * 2)
    bg = Image.new("RGBA", bg_size, (255, 255, 255, 255))
    bg.paste(logo, (pad, pad), logo)
    return bg


def generate_branded_png():
    qr = build_qr()

    img = qr.make_image(
        image_factory=StyledPilImage,
        module_drawer=RoundedModuleDrawer(radius_ratio=1.0),
        color_mask=SolidFillColorMask(front_color=BRAND_DARK, back_color=BACKGROUND),
    ).convert("RGBA")

    img = img.resize((TARGET_SIZE_PX, TARGET_SIZE_PX), Image.LANCZOS)

    logo = prepare_logo(TARGET_SIZE_PX)
    pos = ((img.size[0] - logo.size[0]) // 2,
           (img.size[1] - logo.size[1]) // 2)
    img.paste(logo, pos, logo)

    out = OUT / "qr_code.png"
    img.save(out, "PNG", optimize=True)
    print(f"Wrote {out} ({img.size[0]}x{img.size[1]})")


def generate_plain_png():
    qr = build_qr()
    img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
    img = img.resize((TARGET_SIZE_PX, TARGET_SIZE_PX), Image.NEAREST)
    out = OUT / "qr_code_plain.png"
    img.save(out, "PNG", optimize=True)
    print(f"Wrote {out} ({img.size[0]}x{img.size[1]})")


def generate_svg():
    qr = qrcode.QRCode(
        version=None,
        error_correction=ERROR_CORRECT_H,
        box_size=20,
        border=4,
        image_factory=SvgPathImage,
    )
    qr.add_data(URL)
    qr.make(fit=True)
    img = qr.make_image()
    out = OUT / "qr_code.svg"
    img.save(str(out))
    print(f"Wrote {out}")


if __name__ == "__main__":
    generate_branded_png()
    generate_plain_png()
    generate_svg()
    print("\nAll QR codes written to:", OUT)
    print("Encoded URL:", URL)
