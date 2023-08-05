import logging
import discord
from discord.ext import tasks
from bot.message_builder import MessageBuilder
from null_logger import NullLogger
from scrapers.netonnet.netonnet import NetOnNet
from scrapers.sweclockers.sweclockers import SweClockers
from subscriber_config import SubscriberConfig
from read_config import ReadConfig
from utils import CommandVerifier, get_command

PREFIX = "df "
SET_CHANNEL = 'set-channel'
REMOVE_CHANNEL = 'remove-channel'
SUB_ALL = 'sub'
UNSUB_ALL = 'unsub'
SUB_KW = 'sub-kw'
UNSUB_KW = 'unsub-kw'
SHOW_KWS = 'my-kws'
HELP = 'help'

LOOP_INTERVAL_SECONDS = 180

ACTIVE_COMMANDS = {
    SET_CHANNEL,
    REMOVE_CHANNEL,
    SUB_KW,
    UNSUB_KW,
    SHOW_KWS,
    HELP,
}

class DealAlerterBot(discord.Client):
    def __init__(self, *args, **kwargs):
        kwargs['intents'] = discord.Intents.default()
        super().__init__(*args, **kwargs)
        self.config = SubscriberConfig()
        self.read_config = ReadConfig(self.config)
        self.running = False

        logger = logging
        self.logger = logger.getLogger('DealAlerterBot')
        self.netonnet = NetOnNet(self.read_config, logger=logger.getLogger('NetOnNet'))
        self.sweclockers = SweClockers(self.read_config, logger=logger.getLogger('SweClockers'))

    async def on_ready(self):
        self.logger.info(f'Logged in as {self.user} (ID: {self.user.id})')
        if not self.running:
            self.running = True
            await self.setup_hook()

    async def setup_hook(self) -> None:
        await self.scraper_loop.start()

    @tasks.loop(seconds=LOOP_INTERVAL_SECONDS)
    async def scraper_loop(self):
        self.netonnet.fetch_new_deals()
        self.sweclockers.fetch_new_deals()
        self.logger.info(f'Found {len(self.netonnet.new_deals)} new deals on NetOnNet')
        self.logger.info(f'Found {len(self.sweclockers.new_deals)} new deals on SweClockers')
        if not any([self.netonnet.new_deals, self.sweclockers.new_deals]):
            return

        for guild_id, channel_id in self.config.get_posting_guilds_channels():
            message = self._build_message(guild_id)
            channel = self.get_channel(channel_id)
            await channel.send(message)

    @scraper_loop.before_loop
    async def initialize_scaper_loop(self):
        self.logger.info(f'Starting scraping loop, interval set to {LOOP_INTERVAL_SECONDS} seconds')

    async def on_message(self, message):
        if message.author == self.user:
            return

        command = get_command(message.content, PREFIX)

        if command and command not in ACTIVE_COMMANDS:
            await message.channel.send(f'Command `{command}` not found, use `df help` for available commands')
            return

        if command == SET_CHANNEL:
            channel_name = message.content.split()[-1]
            for channel in self.get_all_channels():
                if channel_name == channel.name:
                    self.config.set_posting_channel(channel.id, message.guild.id)
                    self.logger.info(f'Posting channel set to {channel.name} in {message.guild.name} by {message.author.name}')
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
            self.logger.info(f'Subscribed {message.author.name} to all deals')
            await message.channel.send(f'Subscribed <@{message.author.id}>')

        if command == UNSUB_ALL:
            self.config.should_notify_user(message.author.id, message.guild.id, False)
            self.logger.info(f'Unsubscribed {message.author.name} from all deals')
            await message.channel.send(f'Unsubscribed <@{message.author.id}>')

        if command == SUB_KW:
            verifier = CommandVerifier(PREFIX, SUB_KW)
            if verifier.verify_keyword(message.content):
                self.config.subscribe_to_keyword(message.author.id, message.guild.id, verifier.verified_result)
                self.logger.info(f'Subscribed {message.author.name} to keyword: {verifier.verified_result}')
                await message.channel.send(f'Subbed {message.author.name} to keyword `{verifier.verified_result}`')
            else:
                await message.channel.send(f'Invalid format, use `{PREFIX} help` for instructions')

        if command == UNSUB_KW:
            verifier = CommandVerifier(PREFIX, UNSUB_KW)
            verifier.verify_keyword(message.content)
            self.logger.info(f'Unsubscribed {message.author.name} from keyword: {verifier.verified_result}')
            self.config.unsubscribe_from_keyword(message.author.id, message.guild.id, verifier.verified_result)
            await message.channel.send(f'Unsubbed {message.author.name} from keyword `{verifier.verified_result}`')

        if command == SHOW_KWS:
            to_send = f'Keywords for {message.author.name}\n`{self.read_config.get_keywords_for_user(message.author.id, message.guild.id)}`'
            await message.channel.send(to_send)

        if command == HELP:
            help_message = (
                f'- `df {SET_CHANNEL} <channel name>` to set the channel I should post to\n'
                f'- `df {REMOVE_CHANNEL}` to stop me from posting\n'
                #f'- `df {SUB_ALL}` to get mentioned whenever a new deal is posted\n'
                #f'- `df {UNSUB_ALL}` to unsubscribe from deal mentions on every deal\n'
                f'- `df {SUB_KW} <keyword>` to subscribe to a keyword, such as `RTX` or `4080`\n'
                f'- `df {UNSUB_KW} <keyword>` to unsubscribe from a keyword\n'
                f'- `df {SHOW_KWS}` to what keyword you are subscribed to\n'
            )
            await message.channel.send(help_message)

    def _build_message(self, guild_id):
        netonnet_deals = self.netonnet.get_deals_to_post_in_guild(guild_id)
        sweclockers_deals = self.sweclockers.get_deals_to_post_in_guild(guild_id)
        self.logger.info(f'Found {len(netonnet_deals)} deals to post from NetOnNet')
        self.logger.info(f'Found {len(sweclockers_deals)} deals to post from SweClockers')
        message_builder = MessageBuilder()
        users_to_tag = set()
        if netonnet_deals:
            message_builder.header('NetOnNet').deals(netonnet_deals, self.netonnet.format_deal)
            users_to_tag.update(self.netonnet.get_users_to_tag_in_guild(guild_id))
        if sweclockers_deals:
            message_builder.header('SweClockers').deals(sweclockers_deals, self.sweclockers.format_deal)
            users_to_tag.update(self.sweclockers.get_users_to_tag_in_guild(guild_id))

        message_builder.tags(users_to_tag)
        return message_builder.build()
