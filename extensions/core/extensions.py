import lightbulb
import lynn

class Extensions(lynn.Plugin):

    @lightbulb.check(lightbulb.owner_only)
    @lightbulb.command()
    async def unload(self, ctx: lightbulb.Context, name: str):
        """Unloads an extension"""
        try:
            ctx.bot.unload_extension('extensions.'+name)
            await lynn.Message(f'Extension `{name}` successfully unloaded.').send_content(ctx)
        except lightbulb.errors.ExtensionNotLoaded as e:
            raise lynn.Error(text=f'Extension `{name}` is not loaded.') from e
        except lightbulb.errors.ExtensionMissingUnload as e:
            raise lynn.Error(text=f'Extension `{name}` does not have a valid unload method.') from e

    @lightbulb.check(lightbulb.owner_only)
    @lightbulb.command()
    async def load(self, ctx: lightbulb.Context, name: str):
        """Loads an extension"""
        try:
            ctx.bot.load_extension('extensions.'+name)
            await lynn.Message(f'Extension `{name}` successfully loaded.').send_content(ctx)
        except lightbulb.errors.ExtensionAlreadyLoaded as e:
            raise lynn.Error(text=f'Extension `{name}` is already loaded.') from e
        except lightbulb.errors.ExtensionMissingLoad as e:
            raise lynn.Error(text=f'File `{name}` is not a valid extension.') from e

    @lightbulb.check(lightbulb.owner_only)
    @lightbulb.command()
    async def reload(self, ctx: lightbulb.Context, name: str):
        """Reloads an extension"""
        try:
            ctx.bot.reload_extension('extensions.'+name)
            await lynn.Message(f'Extension `{name}` successfully reloaded.').send_content(ctx)
        except lightbulb.errors.ExtensionNotLoaded as e:
            raise lynn.Error(text=f'Extension `{name}` is not loaded.') from e
        except lightbulb.errors.ExtensionMissingUnload as e:
            raise lynn.Error(text=f'Extension `{name}` does not have a valid unload method.') from e
        except lightbulb.errors.ExtensionAlreadyLoaded as e:
            raise lynn.Error(text=f'Extension `{name}` is already loaded. This should never happen! Is the same extension running twice?') from e
        except lightbulb.errors.ExtensionMissingLoad as e:
            raise lynn.Error(text=f'File `{name}` is not a valid extension.') from e

    @lightbulb.check(lightbulb.owner_only)
    @lightbulb.command()
    async def extensions(self, ctx: lightbulb.Context):
        """Lists all extensions"""
        await lynn.Message('Extensions: ```' + ', '.join([e.lstrip('extensions.') for e in ctx.bot.extensions]) +  '```').send_content(ctx)

def load(bot: lynn.Bot):
    bot.add_plugin(Extensions(bot))

def unload(bot: lynn.Bot):
    bot.remove_plugin('Extensions')
