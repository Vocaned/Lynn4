import logging
import traceback
import os
import aiohttp

import hikari
import lightbulb
import lynn
from lightbulb import errors


plugin = lightbulb.Plugin('errors')

@plugin.listener(lightbulb.CommandErrorEvent)
async def handle_command_error(event: lightbulb.CommandErrorEvent):
    error = event.exception
    if isinstance(error, errors.CommandNotFound) \
    or isinstance(error, errors.HumanOnly) \
    or isinstance(error, errors.BotOnly) \
    or not event.context.command:
        return


    if isinstance(error, errors.CommandInvocationError):
        logging.error('Ignoring exception in %s', event.context.command)
        try:
            if not os.path.exists('data'):
                os.mkdir('data')
            with open('data/error.dat', 'w', encoding='utf-8') as f:
                f.write('\n'.join(traceback.format_exception(*event.exc_info)))
        except:
            logging.error('Could not write error into error.dat')

        if not event.context:
            return

        try:
            await event.context.message.add_reaction('\N{NO ENTRY SIGN}')
        except:
            pass

    errtype = None
    errmsg = None

    if isinstance(error, errors.NotEnoughArguments):
        errtype = f'Not enough arguments for command `{event.context.command.name}`'
        errmsg = f'Usage: \n ```{event.context.prefix}{event.context.command.signature}```\n'
        errmsg += f'Missing arguments: `{", ".join(o.name for o in error.missing_options)}`'

    elif isinstance(error, errors.ConverterFailure):
        errtype = f'Type converter failed for command `{event.context.command.name}`'
        errmsg = f'Usage: \n ```{event.context.prefix}{event.context.command.signature}```\n'

    elif isinstance(error, errors.CommandIsOnCooldown):
        errtype = f'Command `{event.context.command.name}` is on cooldown'
        errmsg = f'Try again in {int(error.retry_after)} seconds.'

    elif isinstance(error, errors.OnlyInGuild):
        errtype = f'Command {event.context.command.name} can only be used in guilds'

    elif isinstance(error, errors.OnlyInDM):
        errtype = f'Command {event.context.command.name} can only be used in DMs'

    elif isinstance(error, errors.NotOwner):
        errtype = f'Command {event.context.command.name} may only be used by the bot owner'

    elif isinstance(error, errors.NSFWChannelOnly):
        errtype = f'Command {event.context.command.name} may only be used in NSFW channels'

    elif isinstance(error, errors.MissingRequiredRole):
        errtype = f'You are missing a role required to run command `{event.context.command.name}`'

    elif isinstance(error, errors.MissingRequiredPermission):
        errtype = f'You are missing a permission required to run command `{event.context.command.name}`'
        errmsg = f'Missing permissions: `{", ".join(str(p) for p in error.missing_perms)}`'

    elif isinstance(error, errors.BotMissingRequiredPermission):
        errtype = f'The bot is missing a permission required to run command `{event.context.command.name}`'
        errmsg = f'Missing permissions: `{", ".join(str(p) for p in error.missing_perms)}`'

    elif isinstance(error, errors.MissingRequiredAttachment):
        errtype = f'You are missing a required attachment to run command `{event.context.command.name}`'

    elif isinstance(error, errors.CommandInvocationError):
        errtype = f'An uncaught exception occured in `{event.context.command.name}`'

        original = error.original
        if isinstance(original, aiohttp.ClientOSError):
            original = original.__cause__ # Get the original cause of errors related to sending a message

        errmsg = f'{type(original).__name__}: {original}'

    elif isinstance(error, lynn.Error):
        errtype = error.title
        errmsg = error.text

    else:
        errtype = f'Unknown error type {type(error)} occured.'

    embed = hikari.Embed(color=lynn.ERROR_COLOR, title=errtype, description=errmsg)
    await lynn.Message(embed=embed).send(event.context)

@lightbulb.add_checks(lightbulb.owner_only)
@plugin.command
@lightbulb.command('debug', 'Displays traceback from the last error')
@lightbulb.implements(lightbulb.PrefixCommand)
async def debug(ctx: lightbulb.Context):
    with open('data/error.dat', 'r', encoding='utf-8') as errors:
        error = errors.read()
        if not error:
            await lynn.Message('No errors logged.').send(ctx)
        else:
            await lynn.Message(f'```{error}```').send(ctx)

def load(bot: lynn.Bot):
    bot.add_plugin(plugin)

def unload(bot: lynn.Bot):
    bot.remove_plugin(plugin)
