import json
import time
from seleniumbase import SB
from selenium.webdriver.common.by import By

# === 1. Загрузка конфигурации ===
with open("data.json", "r", encoding="utf-8") as f:
    config = json.load(f)

url = config["domain_reputation_url"]
selector = config["input_dom_rep"]
values = config["fields"][0]["values"]
pause_seconds = config.get("pause_seconds", 5)

# Индексы, которые нужно проверять (0, 3, 6)
check_indices = [0, 3, 6]

print(f"🌐 Проверка через Domain Reputation: {url}")

with SB(uc=True, headless=False, incognito=True) as sb:
    sb.open(url)
    sb.wait_for_ready_state_complete()
    print("✅ Страница загружена")

    for i in check_indices:
        if i >= len(values):
            print(f"⚠ Индекс {i} выходит за пределы списка значений")
            continue

        value = values[i]
        print(f"\n🔎 Проверка {i+1}/{len(values)}: {value}")

        try:
            sb.wait_for_element(selector, timeout=10)
            sb.clear(selector)
            sb.type(selector, value)
            print(f"➡️ Введено: {value}")
            sb.send_keys(selector, "\n")  # имитация нажатия Enter

            # Даем время для обработки события ввода
            time.sleep(3)

            # Ищем блок "Reputation score" и следующий div
            reputation_header = sb.find_element("//h4[contains(text(), 'Reputation score')]")
            reputation_value_div = reputation_header.find_element(By.XPATH, "following-sibling::div[1]")
            reputation_score_text = reputation_value_div.text.strip()

            # Пытаемся преобразовать в число
            try:
                reputation_score = float(reputation_score_text)
            except ValueError:
                reputation_score = None

            if reputation_score is not None:
                print(f"📊 Reputation score: {reputation_score}")
                if reputation_score < 0:
                    screenshot_path = f"screens/bad_{i}_{int(time.time())}.png"
                    sb.save_screenshot(screenshot_path)
                    print(f"❌ Репутация отрицательная, скриншот сохранён: {screenshot_path}")
                else:
                    print(f"✅ Репутация положительная")
            else:
                print(f"⚠ Не удалось определить числовое значение репутации")
                screenshot_path = f"screens/unknown_{i}_{int(time.time())}.png"
                sb.save_screenshot(screenshot_path)

        except Exception as e:
            print(f"⚠ Ошибка при проверке {value}: {e}")

        # Возврат на главную страницу
        sb.open(url)
        sb.wait_for_ready_state_complete()
        time.sleep(pause_seconds)

    print("\n🎯 Проверка завершена.")