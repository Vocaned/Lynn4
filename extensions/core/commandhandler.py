import lightbulb
import lynn

async def invoke(context) -> None:
    if context.command is None:
        raise TypeError("This context cannot be invoked - no command was resolved.")
    if context.command is not None and context.command.auto_defer:
        await context.app.rest.trigger_typing(context.channel_id)
        context._deferred = True

    context._invoked = context.command
    await context.command.evaluate_checks(context)
    await context.command.evaluate_cooldowns(context)

    assert isinstance(context, lightbulb.context.PrefixContext)
    await context._parser.inject_args_to_context()

    response = await context.command(context)

    if response:
        if not isinstance(response, lynn.Message):
            raise lynn.Error(f'Command responded with an invalid type <{type(response)}>', response)
        await response.send(context)

        if response.files:
            for f in response.files:
                if isinstance(f, lynn.TemporaryFile):
                    f.close() # Close potential temporary files after command is fully handled
    else:
        if response is not False and context.command != context.app.help_command:
            raise lynn.Error(f'Command `{context.command.name}` did not return any data.')


def load(bot: lynn.Bot):
    lightbulb.Context.invoke = invoke

def unload(bot: lynn.Bot):
    raise lynn.Error('CommandHandler extension cannot be unloaded!', 'Doing so would brick the bot')
