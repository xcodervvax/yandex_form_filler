from pathlib import Path
from PIL import Image
import torch
from torch.utils.data import Dataset
import torchvision.transforms as T
import cv2
import numpy as np

def denoise_pil(img):
    """Удаляем мелкий шум с изображения PIL.Image"""
    img_np = np.array(img)
    img_np = cv2.medianBlur(img_np, 3)
    img_np = cv2.fastNlMeansDenoisingColored(
        img_np, None, h=10, hColor=10, templateWindowSize=7, searchWindowSize=21
    )
    return Image.fromarray(img_np)

class CaptchaDataset(Dataset):
    def __init__(self, root, labels_file):
        self.root = Path(root)

        # --- load labels ---
        self.labels = {}
        with open(labels_file, "r") as f:
            for line in f:
                name, text = line.strip().split()
                self.labels[name] = text

        # --- keep only images with GT ---
        self.images = [
            p for p in self.root.glob("*.*")
            if p.stem in self.labels and p.suffix.lower() in [".jpg", ".png", ".jpeg"]
        ]

        # --- transforms ---
        self.transform = T.Compose([
            T.Grayscale(),
            T.Lambda(lambda img: img.crop((25, 16, img.width - 25, img.height - 16))),
            T.Resize((32, 256)),  # ширина увеличена
            T.ToTensor(),
        ])

    def __len__(self):
        return len(self.images)

    def __getitem__(self, idx):
        path = self.images[idx]

        img = Image.open(path).convert("RGB")
        img = denoise_pil(img)
        img = self.transform(img)

        label = self.labels[path.stem]
        return img, label
