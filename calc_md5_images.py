import os
import hashlib
from datetime import datetime

IMAGES_DIR = "images"
LETTERS_FILE = "letters.txt"
LOG_FILE = "process.log"


def log(message: str, level: str = "INFO") -> None:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as log_file:
        log_file.write(f"[{timestamp}] [{level}] {message}\n")


def load_existing_md5() -> set[str]:
    md5_set = set()
    if not os.path.exists(LETTERS_FILE):
        return md5_set

    with open(LETTERS_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if "_" in line:
                md5, _ = line.split("_", 1)
                md5_set.add(md5)

    return md5_set


def calculate_md5(file_path: str) -> str:
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def extract_captcha_from_filename(filename: str) -> str | None:
    name, _ = os.path.splitext(filename)
    parts = name.split("_")
    if len(parts) < 4:
        return None
    return parts[-1]


def main() -> None:
    existing_md5 = load_existing_md5()
    added = 0

    for filename in os.listdir(IMAGES_DIR):
        if not filename.lower().endswith(".jpg"):
            continue

        file_path = os.path.join(IMAGES_DIR, filename)

        captcha_value = extract_captcha_from_filename(filename)
        if not captcha_value:
            log(f"filename format invalid: {filename}", "ERROR")
            continue

        try:
            md5_hash = calculate_md5(file_path)
        except Exception as e:
            log(f"failed to read file {filename}: {e}", "ERROR")
            continue

        if md5_hash in existing_md5:
            log(f"md5 already exists: {md5_hash} ({filename})", "DUPLICATE")
            continue

        with open(LETTERS_FILE, "a", encoding="utf-8") as f:
            f.write(f"{md5_hash}_{captcha_value}\n")

        existing_md5.add(md5_hash)
        added += 1
        log(f"added md5={md5_hash} captcha={captcha_value}")

    log(f"processing finished, added {added} new entries", "INFO")


if __name__ == "__main__":
    main()
