import cv2
import pytesseract
import numpy as np
import os
import csv

# === Конфигурация путей ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGES_DIR = os.path.join(BASE_DIR, "images")
PROCESSED_DIR = os.path.join(BASE_DIR, "processed")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
RESULTS_FILE = os.path.join(OUTPUT_DIR, "results.csv")

# === Создание папок, если их нет ===
os.makedirs(PROCESSED_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# === Настройка Tesseract (если требуется указать путь вручную) ===
pytesseract.pytesseract.tesseract_cmd = r"/usr/bin/tesseract"

# === Подготовка CSV для записи результатов ===
with open(RESULTS_FILE, mode="w", newline="", encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["filename", "recognized_text"])

    # === Обработка всех файлов в папке images ===
    for filename in sorted(os.listdir(IMAGES_DIR)):
        if not filename.lower().endswith((".png", ".jpg", ".jpeg")):
            continue

        file_path = os.path.join(IMAGES_DIR, filename)
        print(f"[INFO] Обрабатываю {filename}...")

        # === Чтение изображения ===
        img = cv2.imread(file_path)
        if img is None:
            print(f"[WARN] Не удалось прочитать файл: {filename}")
            continue

        # === Предобработка изображения ===
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

        # Удаляем шумы морфологическими операциями
        kernel = np.ones((2, 2), np.uint8)
        clean = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=1)

        # === OCR распознавание ===
        text = pytesseract.image_to_string(clean, config="--psm 8")
        recognized_text = text.strip()

        # === Сохраняем очищенное изображение ===
        processed_path = os.path.join(PROCESSED_DIR, filename)
        cv2.imwrite(processed_path, clean)

        # === Запись результата в CSV ===
        writer.writerow([filename, recognized_text])
        print(f"     → Распознанный текст: {recognized_text}")

print("\n✅ Обработка завершена.")
print(f"📁 Результаты сохранены в: {RESULTS_FILE}")
print(f"🖼️ Очищенные изображения в: {PROCESSED_DIR}")
