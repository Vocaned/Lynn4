import datetime
import time
import aiohttp
import hikari
import lightbulb
import feedparser
import lynn
import helpers
from utils.rest import RestOptions

@lightbulb.add_cooldown(5, 1, lightbulb.UserBucket)
@lightbulb.option('query', 'Keyword to search for', required=False, modifier=lightbulb.commands.OptionModifier.CONSUME_REST)
@lightbulb.command('news', 'Looks up news relating to a topic')
@lightbulb.implements(lightbulb.PrefixCommand)
async def news(ctx: lightbulb.Context):
    if ctx.options.query:
        resp = feedparser.parse(
            f'https://news.google.com/rss/search?q={helpers.escape_url(ctx.options.query)}&hl=en-US&gl=US&ceid=US:en'
        )
    else:
        # CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx1YlY4U0FtVnVHZ0pWVXlnQVAB = World News
        resp = feedparser.parse(
            'https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx1YlY4U0FtVnVHZ0pWVXlnQVAB?hl=en-US&gl=US&ceid=US:en'
        )

    if not resp['items']:
        raise lynn.Error('Google News did not return any news for your query.')

    async def build_embed(page_index):
        if page_index < 0:
            page_index = 0
        elif page_index > len(resp['items']):
            page_index = len(resp['items'])

        if page_index in build_embed.cache:
            return build_embed.cache[page_index]

        entry = resp['items'][page_index]

        article = await helpers.rest(entry['link'], RestOptions(returns='text'))
        ogparser = helpers.OpenGraphParser()
        ogparser.feed(article)

        if not ogparser.tags: # Article didn't have any OpenGraph meta tags. Probably blocked in EU.
            del resp['items'][page_index] # Delete result and try the next one
            return await build_embed(page_index)

        embed = hikari.Embed(color=0xf5c518)
        embed.url = entry['link']
        embed.set_author(name=entry['source']['title'])
        embed.timestamp = datetime.datetime.fromtimestamp(time.mktime(entry.published_parsed)).astimezone()

        if page_index == len(resp['items']):
            embed.set_footer('(last page reached)')

        if 'og:title' in ogparser.tags:
            embed.title = ogparser.tags['og:title']
        else:
            embed.title = entry['title'].rstrip(' - ' + entry['source']['title']) # Google News shows source in title, so remove it

        if 'og:description' in ogparser.tags:
            embed.description = ogparser.tags['og:description']
        if 'og:image' in ogparser.tags:
            embed.set_image(ogparser.tags['og:image'])

        build_embed.cache[page_index] = embed

        return embed

    build_embed.cache = {}
    nav = helpers.DynamicButtonNavigator(build_embed)
    await nav.run(ctx)
    return False

PLUGIN_NAME = 'apis'
PLUGIN_DESC = 'Getting data from APIs around the internet'
COMMANDS = [
    news
]
LISTENERS = {}
