properties = [
    {"id": "olx_101", "city": "Lublin", "details": {"rooms": 2, "price": 2500}},
    {"id": "olx_102", "city": "Warsaw", "details": {"rooms": 1}},
    {"id": "olx_103", "city": "Krakow"},
    {"id": "olx_104", "city": "Poznan", "details": {}},
    {"id": "olx_105", "city": "Wroclaw", "details": {"rooms": 3, "price": 3200}},
    {"id": "olx_106", "city": "Lublin"}
]

def get_price(products):
    final_prices = []
    for prop in products:
        details = prop.get("details", {})
        price = details.get("price", 0)
        final_prices.append(price)
    return final_prices

prices = get_price(properties)
print(prices)

clean_prices = [price for price in prices if price > 0]

print(clean_prices)

mean_price = sum(clean_prices) / len(clean_prices)
print(f'Mean price: {mean_price:.2f}')