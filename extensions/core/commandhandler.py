import hikari
import lightbulb
from lightbulb import events, errors
import lynn
import re
import logging

global_bot = None
ARG_SEP_REGEX = re.compile(r"(?:\s+|\n)")

# WARN: This file is an absolute mess, and will break whenever lightbulb's default command handler is updated
# Most of the file is duplicate code copy pasted from lightbulb

async def handle(event: hikari.MessageCreateEvent) -> None:
    bot = event.app
    if bot.ignore_bots and not event.is_human:
        return

    if not event.message.content:
        return

    context = await bot.get_prefix_context(event)
    if context is None:
        return

    if context.command is not None:
        await bot.dispatch(events.PrefixCommandInvocationEvent(app=bot, command=context.command, context=context))

    try:
        if context.command is None:
            raise errors.CommandNotFound(
                f"A command with name or alias {context.invoked_with!r} does not exist",
                invoked_with=context.invoked_with,
            )

        if context.command is None:
            raise TypeError("This context cannot be invoked - no command was resolved.")
        if context._command is not None and context._command.auto_defer:
            await context.app.rest.trigger_typing(context.channel_id)
            context._deferred = True

        context._invoked = context.command
        await context.command.evaluate_checks(context)
        await context.command.evaluate_cooldowns(context)
        assert isinstance(context, lightbulb.context.PrefixContext)
        await context._parser.inject_args_to_context()

        # CUSTOM CODE BEGINS
        response = await context.command(context)

        if response:
            if not isinstance(response, lynn.Message):
                raise lynn.Error(f'Command responded with an invalid type <{type(response)}>', response)
            await response.send(context)

            if response.files:
                for f in response.files:
                    if isinstance(f, lynn.TemporaryFile):
                        f.close() # Close potential temporary files after command is fully handled
        # CUSTOM CODE ENDS
    except Exception as exc:
        new_exc = exc
        if not isinstance(exc, errors.LightbulbError):
            assert context.command is not None
            new_exc = errors.CommandInvocationError(
                f"An error occurred during command {context.command.name!r} invocation", original=exc
            )
        assert isinstance(new_exc, errors.LightbulbError)
        error_event = events.PrefixCommandErrorEvent(app=bot, exception=new_exc, context=context)
        handled = await bot.maybe_dispatch_error_event(
            error_event,
            [
                getattr(context.command, "error_handler", None),
                getattr(context.command.plugin, "_error_handler", None) if context.command is not None else None,
            ],
        )

        if not handled:
            raise new_exc
    else:
        assert context.command is not None
        await bot.dispatch(events.PrefixCommandCompletionEvent(app=bot, command=context.command, context=context))


def load(bot: lynn.Bot):
    global global_bot
    global_bot = bot
    # Overwrite lightbulb message handler
    bot.unsubscribe(hikari.MessageCreateEvent, bot.handle_messsage_create_for_prefix_commands)
    bot.subscribe(hikari.MessageCreateEvent, handle)

def unload(bot: lynn.Bot):
    bot.unsubscribe(hikari.MessageCreateEvent, handle)
    bot.subscribe(hikari.MessageCreateEvent, bot.handle_messsage_create_for_prefix_commands)
