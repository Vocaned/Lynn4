import hikari
import lightbulb
from utils import respond

class Help(lightbulb.Plugin):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        self._original_help_command = bot.help_command
        bot.help_command = CustomHelp(bot)

class CustomHelp(lightbulb.help.HelpCommand):
    async def object_not_found(self, ctx: lightbulb.Context, name: str):
        await respond(ctx, embed=hikari.Embed(color=0xff4444, description=f'`{name}` is not a valid command, group or category.'))

    # TODO:
    #async def send_help_overview(self, ctx: lightbulb.Context):
    #    ...

    async def send_plugin_help(self, ctx: lightbulb.Context, plugin: lightbulb.Plugin):
        embed = hikari.Embed(color=0x8f8f8f)
        embed.title = f'Help for plugin {plugin.name}'
        embed.description = lightbulb.get_help_text(plugin) or 'No help text provided.'
        embed.add_field('Commands', ', '.join(f'`{c.name}`' for c in sorted(plugin._commands.values(), key=lambda c: c.name)) or 'No commands in the category')
        await respond(ctx, embed=embed)

    async def send_command_help(self, ctx: lightbulb.Context, command: lightbulb.Command):
        embed = hikari.Embed(color=0x8f8f8f)
        embed.title = f'Help for command {command.name}'
        embed.description = f'Usage: \n ```{ctx.clean_prefix}{lightbulb.get_command_signature(command)}```\n'
        embed.description += lightbulb.get_help_text(command) or 'No help text provided.'
        await respond(ctx, embed=embed)

    async def send_group_help(self, ctx: lightbulb.Context, group: lightbulb.Group):
        embed = hikari.Embed(color=0x8f8f8f)
        embed.title = f'Help for command group {group.name}'
        embed.description = f'Usage: \n ```{ctx.clean_prefix}{lightbulb.get_command_signature(group)}```\n'
        embed.description += lightbulb.get_help_text(command) or 'No help text provided.'

        if group.subcommands:
            embed.add_field('Subcommands', ', '.join(f'`{c.name}`' for c in sorted(group.subcommands, key=lambda c: c.name)))
        
        await respond(ctx, embed=embed)


def load(bot: lightbulb.Bot):
    bot.add_plugin(Help(bot))

def unload(bot: lightbulb.Bot):
    bot.remove_plugin('Help')
