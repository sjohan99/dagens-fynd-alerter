import json
import os
from time import time
from dotenv import load_dotenv
from copy import deepcopy


class DealUpdater:

    ONE_WEEK_IN_SECONDS = 604_800

    def __init__(self, source) -> None:
        self.new_deals = None
        self.pre_update_deals = None
        self.post_update_deals = None
        self.source = source

    def update_deals(self, deals, save=True):
        deals_path = deals_file_path(self.source)
        existing_deals = get_existing_deals(deals_path)
        self.pre_update_deals = deepcopy(existing_deals)

        existing_deals = filter_old_deals(existing_deals, self.ONE_WEEK_IN_SECONDS)
        deals.update(existing_deals)
        self.post_update_deals = deals

        new_deals = dict(filter(lambda d: d[0] not in existing_deals, deals.items()))
        self.new_deals = new_deals

        if save:
            self.save_deals()

        return deals, new_deals

    def save_deals(self):
        assert self.post_update_deals is not None
        deals_path = deals_file_path(self.source)
        with open(deals_path, 'w', encoding='utf-8') as f:
            f.write(json.dumps(self.post_update_deals, indent=4))


def filter_old_deals(deals, time_limit_in_seconds):
    current_time = time()

    def is_not_old_deal(deal):
        product_key, product_info = deal
        return product_info['detected'] + time_limit_in_seconds > current_time

    return dict(filter(lambda deal: is_not_old_deal(deal), deals.items()))


def get_existing_deals(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return dict()
    except json.decoder.JSONDecodeError:
        with open(path, 'r', encoding='utf-8') as f:
            if f.read() == '':
                return dict()
        raise


def deals_file_path(source):
    load_dotenv()
    db_path = os.environ['DFA_DB_PATH']
    deals_folder_path = os.path.join(db_path, 'deals')
    if not os.path.exists(deals_folder_path):
        os.makedirs(deals_folder_path)
    deals_file_path = os.path.join(deals_folder_path, f'{source}.json')
    return deals_file_path
