from dataset import CaptchaDataset
import matplotlib.pyplot as plt

ds = CaptchaDataset("data/train")
img, label = ds[0]

plt.imshow(img.squeeze(0), cmap="gray")
plt.title(label)
plt.axis("off")
plt.savefig("debug_sample.png", dpi=400, bbox_inches="tight")
print("Saved to debug_sample.png")
