import json
import time
import subprocess
import sys
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import Select

# === 0. Запуск create_RKN_json.py ===
current_dir = os.path.dirname(os.path.abspath(__file__))
script_path = os.path.join(current_dir, "create_RKN_json.py")

print("Запускаю create_RKN_json.py ...")
result = subprocess.run([sys.executable, script_path])

if result.returncode != 0:
    print("ошибка при выполнении create_RKN_json.py")
    sys.exit(1)

print("create_RKN_json.py успешно выполнен")

# === 1. Загрузка конфигурации  data.json ===
with open("data.json", "r", encoding="utf-8") as f:
    config = json.load(f)

url = config["rkn_feedback_url"]

# === 1a. Загрузка конфигурации  RKN.json ===
with open("RKN.json", "r", encoding="utf-8") as f:
    values = json.load(f)

pause_seconds = config.get("pause_seconds", 15)

# === 2. Настройка Selenium ===
options = Options()
options.binary_location = "/snap/bin/chromium"
# options.binary_location = "/snap/bin/yandex-browser"
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")
options.add_argument("--disable-quic")
options.add_argument("--disable-ipv6")
options.add_argument("--remote-debugging-port=9222")
options.add_experimental_option("detach", True)

service = Service('../chromedriver')
driver = webdriver.Chrome(service=service, options=options)
wait = WebDriverWait(driver, 20)

print(f"🌐 Загружаю сайт: {url}")

driver.get(url)

wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
print("✅ Страница загружена")

# === 3. Цикл по ссылкам ===
for i, value in enumerate(values, start=1):
    print(f"\n🔹 Проверяю ссылку {i}/{len(values)}: {value}")

    try:
        sex = wait.until(
            EC.presence_of_element_located((By.ID, "Type"))
        )

        select = Select(sex)
        select.select_by_value("lgbt")
    except Exception as e:
        print("Ошибка при выборе типа информации: {e}")

    print(value)

    try:
        link = wait.until(
            EC.presence_of_element_located((By.ID, "ResourceUrl"))
        )

        link.clear()
        link_val = value["link"]
        link.send_keys(link_val)
    except Exception as e:
        print("Ошибка при вводе ссылки: {e}")

    
    try:
        image_name = value["image"]

        current_dir = os.path.dirname(os.path.abspath(__file__))
        images_dir = os.path.join(current_dir, "images")

        # Возможные расширения
        possible_extensions = [".jpg", ".jpeg", ".png", ".webp"]

        image_path = None

        if os.path.splitext(image_name)[1]:
            full_path = os.path.join(images_dir, image_name)

            if os.path.exists(full_path):
                image_path = full_path
        else:
            for ext in possible_extensions:
                full_path = os.path.join(images_dir, image_name + ext)

                if os.path.exists(full_path):
                    image_path = full_path
                    break

        if not image_path:
            print(f"Файл не найден: {image_name}")
        else:
            file_input = wait.until(
            EC.presence_of_element_located((By.ID, "screenShot"))
            )

            file_input.send_keys(image_path)
            print(f"Загружено изображение: {image_name}")
    except Exception as e:
        print(f"Ошибка при загрузке изображения: {e}")
# driver.quit()
