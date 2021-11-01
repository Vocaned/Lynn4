import json
import logging
import os
import time
import sys
import typing

import hikari
from hikari import undefined
import lavasnek_rs
import lightbulb


class Config:
    config_template = {
        'token': None, # Bot's token
        'prefix': '%', # Bot's prefix
        'typingindicator': False, # Should the bot trigger "is typing..." activity when processing commands
        'status': 'online', # Bot's default status
        'activity': None, # Bot's default activity
        'lavalink_pass': "password", # Password for lavalink instance
        'lavalink_host': '127.0.0.1' # Lavalink instance host, null to disable lavalink
    }
    required_values = ('token',)

    def __init__(self, path='config.json'):
        if not os.path.exists(path):
            logging.critical('Config does not exist. A %s file was created, please edit it before running the bot again.', path)
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(self.config_template, f, indent=2)
            sys.exit(1)

        self.path = path
        self.dict = self.get_config()

        for val in self.required_values:
            if self.dict.get(val) is None:
                logging.critical('Required value "%s" not set in %s. Please edit the file before running the bot again.', val, self.path)
                sys.exit(1)

        for k, v in self.config_template.items():
            if k not in self.dict:
                logging.warning('Required value "%s" not found in %s. The default value of "%s" was used. Please edit the file if necessary.', val, self.path, v)
                self.set(val, v)

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


class Plugin(lightbulb.Plugin):
    """Improved Plugin class"""
    def __init__(self, bot: lightbulb.Bot):
        super().__init__()
        self.bot = bot

class Error(lightbulb.errors.CommandError):
    """Custom error message, raise to send an error embed."""

    def __init__(self, title: str = None, text: str = None):
        self.title: str = title
        """The error title."""
        self.text: str = text
        """The error text."""

class Response:
    """Better response handling"""

    def __init__(self, content: undefined.UndefinedOr[typing.Any] = undefined.UNDEFINED,
        *,
        attachment: undefined.UndefinedOr[hikari.files.Resourceish] = undefined.UNDEFINED,
        attachments: undefined.UndefinedOr[typing.Sequence[hikari.files.Resourceish]] = undefined.UNDEFINED,
        component = undefined.UNDEFINED,
        components = undefined.UNDEFINED,
        embed: undefined.UndefinedOr[hikari.Embed] = undefined.UNDEFINED,
        embeds: undefined.UndefinedOr[typing.Sequence[hikari.Embed]] = undefined.UNDEFINED,
        nonce: undefined.UndefinedOr[str] = undefined.UNDEFINED,
        tts: undefined.UndefinedOr[bool] = undefined.UNDEFINED,
        reply: typing.Union[
            undefined.UndefinedType, hikari.snowflakes.SnowflakeishOr[hikari.PartialMessage], bool
        ] = undefined.UNDEFINED,
        mentions_everyone: undefined.UndefinedOr[bool] = undefined.UNDEFINED,
        mentions_reply: undefined.UndefinedOr[bool] = undefined.UNDEFINED,
        user_mentions: undefined.UndefinedOr[
            typing.Union[hikari.snowflakes.SnowflakeishSequence[hikari.PartialUser], bool]
        ] = undefined.UNDEFINED,
        role_mentions: undefined.UndefinedOr[
            typing.Union[hikari.snowflakes.SnowflakeishSequence[hikari.PartialRole], bool]
        ] = undefined.UNDEFINED,):
        self.content = content
        self.force_disable_reply = False
        if reply is False:
            self.force_disable_reply = True
        self.data = {
            'attachment': attachment, 'attachments': attachments, 'component': component, 'components': components,
            'embed': embed, 'embeds': embeds, 'nonce': nonce, 'tts': tts, 'mentions_everyone': mentions_everyone,
            'mentions_reply': mentions_reply, 'user_mentions': user_mentions, 'role_mentions': role_mentions
        }

    async def send_channel(self, channel: hikari.SnowflakeishOr[hikari.TextableChannel], author_id: typing.Union[str, int, hikari.Snowflakeish]) -> hikari.Message:
        raise NotImplementedError()
        """
        try:
            return await self.bot.rest.create_message(content=self.content, channel=channel, **self.data)
        except hikari.BadRequestError as e:
            try:
                # pylint: disable=unsubscriptable-object
                if len(e.errors['message_reference']['_errors']) == 1 and e.errors['message_reference']['_errors'][0]['code'] == 'REPLIES_UNKNOWN_MESSAGE':
                    msg = self.content
                    if author_id:
                        if msg:
                            msg.append(f'<@{author_id}>, {self.content}')
                        else:
                            msg = f'<@{author_id}>'
                    return await self.bot.rest.create_message(content=msg, channel=channel, **self.data)
            except KeyError:
                pass
            return None"""

    async def send(self, ctx: lightbulb.Context) -> hikari.Message:
        if not self.force_disable_reply:
            self.data['reply'] = ctx.message
        #return await self.send_channel(ctx.channel_id, ctx.author.id)
        return await ctx.respond(content=self.content, **self.data)

class Data:
    """Global data shared across the entire bot."""
    def __init__(self) -> None:
        self.lavalink: lavasnek_rs.Lavalink = None # pylint: disable=no-member

class Bot(lightbulb.Bot):
    """Improved Bot class"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data = Data()

ERROR_COLOR = 0xff4444
EMBED_COLOR = 0x8f8f8f

config = Config()
startup_time = time.time()
