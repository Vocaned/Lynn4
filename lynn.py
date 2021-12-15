"""Abstraction layer for Discord APIs"""

import json
import logging
import os
import time
import sys
import typing

from helpers import rest
import hikari
from hikari import undefined
import lavasnek_rs
import lightbulb


class Config:
    config_template = {
        'secrets': {
            'discord_token': None # Bot's token
        },
        'prefix': '%', # Bot's prefix
        'typingindicator': False, # Should the bot trigger "is typing..." activity when processing commands
        'status': 'online', # Bot's default status
        'activity': None, # Bot's default activity
        'lavalink_pass': "password", # Password for lavalink instance
        'lavalink_host': '127.0.0.1', # Lavalink instance host, null to disable lavalink
        'vips': [] # List of IDs (as string) to people who have VIP priviledges (uploading to custom site etc)
    }

    def __init__(self, path='config.json'):
        if not os.path.exists(path):
            logging.critical('Config does not exist. A %s file was created, please edit it before running the bot again.', path)
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(self.config_template, f, indent=2)
            sys.exit(1)

        self.path = path
        self.dict = self.get_config()

        for k, v in self.config_template.items():
            if k not in self.dict:
                logging.warning('Required value "%s" not found in %s. The default value of "%s" was used. Please edit the file if necessary.', k, self.path, v)
                self.set(k, v)

    def get_config(self) -> dict:
        if not os.path.exists('config.json'):
            return None

        with open(self.path, encoding='utf-8') as f:
            return json.load(f)

    def set(self, key: str, value) -> None:
        # Make sure the dict is up to date with the file
        self.dict = self.get_config()
        self.dict[key] = value

        with open(self.path, 'w', encoding='utf-8') as f:
            json.dump(self.dict, f, indent=2)

    def get(self, key: str, default=None):
        return self.dict.get(key, default)

    def get_secret(self, key: str):
        secret = self.dict['secrets'].get(key, None)
        if not secret:
            raise Error('This command is currently disabled.', 'Secret key missing, please contact the bot owner.')
        return secret

class Error(lightbulb.errors.LightbulbError):
    """Custom error message, raise to send an error embed."""

    def __init__(self, title: str = None, text: str = None):
        self.title: str = title
        """The error title."""
        self.text: str = text
        """The error text."""

class Data:
    """Global data shared across the entire bot."""
    def __init__(self) -> None:
        self.lavalink: lavasnek_rs.Lavalink = None # pylint: disable=no-member

class Bot(lightbulb.BotApp):
    """Improved Bot class"""
    def __init__(self, *args, **kwargs):
        self.data = Data()
        self.config = Config()
        self.startup_time = time.time()

        self.token = self.config.get_secret('discord_token')
        self.prefix = lightbulb.when_mentioned_or(self.config.get('prefix'))

        super().__init__(token=self.token, prefix=self.prefix, *args, **kwargs)

class Message:
    def __init__(self, content: str = None, embed: hikari.Embed = None, image: typing.Union[hikari.File, str] = None, files: typing.List[hikari.File] = None, output: str = 'all') -> None:
        self.content = content if content else ''
        self.embed = embed if embed else None
        self.image = image if image else None
        self.files = files if files else None
        self.output = output

    async def send(self, context: lightbulb.Context) -> hikari.Message:
        return await self.send_channel(context.bot, context.channel_id)

    async def send_channel(self, bot: Bot, channel: hikari.Snowflakeish) -> hikari.Message:
        content = self.content

        # TODO: mix and match multiple outputs, same as helpers.rest but with a better system for both of them
        out = {}
        if self.output == 'all':
            attachments = []
            attachments.append(self.image if self.image else None)
            attachments.append(self.files if self.files else None)
            if not attachments:
                attachments = undefined.UNDEFINED

            out['embed'] = self.embed
            out['attachments'] = attachments
        elif self.output == 'embed':
            content = ''
            if self.embed:
                out['embed'] = self.embed
        elif self.output == 'image':
            content = ''
            if isinstance(self.image, str):
                self.image = await rest(self.image, returns='raw')
            if self.image:
                out['attachments'] = [self.image,]
        elif self.output == 'files':
            content = ''
            if self.files:
                out['attachments'] = self.files

        return await bot.rest.create_message(channel, content, **out)

def get_plugin():
    ...

ERROR_COLOR = 0xff4444
EMBED_COLOR = 0x8f8f8f
