from pathlib import Path
from PIL import Image

SRC_DIR = Path("data/train")

# crop params
LEFT = 20
TOP = 12
RIGHT = 200 - 20
BOTTOM = 73 - 12


def main():
    images = list(SRC_DIR.glob("*.jpg"))
    print(f"Found {len(images)} images")

    for path in images:
        img = Image.open(path)

        # sanity check
        if img.size != (200, 80):
            print(f"Skip {path.name}, size={img.size}")
            continue

        cropped = img.crop((LEFT, TOP, RIGHT, BOTTOM))
        cropped.save(path)

    print("Done cropping")


if __name__ == "__main__":
    main()
