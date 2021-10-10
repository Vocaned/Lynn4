import hikari
import lightbulb
import asyncio
import lynn

class Echo(lynn.Plugin):

    @lightbulb.check(lightbulb.has_guild_permissions(hikari.Permissions.MANAGE_MESSAGES))
    @lightbulb.command()
    async def echo(self, ctx: lightbulb.Context, *, msg: str):
        """Echoes"""
        await lynn.Response(msg).send(ctx)

def load(bot: lynn.Bot):
    bot.add_plugin(Echo(bot))

def unload(bot: lynn.Bot):
    bot.remove_plugin('Echo')
