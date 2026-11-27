"""Copy the bundled entry image into the grader output directory."""

import os
import shutil
from pathlib import Path


def locate_source():
    folder = Path(__file__).resolve().parent
    return folder / "entry.png"


def locate_destination_folder():
    chosen = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if chosen:
        return Path(chosen)
    return Path("/output")


def run():
    picture = locate_source()
    if not picture.is_file():
        raise SystemExit(f"error: source image not found: {picture}")
    target_folder = locate_destination_folder()
    target_folder.mkdir(parents=True, exist_ok=True)
    target = target_folder / "entry.png"
    shutil.copyfile(picture, target)
    total = target.stat().st_size
    print(f"Wrote {target} ({total} bytes)")


if __name__ == "__main__":
    run()
