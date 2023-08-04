from null_logger import NullLogger
from read_config import ReadConfig
from .scraper import connect
from deal_updater import DealUpdater


class NetOnNet():

    source = 'netonnet'

    def __init__(self, read_config: ReadConfig, logger=NullLogger()) -> None:
        self.read_config = read_config
        self.new_deals = None
        self.logger = logger

    def fetch_new_deals(self):
        self.logger.info(f'Fetching new {NetOnNet.source} deals')
        products = connect()
        deal_updater = DealUpdater(self.source)
        _, new_deals = deal_updater.update_deals(products)
        self.new_deals = new_deals
        return new_deals

    def get_deals_to_post_in_guild(self, guild_id):
        deals_to_post = []
        keywords = self.read_config.get_all_keywords(guild_id)
        for deal in self.new_deals.values():
            for keyword in keywords:
                if keyword in deal['product'].lower():
                    deals_to_post.append(deal)
                    break
        return deals_to_post

    def get_users_to_tag_in_guild(self, guild_id):
        return self.read_config.get_users_to_notify_for_products(guild_id, self.new_deals)

    @staticmethod
    def format_deal(deal):
        return (
            f'Item: **{deal["product"]}**\n'
            f'Price: **{deal["price"]} kr**\n'
            f'Link: <{deal["link"]}>\n'
        )
