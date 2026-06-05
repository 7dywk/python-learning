products = [
    {"name": "Phone", "price": 999, "rating": 4.5},
    {"name": "Laptop", "price": 1299, "rating": 4.2},
    {"name": "Tablet", "price": 599, "rating": 4.8},
    {"name": "Watch", "price": 299, "rating": 3.9},
]


sorted_products = sorted(products, key=lambda p: p["price"], reverse=False)

for product in sorted_products:
    print(f'{product["name"]} | {product["price"]} | {product["rating"]}')

print(f'-' * 50)

sorted_products2 = sorted(products, key=lambda p: p["rating"], reverse=True)

for product in sorted_products2:
    print(f'{product["name"]} | {product["price"]} | {product["rating"]}')

print(f'-' * 50)

sorted_products3 = [p for p in products if p["price"] < 700]

for product in sorted_products3:
    print(f'{product["name"]} | {product["price"]} | {product["rating"]}')