import os
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import requests

driver = webdriver.Chrome()

os.makedirs("images", exist_ok=True)

for i in range(100):
    driver.get("https://eais.rkn.gov.ru/")

    # Ждём загрузку CAPTCHA
    captcha_img = driver.find_element(By.ID, "captcha_image")

    # Получаем ссылку на изображение
    src = captcha_img.get_attribute("src")

    response = requests.get(src)

    with open(f"images/img_{i+1}.jpg", "wb") as f:
        f.write(response.content)

    time.sleep(4)

print("✅ 100 учебных изображений сохранено.")
