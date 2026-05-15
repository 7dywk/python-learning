import requests
import time
import hmac
import hashlib
api_key = 'vf68zzv77KVr5157hAZu45jjzTzaVpE0NaJ97YDIvHorQk244admNfDImO21CxpB'
api_secret = 'EZt86wmfCGJCh1I7ixdr2Sl0I7apvQLRJ8EKOt1rulyZsaWXSQpCc7FFXOPl1i51'
timestamp = int(time.time()*1000)
query_string = f'timestamp={timestamp}'
signature = hmac.new(
    api_secret.encode('utf-8'),
    query_string.encode('utf-8'),
    hashlib.sha256
).hexdigest()
headers = {
    'X-MBX-APIKEY': api_key,
}
params = {
    'timestamp': timestamp,
    'signature': signature,
}
url = 'https://api.binance.com/sapi/v1/capital/config/getall'
response = requests.get(url, headers=headers, params=params)
print(f"status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"received: {len(data)} coins")
else:
    print(f"ERROR: {response.text}")
user_symbol = input("enter coin symbol: ").upper()
for coins in data:
    if coins['coin'] == user_symbol:
        if coins['depositAllEnable'] == True and coins['withdrawAllEnable'] == True:
            print(f"deposit: ✅ withdrawal: ✅ ")
        elif coins['depositAllEnable'] == True and coins['withdrawAllEnable'] == False:
            print(f"deposit: ✅ withdrawal: ❌")
        elif coins['depositAllEnable'] == False and coins['withdrawAllEnable'] == True:
            print(f"deposit: ❌ withdrawal: ✅")
        else:
            print(f"deposit: ❌ withdrawal: ❌")
