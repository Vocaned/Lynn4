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
import importlib
import types

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

class IncorrectUsageError(Error):
    """Custom error message, raise to send an error embed with usage text."""
    def __init__(self, title: str = None):
        super().__init__(title=title, text=None)

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

    def make_plugin(self, name: str, description: typing.Optional[str] = None, include_datastore: bool = False) -> lightbulb.Plugin:
        """Gets plugin if it's already loaded by bot, or creates a new one if not"""
        plugin = self.get_plugin(name)
        if plugin:
            return plugin

        plugin = lightbulb.Plugin(name, description, include_datastore)
        self.add_plugin(plugin)
        return plugin

    def readd_plugin(self, plugin: lightbulb.Plugin) -> None:
        plugin.app = self

        for command in plugin._all_commands:
            try:
                self._add_command_to_correct_attr(command)
            except lightbulb.errors.CommandAlreadyExists:
                pass
        for event, listeners in plugin._listeners.items():
            for listener in listeners:
                if listener not in self.get_listeners(event):
                    self.subscribe(event, listener)
        logging.debug("Plugin registered %r", plugin.name)
        self._plugins[plugin.name] = plugin

    def clean_plugin(self, plugin: lightbulb.Plugin) -> None:
        """Removes a plugin if all commands and listeners are removed"""
        if len(plugin.raw_commands) == 0 and len(plugin._listeners) == 0:
            self.remove_plugin(plugin)

    def load_extension(self, extension):
        """Loads an extension using a pre-made load/unload functions"""
        if extension in self.extensions:
            raise lightbulb.errors.ExtensionAlreadyLoaded(f"Extension {extension!r} is already loaded.")

        try:
            ext = importlib.import_module(extension)
        except ModuleNotFoundError:
            raise lightbulb.errors.ExtensionNotFound(f"No extension by the name {extension!r} was found") from None

        if not hasattr(ext, 'load') and not hasattr(ext, 'unload'):
            ext.load = extension_load.__get__(ext)
            ext.unload = extension_unload.__get__(ext)

        self._current_extension = ext
        ext.load(self)
        self.extensions.append(extension)
        logging.info("Extension loaded %r", extension)
        self._current_extension = None


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
    content = 1 << 0
    embed = 1 << 1
    image = 1 << 2
    files = 1 << 3
    all = embed | image | files | content

def typeparser(last_option: str, default: MessageOutput, implements: MessageOutput) -> typing.Tuple[str, MessageOutput]:
    last_word = last_option.split()[-1]
    if last_word[0] == '>':
        last_option = ' '.join(last_option.split()[:-1])

        if last_word == '>text':
            if implements & MessageOutput.content != MessageOutput.content:
                raise Error('This command doesn\'t support the output type ' + last_word)
            default = MessageOutput.content
        elif last_word == '>embed':
            if implements & MessageOutput.content != MessageOutput.embed:
                raise Error('This command doesn\'t support the output type ' + last_word)
            default = MessageOutput.embed
        elif last_word == '>image':
            if implements & MessageOutput.content != MessageOutput.image:
                raise Error('This command doesn\'t support the output type ' + last_word)
            default = MessageOutput.image
        elif last_word == '>files':
            if implements & MessageOutput.content != MessageOutput.files:
                raise Error('This command doesn\'t support the output type ' + last_word)
            default = MessageOutput.files
        else:
            raise Error('Unknown output type ' + last_word)

    return (last_option, default)

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
        if self.output & MessageOutput.embed == MessageOutput.embed:
            content = ''
            out['embed'] = self.embed if self.embed else undefined.UNDEFINED
        if self.output & MessageOutput.files == MessageOutput.files or self.output & MessageOutput.image == MessageOutput.image:
            content = ''
            out['attachments'] = attachments if attachments else undefined.UNDEFINED
        if self.output & MessageOutput.content == MessageOutput.content:
            content = self.content

        try:
            return await bot.rest.create_message(channel, content, reply=reply, **out)
        except hikari.BadRequestError as e:
            errors = dict(e.errors)
            if not errors or len(errors['message_reference']['_errors']) > 1 or errors['message_reference']['_errors'][0]['code'] != 'REPLIES_UNKNOWN_MESSAGE':
                raise e

            # Retry message without reply if REPLIES_UNKNOWN_MESSAGE
            return await bot.rest.create_message(channel, content, **out)

def extension_load(ext, bot: Bot):
    plugin = bot.make_plugin(ext.PLUGIN_NAME, ext.PLUGIN_DESC)

    for c in ext.COMMANDS:
        plugin.command(c)

    for k,v in ext.LISTENERS.items():
        plugin.listener(v, k)

    bot.readd_plugin(plugin)

def extension_unload(ext, bot: Bot):
    plugin = bot.plugins[ext.PLUGIN_NAME]

    for c in ext.COMMANDS:
        bot.remove_command(c)
        plugin.raw_commands.remove(c)

    plugin._all_commands.clear()
    plugin.create_commands()

    for k,v in ext.LISTENERS.items():
        bot.unsubscribe(v, k)

    plugin._listeners = {k:v for k,v in plugin._listeners.items() if v not in ext.LISTENERS}

    bot.readd_plugin(plugin)
    bot.clean_plugin(plugin)

ERROR_COLOR = 0xff4444
EMBED_COLOR = 0x8f8f8f
