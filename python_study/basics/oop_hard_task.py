# '''
# Создайте систему регистрации на конференцию.
# Реализуйте классы Conference (конференция),
# Participant (участник) и RegistrationSystem (система регистрации).
# Класс Conference должен иметь атрибуты name (название) и capacity (вместимость),
# класс Participant - атрибуты name (имя) и email (электронная почта),
# а класс RegistrationSystem - атрибуты conference (конференция) и
# participants (список участников), а также методы register(participant)
# для регистрации участника и is_registration_available() для проверки
# доступности регистрации на конференцию. Реализуйте проверку наличия
# свободных мест на конференции перед регистрацией.
# '''
#
# class Conference:
#     def __init__(self, name, capacity):
#         self.name = name
#         self.capacity = capacity
#         print(f'Conference {self.name} created with capacity {self.capacity}')
#
#
# class Participant:
#     def __init__(self, name, email):
#         self.name = name
#         self.email = email
#         print(f'Participant {self.name} created with email {self.email}')
#
#
# class RegistrationSystem:
#     def __init__(self, conference):
#         self.conference = conference
#         self.participants = []
#
#
#     def is_registration_available(self):
#         return len(self.participants) < self.conference.capacity
#
#
#     def register(self, participant):
#         if self.is_registration_available():
#             self.participants.append(participant)
#             print(f'Registered participant: {participant.name}')
#         else:
#             print(f'Participant {participant.name} is not registered, because {self.conference.name} is already full')
#
#
# # 1. Створюємо конференцію на 2 місця
# my_conference = Conference("Global IT Summit", 3)
#
# # 2. Створюємо систему реєстрації та передаємо їй нашу конференцію
# system = RegistrationSystem(my_conference)
#
# print("\n--- Створюємо людей ---")
#
# user1 = Participant("Олександр", "alex@test.com")
# user2 = Participant("Марія", "maria@test.com")
# user3 = Participant("Іван", "ivan@test.com")
# user4 = Participant("Саша", "sasha@test.com")
#
# print("\n--- Починаємо реєстрацію ---")
#
# system.register(user1)
# system.register(user2)
# system.register(user3)
# system.register(user4)
#
#
# print("\n------- Second task -------\n")
#
#
# '''
# Создайте игру "Магазин животных". Реализуйте базовый класс Animal (животное)
# с атрибутами name (имя) и price (цена), а также методом sound(), который возвращает звук,
# издаваемый животным. От него унаследуйте классы Dog, Cat и Bird, каждый из которых переопределяет
# метод sound() для возврата соответствующего звука для каждого типа животного.
# Класс Shop должен иметь атрибуты animals (список доступных животных)
# и budget (бюджет магазина), а также методы buy_animal(animal) для покупки животного и
# sell_animal(animal) для продажи животного. Реализуйте проверки наличия достаточного бюджета
# у магазина для покупки и наличия животного в магазине для продажи.
# '''
# class Animal:
#     def __init__(self, name, price):
#         self.name = name
#         self.price = price
#
#
#     def sound(self):
#         return "Some sound"
#
#
# class Dog(Animal):
#     def sound(self):
#         return "Bark! Bark!"
#
#
# class Cat(Animal):
#     def sound(self):
#         return "Meow! Meow!"
#
#
# class Bird(Animal):
#     def sound(self):
#         return "Bye!"
#
#
# class Shop:
#     def __init__(self, budget):
#         self.budget = budget
#         animals = []
#
#
#     def buy_animal(self, animal):
#         if animal in self.animals:




import asyncio
import random

from web3 import AsyncWeb3


class Client:
    def __init__(self, rpc: str, private_key: str | None = None):
        self.rpc = rpc

        self.w3 = AsyncWeb3(AsyncWeb3.AsyncHTTPProvider(rpc))
        if private_key:
            self.account = self.w3.eth.account.from_key(private_key=private_key)
        else:
            self.account = self.w3.eth.account.create(extra_entropy=str(random.randint(1, 999_999_999)))

    async def get_balance(self, address: str | None = None):
        if not address:
            address = self.account.address
        return await self.w3.eth.get_balance(account=address)


async def main():
    while True:
        client = Client(rpc='https://rpc.ankr.com/arbitrum')
        # client = Client(rpc='https://arbitrum.llamarpc.com')
        balance = await client.get_balance()
        print(client.account.key.hex(), client.account.address, balance, '\n')
        if balance:
            break


if __name__ == '__main__':
    asyncio.run(main())