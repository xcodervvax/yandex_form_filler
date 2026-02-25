from typing import Optional, Tuple

import cv2
import numpy as np
from PIL import Image
import torchvision.transforms as T

# Input image sizes after preprocessing.
IMG_HEIGHT = 32
IMG_WIDTH = 256

# Crop margins from left, top, right, bottom.
DEFAULT_CROP_MARGINS = (25, 16, 25, 16)


def denoise_pil(img: Image.Image) -> Image.Image:
    img_np = np.array(img)
    img_np = cv2.medianBlur(img_np, 3)
    img_np = cv2.fastNlMeansDenoisingColored(
        img_np, None, h=10, hColor=10, templateWindowSize=7, searchWindowSize=21
    )
    return Image.fromarray(img_np)


def safe_crop(
    img: Image.Image, margins: Tuple[int, int, int, int]
) -> Image.Image:
    left, top, right, bottom = margins
    width, height = img.size
    x0 = max(0, left)
    y0 = max(0, top)
    x1 = max(x0 + 1, width - right)
    y1 = max(y0 + 1, height - bottom)
    return img.crop((x0, y0, x1, y1))


def build_captcha_transform(
    image_size: Tuple[int, int] = (IMG_HEIGHT, IMG_WIDTH),
    crop_margins: Optional[Tuple[int, int, int, int]] = DEFAULT_CROP_MARGINS,
    use_denoise: bool = False,
) -> T.Compose:
    transforms = []
    if use_denoise:
        transforms.append(T.Lambda(denoise_pil))
    if crop_margins is not None:
        transforms.append(T.Lambda(lambda img: safe_crop(img, crop_margins)))
    transforms.extend(
        [
            T.Grayscale(),
            T.Resize(image_size),
            T.ToTensor(),
            T.Normalize((0.5,), (0.5,)),
        ]
    )
    return T.Compose(transforms)