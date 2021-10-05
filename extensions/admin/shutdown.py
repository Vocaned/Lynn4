import hikari
import lightbulb
import lynn

class Shutdown(lynn.Plugin):

    @lightbulb.check(lightbulb.owner_only)
    @lightbulb.command()
    async def shutdown(self, ctx: lightbulb.Context):
        await ctx.message.add_reaction('\N{WAVING HAND SIGN}')
        await self.respond(ctx, 'Goodbye!')
        await self.bot.close()

def load(bot: lightbulb.Bot):
    bot.add_plugin(Shutdown(bot))

def unload(bot: lightbulb.Bot):
    bot.remove_plugin('Shutdown')
