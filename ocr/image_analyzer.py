import os
from PIL import Image
import numpy as np
import cv2

# Папка с изображениями
DATA_DIR = "data/train/"

# Получаем список файлов
files = [f for f in os.listdir(DATA_DIR) if f.lower().endswith((".png", ".jpg", ".jpeg"))]
if not files:
    raise FileNotFoundError(f"В папке {DATA_DIR} нет изображений.")

# Берём первое изображение
first_image_path = os.path.join(DATA_DIR, files[0])
print(f"Анализируем: {first_image_path}")

# Загружаем изображение с Pillow
img = Image.open(first_image_path)

# --- Проверка маски (альфа-канал) ---
has_mask = False
if img.mode in ("RGBA", "LA") or ("transparency" in img.info):
    has_mask = True
print(f"Маска (альфа-канал) присутствует: {has_mask}")

# --- Определение шума ---
# Конвертируем в grayscale
gray = cv2.cvtColor(np.array(img.convert("RGB")), cv2.COLOR_RGB2GRAY)
# Фильтр Лапласа для оценки шума
laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
# Порог можно подобрать эмпирически
noise_threshold = 100.0
has_noise = laplacian_var > noise_threshold
print(f"Наличие шума: {has_noise} (laplacian_var={laplacian_var:.2f})")

# --- Определение слоёв ---
# Для PNG/JPG - считаем как 1 слой с возможной маской
layers = 1
if img.mode in ("RGBA", "LA"):
    layers += 1  # альфа-канал как отдельный слой
print(f"Количество слоёв: {layers}")
