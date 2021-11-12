import glob
import logging
import os

import hikari

import errors
import lynn


def create_bot() -> lynn.Bot:
    """Create and return bot"""
    bot = lynn.Bot(intents=hikari.Intents.ALL)

    for extension in [f.replace('.py', '').replace('/', '.').replace('\\', '.') for f in glob.glob('extensions/**/*.py', recursive=True)]:
        try:
            bot.load_extension(extension)
        except errors.ExtensionError as e:
            logging.error('Failed to load extension: %s', e)

    return bot

if __name__ == '__main__':
    # uvloops improves performance, but is only available for UNIX systems.
    if os.name != "nt":
        import uvloop
        uvloop.install()

    bot = create_bot()
    bot.run(activity=bot.config.get('activity'), status=bot.config.get('status'))
