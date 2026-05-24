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
        return float(cleaned.replace(",", "."))
    except TypeError:
        return None


print(clean_price(raw_data[1]))