import urllib
import aiohttp
import hikari
import lynn
import typing

async def rest(url: str, method='GET', headers=None, data=None, auth=None, returns='json'):
    """TODO: Clean up this method just copy pasted from lynn3"""
    async with aiohttp.ClientSession() as s:
        async with s.request(method, url, headers=headers, data=data, auth=auth) as r:
            temp = []
            if isinstance(returns, str):
                returns = (returns,)
            for ret in returns:
                if ret == 'json':
                    try:
                        j = await r.json()
                    except aiohttp.ContentTypeError:
                        j = None
                    finally:
                        temp.append(j)
                elif ret == 'status':
                    temp.append(r.status)
                elif ret == 'raw':
                    temp.append(await r.read())
                elif ret == 'text':
                    temp.append(await r.text())
                elif ret == 'object':
                    return r
                else:
                    raise NotImplementedError('Invalid return type ' + ret)
            if len(temp) == 1:
                return temp[0]
            return temp

def get_args(string: str, parts: int = -1, cmd_spaces: int = 0) -> typing.List[str]:
    return string.split(' ', maxsplit=parts)[cmd_spaces+1:]

def escape_url(url: str) -> str:
    return urllib.parse.quote(url)

def is_vip(bot: lynn.Bot, user: hikari.Snowflakeish):
    if isinstance(user) == hikari.PartialUser:
        user = user.id

    vips = bot.config.get('vips')
    if not vips:
        return False
    return str(user) in vips

def td_format(td_object):
    # https://stackoverflow.com/a/13756038
    seconds = int(td_object.total_seconds())
    periods = [
        ('year',        60*60*24*365),
        ('month',       60*60*24*30),
        ('day',         60*60*24),
        ('hour',        60*60),
        ('minute',      60)
    ]

    strings=[]
    for period_name, period_seconds in periods:
        if seconds > period_seconds:
            period_value , seconds = divmod(seconds, period_seconds)
            has_s = 's' if period_value > 1 else ''
            strings.append('%s %s%s' % (period_value, period_name, has_s))

    if not strings:
        strings.append('less than a minute')

    return ', '.join(strings)

def bytes2human(n):
    # http://code.activestate.com/recipes/578019
    symbols = ('KiB', 'MiB', 'GiB', 'TiB', 'PiB')
    prefix = {}
    for i, s in enumerate(symbols):
        prefix[s] = 1 << (i + 1) * 10
    for s in reversed(symbols):
        if n >= prefix[s]:
            value = float(n) / prefix[s]
            return '%.1f%s' % (value, s)
    return "%sB" % n
