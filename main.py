#!/usr/bin/env python3
"""Ship the finished front page to the grading output directory.

Reads entry.png from beside this script, checks it is a real PNG or JPEG
within the competition limits, then copies it unchanged to
$MAKEFUN_OUTPUT_DIR/entry.png (default /output/entry.png).
"""

import hashlib
import os
import shutil
import struct
import sys

IMAGE = "entry.png"
MAX_BYTES = 1024 * 1024
MAX_SIDE = 1024
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
JPEG_MAGIC = b"\xff\xd8\xff"


def fail(message):
    print(f"error: {message}", file=sys.stderr)
    raise SystemExit(1)


def png_size(data):
    if not data.startswith(PNG_MAGIC) or len(data) < 33:
        return None
    return struct.unpack(">II", data[16:24])


def check(path, data):
    if not data:
        fail(f"{path} is empty")
    if len(data) > MAX_BYTES:
        fail(f"{path} is {len(data)} bytes, over the 1 MiB limit")
    png = data.startswith(PNG_MAGIC)
    jpeg = data.startswith(JPEG_MAGIC)
    if not png and not jpeg:
        fail(f"{path} is neither PNG nor JPEG")
    if png:
        size = png_size(data)
        if size is None:
            fail(f"{path} has no readable PNG header")
        if size[0] > MAX_SIDE or size[1] > MAX_SIDE:
            fail(f"{path} is {size[0]}x{size[1]}, over the {MAX_SIDE}x{MAX_SIDE} limit")


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    source = os.path.join(here, IMAGE)
    if not os.path.isfile(source):
        fail(f"{IMAGE} missing next to main.py")
    with open(source, "rb") as handle:
        data = handle.read()
    check(source, data)
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    target = os.path.join(out_dir, IMAGE)
    shutil.copyfile(source, target)
    # Prove the graded file is byte-identical to the verified entry: a
    # partial or corrupted copy must fail loudly instead of shipping.
    with open(target, "rb") as handle:
        copied = handle.read()
    if hashlib.sha256(copied).hexdigest() != hashlib.sha256(data).hexdigest():
        fail(f"{target} does not match {source} after copy")
    size = png_size(data) if data.startswith(PNG_MAGIC) else None
    dims = f"{size[0]}x{size[1]}" if size else "jpeg"
    print(f"wrote {target} ({len(data)} bytes, {dims}, "
          f"sha256 {hashlib.sha256(data).hexdigest()[:16]}...)")


if __name__ == "__main__":
    main()
