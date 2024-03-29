from argparse import ArgumentError
import datetime
import hikari
import lightbulb
import lynn
from helpers import rest, RestOptions
from pycountry import languages

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
    tolang = 'English'

    newquery = []
    for word in query.split():
        if word.startswith('from:') and word != 'from:': # check that there's no space after from:
            try:
                inlang = word.split(':')[1].lower()
                if inlang == 'en': # En is a language with like 200 native speakers.. english is more important
                    inlang = 'eng'
                inlang = languages.lookup(inlang)
                inlang = inlang.alpha_2
            except:
                raise lynn.Error(f"No language found by `{word.split(':')[1]}`")
        elif word.startswith('to:') and word != 'to:':
            try:
                outlang = word.split(':')[1].lower()
                if outlang == 'en': # En is a language with like 200 native speakers.. english is more important
                    outlang = 'eng'
                outlang = languages.lookup(outlang)
            except:
                raise lynn.Error(f"No language found by `{word.split(':')[1]}`")
            tolang = outlang.name
            outlang = outlang.alpha_2
        else:
            newquery.append(word)
    query = ' '.join(newquery)

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36'}
    data = await rest(f'https://translate.googleapis.com/translate_a/single?client=gtx&dt=t&ie=UTF-8&oe=UTF-8&sl={inlang}&tl={outlang}&q={query}', RestOptions(headers=headers))
    if not data:
        await ctx.reply('Did not get a response from Google. Probably an invalid language.')
        return

    fromlang = languages.get(alpha_2=data[2])
    if not fromlang:
        fromlang = data[2]
    else:
        fromlang = fromlang.name

    confidence = ''
    if data[6] and data[6] != 1:
        confidence = f'(confidence: {round(data[6]*100)}%)'


    embed = hikari.Embed(title='Google Translate', description=confidence, color=lynn.EMBED_COLOR)
    embed.add_field(f'From `{fromlang}`', query)
    embed.add_field(f'To `{tolang}`', data[0][0][0])
    return lynn.Message(content=f'{fromlang} -> {tolang}: {data[0][0][0]} {confidence}',
                        embed=embed, output=out)


PLUGIN_NAME = 'apis'
PLUGIN_DESC = 'Getting data from APIs around the internet'
COMMANDS = [
    translate
]
LISTENERS = {}
