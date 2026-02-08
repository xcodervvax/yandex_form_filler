# model.py
import torch
import torch.nn as nn
from alphabet import NUM_CLASSES


class CRNN(nn.Module):
    def __init__(self, hidden_size=256):
        super().__init__()

        # =====================
        # CNN feature extractor
        # =====================
        self.cnn = nn.Sequential(
            # [B, 1, 32, 128]
            nn.Conv2d(1, 64, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2, 2),          # [B, 64, 16, 64]

            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2, 2),          # [B, 128, 8, 32]

            nn.Conv2d(128, 256, kernel_size=3, padding=1),
            nn.BatchNorm2d(256),
            nn.ReLU(inplace=True),

            nn.Conv2d(256, 256, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.MaxPool2d((2, 1)),        # [B, 256, 4, 32]

            nn.Conv2d(256, 512, kernel_size=3, padding=1),
            nn.BatchNorm2d(512),
            nn.ReLU(inplace=True),

            nn.Conv2d(512, 512, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.MaxPool2d((2, 1)),        # [B, 512, 2, 32]

            nn.Conv2d(512, 512, kernel_size=2),  # [B, 512, 1, 31]
            nn.ReLU(inplace=True),
        )

        # =====================
        # RNN sequence modeler
        # =====================
        self.rnn = nn.LSTM(
            input_size=512,
            hidden_size=hidden_size,
            num_layers=2,
            bidirectional=True,
            batch_first=False,
        )

        # =====================
        # Output classifier
        # =====================
        self.fc = nn.Linear(hidden_size * 2, NUM_CLASSES)

    def forward(self, x):
        """
        x: [B, 1, 32, 128]
        returns logits: [T, B, NUM_CLASSES]
        """

        features = self.cnn(x)
        # features: [B, 512, 1, T]

        b, c, h, w = features.size()
        assert h == 1, "Height after CNN must be 1"

        features = features.squeeze(2)      # [B, 512, T]
        features = features.permute(2, 0, 1)  # [T, B, 512]

        rnn_out, _ = self.rnn(features)      # [T, B, 2*hidden]
        logits = self.fc(rnn_out)             # [T, B, NUM_CLASSES]

        return logits
