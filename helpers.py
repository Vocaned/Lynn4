import urllib
import aiohttp
import hikari
import typing

class RestOutput(int):
    json = 1 << 0
    status = 1 << 1
    raw = 1 << 2
    text = 1 << 3
    object = 1 << 4

class RestOptions:
    def __init__(self, method='GET', headers=None, data=None, auth=None, returns: RestOutput = RestOutput.json) -> None:
        self.method = method
        self.headers = headers
        self.data = data
        self.auth = auth
        self.returns = returns


async def rest(url: str, opts: RestOptions = RestOptions()) -> typing.Union[object, typing.List[object]]:
    async with aiohttp.ClientSession() as s:
        async with s.request(opts.method, url, headers=opts.headers, data=opts.data, auth=opts.auth) as r:
            temp = []

            if opts.returns & RestOutput.json == RestOutput.json:
                try:
                    j = await r.json()
                except aiohttp.ContentTypeError:
                    j = None
                finally:
                    temp.append(j)
            if opts.returns & RestOutput.status == RestOutput.status:
                temp.append(r.status)
            if opts.returns & RestOutput.raw == RestOutput.raw:
                temp.append(await r.read())
            if opts.returns & RestOutput.text == RestOutput.text:
                temp.append(await r.text())
            if opts.returns & RestOutput.object == RestOutput.object:
                temp.append(r)

            if not temp:
                raise NotImplementedError('Invalid rest return type ' + opts.returns)
            if len(temp) == 1:
                return temp[0]
            return temp

def escape_url(url: str) -> str:
    return urllib.parse.quote(url)

def is_vip(bot, user: hikari.Snowflakeish):
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
            strings.append(f'{period_value} {period_name}{has_s}')

    if not strings:
        strings.append('less than a minute')

    return ', '.join(strings)

def bytes2human(n: int) -> str:
    # http://code.activestate.com/recipes/578019
    symbols = ('KiB', 'MiB', 'GiB', 'TiB', 'PiB')
    prefix = {}
    for i, s in enumerate(symbols):
        prefix[s] = 1 << (i + 1) * 10
    for s in reversed(symbols):
        if n >= prefix[s]:
            value = float(n) / prefix[s]
            return f'{value:.1f}{s}'
    return f'{n}B'
