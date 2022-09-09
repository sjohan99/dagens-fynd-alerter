import sys

import discord
from discord.ext import tasks
import suggestion_scraper
from bot_settings import DagensFyndConfig

PREFIX = "df "


def format_mentions(user_ids):
    mentions = ''
    for user_id in user_ids:
        mentions += f'<@{user_id}> '
    return mentions.strip()


def format_suggestion(suggestion):
    return (
        f'**Item**: {suggestion["product"]}\n'
        f'**Price**: {suggestion["price"]}\n'
        f'**Link**: {suggestion["link"]}\n'
    )


class DagensFynd(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # an attribute we can access from our task
        self.config = DagensFyndConfig()
        self.running = False

    async def setup_hook(self) -> None:
        # start the task to run in the background
        self.run_scraper.start()

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')
        if not self.running:
            await self.setup_hook()

    async def on_message(self, message):
        if message.author == self.user:
            return

        if message.content.startswith(PREFIX + 'set channel'):
            channel_name = message.content.split()[-1]
            for channel in client.get_all_channels():
                if channel_name == channel.name:
                    self.config.set_posting_channel(channel.id, message.guild.id)
                    await message.channel.send(f'Deals will now be posted to <#{channel.id}>')

        if message.content.startswith(PREFIX + 'subscribe'):
            self.config.should_notify_user(message.author.id, message.guild.id)
            await message.channel.send(f'Subscribed <@{message.author.id}>')

        if message.content.startswith(PREFIX + 'unsubscribe'):
            self.config.should_notify_user(message.author.id, message.guild.id, False)
            await message.channel.send(f'Unsubscribed <@{message.author.id}>')

        if message.content.startswith(PREFIX + 'help'):
            help_message = (
                f'- `df set channel <channel name>` to set the channel I should post to\n'
                f'- `df subscribe` to get mentioned when a new deal is posted\n'
                f'- `df unsubscribe` to unsubscribe from deal mentions\n'
            )
            await message.channel.send(help_message)

    async def send_suggestions(self, suggestions):
        formatted_suggestions = [format_suggestion(suggestion) for suggestion in suggestions]
        for guild_id, channel_id in self.config.get_posting_guilds_channels():
            channel = client.get_channel(channel_id)
            for suggestion in formatted_suggestions:
                await channel.send(suggestion)
            users_to_notify = self.config.get_user_ids_to_notify(guild_id)
            if suggestions and users_to_notify:
                await channel.send(format_mentions(users_to_notify))
        print(f'Found {len(suggestions)} new suggestions')

    @tasks.loop(seconds=180)
    async def run_scraper(self):
        suggestions = suggestion_scraper.get_all_new_suggestions(update=True)
        await self.send_suggestions(suggestions)

    @run_scraper.before_loop
    async def before_my_task(self):
        await self.wait_until_ready()  # wait until the bot logs in
        print('starting run scraper')


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1]:
        token = sys.argv[1]
    else:
        try:
            with open('tokensecret.txt', 'r', encoding='utf-8') as f:
                token = f.read().strip()
        except FileNotFoundError as e:
            print(e)
            exit()

client = DagensFynd(intents=discord.Intents.default())
client.run(token)
