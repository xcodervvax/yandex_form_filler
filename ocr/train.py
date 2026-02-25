import argparse
import json
from pathlib import Path
from typing import List, Sequence, Tuple

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.nn.utils import clip_grad_norm_
from torch.utils.data import DataLoader, random_split

from alphabet import char2idx, idx2char
from dataset import CaptchaDataset
from model import CRNN
from preprocessing import DEFAULT_CROP_MARGINS, IMG_HEIGHT, IMG_WIDTH, build_captcha_transform


def encode_labels(labels: Sequence[str], label_length: int) -> torch.Tensor:
    encoded = []
    for text in labels:
        if len(text) != label_length:
            raise ValueError(f"Label length mismatch: expected {label_length}, got {len(text)} for {text!r}")
        row = []
        for ch in text:
            if ch not in char2idx:
                raise ValueError(f"Unsupported char in label: {ch!r} from {text!r}")
            row.append(char2idx[ch])
        encoded.append(row)
    return torch.tensor(encoded, dtype=torch.long)


def make_collate_fn(label_length: int):
    def collate_fn(batch):
        images, labels = zip(*batch)
        images = torch.stack(images, dim=0)
        targets = encode_labels(labels, label_length)
        return images, targets, labels

    return collate_fn


def decode_logits(seq_logits: torch.Tensor) -> List[str]:
    preds = seq_logits.argmax(dim=2)  # [B, L]
    results = []
    for row in preds:
        results.append("".join(idx2char[idx.item()] for idx in row))
    return results


def compute_char_accuracy(pred_texts: Sequence[str], gt_texts: Sequence[str]) -> float:
    correct = 0
    total = 0
    for pred, gt in zip(pred_texts, gt_texts):
        total += len(gt)
        correct += sum(1 for p, g in zip(pred, gt) if p == g)
    return (correct / total) if total > 0 else 0.0


def run_epoch(
    model,
    loader,
    criterion,
    optimizer,
    device,
    grad_clip,
    train_mode,
):
    model.train(mode=train_mode)
    total_loss = 0.0
    all_preds = []
    all_gt = []

    for images, targets, labels in loader:
        images = images.float().to(device)
        targets = targets.to(device)

        if train_mode:
            optimizer.zero_grad(set_to_none=True)

        logits_tbc = model(images)  # [T, B, C]
        seq_logits = logits_tbc.permute(1, 2, 0)  # [B, C, T]
        seq_logits = F.adaptive_avg_pool1d(seq_logits, output_size=targets.size(1))
        seq_logits = seq_logits.permute(0, 2, 1).contiguous()  # [B, L, C]

        loss = criterion(seq_logits.view(-1, seq_logits.size(-1)), targets.view(-1))

        if train_mode:
            loss.backward()
            clip_grad_norm_(model.parameters(), max_norm=grad_clip)
            optimizer.step()

        total_loss += loss.item()
        batch_preds = decode_logits(seq_logits.detach())
        all_preds.extend(batch_preds)
        all_gt.extend(labels)

    avg_loss = total_loss / max(1, len(loader))
    seq_acc = sum(p == g for p, g in zip(all_preds, all_gt)) / max(1, len(all_gt))
    char_acc = compute_char_accuracy(all_preds, all_gt)
    return avg_loss, seq_acc, char_acc


def build_loaders(args):
    crop_margins = None if args.no_crop else DEFAULT_CROP_MARGINS
    transform = build_captcha_transform(
        image_size=(IMG_HEIGHT, IMG_WIDTH),
        crop_margins=crop_margins,
        use_denoise=args.use_denoise,
    )
    dataset = CaptchaDataset(args.data_dir, args.labels_file, transform=transform)

    if len(dataset) < 2:
        raise ValueError("Need at least 2 labeled images for train/val split")

    label_lengths = {len(text) for text in dataset.labels.values()}
    if len(label_lengths) != 1:
        raise ValueError(f"All labels must have the same length, got lengths: {sorted(label_lengths)}")
    label_length = next(iter(label_lengths))

    val_size = max(1, int(len(dataset) * args.val_ratio))
    train_size = len(dataset) - val_size
    if train_size < 1:
        train_size = len(dataset) - 1
        val_size = 1

    split_gen = torch.Generator().manual_seed(args.seed)
    train_ds, val_ds = random_split(dataset, [train_size, val_size], generator=split_gen)

    collate_fn = make_collate_fn(label_length)
    train_loader = DataLoader(
        train_ds,
        batch_size=args.batch_size,
        shuffle=True,
        collate_fn=collate_fn,
        num_workers=args.num_workers,
        pin_memory=torch.cuda.is_available(),
    )
    val_loader = DataLoader(
        val_ds,
        batch_size=args.batch_size,
        shuffle=False,
        collate_fn=collate_fn,
        num_workers=args.num_workers,
        pin_memory=torch.cuda.is_available(),
    )
    return train_loader, val_loader, len(dataset), train_size, val_size, label_length, crop_margins


def save_checkpoint(
    path: Path,
    model,
    optimizer,
    epoch: int,
    metrics: dict,
    args,
    label_length: int,
    crop_margins,
):
    payload = {
        "model_state": model.state_dict(),
        "optimizer_state": optimizer.state_dict(),
        "epoch": epoch,
        "metrics": metrics,
        "config": {
            "hidden_size": args.hidden_size,
            "img_height": IMG_HEIGHT,
            "img_width": IMG_WIDTH,
            "crop_margins": crop_margins,
            "use_denoise": args.use_denoise,
            "label_length": label_length,
        },
    }
    torch.save(payload, path)


def parse_args():
    parser = argparse.ArgumentParser(description="Train CRNN for captcha recognition")
    parser.add_argument("--data-dir", default="data/train")
    parser.add_argument("--labels-file", default="data/train/labels.txt")
    parser.add_argument("--output-dir", default="checkpoints")
    parser.add_argument("--epochs", type=int, default=40)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--lr", type=float, default=1e-3)
    parser.add_argument("--val-ratio", type=float, default=0.15)
    parser.add_argument("--hidden-size", type=int, default=256)
    parser.add_argument("--grad-clip", type=float, default=5.0)
    parser.add_argument("--num-workers", type=int, default=0)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--use-denoise", action="store_true")
    parser.add_argument("--no-crop", action="store_true")
    return parser.parse_args()


def main():
    args = parse_args()
    torch.manual_seed(args.seed)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Device: {device}")

    train_loader, val_loader, dataset_size, train_size, val_size, label_length, crop_margins = build_loaders(args)
    print(f"Dataset size: {dataset_size} (train={train_size}, val={val_size})")
    print(f"Label length: {label_length}")

    model = CRNN(hidden_size=args.hidden_size).to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=args.lr)

    best_score = (-1.0, -1.0, float("-inf"))
    history = []

    for epoch in range(1, args.epochs + 1):
        train_loss, train_seq_acc, train_char_acc = run_epoch(
            model,
            train_loader,
            criterion,
            optimizer,
            device,
            args.grad_clip,
            train_mode=True,
        )

        with torch.no_grad():
            val_loss, val_seq_acc, val_char_acc = run_epoch(
                model,
                val_loader,
                criterion,
                optimizer,
                device,
                args.grad_clip,
                train_mode=False,
            )

        metrics = {
            "train_loss": train_loss,
            "train_seq_acc": train_seq_acc,
            "train_char_acc": train_char_acc,
            "val_loss": val_loss,
            "val_seq_acc": val_seq_acc,
            "val_char_acc": val_char_acc,
        }
        history.append({"epoch": epoch, **metrics})

        print(
            f"Epoch {epoch:03d} | "
            f"train_loss={train_loss:.4f} train_seq_acc={train_seq_acc:.3f} train_char_acc={train_char_acc:.3f} | "
            f"val_loss={val_loss:.4f} val_seq_acc={val_seq_acc:.3f} val_char_acc={val_char_acc:.3f}"
        )

        last_path = output_dir / "last.pt"
        save_checkpoint(last_path, model, optimizer, epoch, metrics, args, label_length, crop_margins)

        score = (val_seq_acc, val_char_acc, -val_loss)
        if score > best_score:
            best_score = score
            best_path = output_dir / "best.pt"
            save_checkpoint(best_path, model, optimizer, epoch, metrics, args, label_length, crop_margins)
            print(f"  Saved new best checkpoint: {best_path}")

    history_path = output_dir / "history.json"
    history_path.write_text(json.dumps(history, indent=2), encoding="utf-8")
    print(f"Training complete. History saved to: {history_path}")


if __name__ == "__main__":
    main()