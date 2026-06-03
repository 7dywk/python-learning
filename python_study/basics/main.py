# lst = [4, 5, 3, 4, 7, 7, 8, 11, 10,]
# min = lst[0]
# x = 0
# max = lst[0]
# y = 0
# for i in lst:
#     if min > i:
#         min = i
#     if max < i:
#         max = i
# print(x,min, y,max)


# lst = ['milk',
#        'cucmber',
#        'beer',
#        'fish',
#        'tea',
#        'sugar',
#        'chips',
#        ]
# x = 0
# del lst[2], lst[3]
# for i in lst:
#     x += 1
#     print(i)
# print(x,'пунктов')

# 1) Есть 2 словаря. Объединить их без помощи функции update
# d1 = {1: 'one',
#       2: 'two',
#       3:'three',
#       }
# d2 = {4:'four',
#       5:'five',
#       }
# print(d1)
# print(d2)
#
# for key,val in d2.items():
#     d1[key] = val
# print(d1)
# print(d2)



# 2) Есть словарь с числовыми значениями. Посчитать среднюю по значениям
# d1 = {'a': 5, 'b': 5, 'c': 5, 'd': 5, 'e': 5}
#
#
# val_summ = 0
# for val in d1.values():
#
#     val_summ += val
# print(f'сума чисел', val_summ)
# print(f'среднее число:', val_summ//len(d1))


# 3) Даны два списка одинаковой длины. Необходимо создать из них словарь таким образом,
# чтобы элементы первого списка были ключами, а элементы второго — соответственно
# значениями нашего словаря.

# d = {}
#
# lst1 = (4,5,6,)
# lst2 = (1,2,3)
# for i in range(len(lst1)):
#     d[lst1[i]]=lst2[i]
# print(d)




# 4) Когда Антон прочитал «Войну и мир», ему стало интересно,
# сколько слов и в каком количестве используется в этой книге.
# Помогите Антону написать упрощённую версию такой программы,
# которая сможет подсчитать слова, разделённые пробелом и вывести получившуюся статистику.
# Программа должна считывать одну строку со стандартного ввода и выводить для каждого
# уникального слова в этой строке число его повторений (без учёта регистра)
# в формате "слово количество" (см. пример вывода).
# Порядок вывода слов может быть произвольным, каждое уникальное слово  должно выводиться
# только один раз
# fd = 100
# print(f'fdjhsf', fd, 10)
# print(f'/',name, '/', rpc)


# 1) Написать функцию, которая будет искать и выводить на экран минимальное число,
# большее 300 и кратное 19.

#
# def get_smallest_number(a: int | float, b: int | float):
#     if a > 300 and a % 19 == 0:
#         print(a,'подъодит')
#     elif b > 300 and b % 19 == 0:
#         print(b,'подходит')
#     else:
#         print(f'числа не подходят')
# get_smallest_number(a=400, b=20)

# v2

# def foo (i, b):
#     while i < 300 or i % b != 0:
#         i += 1
#     print(i)
# foo(int(input('число')),int(input('второе число')))





# 2) Написать функцию, которая будет обменивать местами
# первую и последнюю цифру числа N (1234 → 4231).

# def swap_digits(n):
#     s = str(n)
#     if len(s) == 1:
#         return n
#     swapped = s[-1] + s[1:-1] + s[0]
#     return int(swapped)

# Виклик функції
# n = int(input("Введи число: "))
# print(swap_digits(n))






#
# 3) Написать функцию, которая будет определять,
# делится ли число N на: 2, 3, 4, 5, ... (без использования оператора % )

# n = int(input("число:" ))
#
#
# def dist (i):
#     if n / i== n // i:
#         print(f'число', n ,'делится на число', i)
#     else:
#         print(f'число', n ,'не делится на число', i)
#
#
# dist(int(input('делится ли число')))

# 4) Написать функцию, которая будет вычислять и выводить на экран значение выражения
# N^M без использования оператора возведения в степень (**).



# def mult(n=10,m=2):
#     i = 0
#     q = 0
#     while i < m:
#         i += 1
#         n * n
#     print(q)









#
# 5) С клавиатуры вводится пять чисел. Для каждого из них вывести,
# является ли оно степенью числа 3. Вынести определение степени в функцию.
#

# a = 27
# i = 1
# while a != i**3:
#     i += 1


#gpt task
# Напиши функцію square_sum(a, b),
# яка обчислює квадрат суми двох чисел — тобто
# (𝑎+𝑏)2(a+b)2
# 🔹 Умови:
# Функція має повертати результат, а не просто виводити його.
# Потім цей результат треба передати в іншу функцію,
# наприклад, у функцію half(x), яка ділить число на 2.

# def square_sum(a, b):
#     return (a+b)**2
#
#
# def half_sum(d):
#     return d/2
#
# final = half_sum(square_sum(4, 5))
# print(final)














#
# portfolio = {
#     "BTC": 0.1,
#     "ETH": 1.5,
#     "SOL": 12,
#
# }
#
# prices = {
#     "BTC": 95000,
#     "ETH": 3000,
#     "SOL": 180,
# }
#
# # Функція для обчислення вартості одного активу
# def asset_value(q):
#     if q in portfolio:
#         return portfolio[q] * prices[q]
#     else:
#         return None
# q = (str(input("введіть назву монети: ")))
#
# value = asset_value(q)
#
# if value is None:
#     print("такої монети немає:", q)
# else:
#     print("вартість монети:", value)
#
#
# # Функція для розрахунку всього портфеля
#
# def portfolio_value():
#     total = 0
#     for q in portfolio:
#         total += asset_value(q)
#     return total
# print('вартість всього портфелю:', portfolio_value())
#
#
# def most_expensive_coin():
#     max_value = 0
#     max_coin = ""
#     for coin in portfolio:
#         value = asset_value(coin)
#         if value > max_value:
#             max_value = value
#             max_coin = coin
#     return max_coin, max_value
#
#
# print('найдорожча монета: ', most_expensive_coin())
#
#
# # 1 — Показати портфель
# # 2 — Додати монету
# # 3 — Перерахувати загальну вартість
# # 4 — Вийти
#
# while True:
#     print("\nМеню:")
#     print("1 — Показати портфель")
#     print("2 — Додати монету")
#     print("3 — Перерахувати загальну вартість")
#     print("4 — Вийти")
#
#     choice = input("Виберіть опцію: ")
#
#     if choice == "1":
#         # показати портфель
#         for coin, amount in portfolio.items():
#             print(coin, "-", amount, "шт")
#     elif choice == "2":
#         # додати монету
#         coin_name = input("Назва монети: ")
#         coin_amount = float(input("Кількість: "))
#         portfolio[coin_name] = coin_amount
#         coin_price = float(input("Ціна монети: "))
#         prices[coin_name] = coin_price
#         print("Монету додано!")
#     elif choice == "3":
#         # перерахувати загальну вартість
#         total = portfolio_value()
#         print("Вартість всього портфеля:", total)
#     elif choice == "4":
#         print("Вихід з програми...")
#         break
#     else:
#         print("Невірний вибір, спробуйте ще раз.")


# def even_or_odd(num):
#     if num % 2 == 0:
#         return ('even')
#     else:
#         return ('odd')
#
#
# print(even_or_odd(10))


# def sum_numbers():
#     user_input = input('Enter a number: ').split()
#
#     total = 0
#     for n in user_input:
#         total += int(n)
#     return total
#
#
# result = sum_numbers()
# print(result)


# print('420' < '5')

'''
1) Паша очень любит кататься на общественном транспорте,
а получая билет, сразу проверяет, счастливый ли ему попался.
Билет считается счастливым, если сумма первых трех цифр совпадает с
суммой последних трех цифр номера билета.
Программа должна выводить “Счастливый” или “Обычный”.  (Решить с помощью индексов строк, то есть без математики)
'''


# num = str(input('ticket num:' ))
# sum1 = int(num[0]) + int(num[1]) + int(num[2])
# sum2 = int(num[-1]) + int(num[-2]) + int(num[-3])
# if sum1 == sum2:
#     print('lucky')
# else:
#     print('default')

'''
2) Дана последовательность символов. Проверить, является ли она палиндромом
(слово или текст, одинаково читающееся в обоих направлениях)
'''
# s = str(input('enter a word: '))
# if s == s[::-1]:
#     print('slovo palindrom')
# else:
#     print('slovo non palindrom')


'''
3) Написать функцию проверки email 
(представьте, что для своего сайта эту функцию пишете. 
Сделать проверки, которые считаете нужными, а я буду пробовать сломать)
'''

# email = str(input('enter email: '))
# lst = email.split('@')
# if lst[1] != 'gmail.com' or len(lst[0]) <= 3:
#     print('not valid email')
# else:
#     print('valid email')

'''
4) Определить количество слов в строке.
Вводится строка, состоящая из слов, разделенных пробелами. 
Требуется посчитать количество слов в ней.
'''
# def quant():
#     sen = str(input('enter sentence: ')).split()
#     q = 0
#     for i in sen:
#         q += 1
#     return q
#
# result = quant()
# print(f'number of words', result)


'''
1) Определить сложность пароля 
(сделать функцию как на обычных сайтах. 
То есть проверять большие буквы, символы, 
цифры И так далее. Подсказка: ascii)
'''

# def password(pswrd):
#     up_char = False
#     digit = False
#     def_char = False
#     length = False
#
#     for char in pswrd:
#         qwe = ord(char)
#         if 65 <= qwe <= 90:
#             up_char = True
#         if 48 <= qwe <= 57:
#             digit = True
#         if 97 <= qwe <= 122:
#             def_char = True
#
#     if len(pswrd) > 8:
#         length = True
#
#     flags = [up_char, digit, def_char, length]
#     return all(flags)
#
# pswrd = input('Enter password:')
#
# if password(pswrd):
#     print('Password accepted')
# else:
#     print('Password rejected')


'''
2) Необходимо написать программу, 
которая сможет посчитать повторяющиеся символы
и вывести сокращенную строку, пример:
Вход: s = 'aaaabbcaa'
Выход: 'a4b2c1a2'
'''
# сам не зробив
# s = 'aaaabbcaa'
# new_s = ''
# i = 0
# while i < len(s):
#     ch = s[i]
#     new_s += ch
#     count = 0
#     while i < len(s) and s[i] == ch:
#         count += 1
#         i += 1
#     new_s += str(count)
# print(new_s)

'''
3) На основании предоставленного отрывка текста определить 3 наиболее часто встречаемых символа в нем. 
Пробелы нужно игнорировать (не учитывать при подсчете). 
Для выведения результатов вычислений требуется написать функцию top3(st). 
Итог работы функции представить в виде строки: «символ – количество раз, символ – количество раз…».
'''

# def foo (s):
#     result_lst = []
#     d = {}
#     for char in s:
#         if char == ' ':
#             continue
#         if char in d:
#             d[char] += 1
#         else:
#             d[char] = 1
#     for key, value in d.items():
#         result_lst.append (f'{key} - {value}')
#     return ', '.join(result_lst)
# s = str(input('enter words: '))
# print(foo(s))


# dict = {'a': 1, 'b': 2, 'c': 3, 'd': 4, 'e': 5, 'f': 6}
# def foo ():
#     for key, value in dict.items():
#         print (key, '-', value)
# foo()

'''
4) Дмитрий считает, что когда текст пишут в скобках 
(как вот тут, например), его читать не нужно. 
Вот и надумал он существенно укоротить время чтения, 
написав функцию, которая будет удалять все, что расположено внутри скобок.
'''

# def text(s):
#     start = s.find('(')
#     end = s.find(')')
#     new_s = s[:start] + s[end + 1:].strip()
#     return new_s
# s = input('Enter text:')
# result = text(s)
# print(result)

# def remove_brackets(text):
#     result = ''
#     inside = False
#     for char in text:
#         if char == '(':
#             inside = True
#         elif char == ')':
#             inside = False
#         elif not inside:
#             result += char
#     return result
#
# text = input('Enter the text:')
# print(remove_brackets(text))



