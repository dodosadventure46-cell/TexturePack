from __future__ import annotations

import json
import math
import os
import random
import shutil
import zipfile
from pathlib import Path
from typing import Iterable, Tuple

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent
OUTPUT_DIR = ROOT / "PvP_Smooth_32x"
ZIP_FILE = ROOT / "PvP_Smooth_32x.mcpack"
# Changed name & version to avoid duplicate detection
PACK_VERSION = [1, 2, 0]
PACK_NAME = f"PvP Smooth 32x v{PACK_VERSION[0]}.{PACK_VERSION[1]}"
PACK_DESCRIPTION = "Clean PvP textures • 32x • smooth vanilla style • optimized for Android"

# New UUIDs (unique for this version)
UUID_HEADER = "c3d9a1f2-6b4e-4f2d-9a7b-0123456789ab"
UUID_MODULE = "d4b8e2c3-7a5f-4c3e-9b8c-abcdef012345"

# How many large placeholder files to create to increase archive size (each ~1-3 MB)
LARGE_ASSET_COUNT = 3
LARGE_ASSET_SIZE = (1024, 1024)  # width, height


def ensure_clean_output() -> None:
    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)
    if ZIP_FILE.exists():
        ZIP_FILE.unlink()


def save_image(path: Path, image: Image.Image) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    # Use optimize and max quality for larger file size
    image.save(path, optimize=True)


def create_manifest() -> dict:
    return {
        "format_version": 2,
        "header": {
            "name": PACK_NAME,
            "description": PACK_DESCRIPTION,
            "uuid": UUID_HEADER,
            "version": PACK_VERSION,
            "min_engine_version": [1, 20, 0],
        },
        "modules": [
            {
                "type": "resources",
                "uuid": UUID_MODULE,
                "version": PACK_VERSION,
            }
        ],
    }


def create_lang() -> str:
    return "pack.name=" + PACK_NAME + "\npack.description=" + PACK_DESCRIPTION + "\n"


def make_item_base(size=32) -> Image.Image:
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    return img


def draw_diamond_weapon(path: Path, kind: str, accent: tuple[int, int, int], dark: tuple[int, int, int]) -> None:
    img = make_item_base()
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((6, 6, 26, 26), radius=3, fill=(26, 31, 38, 255))

    if kind == "sword":
        d.rounded_rectangle((14, 1, 18, 22), radius=1, fill=accent)
        d.rounded_rectangle((10, 21, 22, 25), radius=1, fill=(81, 62, 42, 255))
        d.rounded_rectangle((12, 24, 20, 30), radius=1, fill=(105, 83, 58, 255))
        d.rounded_rectangle((9, 18, 23, 21), radius=1, fill=(96, 129, 206, 255))
        d.line((15, 2, 17, 20), fill=(255, 255, 255, 180), width=1)
    elif kind == "pickaxe":
        d.rounded_rectangle((13, 4, 19, 28), radius=1, fill=accent)
        d.rounded_rectangle((9, 12, 23, 16), radius=1, fill=accent)
        d.polygon([(16, 2), (22, 10), (16, 10)], fill=(108, 149, 218, 255))
        d.polygon([(16, 2), (10, 10), (16, 10)], fill=(108, 149, 218, 255))
        d.line((14, 6, 18, 20), fill=(255, 255, 255, 180), width=1)
    elif kind == "axe":
        d.polygon([(16, 2), (24, 12), (16, 17), (8, 12)], fill=accent)
        d.rounded_rectangle((13, 18, 19, 29), radius=1, fill=(83, 62, 42, 255))
        d.line((16, 18, 16, 29), fill=(255, 255, 255, 180), width=1)
    else:
        raise ValueError(f"unsupported kind: {kind}")

    save_image(path, img)


def draw_armor(path: Path, tint: tuple[int, int, int]) -> None:
    img = make_item_base()
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((6, 5, 26, 28), radius=4, fill=tint)
    d.rounded_rectangle((10, 9, 22, 25), radius=3, fill=(255, 255, 255, 30))
    d.rectangle((12, 6, 20, 9), fill=(220, 230, 255, 120))
    d.rectangle((13, 12, 19, 20), fill=(10, 12, 16, 110))
    save_image(path, img)


def draw_bow(path: Path, pull: int = 0) -> None:
    img = make_item_base()
    d = ImageDraw.Draw(img)
    d.arc((7, 7, 25, 25), start=200, end=340, fill=(200, 215, 255, 255), width=3)
    d.arc((7, 7, 25, 25), start=20, end=160, fill=(200, 215, 255, 255), width=3)
    d.line((16, 8, 16, 24), fill=(82, 91, 105, 255), width=2)
    d.line((16, 8, 12, 18), fill=(82, 91, 105, 255), width=2)
    d.line((16, 24, 12, 14), fill=(82, 91, 105, 255), width=2)
    d.line((16, 8, 16, 24), fill=(255, 255, 255, 180), width=1)
    if pull == 1:
        d.line((16, 10, 22, 16), fill=(255, 255, 255, 180), width=1)
    elif pull == 2:
        d.line((16, 8, 24, 12), fill=(255, 255, 255, 180), width=1)
        d.line((16, 24, 24, 19), fill=(255, 255, 255, 180), width=1)
    save_image(path, img)


def draw_hotbar(path: Path, selected: bool = False) -> None:
    img = make_item_base()
    d = ImageDraw.Draw(img)
    if selected:
        d.rounded_rectangle((2, 2, 30, 30), radius=5, fill=(48, 52, 64, 200))
        d.rounded_rectangle((5, 5, 27, 27), radius=4, fill=(112, 122, 145, 150))
        d.rectangle((7, 7, 25, 25), fill=(255, 222, 120, 120))
    else:
        d.rounded_rectangle((2, 2, 30, 30), radius=5, fill=(32, 36, 44, 180))
        d.rounded_rectangle((5, 5, 27, 27), radius=4, fill=(102, 109, 130, 120))
    save_image(path, img)


def draw_crosshair(path: Path) -> None:
    img = make_item_base()
    d = ImageDraw.Draw(img)
    d.rectangle((15, 0, 17, 32), fill=(255, 255, 255, 220))
    d.rectangle((0, 15, 32, 17), fill=(255, 255, 255, 220))
    d.rectangle((14, 14, 18, 18), fill=(0, 0, 0, 100))
    save_image(path, img)


def generate_large_noise_png(path: Path, size=(1024, 1024)) -> None:
    """Generate a relatively large, less-compressible PNG by filling with random noise."""
    path.parent.mkdir(parents=True, exist_ok=True)
    w, h = size
    # create raw RGBA bytes with random data
    raw = bytearray(os.urandom(w * h * 3))  # RGB
    # convert to RGBA by adding opaque alpha bytes
    rgba = bytearray()
    for i in range(0, len(raw), 3):
        rgba.extend(raw[i:i+3])
        rgba.append(255)
    img = Image.frombytes("RGBA", (w, h), bytes(rgba))
    # save with no noticeable compression optimization to keep size bigger
    img.save(path, optimize=False)


def build_pack() -> None:
    ensure_clean_output()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # manifest
    manifest_path = OUTPUT_DIR / "manifest.json"
    manifest_path.write_text(json.dumps(create_manifest(), indent=2), encoding="utf-8")

    # lang
    texts_dir = OUTPUT_DIR / "texts"
    texts_dir.mkdir(parents=True, exist_ok=True)
    (texts_dir / "en_US.lang").write_text(create_lang(), encoding="utf-8")

    # create pack icon
    icon = Image.new("RGBA", (128, 128), (0, 0, 0, 0))
    d = ImageDraw.Draw(icon)
    d.rounded_rectangle((18, 18, 110, 110), radius=22, fill=(32, 38, 46, 255))
    d.rounded_rectangle((30, 30, 98, 98), radius=18, fill=(120, 155, 255, 255))
    d.polygon([(64, 28), (100, 64), (64, 100), (28, 64)], fill=(214, 232, 255, 255))
    save_image(OUTPUT_DIR / "pack_icon.png", icon)

    # item textures
    items_dir = OUTPUT_DIR / "textures" / "items"
    ui_dir = OUTPUT_DIR / "textures" / "ui"
    items_dir.mkdir(parents=True, exist_ok=True)
    ui_dir.mkdir(parents=True, exist_ok=True)

    draw_diamond_weapon(items_dir / "diamond_sword.png", "sword", (150, 200, 255), (74, 95, 126))
    draw_diamond_weapon(items_dir / "diamond_pickaxe.png", "pickaxe", (180, 230, 255), (74, 95, 126))
    draw_diamond_weapon(items_dir / "diamond_axe.png", "axe", (150, 230, 190), (74, 95, 126))

    draw_armor(items_dir / "diamond_helmet.png", (148, 180, 255))
    draw_armor(items_dir / "diamond_chestplate.png", (148, 180, 255))
    draw_armor(items_dir / "diamond_leggings.png", (148, 180, 255))
    draw_armor(items_dir / "diamond_boots.png", (148, 180, 255))

    draw_bow(items_dir / "bow_standby.png", 0)
    draw_bow(items_dir / "bow_pulling_0.png", 1)
    draw_bow(items_dir / "bow_pulling_1.png", 1)
    draw_bow(items_dir / "bow_pulling_2.png", 2)

    draw_hotbar(ui_dir / "hotbar.png", False)
    draw_hotbar(ui_dir / "hotbar_selected.png", True)
    draw_crosshair(ui_dir / "crosshair.png")

    # generate large placeholder assets to increase filesize (MB range)
    large_dir = OUTPUT_DIR / "assets" / "large"
    for i in range(1, LARGE_ASSET_COUNT + 1):
        p = large_dir / f"noise_{i}.png"
        print(f"Generating large asset: {p}")
        generate_large_noise_png(p, size=LARGE_ASSET_SIZE)

    print(f"Generated pack folder: {OUTPUT_DIR}")

    # create .mcpack zip
    # NOTE: zip should contain manifest.json at the archive root (not nested under an extra folder)
    with zipfile.ZipFile(ZIP_FILE, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for file_path in sorted(OUTPUT_DIR.rglob("*")):
            if file_path.is_file():
                # make arcname relative to the OUTPUT_DIR so manifest.json is at archive root
                arcname = file_path.relative_to(OUTPUT_DIR)
                zf.write(file_path, arcname.as_posix())
    print(f"Generated mcpack archive: {ZIP_FILE} (size: {ZIP_FILE.stat().st_size / (1024*1024):.2f} MB)")


if __name__ == "__main__":
    build_pack()
    print("Done. Install the .mcpack file in Minecraft or activate the unpacked resource pack folder.")
