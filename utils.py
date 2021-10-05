import json
import os
import hikari
import lightbulb
import logging

class Config:
    config_template = {'token': None, 'prefix': '%', 'typingindicator': False}

    def __init__(self, path='config.json'):
        if not os.path.exists(path):
            logging.critical(f'Config does not exist. A {path} file was created, please edit it before running the bot again.')
            with open(path, 'w') as f:
                json.dump(self.config_template, f, indent=2)
            exit(1)

        self.path = path
        self.dict = self.get_config()

        for val in self.config_template:
            if self.dict.get(val) is None:
                logging.critical(f'Required value "{val}" not found in {self.path}. Please edit the file before running the bot again.')
                exit(1)

    def get_config(self) -> dict:
        if not os.path.exists('config.json'):
            return None
        
        with open(self.path) as f:
            return json.load(f)

    def set(self, key: str, value) -> None:
        # Make sure the dict is up to date with the file
        self.dict = self.get_config()
        self.dict[key] = value

        with open(self.path, 'w') as f:
            json.dump(f)

    def get(self, key: str, default=None):
        return self.dict.get(key, default)

config = Config()


async def respond(ctx: lightbulb.Context, *args, **kwargs) -> hikari.Message:
    try:
        return await ctx.respond(reply=True, *args, **kwargs)
    except hikari.BadRequestError as e:
        try:
            if len(e.errors['message_reference']['_errors']) == 1 and e.errors['message_reference']['_errors'][0]['code'] == 'REPLIES_UNKNOWN_MESSAGE':
                # Resend the response without a reply, since the message no longer exists
                # TODO: Assumes args[0] is message, need to investigate if it can be something else as well
                msg = list(args)
                msg[0] = f'{ctx.author.mention}, {msg[0]}'
                return await ctx.respond(*msg, **kwargs)
        except KeyError:
            pass
        return None