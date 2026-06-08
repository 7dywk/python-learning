properties = [
    {"id": "olx_101", "city": "Lublin", "details": {"rooms": 2, "price": 2500}},
    {"id": "olx_102", "city": "Warsaw", "details": {"rooms": 1}},
    {"id": "olx_103", "city": "Krakow"},
    {"id": "olx_104", "city": "Poznan", "details": {}},
    {"id": "olx_105", "city": "Wroclaw", "details": {"rooms": 3, "price": 3200}},
    {"id": "olx_106", "city": "Lublin"}
]

for prop in properties:
    details = prop.get("details", {})
    price = details.get("price", 0)
    print(price)