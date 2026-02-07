import os
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import requests
from datetime import datetime

RUN_TIME = datetime.now().strftime("%H%M%S")

driver = webdriver.Chrome()

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
