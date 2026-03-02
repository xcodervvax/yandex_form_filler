import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

# === 1. Загрузка конфигурации ===
with open("data.json", "r", encoding="utf-8") as f:
    config = json.load(f)

url = config["url"]
field = config["fields"][0]
selector = field["selector"]
values = field["values"]
submit_selector = config["submit"]
blocked_text = config.get("blocked_text", "Орган, принявший решение о внесении в реестр")
pause_seconds = config.get("pause_seconds", 15)

# === 2. Настройка Selenium ===
options = Options()
# options.binary_location = "/snap/bin/chromium"
options.binary_location = "/snap/bin/yandex-browser"
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")
options.add_argument("--disable-quic")
options.add_argument("--disable-ipv6")
options.add_argument("--remote-debugging-port=9222")

driver = webdriver.Chrome(service=Service(ChromeDriverManager(driver_version="120.0.6099.109").install()), options=options)
wait = WebDriverWait(driver, 20)

print(f"🌐 Загружаю сайт: {url}")

driver.get(url)

wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
print("✅ Страница загружена")

# === 3. Цикл по ссылкам ===
for i, value in enumerate(values, start=1):
    print(f"\n🔹 Проверяю ссылку {i}/{len(values)}: {value}")

    # Очистка поля и ввод значения
    try:
        element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
        element.clear()
        element.send_keys(value)
        print(f"➡️ Введено: {value}")
    except Exception as e:
        print(f"⚠ Ошибка при вводе: {e}")
        continue

    # === Блок капчи ===
    while True:
        try:
            # Найти инпут капчи
            captcha_inputs = driver.find_elements(By.CSS_SELECTOR, "input[type='text'], input[name*='captcha'], input[id*='captcha']")
            captcha_value = ""

            # Проверяем каждый найденный инпут
            for inp in captcha_inputs:
                v = inp.get_attribute("value").strip()
                if len(v) == 6:
                    captcha_value = v
                    break

            if captcha_value:
                print(f"🤖 Капча введена ({captcha_value}) → автоотправка")
                button = driver.find_element(By.CSS_SELECTOR, submit_selector)
                button.click()
                print("🚀 Кнопка отправки нажата автоматически")
            else:
                # Ждём, пока не появится 6 символов
                print("⏳ Ждём ввода капчи...")
                time.sleep(1)
                continue

            time.sleep(3)

            # Проверка на неверный защитный код
            try:
                modal = driver.find_element(By.ID, "divMsgModal")
                modal_text = modal.text.strip().lower()
                if "неверно указан защитный код" in modal_text:
                    print("⚠ Неверно введён код. Повторяем ввод капчи.")
                    try:
                        close_btn = modal.find_element(By.XPATH, ".//button | .//input[@value='Закрыть']")
                        close_btn.click()
                    except:
                        driver.execute_script("document.getElementById('divMsgModal').style.display='none';")
                    time.sleep(1)
                    continue  # Повторяем попытку
            except:
                pass

            break  # Всё успешно — выходим из while

        except Exception as e:
            print(f"⚠ Ошибка при обработке капчи: {e}")
            time.sleep(1)
            continue

        break  # Всё успешно — выходим из while

    # Небольшая задержка для загрузки результатов
    time.sleep(5)

    # Проверка на блокировку ресурса
    wait = WebDriverWait(driver, 20)
    page_source = driver.page_source.lower()

    if blocked_text.lower() in page_source:
        try:
            # Найти элемент с текстом блокировки
            element = driver.find_element(By.XPATH, f"//*[contains(translate(., 'ОРГАНПРИНЯВШИЙРЕШЕНИЕОВНЕСЕНИИ', 'органпринявшийрешениеовнесении'), '{blocked_text.lower()}')]")
            screenshot_path = f"screens/blocked_{i}_{int(time.time())}.png"
            element.screenshot(screenshot_path)
            print(f"📸 Сохранён фрагмент страницы: {screenshot_path}")
        except Exception as e:
            print(f"⚠ Не удалось сделать скриншот блока: {e}")
            fallback_path = f"blocked_full_{i}_{int(time.time())}.png"
            driver.save_screenshot(fallback_path)

            print(f"📸 Сохранён полный скриншот: {fallback_path}")
        time.sleep(pause_seconds)
    else:
        print("✅ Ресурс не заблокирован")

    # === 4. Физическая проверка сайта для индексов 2, 5, 8 ===
    check_indexes = [2, 5, 8, 10, 12, 14, 15]  # индексы (нумерация начинается с 1)

    if i in check_indexes:
        check_value = value.strip()
        if not check_value.startswith("http"):
            check_value = "https://" + check_value

        print(f"\n🌐 Выполняю физическую проверку сайта (индекс {i}): {check_value}")

        try:
            driver.get(check_value)
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            time.sleep(6)
            page_text = driver.page_source.lower()

            # Список типичных ошибок
            error_signatures = [
                "404 not found",
                "page not found",
                "ошибка 404",
                "forbidden",
                "доступ запрещен",
                "error 403",
                "ошибка сервера",
                "<title>404",
            ]

            # Проверка на типичные ошибки
            if any(err in page_text for err in error_signatures):
                print(f"❌ Сайт {check_value} недоступен или вернул ошибку.")
                # Сохраняем скриншот для отчёта
                screenshot_path = f"screens/unavailable_{i}_{int(time.time())}.png"
                driver.save_screenshot(screenshot_path)
                print(f"📸 Скриншот сохранён: {screenshot_path}")
            else:
                print(f"✅ Сайт {check_value} успешно открылся и доступен.")
        except Exception as e:
            print(f"⚠ Ошибка при проверке сайта {check_value}: {e}")

    # Возврат на главную страницу
    driver.get(url)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))

print("\n🎯 Проверка завершена.")
driver.quit()
