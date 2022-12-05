from bot_settings import DagensFyndConfig, GUILDS, SUBSCRIBERS, KEYWORD_SUBS


class ReadConfig:

    def __init__(self, config: DagensFyndConfig):
        self.config = config

    def get_keywords_for_user(self, user_id, guild_id):
        user_id = str(user_id)
        guild_id = str(guild_id)
        try:
            keywords = list(self.config[KEYWORD_SUBS][guild_id][user_id])
            return sorted(keywords)
        except KeyError:
            return []

    def _get_keyword_sub_user_ids_in_guild(self, guild_id):
        if guild_id not in self.config[KEYWORD_SUBS]:
            return []
        kw_subscribed_user_ids = self.config[KEYWORD_SUBS][guild_id]
        return kw_subscribed_user_ids

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