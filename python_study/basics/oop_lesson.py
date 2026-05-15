# class Car:
#     def __init__(self, make, model):
#         self.make = make
#         self.model = model
#
#
#     def show_info(self):
#         print(f'Make: {self.make}; Model: {self.model};')
#
#
# car1 = Car(make = 'audi', model = 'a3' )
# car1.show_info()
#
#
# class Rectangle:
#     def __init__(self, width, height):
#         self.width = width
#         self.height = height
#
#
#     def calculate_area(self):
#         return self.width * self.height
#
#
# square_rectangle = Rectangle(width=24, height=3)
# print(f'Square of rectangle: {square_rectangle.calculate_area()}')
#
#
# print(f'\n---------------------------------------------\n')
# class BankAccount:
#     def __init__(self, owner: str, balance=0):
#         self.balance = balance
#         self.owner = owner
#
#
#     def deposit(self, amount: int):
#         self.balance += amount
#         print(f'Рахунок поповненно {amount}. Поточний баланс: {self.balance}')
#
#
#     def withdraw(self, amount: int):
#         if amount <= self.balance:
#             self.balance -= amount
#             print(f'Успішно знято: {amount}. Залишок {self.balance}')
#         else:
#             print(f'Недостатньо коштів на рахунку лише {self.balance}')
#
#
# i_account = BankAccount('bob', 100)
# i_account.deposit(100)
# i_account.withdraw(100)
# i_account.withdraw(100)
# i_account.deposit(1000)
#
# print(f'\n---------------------------------------------\n')
#
# class Library:
#     def __init__(self):
#         self.books = []
#         self.members = []
#
#
#     def add_book(self, book):
#         self.books.append(book)
#         print(f'Added book: {book}')
#
#
#     def remove_book(self, book):
#         self.books.remove(book)
#         print(f'Removed book: {book}')
#
#
#     def add_member(self, member):
#         self.members.append(member)
#         print(f'Added member: {member}')
#
#
#     def remove_member(self, member):
#         self.members.remove(member)
#         print(f'Removed member: {member}')
#
#
#     def checkout_book(self, member, book):
#         if book in self.books and member in self.members:
#             self.remove_book(book)
#         elif book not in self.books:
#             print(f'Book {book} not in library')
#         elif member not in self.members:
#             print(f'Member {member} not registered in library')
#
#
#     def return_book(self, book, member):
#         if book not in self.books and member in self.members:
#             self.add_book(book)
#             print(f'Book {book} returned to library')
#         elif book in self.books:
#             print(f'Book {book} already in library')
#         elif member not in self.members:
#             print(f'Member {member} not registered in library')
#
#
# # 1. Створюємо бібліотеку
# my_library = Library()
#
# # 2. Додаємо книги та читачів
# my_library.add_book("1984")
# my_library.add_book("Python Crash Course")
# my_library.add_member("Illia")
#
# # 3. Тестуємо видачу
# my_library.checkout_book("Illia", "1984") # Успішно
# my_library.checkout_book("Illia", "kobzar") # Помилка (немає книги)
# my_library.checkout_book("Ivan", "Python Crash Course") # Помилка (немає читача)
#
# # 4. Тестуємо повернення
# my_library.return_book("1984", "Illia") # Успішно повернуто
#
#
from soupsieve.util import lower

l = []
i = 0
while i <= 5:
    l.append(0)
    i += 1
print(l)