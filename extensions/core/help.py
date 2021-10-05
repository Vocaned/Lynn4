import hikari
import lightbulb
import lynn

original_help_command = None

class Help(lynn.Plugin):
    class CustomHelp(lightbulb.help.HelpCommand):
        def __init__(self, bot, plugin) -> None:
            self.bot = bot
            self.plugin = plugin
            if self.bot.get_command("help") is None:
                self.bot.add_command(_help_cmd)

        async def object_not_found(self, ctx: lightbulb.Context, name: str):
            await self.plugin.respond(ctx, embed=hikari.Embed(color=lynn.ERROR_COLOR, description=f'`{name}` is not a valid command, group or category.'))

        # TODO:
        #async def send_help_overview(self, ctx: lightbulb.Context):
        #    ...

        async def send_plugin_help(self, ctx: lightbulb.Context, plugin: lightbulb.Plugin):
            embed = hikari.Embed(color=lynn.EMBED_COLOR)
            embed.title = f'Help for plugin `{plugin.name}`'
            embed.description = lightbulb.get_help_text(plugin) or 'No help text provided.'
            embed.add_field('Commands', ', '.join(f'`{c.name}`' for c in sorted(plugin._commands.values(), key=lambda c: c.name)) or 'No commands in the category')
            await self.plugin.respond(ctx, embed=embed)

        async def send_command_help(self, ctx: lightbulb.Context, command: lightbulb.Command):
            embed = hikari.Embed(color=lynn.EMBED_COLOR)
            embed.title = f'Help for command `{command.name}`'
            embed.description = f'Usage: \n ```{ctx.clean_prefix}{lightbulb.get_command_signature(command)}```\n'
            embed.description += lightbulb.get_help_text(command) or 'No help text provided.'
            await self.plugin.respond(ctx, embed=embed)

        async def send_group_help(self, ctx: lightbulb.Context, group: lightbulb.Group):
            embed = hikari.Embed(color=lynn.EMBED_COLOR)
            embed.title = f'Help for command group `{group.name}`'
            embed.description = f'Usage: \n ```{ctx.clean_prefix}{lightbulb.get_command_signature(group)}```\n'
            embed.description += lightbulb.get_help_text(command) or 'No help text provided.'

            if group.subcommands:
                embed.add_field('Subcommands', ', '.join(f'`{c.name}`' for c in sorted(group.subcommands, key=lambda c: c.name)))

            await self.plugin.respond(ctx, embed=embed)


def load(bot: lightbulb.Bot):
    global original_help_command

    original_help_command = bot.help_command
    help_plugin = Help(bot)
    bot.help_command = help_plugin.CustomHelp(bot, help_plugin)
    bot.add_plugin(help_plugin)

def unload(bot: lightbulb.Bot):
    bot.remove_plugin('Help')
    bot.help_command = original_help_command
