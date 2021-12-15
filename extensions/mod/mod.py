import hikari
import lightbulb
import lynn

plugin = lightbulb.Plugin('mod', 'Commands related to Discord moderation')

@lightbulb.add_checks(lightbulb.has_guild_permissions(hikari.Permissions.MANAGE_MESSAGES))
@lightbulb.option('msg', 'Message to echo', modifier=lightbulb.commands.base.OptionModifier.CONSUME_REST)
@plugin.command
@lightbulb.command('echo', 'Echoes')
@lightbulb.implements(lightbulb.PrefixCommand)
async def echo(ctx: lightbulb.Context) -> None:
    return lynn.Message(ctx.options.msg)


def load(bot: lynn.Bot):
    bot.add_plugin(plugin)

def unload(bot: lynn.Bot):
    bot.remove_plugin(plugin)
