import os
import discord
from discord.ext import tasks
import suggestion_scraper
from bot_settings import DagensFyndConfig
from read_config import ReadConfig
from utils import CommandVerifier, get_command
from dotenv import load_dotenv

PREFIX = "df "
SET_CHANNEL = 'set-channel'
REMOVE_CHANNEL = 'remove-channel'
SUB_ALL = 'sub'
UNSUB_ALL = 'unsub'
SUB_KW = 'sub-kw'
UNSUB_KW = 'unsub-kw'
SHOW_KWS = 'my-kws'
HELP = 'help'


def format_mentions(user_ids):
    mentions = ''
    for user_id in user_ids:
        mentions += f'<@{user_id}> '
    return mentions.strip()


def format_suggestion(suggestion):
    return (
        f'Item: **{suggestion["product"]}**\n'
        f'Price: **{suggestion["price"]}**\n'
        f'Link: <{suggestion["link"]}>\n'
        f'Post: <{suggestion["post_link"]}>\n'
    )


class DagensFynd(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # an attribute we can access from our task
        self.config = DagensFyndConfig()
        self.read_config = ReadConfig(self.config)
        self.running = False

    async def setup_hook(self) -> None:
        # start the task to run in the background
        await self.run_scraper.start()

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')
        if not self.running:
            self.running = True
            await self.setup_hook()

    async def on_message(self, message):
        command = get_command(message.content, PREFIX)

        if message.author == self.user:
            return

        if command == SET_CHANNEL:
            channel_name = message.content.split()[-1]
            for channel in client.get_all_channels():
                if channel_name == channel.name:
                    self.config.set_posting_channel(channel.id, message.guild.id)
                    await message.channel.send(f'Deals will now be posted to <#{channel.id}>')

        if command == REMOVE_CHANNEL:
            guild = message.guild.id
            success = self.config.remove_posting_channel(guild)
            if success:
                await message.channel.send(f'Posting channel removed. Use `df help` for how to set a new channel.')
            else:
                await message.channel.send(f'No posting channel to remove found.')

        if command == SUB_ALL:
            self.config.should_notify_user(message.author.id, message.guild.id)
            await message.channel.send(f'Subscribed <@{message.author.id}>')

        if command == UNSUB_ALL:
            self.config.should_notify_user(message.author.id, message.guild.id, False)
            await message.channel.send(f'Unsubscribed <@{message.author.id}>')

        if command == SUB_KW:
            verifier = CommandVerifier(PREFIX, SUB_KW)
            if verifier.verify_keyword(message.content):
                self.config.subscribe_to_keyword(message.author.id, message.guild.id, verifier.verified_result)
                await message.channel.send(f'Subbed {message.author.name} to keyword `{verifier.verified_result}`')
            else:
                await message.channel.send(f'Invalid format, use `{PREFIX} help` for instructions')

        if command == UNSUB_KW:
            verifier = CommandVerifier(PREFIX, UNSUB_KW)
            verifier.verify_keyword(message.content)
            self.config.unsubscribe_from_keyword(message.author.id, message.guild.id, verifier.verified_result)

        if command == SHOW_KWS:
            to_send = f'Keywords for {message.author.name}\n`{self.read_config.get_keywords_for_user(message.author.id, message.guild.id)}`'
            await message.channel.send(to_send)

        if command == HELP:
            help_message = (
                f'- `df {SET_CHANNEL} <channel name>` to set the channel I should post to\n'
                f'- `df {REMOVE_CHANNEL}` to stop me from posting\n'
                f'- `df {SUB_ALL}` to get mentioned whenever a new deal is posted\n'
                f'- `df {UNSUB_ALL}` to unsubscribe from deal mentions on every deal\n'
                f'- `df {SUB_KW} <keyword>` to subscribe to a keyword, such as `RTX` or `4080`\n'
                f'- `df {UNSUB_KW} <keyword>` to unsubscribe from a keyword\n'
                f'- `df {SHOW_KWS}` to what keyword you are subscribed to\n'
            )
            await message.channel.send(help_message)

    async def send_suggestions(self, suggestions):
        formatted_suggestions = [format_suggestion(suggestion) for suggestion in suggestions]
        for guild_id, channel_id in self.config.get_posting_guilds_channels():
            channel = client.get_channel(channel_id)
            for suggestion in formatted_suggestions:
                await channel.send(suggestion)
            users_to_notify = self.get_users_to_notify_for_message(guild_id, suggestions)
            if suggestions and users_to_notify:
                await channel.send(format_mentions(users_to_notify))
        print(f'Found {len(suggestions)} new suggestions')

    def get_users_to_notify_for_message(self, guild_id, suggestions):
        users = set()
        users.update(self.read_config.get_user_ids_to_notify(guild_id))
        for suggestion in suggestions:
            keyword_users_to_notify = self.read_config.get_user_ids_to_notify_keyword(guild_id, suggestion['product'])
            users.update(keyword_users_to_notify)
        return users

    @tasks.loop(seconds=90)
    async def run_scraper(self):
        print('scraping ...')
        suggestions = suggestion_scraper.get_all_new_suggestions(update=True)
        await self.send_suggestions(suggestions)

    @run_scraper.before_loop
    async def before_my_task(self):
        print('waiting until bot ready ...')
        # await self.wait_until_ready()  # wait until the bot logs in
        print('starting run scraper')


if __name__ == '__main__':
    load_dotenv()
    token = os.environ['BOTTOKEN']

client = DagensFynd(intents=discord.Intents.default())
client.run(token)
