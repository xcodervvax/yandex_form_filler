from pathlib import Path
from PIL import Image
import torch
from torch.utils.data import Dataset
import torchvision.transforms as T


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
            p for p in self.root.glob("*.jpg")
            if p.stem in self.labels
        ]

        self.transform = T.Compose([
            T.Grayscale(),

            # safe crop
            T.Lambda(lambda img: img.crop((25, 16, img.width - 25, img.height - 16))),

            T.Resize((32, 128)),
            T.ToTensor(),
        ])

    def __len__(self):
        return len(self.images)

    def __getitem__(self, idx):
        path = self.images[idx]

        img = Image.open(path).convert("RGB")
        img = self.transform(img)

        label = self.labels[path.stem]
        return img, label
