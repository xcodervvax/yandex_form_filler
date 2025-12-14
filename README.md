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