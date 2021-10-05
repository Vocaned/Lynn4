import hikari
import lightbulb
from utils import respond

class Extensions(lightbulb.Plugin):

    @lightbulb.check(lightbulb.owner_only)
    @lightbulb.command()
    async def unload(self, ctx: lightbulb.Context, name: str):
        """Unloads an extension"""
        ctx.bot.unload_extension('extensions.'+name)
        await respond(ctx, f'Extension `{name}` successfully unloaded.')

    @lightbulb.check(lightbulb.owner_only)
    @lightbulb.command()
    async def load(self, ctx: lightbulb.Context, name: str):
        """Loads an extension"""
        ctx.bot.load_extension('extensions.'+name)
        await respond(ctx, f'Extension `{name}` successfully loaded.')
    
    @lightbulb.check(lightbulb.owner_only)
    @lightbulb.command()
    async def reload(self, ctx: lightbulb.Context, name: str):
        """Reloads an extension"""
        ctx.bot.reload_extension('extensions.'+name)
        await respond(ctx, f'Extension `{name}` successfully reloaded.')

    @lightbulb.check(lightbulb.owner_only)
    @lightbulb.command()
    async def extensions(self, ctx: lightbulb.Context):
        """Lists all extensions"""
        await respond(ctx, 'Extensions: ```' + ', '.join(ctx.bot.extensions) +  '```')

def load(bot: lightbulb.Bot):
    bot.add_plugin(Extensions())

def unload(bot: lightbulb.Bot):
    bot.remove_plugin('Extensions')
