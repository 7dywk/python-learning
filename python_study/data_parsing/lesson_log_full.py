import csv
from datetime import datetime

'''
Файл log_full.csv:
5) найти максимально часто встречающийся IP
6) посчитать в процентах вклад этого IP адреса в общее кол-во запросов 
7) найти последнюю запись в логах с этим IP и выяснить какой user-agent был у этой записи
получить словарь:
suspicious_agent = {
    "ip": '...',            # самый частовстречаемый ip в логах
    'fraction': 70.205,     # процент запросов с таким ip от общего кол-ва запросов
    'count': 29427,         # число запросов с таким IP
    'last': {               # вложенный словарь с 2-мя полями
        'agent': '...',     # последний user-agent для этого ip
        'timestamp': '...', # последний timestap для этого ip
    }
}
'''
path = '../test_data/log_full.csv'
d = {}
all_requests = 0
i = 0
last_log = {}
ip_visited = ''
with open(path, 'r') as f:
    reader = csv.reader(f)
    for row in reader:
        if row[1] not in d:
            d[row[1]] = 1
        else:
            d[row[1]] += 1
    for ip, count in d.items():
        all_requests += count
        if count > i:
            i = count
            ip_visited = ip
    percent_result = (i / all_requests) * 100
    # for row in reader:

    print(f'Top IP : {ip_visited} was visited {i} times')
    print(f'percent : {percent_result:.2f}%')