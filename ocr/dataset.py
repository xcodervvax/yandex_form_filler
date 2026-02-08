from pathlib import Path
from PIL import Image
import torch
from torch.utils.data import Dataset
import torchvision.transforms as T

class CaptchaDataset(Dataset):
    def __init__(self, root):
        self.images = list(Path(root).glob("*.jpg"))
        self.transform = T.Compose([
            T.Grayscale(),

            # CROP: (top, left, height, width)
            T.Lambda(lambda img: img.crop((
                20,        # left
                12,        # top
                200 - 20,  # right
                73 - 12    # bottom
            ))),

            T.Resize((32, 128)),
            T.ToTensor(),
        ])

    def __len__(self):
        return len(self.images)

    def __getitem__(self, idx):
        path = self.images[idx]
        img = Image.open(path).convert("RGB")
        img = self.transform(img)
        label = path.stem
        return img, label
