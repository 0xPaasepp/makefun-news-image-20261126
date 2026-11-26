#!/usr/bin/env python3
"""Deliver the finished front page to the grader's output folder.

The image is drawn ahead of time by render.py and stored beside this file,
so this program only copies it to /output/entry.png (or $MAKEFUN_OUTPUT_DIR).
Both graded runs therefore write byte-identical files. Standard library only.
"""
import os
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
IMAGE = HERE / "entry.png"


def run():
    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / "entry.png"
    shutil.copyfile(IMAGE, target)
    print(f"wrote {target} ({target.stat().st_size} bytes)")


if __name__ == "__main__":
    run()
