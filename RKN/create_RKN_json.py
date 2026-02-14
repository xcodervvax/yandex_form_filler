import json
import re

# Функция для очистки ссылки и получения имени файла
def get_image_name(link):
    # Удаляем протокол (http:// или https://)
    link = re.sub(r'^https?://', '', link)
    # Убираем слэш в конце, если есть
    link = link.rstrip('/')
    return link

# Основная функция
def parse_file(input_filename, images_dir='images'):
    records = []
    with open(input_filename, 'r', encoding='utf-8') as file:
        content = file.read()

    # Разделяем по разделителю '---'
    blocks = [block.strip() for block in content.split('---') if block.strip()]

    for block in blocks:
        # Ищем строку с link
        link_match = re.search(r'link:\s*(.+)', block)

        if link_match:
            link = link_match.group(1).strip()
            image_name = get_image_name(link)
            image_path = f"{images_dir}/{image_name}"
        else:
            link = ''
            image_path = ''

        info_match = re.search(r'info:\s*(.+)', block, re.IGNORECASE | re.DOTALL)
        info = info_match.group(1).strip() if info_match else ''
        surname_match = re.search(r'surname:\s*([^\n]+)', block, re.IGNORECASE | re.DOTALL)
        surname = surname_match.group(1).strip() if info_match else ''
        name_match = re.search(r'name:\s*([^\n]+)', block, re.IGNORECASE | re.DOTALL)
        name = surname_match.group(1).strip() if info_match else ''
        patronimic_match = re.search(r'patronimic:\s*([^\n]+)', block, re.IGNORECASE | re.DOTALL)
        patronimic = patronimic_match.group(1).strip() if info_match else ''
        born_year_match = re.search(r'born_year:\s*([^\n]+)', block, re.IGNORECASE | re.DOTALL)
        born_year = born_year_match.group(1).strip() if info_match else ''
        work_place_match = re.search(r'work_place:\s*([^\n]+)', block, re.IGNORECASE | re.DOTALL)
        work_place = work_place_match.group(1).strip() if info_match else ''
        country_match = re.search(r'country:\s*([^\n]+)', block, re.IGNORECASE | re.DOTALL)
        country = country_match.group(1).strip() if info_match else ''
        region_match = re.search(r'region:\s*([^\n]+)', block, re.IGNORECASE | re.DOTALL)
        region = region_match.group(1).strip() if info_match else ''

        # Создаем словарь для записи
        record = {
            'link': link,
            'info': info,
            'image': image_path,
            'surname': surname,
            'name': name,
            'patronimic': patronimic,
            'born_year': born_year,
            'work_place': work_place,
            'country': country,
            'region': region
        }
        records.append(record)

    # Записываем в JSON
    with open('RKN.json', 'w', encoding='utf-8') as outfile:
        json.dump(records, outfile, ensure_ascii=False, indent=4)

# Вызов функции
parse_file('RKN_data.txt')