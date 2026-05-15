# import requests
#
# url = 'https://chainid.network/chains.json'
# response = requests.get(url)
# data = response.json()
# #"name | первое rpc |
# # есть ли поддержка EIP1559 | название нативной монеты |
# # decimals нативной монеты | chain id | ссылка на експлорер"
# print(data)

# for elem in data:
#     name = elem['name']
#     if elem['rpc']:
#         rpc = elem['rpc'][0]
#     else:
#         rpc = 'no rpc'
#
#     if 'features' in elem:
#        for f in elem['features']:
#           if 'EIP1559' in f['name']:
#               f = 'EIP1559 enabled'
#           else:
#               f = 'EIP1559 disabled'
#     natcur = elem['nativeCurrency']['name']
#     decimals = elem['nativeCurrency']['decimals']
#     chainid = elem['chainId']
#     if 'explorers' in elem:
#        for e in elem['explorers']:
#            if 'url' in e:
#                url = e['url']
#
#
#     print(f'/', name, '//', rpc, '//',
#           f,'//', natcur,'//', decimals, '//',
#           chainid, '//', url, '//'
#           )






