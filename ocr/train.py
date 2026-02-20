import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from dataset import CaptchaDataset
from model import CRNN
from alphabet import char2idx, idx2char, BLANK_IDX

# -------------------------
# Функции
# -------------------------
def encode_labels(labels):
    targets = []
    lengths = []
    for text in labels:
        encoded = [char2idx[c] for c in text]
        targets.extend(encoded)
        lengths.append(len(encoded))
    return torch.tensor(targets, dtype=torch.long), torch.tensor(lengths, dtype=torch.long)

def collate_fn(batch):
    images, labels = zip(*batch)
    images = torch.stack(images, dim=0)
    targets, target_lengths = encode_labels(labels)
    return images, targets, target_lengths, labels

def greedy_decode(log_probs, idx2char, blank=BLANK_IDX):
    preds = log_probs.argmax(2)  # [T, B]
    results = []
    for b in range(preds.size(1)):
        prev = None
        chars = []
        for t in range(preds.size(0)):
            p = preds[t, b].item()
            if p != prev and p != blank:
                chars.append(idx2char[p])
            prev = p
        results.append("".join(chars))
    return results

def preprocess_batch(images, device):
    return torch.stack([img.float() for img in images]).to(device)

# -------------------------
# Training loop
# -------------------------
def main():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print("Device:", device)

    dataset = CaptchaDataset("data/train", "data/train/labels.txt")
    loader = DataLoader(dataset, batch_size=4, shuffle=True, collate_fn=collate_fn)

    model = CRNN(hidden_size=256).to(device)
    criterion = nn.CTCLoss(blank=BLANK_IDX, zero_infinity=True)
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-4)

    model.train()
    num_epochs = 10

    for epoch in range(num_epochs):
        total_loss = 0.0
        print(f"\n=== Epoch {epoch+1} ===")

        for batch_idx, (images, targets, target_lengths, labels) in enumerate(loader):
            images = preprocess_batch(images, device)
            targets = targets.to(device)
            target_lengths = target_lengths.to(device)

            optimizer.zero_grad()
            logits = model(images)  # [B, T, C] или [T, B, C]

            # Приведение к [T,B,C]
            if logits.dim() == 3 and logits.shape[0] == images.size(0):
                logits = logits.permute(1, 0, 2)

            input_lengths = torch.full(
                size=(images.size(0),), fill_value=logits.size(0), dtype=torch.long
            ).to(device)

            log_probs = logits.log_softmax(2)
            loss = criterion(log_probs, targets, input_lengths, target_lengths)

            loss.backward()

            # Gradient clipping
            from torch.nn.utils import clip_grad_norm_
            clip_grad_norm_(model.parameters(), max_norm=5.0)

            optimizer.step()
            total_loss += loss.item()

            # --- DEBUG DECODE (первые 2 батча) ---
            if batch_idx < 2:
                decoded = greedy_decode(log_probs.detach(), idx2char, BLANK_IDX)
                print("GT:", labels)
                print("PR:", decoded)

        avg_loss = total_loss / len(loader)
        print(f"Epoch {epoch+1} average loss: {avg_loss:.4f}")

if __name__ == "__main__":
    main()
