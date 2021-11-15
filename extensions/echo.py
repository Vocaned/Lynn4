import hikari
import lynn
import helpers

class Extension(lynn.Extension):
    def __init__(self, bot: lynn.Bot):
        super().__init__(bot)
        self.commands = {'echo': self.echo}

    async def echo(self, ctx: hikari.GuildMessageCreateEvent):
        args = helpers.get_args(ctx.content)
        if not args:
            return lynn.Response('echooo...')
        else:
            return lynn.Response(' '.join(args))
