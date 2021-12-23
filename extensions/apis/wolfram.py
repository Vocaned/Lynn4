import hikari
import lightbulb
import lynn
import helpers

plugin = lightbulb.Plugin('apis', 'Commands that get information from web APIs')

@lightbulb.add_cooldown(5, 1, lightbulb.UserBucket)
@lightbulb.option('query', 'Query for WolframAlpha', modifier=lightbulb.commands.OptionModifier.CONSUME_REST)
@plugin.command
@lightbulb.command('wolframalpha', 'Queries WolframAlpha', aliases=['wa', 'wolfram'], auto_defer=True)
@lightbulb.implements(lightbulb.PrefixCommand)
async def wolframalpha(ctx: lightbulb.Context):
    query, out = lynn.typeparser(ctx.options.query, lynn.MessageOutput.image, lynn.MessageOutput.image | lynn.MessageOutput.content)
    if out == lynn.MessageOutput.content:
        data, status = await helpers.rest(
            f"http://api.wolframalpha.com/v1/result?appid={ctx.app.config.get_secret('wolframalpha')}&i={helpers.escape_url(query)}",
            opts=helpers.RestOptions(returns=('raw', 'status'))
        )
    else:
        data, status = await helpers.rest(
            f"http://api.wolframalpha.com/v1/simple?appid={ctx.app.config.get_secret('wolframalpha')}&layout=labelbar&ip=None&background=2F3136&foreground=white&i={helpers.escape_url(ctx.options.query)}",
            opts=helpers.RestOptions(returns=('raw', 'status'))
        )

    if status != 200:
        err = data.decode('utf-8')
        if not err:
            err = '[unknown error]'

        if status == 501:
            raise lynn.Error('WolframAlpha could not parse the query', err)
        raise lynn.Error(f'WolframAlpha returned an error status {status}', err)

    if len(data) == 0:
        raise lynn.Error('WolframAlpha did not return any data.')

    if out == lynn.MessageOutput.content:
        return lynn.Message(data.decode('utf-8'), output=out)
    return lynn.Message(image=data, output=out)


def load(bot: lynn.Bot):
    bot.add_plugin(plugin)

def unload(bot: lynn.Bot):
    bot.remove_plugin(plugin)
