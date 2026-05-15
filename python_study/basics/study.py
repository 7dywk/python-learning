# 6) Реализовать набор функций для работы со списком:
# • Ввод с клавиатуры/инициализация случайными числами (с параметрами).
# • Вывод списка на экран (в одну строчку).
# • Подсчет максимума и минимума (с индексами).
# • Подсчет количества элементов, равных (больших/меньших) N.
# • Добавление элемента К [в конец массива/на N-ю позицию].
# • Удаление из списка [последнего/Nго элемента].
# • Сортировка списка по (возрастанию/убыванию). Повторяющиеся — убирать.







# input_str = input("Введіть числа через пробіл: ")  # рядок "5 2 9 1 7"
# str_list = input_str.split()  # ["5", "2", "9", "1", "7"]
# num_list = [int(x) for x in str_list]  # [5, 2, 9, 1, 7]
# print(num_list)
#
#
# def min_num():
#     s = 0
#     q = -1
#     i = num_list[0]
#     for min in num_list:
#         q += 1
#         if min < i:
#             i = min
#             s = q
#
#     print("мін число: ", i ,"індекс числа: ", s)
#
#
# min_num()
#
#
# def max_num():
#     s = 0
#     q = -1
#     i = num_list[0]
#     for min in num_list:
#         q += 1
#         if min > i:
#             i = min
#             s = q
#     print("макс число: ", i ,"індекс числа: ", s)
#
#
# max_num()

# input_str = input("Введіть числа через пробіл: ")
# num_list = [int(x) for x in input_str.split()]
# print(num_list)
#
#
# def entered_num():
#     n = int(input("Любе число: "))
#     gre = 0
#     sim = 0
#     low = 0
#     for i in num_list:
#         if i == n:
#             sim += 1
#         elif i > n:
#             gre += 1
#         elif i < n:
#             low += 1
#     return sim, low, gre
#
#
# sim, low, gre = entered_num()
# print("кількість чисел які дорівнюють вашому: ",sim,
#       "кількість чисел менших за ваше:", low,
#       "кількість чисел більших за ваше:", gre)
#
#
# def min_num():
#     min_value = num_list[0]
#     min_index = 0
#
#     for idx, value in enumerate(num_list):
#         if value < min_value:
#             min_value = value
#             min_index = idx
#
#     return min_value, min_index
#
#
# def max_num():
#     max_value = num_list[0]
#     max_index = 0
#
#     for idx, value in enumerate(num_list):
#         if value > max_value:
#             max_value = value
#             max_index = idx
#
#     return max_value, max_index
#
#
# mn, mi = min_num()
# print("мін число:", mn, "індекс:", mi)
#
# mx, xi = max_num()
# print("макс число:", mx, "індекс:", xi)



