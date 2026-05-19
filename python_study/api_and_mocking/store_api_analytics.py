import requests

def analyze_electronic():
    url = "https://fakestoreapi.com/products"
    response = requests.get(url)
    data = response.json()
    highest_price = 0
    for item in data:
        # if item["category"] == "electronics":
        if "electronics" in item["category"]:
            if highest_price < item["price"]:
                highest_price = item["price"]
            print(f'{item["title"]} | {item["price"]}$')
    print(f'Highest price: {highest_price}$')


if __name__ == "__main__":
    analyze_electronic()