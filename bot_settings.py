import json

CONFIG_PATH = 'config.json'
GUILDS = 'posting_guilds'
SUBSCRIBERS = 'subscribers'


class DagensFyndConfig:

    def __init__(self):
        self.config = get_config(CONFIG_PATH)
        self.init_json()

    def init_json(self):
        if GUILDS not in self.config:
            self.config[GUILDS] = {}
        if SUBSCRIBERS not in self.config:
            self.config[SUBSCRIBERS] = {}

    def set_posting_channel(self, channel_id, guild_id):
        self.config[GUILDS][guild_id] = int(channel_id)
        with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
            f.write(json.dumps(self.config, indent=4))

    def get_posting_guilds_channels(self):
        return self.config[GUILDS].items()

    def should_notify_user(self, user_id, guild_id, notify=True):
        guild_id = str(guild_id)
        if guild_id not in self.config[SUBSCRIBERS]:
            self.config[SUBSCRIBERS][guild_id] = []
        if notify and user_id not in self.config[SUBSCRIBERS][guild_id]:
            self.config[SUBSCRIBERS][guild_id].append(user_id)
        elif user_id in self.config[SUBSCRIBERS][guild_id]:
            self.config[SUBSCRIBERS][guild_id].remove(user_id)

        with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
            f.write(json.dumps(self.config, indent=4))

    def get_user_ids_to_notify(self, guild_id):
        try:
            return self.config[SUBSCRIBERS][guild_id]
        except KeyError:
            return []


def get_config(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        return {}
