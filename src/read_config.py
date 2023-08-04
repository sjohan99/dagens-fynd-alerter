from subscriber_config import SubscriberConfig, GUILDS, SUBSCRIBERS, KEYWORD_SUBS


class ReadConfig:

    def __init__(self, config: SubscriberConfig):
        self.config = config

    def get_keywords_for_user(self, user_id, guild_id):
        try:
            keywords = list(self.config[KEYWORD_SUBS][str(guild_id)][str(user_id)])
            return sorted(keywords)
        except KeyError:
            return []

    def _get_keyword_sub_user_ids_in_guild(self, guild_id):
        try:
            return self.config[KEYWORD_SUBS][guild_id]
        except KeyError:
            return []

    def get_user_ids_to_notify(self, guild_id):
        try:
            everything_subs_to_notify = self.config[SUBSCRIBERS][guild_id]
            return everything_subs_to_notify
        except KeyError:
            return []

    def get_user_ids_to_notify_keyword(self, guild_id, product_string):
        keyword_subs_to_notify = set()
        product_string = product_string.lower()
        for user_id in self._get_keyword_sub_user_ids_in_guild(guild_id):
            keywords = self.get_keywords_for_user(user_id, guild_id)
            for keyword in keywords:
                if keyword in product_string:
                    keyword_subs_to_notify.add(user_id)
                    break
        return keyword_subs_to_notify

    def get_users_to_notify_for_products(self, guild_id, products):
        users_to_notify = set()
        for product in products:
            users_to_notify.update(self.get_user_ids_to_notify_keyword(guild_id, product))
        return users_to_notify

    def get_all_keywords(self, guild_id):
        all_keywords = set()
        for user_id in self._get_keyword_sub_user_ids_in_guild(guild_id):
            keywords = self.get_keywords_for_user(user_id, guild_id)
            all_keywords.update(keywords)
        return all_keywords