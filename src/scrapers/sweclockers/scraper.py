import time
import json
from urllib import request
from bs4 import BeautifulSoup

DAGENS_FYND_URL = 'https://www.sweclockers.com/dagensfynd'

def connect():
    html = download_html(DAGENS_FYND_URL)
    soup = get_soup_parser_for_html(html)
    return create_products_dict(soup)

def download_html(url):
    response = request.urlopen(url)
    web_content = response.read().decode('UTF-8')
    return web_content


def get_soup_parser_for_html(html):
    return BeautifulSoup(html, features="html.parser")


def create_products_dict(soup):
    suggestions = dict()
    tips_div = soup.find('div', class_='tips-data')
    tips_rows = list(tips_div.find_all("div", class_='tips-row'))

    for tip in tips_rows:
        product = tip.find('div', class_='col-product-inner-wrapper').text.strip()
        author = tip.find('div', class_='cell-col col-user hide-viewport-small display-none display-s-block').text.strip()
        upvotes = get_upvotes(tip)
        price = tip.find('div', class_='cell-col col-price').text.strip()
        product_link = tip.find('a', class_='col-wrapper cell-product')['href']
        post_link = f"https://www.sweclockers.com{tip.find('a', class_='col-wrapper cell-user')['href']}"
        detected = int(time.time())
        filtered_price = ''.join(filter(lambda char: char.isdigit(), price))

        suggestions[f'{author}: {product}'] = {
            'product': product,
            'author': author,
            'upvotes': upvotes,
            'price': filtered_price,
            'link': product_link,
            'post_link': post_link,
            'detected': detected
        }

    return suggestions


def get_upvotes(tip):
    try:
        return remove_plus_and_convert_to_int(tip.find('span', class_='label').text.strip())
    except AttributeError:
        return 0


def remove_plus_and_convert_to_int(tag):
    # removes leading '+' from text: '+123' -> '123'
    return int(str(tag)[1:])
