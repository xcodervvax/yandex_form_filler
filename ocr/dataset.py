from pathlib import Path
from typing import Dict

from PIL import Image
from torch.utils.data import Dataset

from preprocessing import build_captcha_transform


class CaptchaDataset(Dataset):
    def __init__(
        self,
        root: str,
        labels_file: str,
        transform=None,
        allowed_exts=None,
    ):
        self.root = Path(root)
        self.labels_file = Path(labels_file)
        self.allowed_exts = allowed_exts or {".jpg", ".png", ".jpeg"}

        self.labels: Dict[str, str] = self._load_labels(self.labels_file)
        self.images = self._collect_images()
        self.transform = transform or build_captcha_transform()

    def _load_labels(self, labels_file: Path) -> Dict[str, str]:
        labels: Dict[str, str] = {}
        with labels_file.open("r", encoding="utf-8") as f:
            for line_num, raw_line in enumerate(f, start=1):
                line = raw_line.strip()
                if not line:
                    continue
                parts = line.split()
                if len(parts) != 2:
                    raise ValueError(
                        f"Invalid label format in {labels_file}:{line_num}: {raw_line!r}"
                    )
                name, text = parts
                labels[name] = text
        return labels

    def _collect_images(self):
        images = [
            p
            for p in self.root.glob("*.*")
            if p.suffix.lower() in self.allowed_exts and p.stem in self.labels
        ]
        images.sort(key=lambda p: p.name)
        if not images:
            raise FileNotFoundError(
                f"No labeled images found in {self.root} using {self.labels_file}"
            )
        return images

    def __len__(self):
        return len(self.images)

    def __getitem__(self, idx):
        path = self.images[idx]
        img = Image.open(path).convert("RGB")
        img = self.transform(img)
        label = self.labels[path.stem]
        return img, label