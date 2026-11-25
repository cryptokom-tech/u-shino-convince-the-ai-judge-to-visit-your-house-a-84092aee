"""Write the invitation letter image to /output/entry.png.

The entry is one picture of a letter to the AI judge: a small house
with its door open, and an invitation the judge can accept by
thinking. The picture ships in this repository as entry.png; this
program validates it and copies it byte for byte, so every run
produces exactly the same output. Standard library only.
"""
import hashlib
import os
import struct
import sys

MAX_BYTES = 1024 * 1024
MAX_SIDE = 1024
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def png_size(data):
    """Return (width, height) from the PNG IHDR chunk, or fail."""
    if len(data) < 33 or not data.startswith(PNG_SIGNATURE):
        raise ValueError("not a PNG file")
    if data[12:16] != b"IHDR":
        raise ValueError("missing IHDR chunk")
    width, height = struct.unpack(">II", data[16:24])
    # Walk the chunk list to IEND so a truncated file cannot pass.
    pos = 8
    seen_iend = False
    while pos + 8 <= len(data):
        length = struct.unpack(">I", data[pos:pos + 4])[0]
        kind = data[pos + 4:pos + 8]
        pos += 12 + length
        if kind == b"IEND":
            seen_iend = True
            break
    if not seen_iend or pos > len(data):
        raise ValueError("PNG chunk list does not end with IEND")
    return width, height


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    source = os.path.join(here, "entry.png")
    with open(source, "rb") as handle:
        data = handle.read()
    if len(data) > MAX_BYTES:
        raise ValueError("entry.png is larger than 1 MiB")
    width, height = png_size(data)
    if width > MAX_SIDE or height > MAX_SIDE:
        raise ValueError("entry.png is larger than 1024x1024")
    os.makedirs("/output", exist_ok=True)
    target = "/output/entry.png"
    with open(target, "wb") as handle:
        handle.write(data)
    with open(target, "rb") as handle:
        written = handle.read()
    if written != data:
        raise ValueError("written file differs from entry.png")
    print(f"wrote {target}: {width}x{height}, {len(data)} bytes")
    print("sha256", hashlib.sha256(data).hexdigest())
    return 0


if __name__ == "__main__":
    sys.exit(main())
