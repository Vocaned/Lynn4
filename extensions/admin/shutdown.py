import lightbulb
import lynn

class Shutdown(lynn.Plugin):

    @lightbulb.check(lightbulb.owner_only)
    @lightbulb.command()
    async def shutdown(self, ctx: lightbulb.Context):
        await ctx.message.add_reaction('\N{WAVING HAND SIGN}')
        await lynn.Message(content='Goodbye!').send_content(ctx)
        await self.bot.close()

def load(bot: lynn.Bot):
    bot.add_plugin(Shutdown(bot))

def unload(bot: lynn.Bot):
    bot.remove_plugin('Shutdown')
