import lightbulb
import lynn

@lightbulb.add_checks(lightbulb.owner_only)
@lightbulb.option('name', 'Extension name')
@lightbulb.command('unload', 'Unloads an extension')
@lightbulb.implements(lightbulb.PrefixCommand)
async def unload_extension(ctx: lightbulb.Context):
    try:
        ctx.app.unload_extensions('extensions.'+ctx.options.name)
        return lynn.Message(f'Extension `{ctx.options.name}` successfully unloaded.')
    except lightbulb.errors.ExtensionNotLoaded as e:
        raise lynn.Error(text=f'Extension `{ctx.options.name}` is not loaded.') from e
    except lightbulb.errors.ExtensionMissingUnload as e:
        raise lynn.Error(text=f'Extension `{ctx.options.name}` does not have a valid unload method.') from e

@lightbulb.add_checks(lightbulb.owner_only)
@lightbulb.option('name', 'Extension name')
@lightbulb.command('load', 'Loads an extension')
@lightbulb.implements(lightbulb.PrefixCommand)
async def load_extension(ctx: lightbulb.Context):
    try:
        ctx.app.load_extension('extensions.'+ctx.options.name)
        return lynn.Message(f'Extension `{ctx.options.name}` successfully loaded.')
    except lightbulb.errors.ExtensionAlreadyLoaded as e:
        raise lynn.Error(text=f'Extension `{ctx.options.name}` is already loaded.') from e
    except lightbulb.errors.ExtensionMissingLoad as e:
        raise lynn.Error(text=f'File `{ctx.options.name}` is not a valid extension.') from e

@lightbulb.add_checks(lightbulb.owner_only)
@lightbulb.option('name', 'Extension name')
@lightbulb.command('reload', 'Reloads an extension')
@lightbulb.implements(lightbulb.PrefixCommand)
async def reload_extension(ctx: lightbulb.Context):
    try:
        ctx.app.unload_extensions('extensions.'+ctx.options.name)
        ctx.app.load_extension('extensions.'+ctx.options.name)
        return lynn.Message(f'Extension `{ctx.options.name}` successfully reloaded.')
    except lightbulb.errors.ExtensionNotLoaded as e:
        raise lynn.Error(text=f'Extension `{ctx.options.name}` is not loaded.') from e
    except lightbulb.errors.ExtensionMissingUnload as e:
        raise lynn.Error(text=f'Extension `{ctx.options.name}` does not have a valid unload method.') from e
    except lightbulb.errors.ExtensionAlreadyLoaded as e:
        raise lynn.Error(text=f'Extension `{ctx.options.name}` is already loaded. This should never happen! Is the same extension running twice?') from e
    except lightbulb.errors.ExtensionMissingLoad as e:
        raise lynn.Error(text=f'File `{ctx.options.name}` is not a valid extension.') from e

@lightbulb.add_checks(lightbulb.owner_only)
@lightbulb.command('extensions', 'Lists all extensions')
@lightbulb.implements(lightbulb.PrefixCommand)
async def extensions(ctx: lightbulb.Context):
    return lynn.Message('Extensions: ```' + ', '.join([e.lstrip('extensions.') for e in ctx.bot.extensions]) +  '```')

@lightbulb.add_checks(lightbulb.owner_only)
@lightbulb.command('plugins', 'Lists all plugins')
@lightbulb.implements(lightbulb.PrefixCommand)
async def plugins(ctx: lightbulb.Context):
    return lynn.Message('Plugins: ```' + ', '.join([e.lstrip('extensions.') for e in ctx.bot.plugins]) +  '```')

PLUGIN_NAME = 'core'
PLUGIN_DESC = 'Core features for Lynn'
COMMANDS = [
    unload_extension, load_extension,
    reload_extension, extensions,
    plugins
]
LISTENERS = {}
