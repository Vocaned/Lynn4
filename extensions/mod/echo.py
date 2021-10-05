import hikari
import lightbulb
import asyncio
from utils import respond

class Echo(lightbulb.Plugin):

    @lightbulb.check(lightbulb.has_guild_permissions(hikari.Permissions.MANAGE_MESSAGES))
    @lightbulb.command()
    async def echo(self, ctx: lightbulb.Context, *, msg: str):
        """Echoes"""
        await respond(ctx, msg)

def load(bot: lightbulb.Bot):
    bot.add_plugin(Echo())

def unload(bot: lightbulb.Bot):
    bot.remove_plugin('Echo')
