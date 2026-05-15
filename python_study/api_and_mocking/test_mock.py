import requests
from unittest.mock import patch


def get_price(symbol):
    url = f'https://api.binance.com/api/v3/ticker/price?symbol={symbol}'
    response = requests.get(url)
    data = response.json()
    price_str = data['price']
    price_flt = float(price_str)
    return price_flt

@patch('requests.get')
def test_invalid_symbol(mock_requests):
    mock_requests.return_value.json.return_value = {'code': -1121, 'msg': 'invalid symbol'}
    mock_requests.return_value.status_code = 400
    get_price('bob')



@patch('requests.get')
def test_fake_price(mock_requests):
    mock_requests.return_value.json.return_value = {'price': 999.99}
    mock_requests.return_value.status_code = 200
    current_price = get_price('BTCUSDT')
    assert current_price == 999.99

test_fake_price()
test_invalid_symbol()