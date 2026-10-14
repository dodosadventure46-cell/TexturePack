"""generate_packs.py

Generates a resource pack (32x PvP textures) and a behavior pack (lightweight FPS counter script)
and packages each into a correct .mcpack (zip) structure with manifest.json at the archive root.

Usage:
    pip install pillow
    python generate_packs.py

Outputs (in repo root):
    resource_<timestamp>.mcpack
    behavior_<timestamp>.mcpack

The script creates unique names, versions and UUIDs so repeated runs don't create duplicate packs.
"""

from __future__ import annotations

import json
import os
import shutil
import time
import uuid
import zipfile
from pathlib import Path
from typing import Tuple

try:
    from PIL import Image, ImageDraw
except Exception as e:
    raise SystemExit("Pillow is required. Install with: pip install pillow")

ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "built_packs"
BASE_RESOURCE_NAME = "PvP Smooth 32x"
BASE_BEHAVIOR_NAME = "PvP Smooth FPS Behavior"
DESCRIPTION = "Clean PvP textures • 32x • optimized for Android"


def ensure_clean(path: Path):
    if path.exists():
        shutil.rmtree(path)


def write_json(path: Path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2), encoding="utf-8")


def save_image(path: Path, img: Image.Image, optimize: bool = True):
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path, optimize=optimize)


def make_manifest_resource(name: str, version: Tuple[int, int, int], uuid_header: str, uuid_module: str) -> dict:
    return {
        "format_version": 2,
        "header": {
            "name": name,
            "description": DESCRIPTION,
            "uuid": uuid_header,
            "version": list(version),
            "min_engine_version": [1, 20, 0]
        },
        "modules": [
            {
                "type": "resources",
                "uuid": uuid_module,
                "version": list(version)
            }
        ]
    }


def make_manifest_behavior(name: str, version: Tuple[int, int, int], uuid_header: str, uuid_module: str, entry: str) -> dict:
    return {
        "format_version": 2,
        "header": {
            "name": name,
            "description": DESCRIPTION + " (behavior pack, experimental scripting)",
            "uuid": uuid_header,
            "version": list(version),
            "min_engine_version": [1, 20, 0]
        },
        "modules": [
            {
                "type": "scripting",
                "uuid": uuid_module,
                "version": list(version),
                "entry": entry
            }
        ]
    }


def make_basic_textures(root: Path):
    items_dir = root / "textures" / "items"
    ui_dir = root / "textures" / "ui"
    items_dir.mkdir(parents=True, exist_ok=True)
    ui_dir.mkdir(parents=True, exist_ok=True)

    def base_img(size=32):
        return Image.new("RGBA", (size, size), (0, 0, 0, 0))

    # simple sword
    img = base_img()
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((6, 6, 26, 26), radius=3, fill=(28, 34, 44, 255))
    d.rounded_rectangle((14, 1, 18, 22), radius=1, fill=(150, 200, 255, 255))
    d.rounded_rectangle((10, 21, 22, 25), radius=1, fill=(90, 65, 45, 255))
    save_image(items_dir / "diamond_sword.png", img)

    # pickaxe
    img = base_img()
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((6, 6, 26, 26), radius=3, fill=(28, 34, 44, 255))
    d.rounded_rectangle((13, 4, 19, 28), radius=1, fill=(180, 230, 255, 255))
    d.rounded_rectangle((9, 12, 23, 16), radius=1, fill=(180, 230, 255, 255))
    save_image(items_dir / "diamond_pickaxe.png", img)

    # axe
    img = base_img()
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((6, 6, 26, 26), radius=3, fill=(28, 34, 44, 255))
    d.polygon([(16, 2), (24, 12), (16, 17), (8, 12)], fill=(150, 230, 190, 255))
    save_image(items_dir / "diamond_axe.png", img)

    # armor placeholders
    for name in ["diamond_helmet.png", "diamond_chestplate.png", "diamond_leggings.png", "diamond_boots.png"]:
        img = base_img()
        d = ImageDraw.Draw(img)
        d.rounded_rectangle((6, 5, 26, 28), radius=4, fill=(148, 180, 255, 255))
        save_image(items_dir / name, img)

    # hotbar + selected
    img = base_img()
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((2, 2, 30, 30), radius=5, fill=(32, 36, 44, 200))
    save_image(ui_dir / "hotbar.png", img)

    img = base_img()
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((2, 2, 30, 30), radius=5, fill=(48, 52, 64, 200))
    save_image(ui_dir / "hotbar_selected.png", img)

    # crosshair
    img = base_img()
    d = ImageDraw.Draw(img)
    d.rectangle((15, 0, 17, 32), fill=(255, 255, 255, 220))
    d.rectangle((0, 15, 32, 17), fill=(255, 255, 255, 220))
    save_image(ui_dir / "crosshair.png", img)

    # pack icon
    icon = Image.new("RGBA", (128, 128), (0, 0, 0, 0))
    d = ImageDraw.Draw(icon)
    d.rounded_rectangle((18, 18, 110, 110), radius=22, fill=(32, 38, 46, 255))
    d.rounded_rectangle((30, 30, 98, 98), radius=18, fill=(120, 155, 255, 255))
    save_image(root / "pack_icon.png", icon, optimize=False)

    # texts
    texts = root / "texts"
    texts.mkdir(parents=True, exist_ok=True)
    (texts / "en_US.lang").write_text(f"pack.name={BASE_RESOURCE_NAME}\npack.description={DESCRIPTION}\n", encoding="utf-8")


FPS_SCRIPT = """import { world, system } from '@minecraft/server';

const updateRate = 10; // ticks (~0.5s)
let tickCounter = 0;
let lastTime = Date.now();
let lastFps = 0;

system.runInterval(() => {
  // count ticks
  tickCounter += 1;
  const now = Date.now();
  const deltaSec = (now - lastTime) / 1000;
  if (deltaSec > 0) {
    lastFps = Math.min(999, Math.max(0, Math.round(tickCounter / deltaSec)));
    tickCounter = 0;
    lastTime = now;
  }

  // send actionbar to all players
  for (const player of world.getPlayers()) {
    try {
      player.runCommand(`title @s actionbar FPS: ${lastFps}`);
    } catch (e) {
      // ignore
    }
  }

}, updateRate);
"""


def make_resource_pack(out_root: Path) -> Path:
    ts = int(time.time())
    name = f"{BASE_RESOURCE_NAME} {ts}"
    version = (1, 0, ts % 100000)
    uuid_header = str(uuid.uuid4())
    uuid_module = str(uuid.uuid4())

    out = out_root / f"resource_{ts}"
    ensure_clean(out)
    out.mkdir(parents=True, exist_ok=True)

    # manifest
    manifest = make_manifest_resource(name, version, uuid_header, uuid_module)
    write_json(out / "manifest.json", manifest)

    # textures + pack data
    make_basic_textures(out)

    # zip into .mcpack with manifest at root
    mcpack = ROOT / f"resource_{ts}.mcpack"
    with zipfile.ZipFile(mcpack, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for f in sorted(out.rglob("*")):
            if f.is_file():
                arc = f.relative_to(out)
                zf.write(f, arc.as_posix())

    size_mb = mcpack.stat().st_size / (1024 * 1024)
    print(f"Built resource pack: {mcpack} ({size_mb:.2f} MB)")
    return mcpack


def make_behavior_pack(out_root: Path) -> Path:
    ts = int(time.time())
    name = f"{BASE_BEHAVIOR_NAME} {ts}"
    version = (1, 0, ts % 100000)
    uuid_header = str(uuid.uuid4())
    uuid_module = str(uuid.uuid4())

    out = out_root / f"behavior_{ts}"
    ensure_clean(out)
    out.mkdir(parents=True, exist_ok=True)

    # manifest with scripting entry
    entry_path = "scripts/client/fps_counter.js"
    manifest = make_manifest_behavior(name, version, uuid_header, uuid_module, entry_path)
    write_json(out / "manifest.json", manifest)

    # write script file
    script_file = out / entry_path
    script_file.parent.mkdir(parents=True, exist_ok=True)
    script_file.write_text(FPS_SCRIPT, encoding="utf-8")

    # write README/lang if wanted
    texts = out / "texts"
    texts.mkdir(parents=True, exist_ok=True)
    (texts / "en_US.lang").write_text(f"pack.name={name}\npack.description=Experimental FPS behavior (enable scripting)\n", encoding="utf-8")

    # zip into .mcpack
    mcpack = ROOT / f"behavior_{ts}.mcpack"
    with zipfile.ZipFile(mcpack, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for f in sorted(out.rglob("*")):
            if f.is_file():
                arc = f.relative_to(out)
                zf.write(f, arc.as_posix())

    size_mb = mcpack.stat().st_size / (1024 * 1024)
    print(f"Built behavior pack: {mcpack} ({size_mb:.2f} MB)")
    return mcpack


def build_all():
    ensure_clean(OUT_DIR)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    res = make_resource_pack(OUT_DIR)
    beh = make_behavior_pack(OUT_DIR)

    print("Done. Generated packs:")
    print(" - ", res)
    print(" - ", beh)


if __name__ == '__main__':
    build_all()
