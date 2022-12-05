import json

CONFIG_PATH = 'config.json'
GUILDS = 'posting_guilds'
SUBSCRIBERS = 'subscribers'
KEYWORD_SUBS = 'keyword_subscribers'


class DagensFyndConfig:

    def __init__(self):
        self.config = get_config(CONFIG_PATH)
        self.init_json()

    def _save(self):
        with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
            f.write(json.dumps(self.config, indent=4))

    def init_json(self):
        if GUILDS not in self.config:
            self.config[GUILDS] = {}
        if SUBSCRIBERS not in self.config:
            self.config[SUBSCRIBERS] = {}
        if KEYWORD_SUBS not in self.config:
            self.config[KEYWORD_SUBS] = {}

    def subscribe_to_keyword(self, user_id, guild_id, keyword):
        user_id = str(user_id)
        guild_id = str(guild_id)
        if guild_id not in self.config[KEYWORD_SUBS]:
            self.config[KEYWORD_SUBS][guild_id] = dict()
        self._add_keyword_for_user(guild_id, keyword, user_id)
        self._save()

    def _add_keyword_for_user(self, guild_id, keyword, user_id):
        keyword = keyword.lower()
        if user_id in self.config[KEYWORD_SUBS][guild_id]:
            if keyword not in self.config[KEYWORD_SUBS][guild_id][user_id]:
                self.config[KEYWORD_SUBS][guild_id][user_id].append(keyword)
        else:
            self.config[KEYWORD_SUBS][guild_id][user_id] = [keyword]

    def unsubscribe_from_keyword(self, user_id, guild_id, keyword):
        keyword = keyword.lower()
        user_id = str(user_id)
        guild_id = str(guild_id)
        if guild_id not in self.config[KEYWORD_SUBS]:
            return True
        if user_id not in self.config[KEYWORD_SUBS][guild_id]:
            return True
        if keyword in self.config[KEYWORD_SUBS][guild_id][user_id]:
            self.config[KEYWORD_SUBS][guild_id][user_id].remove(keyword)
        self._save()

    def set_posting_channel(self, channel_id, guild_id):
        self.config[GUILDS][guild_id] = int(channel_id)
        self._save()

    def remove_posting_channel(self, guild_id):
        guild_id = str(guild_id)
        if guild_id in self.config[GUILDS]:
            del self.config[GUILDS][guild_id]
            self._save()
            return True
        return False

    def get_posting_guilds_channels(self):
        return self.config[GUILDS].items()

    def should_notify_user(self, user_id, guild_id, notify=True):
        guild_id = str(guild_id)
        if guild_id not in self.config[SUBSCRIBERS]:
            self.config[SUBSCRIBERS][guild_id] = []
        if notify and user_id not in self.config[SUBSCRIBERS][guild_id]:
            self.config[SUBSCRIBERS][guild_id].append(user_id)
        elif not notify and user_id in self.config[SUBSCRIBERS][guild_id]:
            self.config[SUBSCRIBERS][guild_id].remove(user_id)

        self._save()

    def __getitem__(self, key):
        return self.config[key]

def get_config(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        return {}
