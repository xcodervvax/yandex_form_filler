import torch
from model import CRNN

model = CRNN(hidden_size=256)
x = torch.randn(2, 1, 32, 128)

y = model(x)
print("Output shape:", y.shape)
