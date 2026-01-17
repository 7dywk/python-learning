import csv

'''
Файл log_cereals.csv:
3) наименьшая стоимость пачки манки
4) средняя цена на крупу за весь период наблюдений
'''

# path = './log_cereals.csv'
# with open(path) as f:
#     reader = csv.reader(f)
    # val = None
    # for row in reader:
    #     try:
    #         manka = int(row[1])
    #     except ValueError:
    #         continue
    #     if val is None or manka < val:
    #         val = int(manka)
    # print(val)


path = './log_cereals.csv'
with open(path) as f:
    reader = csv.reader(f)
    first_sum = 0
    second_sum = 0
    count = 0
    for row in reader:
        try:
            first = float(row[1].strip())
            second = float(row[2].strip())
        except ValueError:
            continue
        first_sum += first
        second_sum += second
        count += 1
        result = ((first_sum + second_sum) / (count * 2))
    print(first_sum, second_sum, count)
    print(result)