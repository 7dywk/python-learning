import requests
from fake_useragent import FakeUserAgent

cookies = {
    '_ga': 'GA1.1.950891508.1772989970',
    'csrf_token': '8fb8b7a3eda6ac2cbf9bb61e93dcf0bebff963707c475c4084f397e7427d5e16',
    'cf_clearance': '62Rn_j4pTj9dH2h_CO1fQVPd3mQVE_DbD4.l3RfPCFw-1773070792-1.2.1.1-VJxikE_fil_mB3ErTcBgt1cpaIqYorMA6MOFgzDPS1e0VRVQ7b_Tib0VJW7O2orSZaojfG7KmTjP80fDZqjuYwLFvNTsfJ1e0gBp46fcgJAUkDtcqx_fRpUN0ysiaNgHnOed2W_hxB53hO3fpjwmFHV8cN1D.G9NjLaEiUDn9ldRANqJPUubPO9gpU1nkl1c3mUHOwhu17__c5w7d_Uc.lQcPrfP18f1EnsALY7oZIQ',
    '_ga_2YVCQ4QDRJ': 'GS2.1.s1773069418$o2$g1$t1773070800$j57$l0$h0',
}

headers = {
    'accept': '*/*',
    'accept-language': 'ru-UA,ru;q=0.9,uk-UA;q=0.8,uk;q=0.7,ru-RU;q=0.6,en-US;q=0.5,en;q=0.4',
    'baggage': 'sentry-environment=production,sentry-public_key=815d9942889e478088291501a57a59a7,sentry-trace_id=61178125d24f990ca587f22de90b193d,sentry-org_id=4510185929834496,sentry-sampled=false,sentry-sample_rand=0.7987069492023865,sentry-sample_rate=0.1',
    'content-type': 'application/json',
    'origin': 'https://www.spinxo.com',
    'priority': 'u=1, i',
    'referer': 'https://www.spinxo.com/',
    'sec-ch-ua': '"Google Chrome";v="143", "Chromium";v="143", "Not A(Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'sentry-trace': '61178125d24f990ca587f22de90b193d-a0d7e471e891a4df-0',
    'user-agent': FakeUserAgent().random,
    'x-csrf-token': '8fb8b7a3eda6ac2cbf9bb61e93dcf0bebff963707c475c4084f397e7427d5e16',
}

json_data = {
    'category': 'default',
    'language': 'english',
    'isGame': False,
    'count': 30,
    '_t': 1773070837525,
}


response = requests.post('https://www.spinxo.com/api/names', cookies=cookies, headers=headers, json=json_data)
data = response.json()
with open('../test_data/names_parsing_lesson.txt', 'w') as f:
    for name in data['data']['names']:
        f.write(name + '\n')



#data = '{"category":"default","language":"english","isGame":false,"count":30,"_t":1773070837525}'
#response = requests.post('https://www.spinxo.com/api/names', cookies=cookies, headers=headers, data=data)