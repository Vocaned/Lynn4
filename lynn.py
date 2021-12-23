"""Abstraction layer for Discord APIs"""

from fileinput import filename
import json
import logging
import os
import tempfile
import time
import sys
import typing
import io

from helpers import rest, RestOptions
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

class TemporaryFile:
    def __init__(self, filename: str = None) -> None:
        self.directory = tempfile.TemporaryDirectory()
        self.filename = filename

    def get_path(self):
        return os.path.join(self.directory.name, self.get_filename())

    def hikari_file(self):
        return hikari.File(self.get_path())

    def get_filename(self):
        if not self.filename:
            files = os.listdir(self.directory.name)
            if len(files) == 0:
                raise Error('Temporary file has no known file name, and there are no files in the directory.')
            if len(files) > 1:
                raise Error('Temporary file has no known file name, and directory has more than 1 file.')
            self.filename = files[0]
        return self.filename

    def close(self):
        self.directory.cleanup()
        del self

class MessageOutput(int):
    all = 1 << 0
    embed = 1 << 1
    image = 1 << 2
    files = 1 << 3

class Message:
    def __init__(self,
            content: str = None,
            embed: hikari.Embed = None,
            image: typing.Union[hikari.File, hikari.Resourceish, str] = None,
            files: typing.List[typing.Union[hikari.File, hikari.Resourceish, TemporaryFile]] = None,
            output: MessageOutput = MessageOutput.all
        ) -> None:
        self.content = content if content else ''
        self.embed = embed if embed else None
        self.image = image if image else None
        self.files = files if files else None
        self.output = output

    async def send(self, context: lightbulb.Context) -> hikari.Message:
        return await self.send_channel(context.bot, context.channel_id, reply=context.event.message_id)

    async def send_channel(self, bot: Bot, channel: hikari.Snowflakeish, reply=undefined.UNDEFINED) -> hikari.Message:
        content = self.content

        attachments = []
        if self.image:
            if isinstance(self.image, str):
                self.image = await rest(self.image, RestOptions(returns='raw'))
            attachments.append(self.image)
        if self.files:
            newfiles = []
            for f in self.files:
                if isinstance(f, TemporaryFile):
                    newfiles.append(f.hikari_file())
                else:
                    newfiles.append(f)

            attachments += newfiles

        out = {}
        if self.output & MessageOutput.all == MessageOutput.all:
            out['embed'] = self.embed if self.embed else undefined.UNDEFINED
            out['attachments'] = attachments if attachments else undefined.UNDEFINED
        if self.output & MessageOutput.embed == MessageOutput.embed:
            content = ''
            out['embed'] = self.embed if self.embed else undefined.UNDEFINED
        if self.output & MessageOutput.files == MessageOutput.files or self.output & MessageOutput.image == MessageOutput.image:
            content = ''
            out['attachments'] = attachments if attachments else undefined.UNDEFINED

        try:
            return await bot.rest.create_message(channel, content, reply=reply, **out)
        except hikari.BadRequestError as e:
            errors = dict(e.errors)
            if not errors or len(errors['message_reference']['_errors']) > 1 or errors['message_reference']['_errors'][0]['code'] != 'REPLIES_UNKNOWN_MESSAGE':
                raise e

            # Retry message without reply if REPLIES_UNKNOWN_MESSAGE
            return await bot.rest.create_message(channel, content, **out)


ERROR_COLOR = 0xff4444
EMBED_COLOR = 0x8f8f8f
