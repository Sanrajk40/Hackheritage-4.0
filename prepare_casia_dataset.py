"""
prepare_casia_dataset.py
--------------------------
Converts CASIA v2.0 into the train/val/test ELA layout expected by
train_resnet50.py.

CASIA v2.0's real folder structure (this is what you get after
unzipping the dataset, commonly distributed as "CASIA2.0" or
"CASIA 2.0"):

    CASIA2.0/
        Au/                 <- Authentic (real) images
            Au_ani_00001.jpg
            Au_art_00002.jpg
            ...
        Tp/                 <- Tampered (fake) images
            Tp_D_CRN_M_N_cha00035_cha00040_11732.jpg
            Tp_S_NNN_S_N_sec20074_sec20074_01664.tif
            ...

Notes specific to this dataset:

- "Au" = Authentic, "Tp" = Tampered. There is no "real"/"fake" naming
  in the raw download — that's what this script produces.
- Filenames mix .jpg and .tif; both are handled here.
- The public download has a small number of corrupted / near-empty
  files. This script filters out anything under --min_bytes (default
  10KB, a threshold commonly used by others working with this
  dataset) and anything PIL can't open, logging what it skipped.
- A "CASIA 2 Groundtruth" folder with tamper masks may also be
  present alongside Au/ and Tp/ — this script ignores it, since we
  only need image-level real/fake labels for classification, not
  pixel-level localization masks.

Usage:
    python prepare_casia_dataset.py \
        --input /path/to/CASIA2.0 \
        --output dataset \
        --val_split 0.15 --test_split 0.15 \
        --quality 90 --scale 15
"""

import argparse
import random
from pathlib import Path

from PIL import Image

from ela_utils import save_ela

IMG_EXTS = {".jpg", ".jpeg", ".tif", ".tiff", ".png", ".bmp"}
DEFAULT_MIN_BYTES = 10_000  # filters out the known corrupted/near-empty files in CASIA v2


def list_valid_images(folder: Path, min_bytes: int, skipped: list) -> list:
    files = []
    for p in sorted(folder.iterdir()):
        if p.suffix.lower() not in IMG_EXTS:
            continue
        if p.stat().st_size < min_bytes:
            skipped.append((str(p), f"file too small (<{min_bytes} bytes), likely corrupted"))
            continue
        try:
            with Image.open(p) as img:
                img.verify()
        except Exception as e:  # noqa: BLE001
            skipped.append((str(p), f"unreadable image: {e}"))
            continue
        files.append(p)
    return files


def split_list(items, val_split, test_split, seed=42):
    rng = random.Random(seed)
    items = items[:]
    rng.shuffle(items)
    n = len(items)
    n_val = int(n * val_split)
    n_test = int(n * test_split)
    val = items[:n_val]
    test = items[n_val:n_val + n_test]
    train = items[n_val + n_test:]
    return train, val, test


def process_class(class_name, src_files, output_root, split_name, quality, scale, errors):
    out_dir = output_root / split_name / class_name
    out_dir.mkdir(parents=True, exist_ok=True)
    for src_path in src_files:
        out_path = out_dir / (src_path.stem + ".png")
        try:
            save_ela(str(src_path), str(out_path), quality=quality, scale=scale)
        except Exception as e:  # noqa: BLE001
            errors.append((str(src_path), str(e)))


def main():
    parser = argparse.ArgumentParser(description="Prepare CASIA v2.0 as an ELA dataset for ResNet50.")
    parser.add_argument("--input", required=True, type=Path,
                         help="Path to the CASIA2.0 root folder, containing Au/ and Tp/")
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--val_split", type=float, default=0.15)
    parser.add_argument("--test_split", type=float, default=0.15)
    parser.add_argument("--quality", type=int, default=90)
    parser.add_argument("--scale", type=int, default=15)
    parser.add_argument("--min_bytes", type=int, default=DEFAULT_MIN_BYTES,
                         help="Skip files smaller than this many bytes (filters known corrupted files)")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    folder_map = {"real": args.input / "Au", "fake": args.input / "Tp"}
    for class_name, folder in folder_map.items():
        if not folder.is_dir():
            raise FileNotFoundError(
                f"Expected folder '{folder}' not found. "
                f"CASIA v2.0 layout must be {args.input}/Au/ (real) and {args.input}/Tp/ (fake)."
            )

    skipped = []
    errors = []

    for class_name, folder in folder_map.items():
        files = list_valid_images(folder, args.min_bytes, skipped)
        if not files:
            raise ValueError(f"No valid images found in {folder}")

        train_files, val_files, test_files = split_list(
            files, args.val_split, args.test_split, seed=args.seed
        )

        print(f"[{class_name}] ({folder.name}/) total_valid={len(files)} "
              f"train={len(train_files)} val={len(val_files)} test={len(test_files)}")

        process_class(class_name, train_files, args.output, "train", args.quality, args.scale, errors)
        process_class(class_name, val_files, args.output, "val", args.quality, args.scale, errors)
        process_class(class_name, test_files, args.output, "test", args.quality, args.scale, errors)

    if skipped:
        print(f"\nSkipped {len(skipped)} corrupted/invalid file(s) during scan:")
        for path, reason in skipped[:20]:
            print(f"  {path}: {reason}")
        if len(skipped) > 20:
            print(f"  ... and {len(skipped) - 20} more")

    if errors:
        print(f"\n{len(errors)} file(s) failed during ELA processing:")
        for path, err in errors[:20]:
            print(f"  {path}: {err}")

    print(f"\nDone. Dataset written to: {args.output.resolve()}")
    print(f"Train with (unchanged): python train_resnet50.py --data_dir {args.output} --output_dir runs/casia")


if __name__ == "__main__":
    main()
