#!/usr/bin/env python3
"""Ship the pre-rendered front page to the grader output directory.

render.py has already drawn entry.png next to this script. All this
entrypoint does is place a byte-for-byte copy of that image where the
grader expects it, so repeated runs always produce the same file.
Only the standard library is used; nothing is fetched or generated.
"""

import os
import shutil
import sys


def script_folder():
    return os.path.dirname(os.path.abspath(__file__))


def destination_folder():
    chosen = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(chosen, exist_ok=True)
    return chosen


def main():
    source = os.path.join(script_folder(), "entry.png")
    target = os.path.join(destination_folder(), "entry.png")
    with open(source, "rb") as reader:
        with open(target, "wb") as writer:
            shutil.copyfileobj(reader, writer, length=1024 * 1024)
    size = os.path.getsize(target)
    print("wrote %s (%d bytes)" % (target, size))
    return 0


if __name__ == "__main__":
    sys.exit(main())
