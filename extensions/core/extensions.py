import hikari
import lightbulb
import lynn

class Extensions(lynn.Plugin):

    @lightbulb.check(lightbulb.owner_only)
    @lightbulb.command()
    async def unload(self, ctx: lightbulb.Context, name: str):
        """Unloads an extension"""
        try:
            ctx.bot.unload_extension('extensions.'+name)
            await self.respond(ctx, f'Extension `{name}` successfully unloaded.')
        except lightbulb.errors.ExtensionNotLoaded:
            raise lynn.Error(text=f'Extension `{name}` is not loaded.')
        except lightbulb.errors.ExtensionMissingUnload:
            raise lynn.Error(text=f'Extension `{name}` does not have a valid unload method.')

    @lightbulb.check(lightbulb.owner_only)
    @lightbulb.command()
    async def load(self, ctx: lightbulb.Context, name: str):
        """Loads an extension"""
        try:
            ctx.bot.load_extension('extensions.'+name)
            await self.respond(ctx, f'Extension `{name}` successfully loaded.')
        except lightbulb.errors.ExtensionAlreadyLoaded:
            raise lynn.Error(text=f'Extension `{name}` is already loaded.')
        except lightbulb.errors.ExtensionMissingLoad:
            raise lynn.Error(text=f'File `{name}` is not a valid extension.')
    
    @lightbulb.check(lightbulb.owner_only)
    @lightbulb.command()
    async def reload(self, ctx: lightbulb.Context, name: str):
        """Reloads an extension"""
        try:
            ctx.bot.reload_extension('extensions.'+name)
            await self.respond(ctx, f'Extension `{name}` successfully reloaded.')
        except lightbulb.errors.ExtensionNotLoaded:
            raise lynn.Error(text=f'Extension `{name}` is not loaded.')
        except lightbulb.errors.ExtensionMissingUnload:
            raise lynn.Error(text=f'Extension `{name}` does not have a valid unload method.')
        except lightbulb.errors.ExtensionAlreadyLoaded:
            raise lynn.Error(text=f'Extension `{name}` is already loaded. This should never happen! Is the same extension running twice?')
        except lightbulb.errors.ExtensionMissingLoad:
            raise lynn.Error(text=f'File `{name}` is not a valid extension.')

    @lightbulb.check(lightbulb.owner_only)
    @lightbulb.command()
    async def extensions(self, ctx: lightbulb.Context):
        """Lists all extensions"""
        await self.respond(ctx, 'Extensions: ```' + ', '.join([e.lstrip('extensions.') for e in ctx.bot.extensions]) +  '```')

def load(bot: lynn.Bot):
    bot.add_plugin(Extensions(bot))

def unload(bot: lynn.Bot):
    bot.remove_plugin('Extensions')
