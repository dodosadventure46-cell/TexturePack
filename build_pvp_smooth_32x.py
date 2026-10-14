from __future__ import annotations

import json
import os
import random
import shutil
import zipfile
import time
import uuid
from pathlib import Path
from typing import Tuple

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent
BASE_OUTPUT_DIR = ROOT / "PvP_Smooth_32x_builds"
# Base name; actual pack name will include a timestamp to avoid duplicates
BASE_PACK_NAME = "PvP Smooth 32x"
BASE_DESCRIPTION = "Clean PvP textures • 32x • smooth vanilla style • optimized for Android"

# Large asset settings for the "full" pack to inflate file size (MB range)
FULL_LARGE_ASSET_COUNT = 3
FULL_LARGE_ASSET_SIZE = (1024, 1024)

# Perf pack uses minimal large assets to keep it lightweight
PERF_LARGE_ASSET_COUNT = 0
PERF_LARGE_ASSET_SIZE = (512, 512)


def ensure_clean_output(out_dir: Path) -> None:
    if out_dir.exists():
        shutil.rmtree(out_dir)


def save_image(path: Path, image: Image.Image, optimize: bool = True) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    # Save with default params; caller decides sizes to affect final file size
    image.save(path, optimize=optimize)


def create_manifest(pack_name: str, pack_version: Tuple[int, int, int], uuid_header: str, uuid_module: str) -> dict:
    return {
        "format_version": 2,
        "header": {
            "name": pack_name,
            "description": BASE_DESCRIPTION,
            "uuid": uuid_header,
            "version": list(pack_version),
            "min_engine_version": [1, 20, 0],
        },
        "modules": [
            {
                "type": "resources",
                "uuid": uuid_module,
                "version": list(pack_version),
            }
        ],
    }


def create_lang(pack_name: str) -> str:
    return f"pack.name={pack_name}\npack.description={BASE_DESCRIPTION}\n"


def make_item_base(size=32) -> Image.Image:
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    return img


def draw_diamond_weapon(path: Path, kind: str, accent: Tuple[int, int, int]) -> None:
    img = make_item_base()
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((6, 6, 26, 26), radius=3, fill=(26, 31, 38, 255))

    if kind == "sword":
        d.rounded_rectangle((14, 1, 18, 22), radius=1, fill=accent)
        d.rounded_rectangle((10, 21, 22, 25), radius=1, fill=(81, 62, 42, 255))
        d.line((15, 2, 17, 20), fill=(255, 255, 255, 180), width=1)
    elif kind == "pickaxe":
        d.rounded_rectangle((13, 4, 19, 28), radius=1, fill=accent)
        d.rounded_rectangle((9, 12, 23, 16), radius=1, fill=accent)
    elif kind == "axe":
        d.polygon([(16, 2), (24, 12), (16, 17), (8, 12)], fill=accent)
    save_image(path, img)


def draw_armor(path: Path, tint: Tuple[int, int, int]) -> None:
    img = make_item_base()
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((6, 5, 26, 28), radius=4, fill=tint)
    save_image(path, img)


def draw_bow(path: Path, pull: int = 0) -> None:
    img = make_item_base()
    d = ImageDraw.Draw(img)
    d.arc((7, 7, 25, 25), start=200, end=340, fill=(200, 215, 255, 255), width=3)
    save_image(path, img)


def draw_hotbar(path: Path, selected: bool = False) -> None:
    img = make_item_base()
    d = ImageDraw.Draw(img)
    if selected:
        d.rounded_rectangle((2, 2, 30, 30), radius=5, fill=(48, 52, 64, 200))
    else:
        d.rounded_rectangle((2, 2, 30, 30), radius=5, fill=(32, 36, 44, 180))
    save_image(path, img)


def draw_crosshair(path: Path) -> None:
    img = make_item_base()
    d = ImageDraw.Draw(img)
    d.rectangle((15, 0, 17, 32), fill=(255, 255, 255, 220))
    d.rectangle((0, 15, 32, 17), fill=(255, 255, 255, 220))
    save_image(path, img)


def generate_large_noise_png(path: Path, size=(1024, 1024)) -> None:
    """Generate a relatively large, less-compressible PNG by filling with random noise."""
    path.parent.mkdir(parents=True, exist_ok=True)
    w, h = size
    raw = bytearray(os.urandom(w * h * 3))  # RGB
    rgba = bytearray()
    for i in range(0, len(raw), 3):
        rgba.extend(raw[i:i+3])
        rgba.append(255)
    img = Image.frombytes("RGBA", (w, h), bytes(rgba))
    img.save(path, optimize=False)


def build_single_pack(out_root: Path, suffix: str = "", large_count: int = 0, large_size=(1024, 1024)) -> Path:
    """Build one pack. Returns path to the .mcpack file."""
    ts = int(time.time())
    pack_name = f"{BASE_PACK_NAME} {suffix} {ts}".strip()
    # Use timestamp as part of the version's patch to avoid duplicates
    pack_version = (1, 0, ts % 100000)
    uuid_header = str(uuid.uuid4())
    uuid_module = str(uuid.uuid4())

    out_dir = out_root / f"{pack_name.replace(' ', '_')}"
    ensure_clean_output(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # manifest
    (out_dir / "manifest.json").write_text(json.dumps(create_manifest(pack_name, pack_version, uuid_header, uuid_module), indent=2), encoding="utf-8")

    # lang
    texts_dir = out_dir / "texts"
    texts_dir.mkdir(parents=True, exist_ok=True)
    (texts_dir / "en_US.lang").write_text(create_lang(pack_name), encoding="utf-8")

    # pack icon
    icon = Image.new("RGBA", (128, 128), (0, 0, 0, 0))
    d = ImageDraw.Draw(icon)
    d.rounded_rectangle((18, 18, 110, 110), radius=22, fill=(32, 38, 46, 255))
    d.rounded_rectangle((30, 30, 98, 98), radius=18, fill=(120, 155, 255, 255))
    save_image(out_dir / "pack_icon.png", icon, optimize=False)

    # textures
    items_dir = out_dir / "textures" / "items"
    ui_dir = out_dir / "textures" / "ui"
    items_dir.mkdir(parents=True, exist_ok=True)
    ui_dir.mkdir(parents=True, exist_ok=True)

    draw_diamond_weapon(items_dir / "diamond_sword.png", "sword", (150, 200, 255))
    draw_diamond_weapon(items_dir / "diamond_pickaxe.png", "pickaxe", (180, 230, 255))
    draw_diamond_weapon(items_dir / "diamond_axe.png", "axe", (150, 230, 190))

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

    # large assets (optional)
    large_dir = out_dir / "assets" / "large"
    for i in range(1, large_count + 1):
        p = large_dir / f"noise_{i}.png"
        generate_large_noise_png(p, size=large_size)

    # write archive (.mcpack)
    mcpack_name = ROOT / f"{pack_name.replace(' ', '_')}.mcpack"
    with zipfile.ZipFile(mcpack_name, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for file_path in sorted(out_dir.rglob("*")):
            if file_path.is_file():
                arcname = file_path.relative_to(out_dir)
                zf.write(file_path, arcname.as_posix())

    print(f"Built pack: {mcpack_name} (size: {mcpack_name.stat().st_size / (1024*1024):.2f} MB)")
    return mcpack_name


def build_all() -> None:
    ensure_clean_output(BASE_OUTPUT_DIR)
    BASE_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Build full (larger) pack
    build_single_pack(BASE_OUTPUT_DIR, suffix="full", large_count=FULL_LARGE_ASSET_COUNT, large_size=FULL_LARGE_ASSET_SIZE)

    # Build perf (lightweight) pack
    build_single_pack(BASE_OUTPUT_DIR, suffix="perf", large_count=PERF_LARGE_ASSET_COUNT, large_size=PERF_LARGE_ASSET_SIZE)


if __name__ == "__main__":
    # Build both packs. Each run will generate packs with unique names, versions and UUIDs.
    build_all()
    print("Done. Two .mcpack files were created in the repository root with timestamped names.")
