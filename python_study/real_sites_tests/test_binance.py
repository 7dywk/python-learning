import requests
import pytest

@pytest.mark.parametrize("symbol", ["BTCUSDT", "ETHUSDT", "SOLUSDT"])

def test_btc_price_is_valid(symbol):
    url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
    response = requests.get(url)
    status = response.status_code
    assert status == 200
    data = response.json()
    assert 'price' in data
    price_str = data['price']
    price_float = float(price_str)
    assert price_float > 0.0
