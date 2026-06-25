from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image


def load_image_tensor(
    image_path: Path,
    input_shape: tuple[int, int, int, int],
    padding_value: int = 114,
) -> np.ndarray:
    batch, channels, target_h, target_w = input_shape
    if batch != 1:
        raise ValueError("only batch size 1 is supported in the first benchmark slice")
    if channels != 3:
        raise ValueError("only 3-channel RGB input is supported in the first benchmark slice")

    with Image.open(image_path) as image:
        rgb = image.convert("RGB")
        resized = letterbox(rgb, target_w=target_w, target_h=target_h, padding_value=padding_value)

    array = np.asarray(resized, dtype=np.float32)
    chw = np.transpose(array, (2, 0, 1))
    return np.expand_dims(chw, axis=0)


def letterbox(image: Image.Image, target_w: int, target_h: int, padding_value: int) -> Image.Image:
    width, height = image.size
    scale = min(target_w / width, target_h / height)
    resized_w = max(1, int(round(width * scale)))
    resized_h = max(1, int(round(height * scale)))
    resized = image.resize((resized_w, resized_h), Image.Resampling.BILINEAR)

    canvas = Image.new("RGB", (target_w, target_h), (padding_value, padding_value, padding_value))
    offset_x = (target_w - resized_w) // 2
    offset_y = (target_h - resized_h) // 2
    canvas.paste(resized, (offset_x, offset_y))
    return canvas

