import lightbulb
import hikari
import lynn
import helpers

@lightbulb.add_checks(lightbulb.owner_only)
@lightbulb.command('git', 'Update the bot')
@lightbulb.implements(lightbulb.PrefixCommandGroup)
async def git(ctx: lightbulb.Context):
    raise lynn.IncorrectUsageError('No subcommand specified')

@lightbulb.add_checks(lightbulb.owner_only)
@git.child
@lightbulb.command('reset', 'Reset the git branch', aliases=['fuck'])
@lightbulb.implements(lightbulb.PrefixSubCommand)
async def reset(ctx: lightbulb.Context):
    msg = await helpers.check_output(['git', 'reset', '--hard', 'origin/master'])
    return lynn.Message(helpers.codeblock(msg))

@lightbulb.add_checks(lightbulb.owner_only)
@git.child
@lightbulb.command('pull', 'Pull from git origin')
@lightbulb.implements(lightbulb.PrefixSubCommand)
async def pull(ctx: lightbulb.Context):
    msg = await helpers.check_output(['git', 'pull'])
    msg += '\n'
    msg += await helpers.check_output(['git', 'log', '@{1}..', '--format="%h %an | %B%n%N"'])
    return lynn.Message(helpers.codeblock(msg))

@lightbulb.add_checks(lightbulb.owner_only)
@git.child
@lightbulb.option('count', 'How many latest commits to show', int, default=1)
@lightbulb.command('log', 'Show a log of last commits', aliases=['show'])
@lightbulb.implements(lightbulb.PrefixSubCommand)
async def log(ctx: lightbulb.Context):
    msg = await helpers.check_output(['git', 'log', f'-{ctx.options.count}'])
    return lynn.Message(helpers.codeblock(msg))


PLUGIN_NAME = 'admin'
PLUGIN_DESC = 'Administrator commands for manipulating the bot'
COMMANDS = [
    git
]
LISTENERS = {}
