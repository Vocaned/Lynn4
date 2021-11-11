import os

import hikari

import lynn

if __name__ == '__main__':
    # uvloops improves performance, but is only available for UNIX systems.
    if os.name != "nt":
        import uvloop
        uvloop.install()

    bot = lynn.Bot()
    bot.run(activity=bot.config.get('activity'), status=bot.config.get('status'))
