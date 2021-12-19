import hikari
import lightbulb
import lynn
import datetime

plugin = lightbulb.Plugin('mod', 'Commands related to Discord moderation')

@lightbulb.add_checks(lightbulb.has_guild_permissions(hikari.Permissions.MANAGE_MESSAGES))
@lightbulb.option('msg', 'Message to echo', modifier=lightbulb.commands.base.OptionModifier.CONSUME_REST)
@plugin.command
@lightbulb.command('echo', 'Echoes')
@lightbulb.implements(lightbulb.PrefixCommand)
async def echo(ctx: lightbulb.Context) -> None:
    return lynn.Message(ctx.options.msg)

@lightbulb.add_checks(lightbulb.has_guild_permissions(hikari.Permissions.BAN_MEMBERS))
@lightbulb.add_checks(lightbulb.bot_has_guild_permissions(hikari.Permissions.BAN_MEMBERS))
@lightbulb.option('reason', 'Reason for the ban', default='', modifier=lightbulb.commands.base.OptionModifier.CONSUME_REST)
@lightbulb.option('member', 'Member to ban', hikari.Member)
@plugin.command
@lightbulb.command('ban', 'Bans a member')
@lightbulb.implements(lightbulb.PrefixCommand)
async def ban(ctx: lightbulb.Context) -> None:
    await ctx.options.member.ban(reason=f'Banned by {ctx.author.username}#{ctx.author.discriminator}{": " + ctx.options.reason if ctx.options.reason else ""}')
    return lynn.Message(f'{ctx.options.member.username}#{ctx.options.member.discriminator} has been banned.')

@lightbulb.add_checks(lightbulb.has_guild_permissions(hikari.Permissions.BAN_MEMBERS))
@lightbulb.add_checks(lightbulb.bot_has_guild_permissions(hikari.Permissions.BAN_MEMBERS))
@lightbulb.option('reason', 'Reason for the ban', default='', modifier=lightbulb.commands.base.OptionModifier.CONSUME_REST)
@lightbulb.option('user', 'User to hackban', hikari.Snowflake)
@plugin.command
@lightbulb.command('hackban', 'Bans an user by their ID')
@lightbulb.implements(lightbulb.PrefixCommand)
async def hackban(ctx: lightbulb.Context) -> None:
    await ctx.app.rest.ban_user(ctx.guild_id, ctx.options.user, reason=f'Banned by {ctx.author.username}#{ctx.author.discriminator}{": " + ctx.options.reason if ctx.options.reason else ""}')
    baninfo = await ctx.app.rest.fetch_ban(ctx.guild.id, ctx.options.user)
    return lynn.Message(f'{baninfo.user.username}#{baninfo.user.discriminator} has been banned.')

@lightbulb.add_checks(lightbulb.has_guild_permissions(hikari.Permissions.BAN_MEMBERS))
@lightbulb.add_checks(lightbulb.bot_has_guild_permissions(hikari.Permissions.BAN_MEMBERS))
@lightbulb.option('user', 'User to unban', hikari.Snowflake)
@plugin.command
@lightbulb.command('unban', 'Bans an user')
@lightbulb.implements(lightbulb.PrefixCommand)
async def unban(ctx: lightbulb.Context) -> None:
    baninfo = await ctx.app.rest.fetch_ban(ctx.guild.id, ctx.options.user)
    await ctx.app.rest.unban_user(ctx.guild_id, ctx.options.user, reason=f'Unbanned by {ctx.author.username}#{ctx.author.discriminator}')
    return lynn.Message(f'{baninfo.user.username}#{baninfo.user.discriminator} has been unbanned.')

@lightbulb.add_checks(lightbulb.has_guild_permissions(hikari.Permissions.KICK_MEMBERS))
@lightbulb.add_checks(lightbulb.bot_has_guild_permissions(hikari.Permissions.KICK_MEMBERS))
@lightbulb.option('reason', 'Reason for the kick', default='', modifier=lightbulb.commands.base.OptionModifier.CONSUME_REST)
@lightbulb.option('member', 'Member to kick', hikari.Member)
@plugin.command
@lightbulb.command('kick', 'Kicks a member')
@lightbulb.implements(lightbulb.PrefixCommand)
async def kick(ctx: lightbulb.Context) -> None:
    await ctx.options.member.kick(reason=f'Kicked by {ctx.author.username}#{ctx.author.discriminator}{": " + ctx.options.reason if ctx.options.reason else ""}')
    return lynn.Message(f'{ctx.options.member.username}#{ctx.options.member.discriminator} has been kicked.')

@lightbulb.add_checks(lightbulb.has_guild_permissions(hikari.Permissions.MANAGE_NICKNAMES))
@lightbulb.add_checks(lightbulb.bot_has_guild_permissions(hikari.Permissions.MANAGE_NICKNAMES))
@lightbulb.option('name', 'New nickname', modifier=lightbulb.commands.base.OptionModifier.CONSUME_REST)
@lightbulb.option('member', 'Member to kick', hikari.Member)
@plugin.command
@lightbulb.command('nick', 'Changes a member\'s nickname', aliases=['nickname'])
@lightbulb.implements(lightbulb.PrefixCommand)
async def nick(ctx: lightbulb.Context) -> None:
    await ctx.options.member.edit(nick=ctx.options.name, reason=f'Changed by {ctx.author.username}#{ctx.author.discriminator}')
    return lynn.Message(f'{ctx.options.member.username}#{ctx.options.member.discriminator}\'s name was set to {ctx.options.nick}.')

@lightbulb.add_checks(lightbulb.has_guild_permissions(hikari.Permissions.MANAGE_ROLES))
@lightbulb.add_checks(lightbulb.bot_has_guild_permissions(hikari.Permissions.MANAGE_ROLES))
@lightbulb.option('role', 'Role to change', hikari.Role, modifier=lightbulb.commands.base.OptionModifier.CONSUME_REST)
@lightbulb.option('member', 'Member to change role on', hikari.Member)
@plugin.command
@lightbulb.command('role', 'Changes a member\'s role')
@lightbulb.implements(lightbulb.PrefixCommand)
async def role(ctx: lightbulb.Context) -> None:
    roles = ctx.options.member.role_ids
    if ctx.options.role in roles:
        await ctx.options.member.remove_role(ctx.options.role, reason=f'Changed by {ctx.author.username}#{ctx.author.discriminator}')
        return lynn.Message(f'Removed {ctx.options.role.name} from {ctx.options.member.username}#{ctx.options.member.discriminator}\'s roles')
    else:
        await ctx.options.member.add_role(ctx.options.role, reason=f'Changed by {ctx.author.username}#{ctx.author.discriminator}')
        return lynn.Message(f'Added {ctx.options.role.name} to {ctx.options.member.username}#{ctx.options.member.discriminator}\'s roles')

@lightbulb.add_checks(lightbulb.has_guild_permissions(hikari.Permissions.CREATE_INSTANT_INVITE))
@lightbulb.add_checks(lightbulb.bot_has_guild_permissions(hikari.Permissions.CREATE_INSTANT_INVITE))
@lightbulb.option('duration', 'Number of minutes the invite is active for', int)
@lightbulb.option('uses', 'Number of uses on the invite', int)
@plugin.command
@lightbulb.command('createinvite', 'Creates an invite to the channel', aliases=['makeinv', 'makeinvite', 'createinv'])
@lightbulb.implements(lightbulb.PrefixCommand)
async def invite(ctx: lightbulb.Context) -> None:
    inv = await ctx.app.rest.create_invite(ctx.channel_id, max_uses=ctx.options.uses, max_age=ctx.options.duration*60)
    return lynn.Message(f'Invite created: https://discord.gg/{inv.code}\n' +
                        f'Invite lasts for `{inv.max_age.seconds//60 if inv.max_age else "∞"}` minutes.\n' +
                        f'Invite can be used `{inv.max_uses if inv.max_uses else "∞"}` times.')

@lightbulb.add_checks(lightbulb.has_guild_permissions(hikari.Permissions.MANAGE_MESSAGES))
@lightbulb.add_checks(lightbulb.bot_has_guild_permissions(hikari.Permissions.MANAGE_MESSAGES))
@lightbulb.option('member', 'Member whose messages should be purged', hikari.Member, required=False)
@lightbulb.option('amount', 'Number of messages to purge (max 100)', int)
@plugin.command
@lightbulb.command('purge', 'Mass remove messages in the channel', aliases=['prune'])
@lightbulb.implements(lightbulb.PrefixCommand)
async def purge(ctx: lightbulb.Context) -> None:
    if ctx.options.amount > 100:
        raise lynn.Error('You may only purge up to 100 messages at once.')

    memberfilter = (lambda m: (m.author.id == ctx.options.member.id if ctx.options.member else True))
    toooldfilter = lambda m: m.created_at.timestamp() > (datetime.datetime.now() - datetime.timedelta(days=14)).timestamp()

    messages = await ctx.app.rest.fetch_messages(ctx.channel_id).filter(memberfilter).filter(toooldfilter).limit(ctx.options.amount+1)
    await ctx.app.rest.delete_messages(ctx.channel_id, *messages)

def load(bot: lynn.Bot):
    bot.add_plugin(plugin)

def unload(bot: lynn.Bot):
    bot.remove_plugin(plugin)
