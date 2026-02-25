import json
import time
from seleniumbase import SB

# === 1. Загрузка конфигурации ===
with open("data.json", "r", encoding="utf-8") as f:
    config = json.load(f)

url = config["url"]
field = config["fields"][0]
selector = field["selector"]
values = field["values"]
submit_selector = config["submit"]
blocked_text = config.get(
    "blocked_text",
    "Орган, принявший решение о внесении в реестр"
)
pause_seconds = config.get("pause_seconds", 15)

print(f"🌐 Загружаю сайт: {url}")

# === 2. Запуск браузера через SeleniumBase ===
with SB(uc=True, incognito=True, headless=False) as sb:

    sb.open(url)
    sb.wait_for_ready_state_complete()
    sb.wait_for_element("body")
    print("✅ Страница загружена")

    # === 3. Цикл по ссылкам ===
    for i, value in enumerate(values, start=1):
        print(f"\n🔹 Проверяю ссылку {i}/{len(values)}: {value}")

        # Ввод значения
        try:
            sb.wait_for_element(selector, timeout=20)
            sb.clear(selector)
            sb.type(selector, value)
            print(f"➡️ Введено: {value}")
        except Exception as e:
            print(f"⚠ Ошибка при вводе: {e}")
            continue

        # === Блок капчи ===
        while True:
            try:
                captcha_inputs = sb.find_elements(
                    "input[type='text'], "
                    "input[name*='captcha'], "
                    "input[id*='captcha']"
                )

                captcha_value = ""

                for inp in captcha_inputs:
                    v = inp.get_attribute("value")
                    if v and len(v.strip()) == 6:
                        captcha_value = v.strip()
                        break

                if captcha_value:
                    print(f"🤖 Капча введена ({captcha_value}) → автоотправка")
                    sb.click(submit_selector)
                    print("🚀 Кнопка отправки нажата автоматически")
                else:
                    print("⏳ Ждём ввода капчи...")
                    time.sleep(1)
                    continue

                time.sleep(3)

                # Проверка неверного кода
                if sb.is_element_present("#divMsgModal"):
                    modal_text = sb.get_text("#divMsgModal").lower()

                    if "неверно указан защитный код" in modal_text:
                        print("⚠ Неверно введён код. Повторяем ввод капчи.")
                        try:
                            sb.click(
                                "#divMsgModal button, "
                                "#divMsgModal input[value='Закрыть']"
                            )
                        except:
                            sb.execute_script(
                                "document.getElementById('divMsgModal').style.display='none';"
                            )
                        time.sleep(1)
                        continue

                break

            except Exception as e:
                print(f"⚠ Ошибка при обработке капчи: {e}")
                time.sleep(1)
                continue

        time.sleep(5)

        # === Проверка на блокировку ===
        page_source = sb.get_page_source().lower()

        if blocked_text.lower() in page_source:
            try:
                element = sb.find_element(
                    f"//*[contains(translate(., "
                    f"'ОРГАНПРИНЯВШИЙРЕШЕНИЕОВНЕСЕНИИ', "
                    f"'органпринявшийрешениеовнесении'), "
                    f"'{blocked_text.lower()}')]",
                    by="xpath"
                )
                screenshot_path = f"screens/blocked_{i}_{int(time.time())}.png"
                element.screenshot(screenshot_path)
                print(f"📸 Сохранён фрагмент страницы: {screenshot_path}")
            except Exception as e:
                print(f"⚠ Не удалось сделать скриншот блока: {e}")
                fallback_path = f"screens/blocked_full_{i}_{int(time.time())}.png"
                sb.save_screenshot(fallback_path)
                print(f"📸 Сохранён полный скриншот: {fallback_path}")

            time.sleep(pause_seconds)
        else:
            print("✅ Ресурс не заблокирован")

        # === 4. Физическая проверка сайта ===
        check_indexes = [2, 5, 8, 10, 12, 14, 15]

        if i in check_indexes:
            check_value = value.strip()
            if not check_value.startswith("http"):
                check_value = "https://" + check_value

            print(f"\n🌐 Проверка сайта (индекс {i}): {check_value}")

            try:
                sb.open(check_value)
                sb.wait_for_element("body", timeout=20)
                time.sleep(6)

                page_text = sb.get_page_source().lower()

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

                if any(err in page_text for err in error_signatures):
                    print(f"❌ Сайт {check_value} недоступен.")
                    screenshot_path = (
                        f"screens/unavailable_{i}_{int(time.time())}.png"
                    )
                    sb.save_screenshot(screenshot_path)
                    print(f"📸 Скриншот сохранён: {screenshot_path}")
                else:
                    print(f"✅ Сайт {check_value} доступен.")
            except Exception as e:
                print(f"⚠ Ошибка при проверке сайта: {e}")

        # Возврат на главную страницу
        sb.open(url)
        sb.wait_for_element(selector)

    print("\n🎯 Проверка завершена.")