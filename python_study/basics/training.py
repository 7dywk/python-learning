'''
Приймає список і адресу гаманця
Повертає всі транзакції де ця адреса є відправником або отримувачем
Виводить суму всіх цих транзакцій
'''

transactions = [
    {"hash": "0xabc", "value": 5.2, "from": "0x111", "to": "0x222"},
    {"hash": "0xdef", "value": 0.3, "from": "0x333", "to": "0x111"},
    {"hash": "0xghi", "value": 12.7, "from": "0x444", "to": "0x555"},
    {"hash": "0xjkl", "value": 1.1, "from": "0x111", "to": "0x666"},
    {"hash": "0xmno", "value": 8.9, "from": "0x777", "to": "0x222"},
]



def get_info(transaction, address):
    sum_value = 0
    tran_list = []
    for item in transaction:
        if item['from'] == address or item['to'] == address:
            sum_value += item['value']
            tran_list.append(item)
    for tran in tran_list:
        print(f'Transactions with address {address}: {tran}')
    return f'sum value is {sum_value:.2f}'

result = get_info(transactions ,"0x222")
print(result)

