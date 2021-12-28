import lightbulb
import lynn

async def invoke(cmd, context) -> None:
    context._invoked = cmd
    await cmd.evaluate_checks(context)
    await cmd.evaluate_cooldowns(context)
    assert isinstance(context, lightbulb.context.PrefixContext)
    await context._parser.inject_args_to_context()

    response = await cmd(context)

    if response:
        if not isinstance(response, lynn.Message):
            raise lynn.Error(f'Command responded with an invalid type <{type(response)}>', response)
        await response.send(context)

        if response.files:
            for f in response.files:
                if isinstance(f, lynn.TemporaryFile):
                    f.close() # Close potential temporary files after command is fully handled
    else:
        if response is not False and cmd is not context.app.help_command:
            raise lynn.Error(f'Command `{cmd.name}` did not return any data.')


def load(bot: lynn.Bot):
    lightbulb.PrefixCommand.invoke = invoke

def unload(bot: lynn.Bot):
    raise lynn.Error('CommandHandler extension cannot be unloaded!', 'Doing so would brick the bot')
