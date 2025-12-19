import os
import cv2
import numpy as np
import random
from sklearn.model_selection import train_test_split

# === Конфигурация ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGES_DIR = os.path.join(BASE_DIR, "images")
OUTPUT_DIR = os.path.join(BASE_DIR, "dataset")
TRAIN_DIR = os.path.join(OUTPUT_DIR, "train")
VAL_DIR = os.path.join(OUTPUT_DIR, "val")

TARGET_SIZE = 32  # размер нормализованного символа
TEST_SPLIT = 0.15  # доля изображений валидации

# === Создание директорий ===
for d in [TRAIN_DIR, VAL_DIR]:
    os.makedirs(d, exist_ok=True)

# === Функция нормализации символа ===
def normalize_char(img, target_size=TARGET_SIZE):
    h, w = img.shape
    square = np.zeros((target_size, target_size), dtype=np.uint8)
    scale = target_size / max(w, h)
    new_w, new_h = int(w * scale), int(h * scale)
    resized = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)
    x_offset = (target_size - new_w) // 2
    y_offset = (target_size - new_h) // 2
    square[y_offset:y_offset + new_h, x_offset:x_offset + new_w] = resized
    return square

# === Основной цикл ===
all_chars = []  # список пар (символ, изображение)

for filename in sorted(os.listdir(IMAGES_DIR)):
    if not filename.lower().endswith((".png", ".jpg", ".jpeg")):
        continue

    label_text = os.path.splitext(filename)[0]  # имя файла = правильный текст капчи
    img_path = os.path.join(IMAGES_DIR, filename)

    img = cv2.imread(img_path)

    if img is None:
        print(f"[WARN] Не удалось прочитать {filename}")
        continue

    # === Предобработка ===
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Бинаризация
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    # --- Удаление линий ---
    # Морфологическая операция: открытие с горизонтальным и вертикальным ядром
    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 1))
    remove_horizontal = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, horizontal_kernel, iterations=1)

    vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 25))
    remove_vertical = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, vertical_kernel, iterations=1)

    # Объединяем результат: вычитаем линии из исходного изображения
    lines_removed = cv2.subtract(thresh, remove_horizontal)
    lines_removed = cv2.subtract(lines_removed, remove_vertical)

    # Удаляем оставшийся шум
    kernel = np.ones((2, 2), np.uint8)
    clean = cv2.morphologyEx(lines_removed, cv2.MORPH_OPEN, kernel, iterations=1)

    # === Контуры ===
    contours, _ = cv2.findContours(clean, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=lambda c: cv2.boundingRect(c)[0])
    
    # === Извлекаем символы ===
    for i, contour in enumerate(contours):
        x, y, w, h = cv2.boundingRect(contour)

        if w < 5 or h < 5:
            continue  # игнорируем шум

        char_img = thresh[y:y+h, x:x+w]
        char_norm = normalize_char(char_img)

        # Определяем метку (если доступна)
        label = label_text[i] if i < len(label_text) else '?'
        all_chars.append((label, char_norm))

# === Разделяем на train/val ===
train_data, val_data = train_test_split(all_chars, test_size=TEST_SPLIT, random_state=42)

# === Функция сохранения ===
def save_chars(data, base_dir):
    for label, img in data:
        label_dir = os.path.join(base_dir, label)
        os.makedirs(label_dir, exist_ok=True)
        file_name = f"{label}_{random.randint(10000, 99999)}.png"
        cv2.imwrite(os.path.join(label_dir, file_name), img)

# === Сохраняем датасеты ===
save_chars(train_data, TRAIN_DIR)
save_chars(val_data, VAL_DIR)

print(f"\n✅ Сегментация завершена:")
print(f"📁 Обучающие данные: {TRAIN_DIR}")
print(f"📁 Валидация: {VAL_DIR}")
print(f"Всего символов: {len(all_chars)} ({len(train_data)} train / {len(val_data)} val)")
