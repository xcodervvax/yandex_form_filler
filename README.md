В проекте создаем [text](data.json)

```json
{
  "url": "https://eais.rkn.gov.ru/",
  "fields": [
    {
      "selector": ".inputMsg",
      "values": [
        "m.intimcity.vin",
        "intimcity.vin",
        "https://gro.intimcity.vin/",
        "https://m.intimcity.icu",
        "https://intimcity.icu",
        "https://a.intimcity.icu/",
        "m.intimstory.lol",
        "intimstory.lol",
        "https://huq.intimstory.lol/",
        "https://btfih.intimcity.uno/",
        "https://btfon.intimstory.cfd/"
      ]  
    }
  ],
  "submit": "input[type='submit']",
  "blocked_text": "орган, принявший решение о внесении в реестр",
  "pause_seconds": 8
}
```
и [text](announcement.json)

```json
{
  "url": "https://huq.intimstory.lol/admin.php",
  "dashboard": "https://huq.intimstory.lol/bullboard?dop=bullboard",
  "selectorLogin": "input[name=NEW_AUTH_USER]",
  "valueLogin": "antivirgin",
  "selectorPass": "input[name=NEW_AUTH_PW]",
  "valuePass": "123456",
  "submit": "input[type='submit'][value='Войти']",
  "days_range": ["Сегодня", "Вчера"],
  "pause_seconds": 30
}
```
Для создания виртуального окружения:
```bash
python3 -m venv venv
```

Генерация lock-файлов:
```bash
pip3 install pip-tools

pip-compile requirements/base.in
pip-compile requirements/api.in
pip-compile requirements/vision.in
```

получаешь чистые *.txt с зафиксированными версиями

Для восстановления необходимо ввести команду, если мы хотим только что-то отдельное:
```bash
pip3 install -r requirements/api.txt
pip3 install -r requirements/vision.txt

pip3 install -r requirements/api.txt -r requirements/vision.txt
```

Как добавлять новую зависимость (правильно). Пример: добавил httpx в API. Открыл api.in, добавить
```bash
httpx
```
после этого выполнить
```bash
pip-compile requirements/api.in
```

А если временно ставил пакет в venv?
```bash
pip3 install some-lib
pip3 uninstall some-lib   # если не нужен
```