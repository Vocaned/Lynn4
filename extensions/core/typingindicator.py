import hikari
import lightbulb
import utils

global_bot = None

async def handle(event: hikari.MessageCreateEvent) -> None:
    if utils.config.get('typingindicator'):
        async with global_bot.rest.trigger_typing(event.channel_id):
            await global_bot.handle(event)
    else:
        await global_bot.handle(event)

def load(bot: lightbulb.Bot):
    global global_bot
    global_bot = bot
    # Overwrite lightbulb message handler
    bot.unsubscribe(hikari.MessageCreateEvent, bot.handle)
    bot.subscribe(hikari.MessageCreateEvent, handle)

def unload(bot: lightbulb.Bot):
    if not typingindicator:
        return

    bot.unsubscribe(hikari.MessageCreateEvent, handle)
    bot.subscribe(hikari.MessageCreateEvent, bot.handle)