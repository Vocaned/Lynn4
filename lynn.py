import importlib
import json
import logging
import os
import sys
import time
import typing

import hikari
from hikari import undefined

import errors


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
            raise errors.LynnError('This command is currently disabled.', 'Secret key missing, please contact the bot owner.')
        return secret

class Bot(hikari.GatewayBot):
    """Bot class"""
    def __init__(self, *args, **kwargs):
        self.data = {}
        self.config = Config()
        self.startup_time = time.time()

        self.extensions = {}

        self.scripting = None

        self.token = self.config.get_secret('discord_token')
        self.prefix = self.config.get('prefix')

        super().__init__(token=self.token, *args, **kwargs)

    def load_extension(self, extension):
        if extension in self.extensions:
            raise errors.ExtensionAlreadyLoadedError(extension)

        module = importlib.import_module(extension)

        if not hasattr(module, "Extension"):
            raise errors.ExtensionNoClass(extension)

        ext = module.Extension(self)
        self.extensions[extension] = ext

    def unload_extension(self, extension):
        if extension not in self.extensions:
            raise errors.ExtensionNotLoaded(extension)

        self.extensions[extension].unload()
        del self.extensions[extension]
        del sys.modules[extension]

class Response:
    def __init__(self, content:str, _dict:dict = None, embed:hikari.Embed = None) -> None:
        """
        @_dict: Return all relevant information the command returns here. The dictionary should not have a `content` or `embed` keys, as those will be overwritten.
        """
        self.dict = _dict if _dict else {}
        self.dict['content'] = content
        if embed:
            self.dict['embed'] = embed

    async def send_content(self, bot: Bot, channel:hikari.Snowflakeish) -> None:
        await bot.rest.create_message(channel, self.dict.get('content'))

    async def send_embed(self, bot: Bot, channel:hikari.Snowflakeish) -> None:
        await bot.rest.create_message(channel, '', embed=self.dict.get('embed'))

    async def send(self, bot: Bot, channel:hikari.Snowflakeish) -> None:
        await bot.rest.create_message(channel, self.dict.get('content'), embed=self.dict.get('embed', undefined.UNDEFINED))

class Extension:
    """Extension class"""
    def __init__(self, bot: Bot):
        self.bot = bot
        self.commands = {}

    def unload(self):
        ...

    async def execute(self, ctx: hikari.GuildMessageCreateEvent) -> Response:
        ...

ERROR_COLOR = 0xff4444
EMBED_COLOR = 0x8f8f8f
