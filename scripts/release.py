#!/usr/bin/env python3
"""Check the public pet payload and create a self-contained release ZIP."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import zipfile
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
PET_IDS = (
    "khalil-suit-handdrawn", "khalil-15live-handdrawn",
    "khalil-blue-handdrawn", "khalil-farmer-handdrawn",
)
DESIGNS = ("01-suit-electric.png", "02-15-live-mic.png", "03-blue-acoustic.png", "04-farmer-cross-legged.png")
PAYLOAD = sorted(
    ["README.md", "index.html", "安装到Codex.command", "检查摘要.json"]
    + [f"{pet}/{name}" for pet in PET_IDS for name in ("pet.json", "spritesheet.webp")]
    + [f"设计原图/{name}" for name in DESIGNS]
    + [f"previews/{name}.gif" for name in ("suit", "mic", "blue", "farmer")]
)
USED_CELLS = (7, 8, 8, 4, 5, 8, 6, 6, 6, 8, 8)  # Row 0 includes the neutral cell.


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def prepare(root: Path = ROOT) -> None:
    lines = [f"{digest(root / name)}  {name}\n" for name in PAYLOAD]
    (root / "SHA256SUMS").write_text("".join(lines), encoding="utf-8")


def verify(root: Path = ROOT) -> dict:
    entries = {}
    for line in (root / "SHA256SUMS").read_text(encoding="utf-8").splitlines():
        match = re.fullmatch(r"([0-9a-f]{64})  (.+)", line)
        if not match:
            raise ValueError("Malformed checksum line")
        checksum, name = match.groups()
        if name in entries or name not in PAYLOAD:
            raise ValueError(f"Unexpected or duplicate checksum entry: {name}")
        entries[name] = checksum
    if set(entries) != set(PAYLOAD):
        raise ValueError("Incomplete checksum manifest")
    for name, checksum in entries.items():
        path = root / name
        if path.is_symlink() or not path.is_file() or digest(path) != checksum:
            raise ValueError(f"Missing, changed or linked payload file: {name}")
        if path.suffix in {".md", ".html", ".json", ".command"}:
            content = path.read_text(encoding="utf-8")
            if re.search(r"/Users/|/private/var/|/var/folders/|gh[pousr]_[A-Za-z0-9]{20,}", content):
                raise ValueError(f"Local path or credential pattern in public file: {name}")
    html = (root / "index.html").read_text(encoding="utf-8")
    for pet in PET_IDS:
        config = json.loads((root / pet / "pet.json").read_text(encoding="utf-8"))
        if config.get("id") != pet or config.get("spriteVersionNumber") != 2:
            raise ValueError(f"Invalid pet identity/version: {pet}")
        if config.get("spritesheetPath") != "spritesheet.webp" or not config.get("displayName"):
            raise ValueError(f"Invalid pet config: {pet}")
        if pet not in html:
            raise ValueError(f"Preview missing pet: {pet}")
        with Image.open(root / pet / "spritesheet.webp") as opened:
            if opened.size != (1536, 2288) or opened.mode != "RGBA":
                raise ValueError(f"Invalid atlas dimensions/mode: {pet}")
            atlas = opened.copy()
        alpha = atlas.getchannel("A")
        if alpha.getextrema()[0] != 0:
            raise ValueError(f"Atlas has no transparent background: {pet}")
        for row, count in enumerate(USED_CELLS):
            for col in range(8):
                cell = alpha.crop((col * 192, row * 208, (col + 1) * 192, (row + 1) * 208))
                used = sum(cell.histogram()[1:])
                if (col < count and used < 400) or (col >= count and used != 0):
                    raise ValueError(f"Unexpected cell content: {pet} row={row} col={col}")
        for pixel in atlas.get_flattened_data():
            if pixel[3] == 0 and pixel[:3] != (0, 0, 0):
                raise ValueError(f"Hidden RGB residue: {pet}")
    for name in ("suit", "mic", "blue", "farmer"):
        with Image.open(root / f"previews/{name}.gif") as image:
            if image.n_frames < 4:
                raise ValueError(f"Preview is not a complete animation: {name}")
    return {"ok": True, "pets": len(PET_IDS), "payload_files": len(PAYLOAD), "atlas": [1536, 2288]}


def build(root: Path = ROOT) -> Path:
    verify(root)
    output = root / "release"
    output.mkdir(exist_ok=True)
    archive = output / "fangdatong-codex-pets.zip"
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
        for name in sorted(PAYLOAD + ["SHA256SUMS"]):
            info = zipfile.ZipInfo(f"fangdatong-codex-pets/{name}", (2026, 10, 8, 0, 0, 0))
            info.create_system = 3
            mode = 0o100755 if name.endswith(".command") else 0o100644
            info.external_attr = mode << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            zf.writestr(info, (root / name).read_bytes())
    with zipfile.ZipFile(archive) as zf:
        if zf.testzip() is not None:
            raise ValueError("ZIP integrity check failed")
    (output / "SHA256SUMS.txt").write_text(f"{digest(archive)}  {archive.name}\n", encoding="utf-8")
    return archive


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("prepare", "verify", "build"))
    action = parser.parse_args().action
    if action == "prepare":
        prepare()
        print("Updated SHA256SUMS")
    elif action == "verify":
        print(json.dumps(verify(), indent=2))
    else:
        print(build())
