import glob
import logging
import os

import hikari

import errors
import lynn
import scripting

if __name__ == '__main__':
    # uvloops improves performance, but is only available for UNIX systems.
    if os.name != "nt":
        import uvloop
        uvloop.install()

    bot = lynn.Bot(intents=hikari.Intents.ALL)

    for extension in [f.replace('.py', '').replace('/', '.').replace('\\', '.') for f in glob.glob('extensions/**/*.py', recursive=True)]:
        try:
            bot.load_extension(extension)
        except errors.ExtensionError as e:
            logging.error('Failed to load extension: %s', e)

    bot.scripting = scripting.Scripting(bot)

    @bot.listen()
    async def on_message(ctx: hikari.GuildMessageCreateEvent) -> None:
        if not ctx.is_human or not ctx.content:
            return

        frst_word = ctx.content.split(' ')[0]
        response = None

        for ext in bot.extensions.values():
            if frst_word in ext.commands:
                response = await ext.commands[frst_word](ctx)

        if response and isinstance(response, lynn.Response):
            await response.send(bot, ctx.channel_id)

    bot.run(activity=bot.config.get('activity'), status=bot.config.get('status'))
