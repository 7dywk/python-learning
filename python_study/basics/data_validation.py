from cytoolz.functoolz import excepts

raw_data = [
    {"name": "Apple iPhone 14", "price": "999.99$", "rating": "4.5"},
    {"name": "Samsung TV", "price": "abc", "rating": "5.1"},
    {"name": "", "price": "599zł", "rating": "3.8"},
    {"name": "Sony Headphones", "price": None, "rating": ""},
    {"name": "Dell Laptop", "price": "1,299.00€", "rating": "4.2"},
]
#TODO:
'''
Очистити price — прибрати символи валют і повернути float. Якщо не можна — повернути None
Очистити rating — повернути float. Якщо більше 5.0 або порожнє — повернути None
Пропустити товари без імені
Вивести чистий список і окремо список з помилками
'''

def clean_price(raw):
    try:
        cleaned = "".join(filter(lambda c: c.isdigit() or c in ".,", raw))
        if not cleaned:
            return None
        return float(cleaned.replace(",", ""))
    except TypeError:
        return None


def clean_rating(raw):
    try:
        if raw == "":
            return None
        clean_rate = float(raw)
        if clean_rate > 5:
            return None
        else:
            return clean_rate
    except ValueError:
        return None


valid = []
errors = []

for item in raw_data:
    name = item["name"]
    if not name:
        errors.append(f"product without name")
        continue

    price = clean_price(item["price"])
    rating = clean_rating(item["rating"])

    if price is None:
        errors.append(f"{name} | invalid price")
    elif rating is None:
        errors.append(f"{name} | invalid rating")
    else:
        valid.append(f"{name} | {price:.2f}$ | {rating}")


for v in valid:
    print(v)
for e in errors:
    print(e)

