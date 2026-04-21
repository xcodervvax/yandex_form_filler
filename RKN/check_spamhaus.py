import json
import os
from seleniumbase import SB
import time

# путь к директории текущего скрипта
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# абсолютный путь к data.json
config_path = os.path.join(BASE_DIR, "data.json")

# === 1. Загрузка конфигурации ===
with open(config_path, "r", encoding="utf-8") as f:
    config = json.load(f)

url = config["spam_haus_url"]
selector = config["input_spam_haus"]
values = config["fields"][0]["values"]
pause_seconds = config.get("pause_seconds", 5)

print(f"🌐 Проверка через Spamhaus: {url}")

# папка для скринов
screens_dir = os.path.join(BASE_DIR, "screens")
os.makedirs(screens_dir, exist_ok=True)

with SB(uc=True, headless=False, incognito=True) as sb:
    sb.open(url)
    sb.wait_for_ready_state_complete()

    print("✅ Страница загружена")

    for i, value in enumerate(values, start=1):
        print(f"\n🔎 Проверка {i}/{len(values)}: {value}")

        try:
            # Ждём поле ввода
            sb.wait_for_element(selector, timeout=10)
            sb.clear(selector)
            sb.type(selector, value)
            print(f"➡️ Введено: {value}")
            time.sleep(2)

            # Нажимаем ENTER вместо кнопки
            sb.send_keys(selector, "\n")

            # Ждём результат
            sb.wait_for_ready_state_complete()
            time.sleep(2)

            page_text = sb.get_text("h2.text-brand-blue-5").lower()

            # === Проверка статуса ===
            if " listing" in page_text:
                print(f"❌ {value} В СПИСКЕ Spamhaus")
                screenshot_path = os.path.join(
                    screens_dir,
                    f"listed_{i}_{int(time.time())}.png"
                )
                sb.save_screenshot(screenshot_path)
                print(f"📸 Скриншот сохранён: {screenshot_path}")

            elif "has no issues" in page_text:
                print(f"✅ {value} чистый")

            else:
                print("⚠ Не удалось определить статус")
                screenshot_path = os.path.join(
                    screens_dir,
                    f"unknown_{i}_{int(time.time())}.png"
                )
                sb.save_screenshot(screenshot_path)

        except Exception as e:
            print(f"⚠ Ошибка при проверке {value}: {e}")

        # Возврат на главную страницу
        sb.open(url)
        sb.wait_for_ready_state_complete()
        time.sleep(pause_seconds)

    print("\n🎯 Проверка завершена.")