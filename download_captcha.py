import os
import requests
import time
import requests
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

RUN_TIME = datetime.now().strftime("%H%M%S")

options = Options()
options.binary_location = "/snap/bin/chromium"
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")
options.add_argument("--disable-quic")
options.add_argument("--disable-ipv6")
options.add_argument("--remote-debugging-port=9222")

service = Service('./chromedriver')
driver = webdriver.Chrome(service=service, options=options)

os.makedirs("images", exist_ok=True)

for i in range(100):
    driver.get("https://eais.rkn.gov.ru/")

    # Ждём загрузку CAPTCHA
    captcha_img = driver.find_element(By.ID, "captcha_image")

    # Получаем ссылку на изображение
    src = captcha_img.get_attribute("src")

    response = requests.get(src)

    filename = f"images/img_{RUN_TIME}_{i+1:03d}.jpg"
    with open(filename, "wb") as f:
        f.write(response.content)

    time.sleep(4)

print("✅ 100 учебных изображений сохранено.")
