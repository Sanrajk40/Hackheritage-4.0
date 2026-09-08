"""
ela_utils.py
------------
Error Level Analysis (ELA) heatmap generation.

ELA works by re-saving an image at a known JPEG quality and taking the
per-pixel difference between the original and the re-saved version.
Regions that were edited/pasted/generated after the last "true" save
tend to have a different compression error signature than untouched
regions, which shows up as brighter areas in the ELA map.

This is the standard preprocessing step used before feeding images
into a CNN (ResNet, VGG, etc.) for tamper/forgery classification.
"""

import io
import numpy as np
from PIL import Image, ImageChops, ImageEnhance


def compute_ela(image_path: str, quality: int = 90, scale: int = 15) -> Image.Image:
    """
    Compute an ELA heatmap for a single image.

    Args:
        image_path: path to the input image (jpg/png/etc).
        quality: JPEG quality used for the resave step (lower quality =
            stronger signal but noisier; 85-95 is typical).
        scale: brightness amplification factor so the difference map
            is visible to the human eye / has enough dynamic range for
            a CNN to learn from. 10-20 is typical.

    Returns:
        A PIL.Image (RGB) containing the amplified ELA difference map,
        same width/height as the input image.
    """
    original = Image.open(image_path).convert("RGB")

    # Re-save the image in-memory at a fixed JPEG quality.
    buffer = io.BytesIO()
    original.save(buffer, "JPEG", quality=quality)
    buffer.seek(0)
    resaved = Image.open(buffer)

    # Per-pixel absolute difference between original and resaved.
    diff = ImageChops.difference(original, resaved)

    # Amplify the difference so faint edits become visible / learnable.
    extrema = diff.getextrema()  # ((rmin,rmax),(gmin,gmax),(bmin,bmax))
    max_diff = max(ex[1] for ex in extrema)
    max_diff = max_diff if max_diff != 0 else 1
    computed_scale = min(255.0 / max_diff, scale)

    ela_image = ImageEnhance.Brightness(diff).enhance(computed_scale)
    return ela_image


def compute_ela_array(image_path: str, quality: int = 90, scale: int = 15) -> np.ndarray:
    """Same as compute_ela but returns a uint8 numpy array (H, W, 3)."""
    return np.array(compute_ela(image_path, quality=quality, scale=scale))


def save_ela(image_path: str, out_path: str, quality: int = 90, scale: int = 15) -> None:
    """Compute the ELA map for image_path and save it to out_path."""
    ela_image = compute_ela(image_path, quality=quality, scale=scale)
    ela_image.save(out_path)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate an ELA heatmap for a single image.")
    parser.add_argument("image", help="Path to the input image")
    parser.add_argument("output", help="Path to save the ELA heatmap")
    parser.add_argument("--quality", type=int, default=90)
    parser.add_argument("--scale", type=int, default=15)
    args = parser.parse_args()

    save_ela(args.image, args.output, quality=args.quality, scale=args.scale)
    print(f"Saved ELA heatmap to {args.output}")
