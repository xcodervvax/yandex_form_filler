import sys
import os
from datetime import datetime


def remove_duplicates_by_second_arg(file_path: str):
    if not os.path.exists(file_path):
        print(f"❌ Файл не найден: {file_path}")
        return

    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    seen_second_args = set()
    unique_lines = []
    duplicates = []

    for line in lines:
        stripped = line.strip()

        if not stripped:
            continue

        parts = stripped.split()

        if len(parts) < 2:
            print(f"⚠ Пропущена строка (нет второго аргумента): {stripped}")
            unique_lines.append(line)
            continue

        second_arg = parts[1]

        if second_arg in seen_second_args:
            duplicates.append(line)
        else:
            seen_second_args.add(second_arg)
            unique_lines.append(line)

    # Перезаписываем файл без дублей
    with open(file_path, "w", encoding="utf-8") as f:
        f.writelines(unique_lines)

    # Логирование
    if duplicates:
        log_name = f"duplicates_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(log_name, "w", encoding="utf-8") as log:
            log.write("Удалённые строки с дублирующимся вторым аргументом:\n\n")
            log.writelines(duplicates)

        print(f"⚠ Удалено строк: {len(duplicates)}")
        print(f"📝 Лог сохранён: {log_name}")
    else:
        print("✅ Дубликатов по второму аргументу не найдено")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Использование: python script.py <имя_файла>")
    else:
        remove_duplicates_by_second_arg(sys.argv[1])