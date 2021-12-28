import lightbulb
import hikari
import lynn

@lightbulb.add_checks(lightbulb.owner_only)
@lightbulb.command('shutdown', 'Goodbye!')
@lightbulb.implements(lightbulb.PrefixCommand)
async def shutdown_cmd(ctx: lightbulb.Context):
    await ctx.message.add_reaction('\N{WAVING HAND SIGN}')
    await lynn.Message(content='Goodbye!').send(ctx)
    await ctx.app.close()

@lightbulb.add_checks(lightbulb.owner_only)
@lightbulb.option('msg', 'Activity name')
@lightbulb.command('activity', 'Sets the bot\'s activity')
@lightbulb.implements(lightbulb.PrefixCommand)
async def activity(ctx: lightbulb.Context):
    msg = ctx.options.msg
    if msg:
        if msg.lower().startswith('competing in'):
            await ctx.app.update_presence(activity=hikari.Activity(type=hikari.ActivityType.COMPETING, name=msg[12:]))
        elif msg.lower().startswith('listening to'):
            await ctx.app.update_presence(activity=hikari.Activity(type=hikari.ActivityType.LISTENING, name=msg[12:]))
        elif msg.lower().startswith('playing'):
            await ctx.app.update_presence(activity=hikari.Activity(type=hikari.ActivityType.PLAYING, name=msg[7:]))
        elif msg.lower().startswith('watching'):
            await ctx.app.update_presence(activity=hikari.Activity(type=hikari.ActivityType.WATCHING, name=msg[8:]))
    else:
        await ctx.app.update_presence(activity=None)

@lightbulb.add_checks(lightbulb.owner_only)
@lightbulb.option('type', 'Presence', choices=['online', 'idle', 'dnd', 'offline'])
@lightbulb.command('presence', 'Sets the bot\'s presence')
@lightbulb.implements(lightbulb.PrefixCommand)
async def presence(ctx: lightbulb.Context):
    await ctx.app.update_presence(status=ctx.options.type.lower())

PLUGIN_NAME = 'admin'
PLUGIN_DESC = 'Administrator commands for manipulating the bot'
COMMANDS = [
    shutdown_cmd, activity, presence
]
LISTENERS = {}
