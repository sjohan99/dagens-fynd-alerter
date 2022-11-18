import time
import json
from urllib import request
from bs4 import BeautifulSoup

SUGGESTION_PATH = 'suggestions/suggestion.json'

SWEC_DAGENSFYND_URL = 'https://www.sweclockers.com/dagensfynd'
SAVE_HTML_PATH = 'suggestions/html'
SECONDS_IN_DAY = 604800
SEVEN_DAYS_IN_SECONDS = 7 * SECONDS_IN_DAY
SUGGESTIONS = 'suggestions'
LAST_UPDATE = 'last_update'


def download_html(url):
    response = request.urlopen(url)
    web_content = response.read().decode('UTF-8')
    return web_content


def get_soup_parser_for_html(link):
    content = download_html(link)
    return BeautifulSoup(content, features="html.parser")


def remove_plus_and_convert_to_int(tag):
    # removes leading '+' from text: '+123' -> '123'
    return int(str(tag)[1:])


def get_upvotes(tip):
    try:
        return remove_plus_and_convert_to_int(tip.find('span', class_='label').text.strip())
    except AttributeError:
        return 0


def create_suggestions_dict(soup):
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

        suggestions[f'{author}: {product}'] = {
            'product': product,
            'author': author,
            'upvotes': upvotes,
            'price': price,
            'link': product_link,
            'post_link': post_link,
            'detected': detected
        }

    return suggestions


def update_suggestions(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            saved_suggestions = json.load(f)
    except FileNotFoundError:
        saved_suggestions = {SUGGESTIONS: dict(), 'last_update': 0}

    remove_old_suggestions(saved_suggestions[SUGGESTIONS], SEVEN_DAYS_IN_SECONDS)
    saved_suggestions[LAST_UPDATE] = int(time.time())
    add_new_suggestions(saved_suggestions[SUGGESTIONS])

    with open(path, 'w', encoding='utf-8') as f:
        f.write(json.dumps(saved_suggestions, indent=4))


def get_all_new_suggestions(path=SUGGESTION_PATH, update=False):
    if update:
        update_suggestions(path)

    try:
        with open(path, 'r', encoding='utf-8') as f:
            saved_suggestions = json.load(f)
    except FileNotFoundError:
        return dict()

    new_suggestions = []
    last_update = saved_suggestions[LAST_UPDATE]
    for suggestion in saved_suggestions[SUGGESTIONS].values():
        if suggestion['detected'] >= last_update:
            new_suggestions.append(suggestion)

    return new_suggestions


def add_new_suggestions(saved_suggestions):
    soup = get_soup_parser_for_html(SWEC_DAGENSFYND_URL)
    scraped_suggestions = create_suggestions_dict(soup)
    for key, suggestion in scraped_suggestions.items():
        if key not in saved_suggestions:
            saved_suggestions[key] = suggestion

    return saved_suggestions


def remove_old_suggestions(saved_suggestions, time_limit_in_seconds):
    to_delete = []
    for key, suggestion in saved_suggestions.items():
        if time.time() > suggestion['detected'] + time_limit_in_seconds:
            to_delete.append(key)
    for key in to_delete:
        del saved_suggestions[key]

    return saved_suggestions


def debug():
    soup = get_soup_parser_for_html(SWEC_DAGENSFYND_URL)
    scraped_suggestions = create_suggestions_dict(soup)

if __name__ == '__main__':
    # update_suggestions(SUGGESTION_PATH)
    # print(get_all_new_suggestions(SUGGESTION_PATH))
    debug()
