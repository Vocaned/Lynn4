import glob
import logging
import os

import hikari
import lightbulb

import lynn


def create_bot(token: str, prefix: str) -> lynn.Bot:
    """Create and return bot"""
    bot = lynn.Bot(token=token, prefix=lightbulb.when_mentioned_or(prefix), intents=hikari.Intents.ALL)

    for extension in [f.replace('.py', '').replace('/', '.').replace('\\', '.') for f in glob.glob('extensions/**/*.py', recursive=True)]:
        try:
            bot.load_extension(extension)
        except lightbulb.errors.ExtensionError as e:
            logging.error('Failed to load extension: %s', e)

    return bot

if __name__ == '__main__':
    # uvloops improves performance, but is only available for UNIX systems.
    if os.name != "nt":
        import uvloop
        uvloop.install()

    create_bot(lynn.config.get('token'), lynn.config.get('prefix')).run(activity=lynn.config.get('activity'), status=lynn.config.get('status'))
