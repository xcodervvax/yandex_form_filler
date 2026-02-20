import torch
from PIL import Image
from torchvision import transforms
from model import CRNN
from alphabet import idx2char, BLANK_IDX

# --- Настройка ---
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = CRNN(hidden_size=256).to(device)
model.load_state_dict(torch.load("crnn.pth", map_location=device))
model.eval()

# --- Трансформация изображения ---
transform = transforms.Compose([
    transforms.Grayscale(),
    transforms.Resize((32, 128)),
    transforms.ToTensor(),
])

def greedy_decode(log_probs):
    preds = log_probs.argmax(2)  # [T, B]
    chars = []
    prev = BLANK_IDX
    for t in range(preds.size(0)):
        p = preds[t, 0].item()  # batch=1
        if p != prev and p != BLANK_IDX:
            chars.append(idx2char[p])
        prev = p
    return "".join(chars)

# --- Предсказание ---
def predict(image_path):
    img = Image.open(image_path).convert("RGB")
    img = transform(img).unsqueeze(0).to(device)  # [B, C, H, W]

    with torch.no_grad():
        logits = model(img)  # [B, C, T]
        if logits.size(0) == 1:
            logits = logits.permute(2, 0, 1)  # [T, B, C]
        log_probs = logits.log_softmax(2)
        text = greedy_decode(log_probs)
    return text

# --- Пример использования ---
if __name__ == "__main__":
    import sys
    image_path = sys.argv[1]
    print("Predicted:", predict(image_path))
