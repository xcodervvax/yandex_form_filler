import json
import time
import subprocess
import sys
import os
import unicodedata
import random
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
submit_selector = config["submit"]

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
print("Страница загружена")

# === 3. Цикл по ссылкам ===
for i, value in enumerate(values, start=1):
    # print(f"\n🔹 Проверяю ссылку {i}/{len(values)}: {value}")

    # type
    try:
        sex = wait.until(
            EC.presence_of_element_located((By.ID, "Type"))
        )

        select = Select(sex)
        select.select_by_value("lgbt")
    except Exception as e:
        print("Ошибка при выборе типа информации: {e}")

    # url
    try:
        link = wait.until(
            EC.presence_of_element_located((By.ID, "ResourceUrl"))
        )

        link.clear()
        link_val = value["link"]
        link.send_keys(link_val)
    except Exception as e:
        print("Ошибка при вводе ссылки: {e}")

    # image
    try:
        raw_value = value["image"]
        raw_value = unicodedata.normalize("NFC", raw_value.strip())

        current_dir = os.path.dirname(os.path.abspath(__file__))
        images_dir = os.path.join(current_dir, "images")

        # Если это URL — берём домен
        if raw_value.startswith("http://") or raw_value.startswith("https://"):
            parsed = urlparse(raw_value)
            image_name = parsed.netloc.replace("www.", "")
            # поиск файла с любым расширением
            image_path = None
            for filename in os.listdir(images_dir):
                name_without_ext, ext = os.path.splitext(filename)
                if name_without_ext == image_name:
                    image_path = os.path.join(images_dir, filename)
                    break
        else:
            image_name = raw_value
            image_path = None
            for filename in os.listdir(images_dir):
                clean_filename = unicodedata.normalize("NFC", filename.strip())
                if clean_filename == image_name:
                    image_path = os.path.join(images_dir, filename)
                    break

        if not image_path:
            print("Файл не найден:", image_name)
            print("Файлы в папке:", os.listdir(images_dir))
        else:
            print("Найден файл:", image_path)
            file_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "screenShot"))
            )
            file_input.send_keys(image_path)

    except Exception as e:
        print(f"Ошибка при загрузке изображения: {e}")

    checkbox_2 = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[name="MediaTypeU[]"][value="2"]'))
    )
    if not checkbox_2.is_selected():
        checkbox_2.click()

    checkbox_4 = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[name="MediaTypeU[]"][value="4"]'))
    )
    if not checkbox_4.is_selected():
        checkbox_4.click()

    # info
    textarea = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "CommentU"))
    )

    comment_text = value["info"]
    textarea.clear()
    textarea.send_keys(comment_text)

    # surname
    try:
        rln = wait.until(
            EC.presence_of_element_located((By.ID, "ReporterLastName"))
        )

        rln.clear()
        rln_val = value["surname"]
        rln.send_keys(rln_val)
    except Exception as e:
        print("Ошибка при вводе surname: {e}")

    # first_name
    try:
        rfn = wait.until(
            EC.presence_of_element_located((By.ID, "ReporterFirstName"))
        )

        rfn.clear()
        rfn_val = value["first_name"]
        rfn.send_keys(rfn_val)
    except Exception as e:
        print("Ошибка при вводе first_name: {e}")

    # patronimic
    try:
        patronimic = wait.until(
            EC.presence_of_element_located((By.ID, "ReporterMiddleName"))
        )

        patronimic.clear()
        patronimic_val = value["patronimic"]
        patronimic.send_keys(patronimic_val)
    except Exception as e:
        print("Ошибка при вводе patronimic: {e}")
        
    # born_year
    try:
        born_year = wait.until(
            EC.presence_of_element_located((By.ID, "ReporterBirthYear"))
        )

        born_year.clear()
        born_year_val = value["born_year"]
        born_year.send_keys(born_year_val)
    except Exception as e:
        print("Ошибка при вводе born_year: {e}")

    # work_place
    try:
        work_place = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'input.inputMsg[name="ReporterOrg"]')
            )
        )

        work_text = value["work_place"]
        work_place.clear()
        work_place.send_keys(work_text)
    except Exception as e:
        print("Ошибка при вводе work_place: {e}")

    # country
    try:
        country_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'input.inputMsg[name="ReporterCountry"]')
            )
        )

        county_text = value["country"]
        country_input.clear()
        country_input.send_keys(county_text)
    except Exception as e:
        print("Ошибка при вводе country: {e}")

    # region
    try:
        region_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'input.inputMsg[name="ReporterRegion"]')
            )
        )

        region_text = value["region"]
        region_input.clear()
        region_input.send_keys(region_text)
    except Exception as e:
        print("Ошибка при вводе region: {e}")

    # email
    try:
        email_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'input.inputMsg[name="ReporterEmail"]')
            )
        )

        email_text = value["email"]
        email_input.clear()
        email_input.send_keys(email_text)
    except Exception as e:
        print("Ошибка при вводе email: {e}")

    # check email
    send_notification_cb = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[type="checkbox"][name="SendNotification"][value="true"]'))
    )

    # Если ещё не выбран — кликаем
    if not send_notification_cb.is_selected():
        send_notification_cb.click()

    # === Блок капчи ===
    while True:
        try:
        # ищем поле капчи
        captcha_input = WebDriverWait(driver, 60).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "input[type='text'][maxlength='6'], input[name*='captcha'], input[id*='captcha']")
            )
        )

        # ждём пока пользователь введёт 6 символов
        WebDriverWait(driver, 10).until(
            lambda d: len(captcha_input.get_attribute("value").strip()) == 6
        )

        print("🧩 Капча заполнена. Отправляем форму...")

        # ждём пока кнопка станет кликабельной
        button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, submit_selector))
        )
        button.click()

        except Exception as e:
            print("⚠ Ошибка при работе с капчей:", e)
            continue

        # Ждём результат отправки
        try:
            WebDriverWait(driver, 10).until(
                lambda d: d.current_url != url or
                d.find_elements(By.ID, "divMsgModal")
            )
        except:
            print("⚠ Нет ответа от страницы")
            continue

    # Если редирект — успех
    if driver.current_url != url:
        print("✅ Успешный редирект")
        break

    # Проверка модалки
    try:
        modal = driver.find_element(By.ID, "divMsgModal")
        modal_text = modal.text.lower()

        if "неверно указан защитный код" in modal_text:
            print("❌ Неверная капча. Ждём повторного ввода.")
            captcha_input.clear()
            continue

        if "успешно" in modal_text or "принято" in modal_text:
            print("✅ Форма успешно отправлена")
            break

    except:
        print("⚠ Статус не определён")
        continue

    # Небольшая задержка для загрузки результатов
    time.sleep(2)

    # Возврат на главную страницу
    driver.get(url)

print("\n🎯 Скрипт отработал успешно.")
driver.quit()
