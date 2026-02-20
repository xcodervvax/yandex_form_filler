from pathlib import Path

FILE_PATH = Path("data/train/labels.txt")
PREFIX = "ocr/data/train/"
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


def is_label_line(parts: list[str]) -> bool:
    """
    Проверяет строку формата:
    <something> <6 alnum chars>
    """
    return (
        len(parts) == 2
        and len(parts[1]) == 6
        and parts[1].isalnum()
    )


def normalize_path(token: str) -> str:
    """
    Удаляет префикс и расширение файла.
    """
    # Удаляем префикс
    if token.startswith(PREFIX):
        token = token[len(PREFIX):]

    # Удаляем расширение
    suffix = Path(token).suffix.lower()
    if suffix in ALLOWED_EXTENSIONS:
        token = token[: -len(suffix)]

    return token


def main():
    # Читаем весь файл
    with open(FILE_PATH, "r", encoding="utf-8") as f:
        lines = f.readlines()

    result = []

    for line in lines:
        line = line.strip()
        if not line:
            continue

        parts = line.split()

        if is_label_line(parts):
            # Строку не разбиваем, но нормализуем первую часть
            normalized_first = normalize_path(parts[0])
            result.append(f"{normalized_first} {parts[1]}\n")
        else:
            # Разбиваем и нормализуем каждую запись
            for token in parts:
                normalized = normalize_path(token)
                result.append(f"{normalized}\n")

    # Перезаписываем тот же файл
    with open(FILE_PATH, "w", encoding="utf-8") as f:
        f.writelines(result)


if __name__ == "__main__":
    main()