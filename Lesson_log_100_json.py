import json


'''
1) чему равен общий вклад топ-3 всех IP по количеству посещений? Указать процентом
2) сколько в файле уникальных IP, с которых на сайт заходили только 1 раз
'''
path = './log_100.json'
ip_dict = {}
j = 0
with open(path, 'r') as f:
    i = json.load(f)
for entry in i:
    ip = entry['ip']
    if ip not in ip_dict:
        ip_dict[ip] = 1
    else:
        ip_dict[ip] += 1
sorted_ip_dict = sorted(ip_dict.items(), key=lambda x: x[1], reverse=True)
while j < 3:
    print(sorted_ip_dict[j])
    j += 1
total_visits = sum(ip_dict.values())
top3_visits = 0
for ip, count in sorted_ip_dict[:3]:
    top3_visits += count
percentage = (top3_visits / total_visits) * 100
print(f'Top-3 IP contribution: {percentage:.2f}%')

print('--------------------------------------')

path = './log_100.json'
val_lst = set()
with open(path, 'r') as f:
    i = json.load(f)
for item in i:
    ip = item.get('ip')
    if ip not in val_lst:
        val_lst.add(ip)
        print(f'IP', ip)
print(f'unique IPs: {len(val_lst)}')






