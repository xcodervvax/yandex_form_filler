import argparse
from pathlib import Path
from typing import Iterable, List

import torch
import torch.nn.functional as F
from PIL import Image

from alphabet import idx2char
from model import CRNN
from preprocessing import DEFAULT_CROP_MARGINS, IMG_HEIGHT, IMG_WIDTH, build_captcha_transform


def decode_logits(seq_logits: torch.Tensor) -> List[str]:
    preds = seq_logits.argmax(dim=2)  # [B, L]
    results = []
    for row in preds:
        results.append("".join(idx2char[idx.item()] for idx in row))
    return results


def load_checkpoint(checkpoint_path: Path, device: torch.device):
    payload = torch.load(checkpoint_path, map_location=device)
    if isinstance(payload, dict) and "model_state" in payload:
        model_state = payload["model_state"]
        config = payload.get("config", {})
    else:
        model_state = payload
        config = {}
    return model_state, config


def build_transform_from_config(config: dict):
    image_size = (
        int(config.get("img_height", IMG_HEIGHT)),
        int(config.get("img_width", IMG_WIDTH)),
    )
    crop_margins = config.get("crop_margins", DEFAULT_CROP_MARGINS)
    use_denoise = bool(config.get("use_denoise", False))
    return build_captcha_transform(
        image_size=image_size,
        crop_margins=tuple(crop_margins) if crop_margins is not None else None,
        use_denoise=use_denoise,
    )


def predict_one(model: CRNN, image_path: Path, transform, device: torch.device, label_length: int) -> str:
    img = Image.open(image_path).convert("RGB")
    x = transform(img).unsqueeze(0).to(device)
    with torch.no_grad():
        logits_tbc = model(x)  # [T, B, C]
        seq_logits = logits_tbc.permute(1, 2, 0)  # [B, C, T]
        seq_logits = F.adaptive_avg_pool1d(seq_logits, output_size=label_length)
        seq_logits = seq_logits.permute(0, 2, 1).contiguous()  # [B, L, C]
        return decode_logits(seq_logits)[0]


def iter_images(path: Path) -> Iterable[Path]:
    if path.is_file():
        yield path
        return
    exts = {".jpg", ".jpeg", ".png"}
    for image_path in sorted(path.glob("*")):
        if image_path.suffix.lower() in exts:
            yield image_path


def parse_args():
    parser = argparse.ArgumentParser(description="Predict captcha text with trained CRNN")
    parser.add_argument("input", help="Image file or directory")
    parser.add_argument("--checkpoint", default="checkpoints/best.pt")
    parser.add_argument("--hidden-size", type=int, default=256)
    parser.add_argument("--label-length", type=int, default=6)
    return parser.parse_args()


def main():
    args = parse_args()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    checkpoint_path = Path(args.checkpoint)
    if not checkpoint_path.exists():
        raise FileNotFoundError(f"Checkpoint not found: {checkpoint_path}")

    model_state, config = load_checkpoint(checkpoint_path, device)
    hidden_size = int(config.get("hidden_size", args.hidden_size))
    label_length = int(config.get("label_length", args.label_length))

    model = CRNN(hidden_size=hidden_size).to(device)
    model.load_state_dict(model_state)
    model.eval()

    transform = build_transform_from_config(config)

    input_path = Path(args.input)
    if not input_path.exists():
        raise FileNotFoundError(f"Input path not found: {input_path}")

    image_paths = list(iter_images(input_path))
    if not image_paths:
        raise FileNotFoundError(f"No images found at: {input_path}")

    for image_path in image_paths:
        text = predict_one(model, image_path, transform, device, label_length)
        print(f"{image_path.name}\t{text}")


if __name__ == "__main__":
    main()