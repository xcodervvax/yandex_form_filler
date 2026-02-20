import os
from PIL import Image
import numpy as np
import cv2

# Папка с изображениями
DATA_DIR = "data/train/"

# Получаем список всех изображений
files = [f for f in os.listdir(DATA_DIR) if f.lower().endswith((".png", ".jpg", ".jpeg"))]
if not files:
    raise FileNotFoundError(f"В папке {DATA_DIR} нет изображений.")

print(f"Найдено {len(files)} изображений. Начинаем обработку...")

for file_name in files:
    image_path = os.path.join(DATA_DIR, file_name)
    print(f"Обрабатываем: {image_path}")

    # Загружаем изображение
    img = Image.open(image_path).convert("RGB")
    img_np = np.array(img)

    # --- Медианный фильтр для удаления мелких точек ---
    median = cv2.medianBlur(img_np, 3)

    # --- Non-Local Means для снижения шума ---
    denoised = cv2.fastNlMeansDenoisingColored(
        median, None, h=10, hColor=10, templateWindowSize=7, searchWindowSize=21
    )

    # --- Перезаписываем изображение ---
    cv2.imwrite(image_path, cv2.cvtColor(denoised, cv2.COLOR_RGB2BGR))

print("Обработка завершена. Все изображения очищены от мелких шумов.")
