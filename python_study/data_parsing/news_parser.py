import requests
from bs4 import BeautifulSoup
from fake_useragent import FakeUserAgent


url = 'https://www.benzinga.com/recent'
headers = {
    'User-Agent': FakeUserAgent().random
}
response = requests.get(url, headers=headers)


html = BeautifulSoup(response.content, 'html.parser')
news_lst = html.select('.content-feed-list ')
for news in news_lst:
    main_text = news.select('content-feed-list')
    print(news)
    # header = news.select('.sc-dJKxXM.sc-bTllmO.gZJsOa.clyLKq.line-wrapper.post-card-title.leading-snug.text-2xl')
