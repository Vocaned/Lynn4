import datetime
import hikari
import lightbulb
import lynn
from helpers import rest, escape_url

@lightbulb.option('query', 'Sentence to translate', modifier=lightbulb.commands.OptionModifier.CONSUME_REST)
@lightbulb.command('translate', 'これは英語で何を言っているのだろうか？', aliases=['trans'], auto_defer=True)
@lightbulb.implements(lightbulb.PrefixCommand)
async def translate(ctx: lightbulb.Context):
    """ Translate stuff using Google Translate.
        Defaults to Auto-Detect -> English
        use 2 letter country codes i guess lol too lazy to make this bot any good
        add from:[lang] and/or to:[lang] to control the translation languages"""
    query, out = lynn.typeparser(ctx.options.query, lynn.MessageOutput.embed, lynn.MessageOutput.content | lynn.MessageOutput.embed)

    inlang = 'auto'
    outlang = 'en'

    newquery = []
    for word in query.split():
        if word.startswith('from:') and word != 'from:': # check that there's no space after from:
            inlang = word.split(':')[1]
        elif word.startswith('to:') and word != 'to:':
            outlang = word.split(':')[1]
        else:
            newquery.append(word)
    query = ' '.join(newquery)

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36'}
    data = await helpers.rest(f'https://translate.googleapis.com/translate_a/single?client=gtx&dt=t&ie=UTF-8&oe=UTF-8&sl={inlang}&tl={outlang}&q={query}', headers=headers)
    if not data:
        await ctx.reply('Did not get a response from Google. Probably an invalid language.')
        return

    fromlang = data[2]

    confidence = ''
    if data[6] and data[6] != 1:
        confidence = f'(confidence: {round(data[6]*100)}%)'


    embed = hikari.Embed(title='WIP', description='use >text for now')
    return lynn.Message(content=f'{fromlang} -> {outlang}: {data[0][0][0]} {confidence}',
                        embed=embed, output=out)


PLUGIN_NAME = 'apis'
PLUGIN_DESC = 'Getting data from APIs around the internet'
COMMANDS = [
    translate
]
LISTENERS = {}
