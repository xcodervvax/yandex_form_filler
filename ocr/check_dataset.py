from dataset import CaptchaDataset

ds = CaptchaDataset("data/train")

print("Dataset size:", len(ds))

img, label = ds[0]

print("Image shape:", img.shape)
print("Label:", label)
print("Image min/max:", img.min().item(), img.max().item())
