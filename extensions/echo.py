import hikari
import lynn

class Extension(lynn.Extension):
    async def execute(self, ctx: hikari.GuildMessageCreateEvent):
        return lynn.Response('echooo...')
