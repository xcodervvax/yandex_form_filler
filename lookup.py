import hashlib
import os
from datetime import datetime

LETTERS_FILE = "letters.txt"
LOG_FILE = "lookup.log"


def log(message: str, level: str = "INFO") -> None:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] [{level}] {message}\n")


def load_letters() -> dict[str, str]:
    mapping: dict[str, str] = {}

    if not os.path.exists(LETTERS_FILE):
        log("letters.txt not found", "ERROR")
        return mapping

    with open(LETTERS_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if "_" not in line:
                log(f"invalid line format: {line}", "ERROR")
                continue

            md5, captcha = line.split("_", 1)
            mapping[md5] = captcha

    log(f"loaded {len(mapping)} md5 entries")
    return mapping


def calculate_md5_from_bytes(data: bytes) -> str:
    return hashlib.md5(data).hexdigest()


def lookup_captcha(image_bytes: bytes, mapping: dict[str, str]) -> str | None:
    md5_hash = calculate_md5_from_bytes(image_bytes)

    if md5_hash in mapping:
        log(f"captcha found md5={md5_hash}")
        return mapping[md5_hash]

    log(f"captcha NOT found md5={md5_hash}", "NOT_FOUND")
    return None


def lookup_from_file(image_path: str, mapping: dict[str, str]) -> str | None:
    try:
        with open(image_path, "rb") as f:
            image_bytes = f.read()
    except Exception as e:
        log(f"failed to read image {image_path}: {e}", "ERROR")
        return None

    return lookup_captcha(image_bytes, mapping)


# ======================
# Example usage
# ======================
if __name__ == "__main__":
    mapping = load_letters()

    test_image = "test.jpg"  # пример
    result = lookup_from_file(test_image, mapping)

    if result:
        print(f"CAPTCHA FOUND: {result}")
    else:
        print("CAPTCHA NOT FOUND")
