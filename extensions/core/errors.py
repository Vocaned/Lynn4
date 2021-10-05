import hikari
import lightbulb
from lightbulb import errors
import logging
import traceback
import lynn

class Errors(lynn.Plugin):

    @lightbulb.plugins.listener(lightbulb.CommandErrorEvent)
    async def handle_command_error(self, event: lightbulb.CommandErrorEvent):
        error = event.exception
        if isinstance(error, errors.CommandNotFound) \
        or isinstance(error, errors.HumanOnly) \
        or isinstance(error, errors.BotOnly) \
        or not event.command:
            return
        

        if isinstance(error, errors.CommandInvocationError) or isinstance(error, errors.SlashCommandInvocationError):
            logging.error(f'Ignoring exception in {event.command}')
            try:
                with open('error.dat', 'w') as f:
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
            errtype = f'Not enough arguments for command `{error.command.name}`'
            errmsg = f'Usage: \n ```{event.context.clean_prefix}{lightbulb.get_command_signature(error.command)}```\n'
            errmsg += f'Missing arguments: `{", ".join(error.missing_args)}`'
        
        elif isinstance(error, errors.TooManyArguments):
            errtype = f'Too many arguments for command `{error.command.name}`'
            errmsg = f'Usage: \n ```{event.context.clean_prefix}{lightbulb.get_command_signature(error.command)}```\n'
        
        elif isinstance(error, errors.ConverterFailure):
            errtype = f'Type converter failed for command `{event.command.name}`'
            errmsg = f'Usage: \n ```{event.context.clean_prefix}{lightbulb.get_command_signature(error.command)}```\n'

        elif isinstance(error, errors.CommandIsOnCooldown):
            errtype = f'Command `{error.command.name}` is on cooldown'
            errmsg = f'Try again in {int(error.retry_in)} seconds.'
        
        elif isinstance(error, errors.UnclosedQuotes):
            errtype = f'Unclosed quotes in arguments'
            errmsg = f'Error found in ```{text}```'

        elif isinstance(error, errors.OnlyInGuild):
            errtype = f'Command {event.command.name} can only be used in guilds'
        
        elif isinstance(error, errors.OnlyInDM):
            errtype = f'Command {event.command.name} can only be used in DMs'

        elif isinstance(error, errors.NotOwner):
            errtype = f'Command {event.command.name} may only be used by the bot owner'

        elif isinstance(error, errors.NSFWChannelOnly):
            errtype = f'Command {event.command.name} may only be used in NSFW channels'
        
        elif isinstance(error, errors.MissingRequiredRole):
            errtype = f'You are missing a role required to run command `{event.command.name}`'
        
        elif isinstance(error, errors.MissingRequiredPermission):
            errtype = f'You are missing a permission required to run command `{event.command.name}`'
            errmsg = f'Missing permissions: ```{", ".join(error.permissions)}'
        
        elif isinstance(error, errors.BotMissingRequiredPermission):
            errtype = f'The bot is missing a permission required to run command `{event.command.name}`'
            errmsg = f'Missing permissions: ```{", ".join(error.permissions)}'

        elif isinstance(error, errors.MissingRequiredAttachment):
            errtype = f'You are missing a required attachment to run command `{event.command.name}`'
    
        elif isinstance(error, errors.CommandInvocationError) \
          or isinstance(error, errors.SlashCommandInvocationError):
            errtype = f'An uncaught exception occured in `{event.command.name}`'
            errmsg = error.text

        else:
            errtype = f'Unknown error type {type(event.exception)} occured.'
        
        embed = hikari.Embed(color=lynn.ERROR_COLOR, title=errtype, description=errmsg)
        await self.respond(event.context, embed=embed)

    @lightbulb.check(lightbulb.owner_only)
    @lightbulb.command()
    async def debug(self, ctx: lightbulb.Context):
        """Displays traceback from the last error"""
        with open('error.dat', 'r') as errors:
            error = errors.read()
            if not error:
                await self.respond(ctx, 'No errors logged.')
            else:
                await self.respond(ctx, f'```{error}```')

def load(bot: lightbulb.Bot):
    bot.add_plugin(Errors(bot))

def unload(bot: lightbulb.Bot):
    bot.remove_plugin('Errors')
