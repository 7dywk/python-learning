api_response = {
    "status": "success",
    "timestamp": 1719335949,
    "data": {
        "transactions": [
            {"hash": "0xabc", "details": {"value": 5.2, "from": "0x111", "to": "0x222"}},
            {"hash": "0xdef", "details": {"value": 0.3, "from": "0x333", "to": "0x111"}},
            {"hash": "0xerr", "details": {"from": "0x999", "to": "0x111"}},
            {"hash": "0xjkl", "details": {"value": 1.1, "from": "0x111", "to": "0x666"}},
            {"hash": "0xzzz", "details": None}
        ]
    }
}

def get_info(response, address):
    txs = response["data"]["transactions"]
    sum_value = 0
    hash_list = []
    print(f'tx details')
    print("-" * 30)
    for tx in txs:
        try:
            tx_value = tx["details"].get("value", "no info")
            if tx["details"]["from"] == address or tx["details"]["to"] == address:
                sum_value += tx_value
                for key,value in tx["details"].items():
                    print(f'{key}: {value}')
                print("-"*30)
            if tx_value > 1:
                hash_list.append(tx["hash"])
        except:
            continue

    return f'all txs value: {sum_value:.2f} \nhashes with value above 1: {", ".join(hash_list)}'





result = get_info(api_response, "0x111")
print(result)


'''
"Дістанеться" до самого списку транзакцій крізь верхні рівні словника.

Пройдеться циклом і знайде всі транзакції для адреси "0x111".

Порахує суму value для цих транзакцій.

Головне: Скрипт не повинен впасти з помилкою KeyError або TypeError, 
коли наткнеться на проблемні рядки (без value або де details дорівнює None). 
Тобі знадобляться перевірки наявності ключів (наприклад, метод .get()) або блок try-except.
'''