import time
from urllib.request import urlopen, Request
from bs4 import BeautifulSoup

NETONNET_URL = 'https://www.netonnet.se'
OUTLET_URL = f'{NETONNET_URL}{"/art/outlet?pageSize=72&sortOrder=20&sortBy=3"}'

CARDS_CLASS = 'row is-equalHeight'
CARD_CLASS = 'cProductItem col-xs-12 col-sm-4 col-md-6 col-lg-4 product'
ITEM_NAME_CLASS = 'subTitle small productList'
LINK_CONTAINER_CLASS = 'col-xs-7 col-sm-12'
PRICE_CLASS = 'price'

def connect():
    html = download_html(OUTLET_URL)
    soup = get_soup_parser_for_html(html)
    return create_products_dict(soup)


def download_html(url):
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
    }
    response = urlopen(Request(url, headers=headers))
    web_content = response.read().decode('UTF-8')
    return web_content


def get_soup_parser_for_html(html):
    return BeautifulSoup(html, features="html.parser")


def create_products_dict(soup):
    products = dict()
    cards_div = soup.find('div', class_=CARDS_CLASS)
    cards = list(cards_div.find_all("div", class_=CARD_CLASS))
    timestamp = int(time.time())

    for card in cards:
        product = card.find('div', class_=ITEM_NAME_CLASS).text.strip()
        price = card.find('span', class_=PRICE_CLASS).text.strip()
        link = NETONNET_URL + card.find('div', class_=LINK_CONTAINER_CLASS).find('a')['href']
        filtered_price = ''.join(filter(lambda char: char.isdigit(), price))

        products[product] = {
            'product': product,
            'price': filtered_price,
            'link': link,
            'detected': timestamp
        }

    return products

