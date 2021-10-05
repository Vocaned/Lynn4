import hikari
import lightbulb
import asyncio
import lynn

class Presence(lynn.Plugin):

    @lightbulb.check(lightbulb.owner_only)
    @lightbulb.command()
    async def activity(self, ctx: lightbulb.Context, *, msg: str):
        if msg:
            if msg.lower().startswith('competing in'):
                await self.bot.update_presence(activity=hikari.Activity(type=hikari.ActivityType.COMPETING, name=msg[12:]))
            elif msg.lower().startswith('listening to'):
                await self.bot.update_presence(activity=hikari.Activity(type=hikari.ActivityType.LISTENING, name=msg[12:]))
            elif msg.lower().startswith('playing'):
                await self.bot.update_presence(activity=hikari.Activity(type=hikari.ActivityType.PLAYING, name=msg[7:]))
            elif msg.lower().startswith('watching'):
                await self.bot.update_presence(activity=hikari.Activity(type=hikari.ActivityType.WATCHING, name=msg[8:]))
        else:
            await self.bot.update_presence(activity=None)

    @lightbulb.check(lightbulb.owner_only)
    @lightbulb.command()
    async def presence(self, ctx: lightbulb.Context, *, msg: str):
            await self.bot.update_presence(status=msg.lower())

def load(bot: lightbulb.Bot):
    bot.add_plugin(Presence(bot))

def unload(bot: lightbulb.Bot):
    bot.remove_plugin('Presence')
