import requests
from fake_useragent import FakeUserAgent
import os





'''
Зайти на сайт с Риком и Морти: https://rickandmortyapi.com/
Выгрузить с сайта все изображения персонажей с главной страницы (задача делается через запросы, а не через BS4)
'''

# headers = {
#     'accept': '*/*',
#     'accept-language': 'ru-UA,ru;q=0.9',
#     'content-type': 'application/json',
#     'origin': 'https://rickandmortyapi.com',
#     'priority': 'u=1, i',
#     'referer': 'https://rickandmortyapi.com/',
#     'sec-ch-ua': '"Google Chrome";v="143", "Chromium";v="143", "Not A(Brand";v="24"',
#     'sec-ch-ua-mobile': '?0',
#     'sec-ch-ua-platform': '"macOS"',
#     'sec-fetch-dest': 'empty',
#     'sec-fetch-mode': 'cors',
#     'sec-fetch-site': 'same-origin',
#     'user-agent': FakeUserAgent().random,
# }
#
# json_data = {
#     'query': '\n    query randomCharacters($ids: [ID!]!) {\n      charactersByIds(ids: $ids) {\n        id\n        name\n        status\n        species\n        image\n        episode {\n          name\n          id\n        }\n        location {\n          name\n          id\n        }\n      }\n    }\n  ',
#     'variables': {
#         'ids': [
#             262,
#             636,
#             788,
#             785,
#             157,
#             143,
#         ],
#     },
# }

# main_dir = 'images'
# main_page_dir = os.path.join(main_dir, 'main_page')
#
# response = requests.post('https://rickandmortyapi.com/graphql', headers=headers, json=json_data)
# # print(response.status_code)
# d = response.json().get('data', {}).get('charactersByIds', {})
# for elem in d:
#     img_src = elem['image']
#     print(img_src)
'''
2) Зайти на сайт с Риком и Морти: https://rickandmortyapi.com/
Определить в каких эпизодах появлялся персонаж с главной страницы.
Выгрузить все фотографии персонажей из данного эпизода в папку,
которая называется episode_N (N - номер эпизода)
Для создания папок используйте модуль os
'''
# os.mkdir("episode_N")

# d = response.json().get('data').get('charactersByIds')
# for i in d:
#     print(i['episode'][0])