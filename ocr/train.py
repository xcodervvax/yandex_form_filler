# train.py
import torch
import torch.nn as nn
from torch.utils.data import DataLoader

from dataset import CaptchaDataset
from model import CRNN
from alphabet import char2idx, BLANK_IDX


# =====================
# Utils
# =====================
def encode_labels(labels):
    """
    labels: list[str]
    returns:
      targets: 1D LongTensor (concatenated)
      lengths: LongTensor
    """
    targets = []
    lengths = []

    for text in labels:
        encoded = [char2idx[c] for c in text]
        targets.extend(encoded)
        lengths.append(len(encoded))

    return (
        torch.tensor(targets, dtype=torch.long),
        torch.tensor(lengths, dtype=torch.long),
    )


def collate_fn(batch):
    """
    batch: list of (img, label)
    """
    images, labels = zip(*batch)
    images = torch.stack(images, dim=0)

    targets, target_lengths = encode_labels(labels)

    return images, targets, target_lengths, labels


# =====================
# Train
# =====================
def main():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print("Device:", device)

    dataset = CaptchaDataset("data/train")
    dataset.images = dataset.images[:8]
    loader = DataLoader(
        dataset,
        # batch_size=16,
        batch_size=4,
        shuffle=True,
        # num_workers=2,
        collate_fn=collate_fn,
    )

    model = CRNN(hidden_size=256).to(device)

    criterion = nn.CTCLoss(blank=BLANK_IDX, zero_infinity=True)
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)

    model.train()

    for epoch in range(30):
        total_loss = 0.0

        for images, targets, target_lengths, _ in loader:
            images = images.to(device)
            targets = targets.to(device)
            target_lengths = target_lengths.to(device)

            optimizer.zero_grad()

            logits = model(images)
            # logits: [T, B, C]

            T, B, C = logits.size()
            input_lengths = torch.full(
                size=(B,),
                fill_value=T,
                dtype=torch.long,
                device=device,
            )

            log_probs = logits.log_softmax(2)  # по классу
            loss = criterion(log_probs, targets, input_lengths, target_lengths)
            loss.backward()
            optimizer.step()

            total_loss += loss.item()

        avg_loss = total_loss / len(loader)
        print(f"Epoch {epoch+1}: loss = {avg_loss:.4f}")


if __name__ == "__main__":
    main()
