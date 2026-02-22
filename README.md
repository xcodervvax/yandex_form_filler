В проекте создаем [text](data.json)

```json
{
  "url": "https://eais.rkn.gov.ru/",
  "rkn_feedback_url": "https://eais.rkn.gov.ru/feedback/",
  "spam_haus_url": "https://check.spamhaus.org/",
  "domain_reputation_url": "https://www.spamhaus.org/domain-reputation/",
  "fields": [
    {
      "selector": ".inputMsg",
      "values": [
        "intimcity.mba",
        "m.intimcity.mba",
        "b.intimcity.mba",
        "intimcity.cyou",
        "m.intimcity.cyou",
        "a.intimcity.cyou",
        "intimstory.guru",
        "m.intimstory.guru",
        "b.intimstory.guru",
        "intimcity6.top",
        "bta.intimcity6.top",
        "intimstory.cfd",
        "btfon.intimstory.cfd",
        "io.intim-city.site",
        "pr.intimcity.bike",
        "btpr.intimcity6.top"
      ]
    }
  ],
  "submit": "input[type='submit']",
  "input_spam_haus": "input[data-placeholder*='IP']",
  "input_dom_rep": "#textfield-295",
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

получаешь чистые \*.txt с зафиксированными версиями

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
По этой сылке скачиваем необходимый хромдрайвер
https://sites.google.com/chromium.org/driver/downloads?authuser=0
и кладём его в корень проекта

По OCR
Для тренировки модели нужно скачать файлы в папку data/train необходимые файлы.
Предположим, они сохраняются в таком формате img_000830_001.jpg
Внутри нужно создать файл labels.txt, в котором будут прописываться соответсвия
имени файла и его значения, то есть GT (Ground Truth) - Правильный, эталонный текст,
который должен быть на изображении. На выходе получаем PR (Prediction) - Текст,
который предсказала модель OCR
