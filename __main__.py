import os
from pathlib import Path
import logging
import hikari
import lightbulb
import utils
import json
import glob

def create_bot(token: str, prefix: str) -> lightbulb.Bot:
    bot = lightbulb.Bot(token=token, prefix=lightbulb.when_mentioned_or(prefix), intents=hikari.Intents.ALL)

    for extension in [f.replace('.py', '').replace('/', '.').replace('\\', '.') for f in glob.glob('extensions/**/*.py', recursive=True)]:
        try:
            bot.load_extension(extension)
        except lightbulb.errors.ExtensionError as e:
            logging.error(f'Failed to load extension: {e}')

    return bot

if __name__ == '__main__':
    # Check config
    if not os.path.exists('config.json'):
        logging.critical('Config does not exist. A config.json file was created, please edit the file before running the bot again.')
        
        with open('config.json', 'w') as f:
            config_template = {'token': None, 'prefix': '%'}
            json.dump(config_template, f, indent=2)

        exit(1)

    token = utils.get_config('token')
    if not token:
        logging.critical('Token not found in config.json. Please edit the file before running the bot again.')
        exit(1)

    # uvloops improves performance, but is only available for UNIX systems.
    if os.name != "nt":
        import uvloop
        uvloop.install()

    create_bot(token, utils.get_config('prefix')).run()