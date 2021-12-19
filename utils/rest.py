import html.parser
import urllib
import aiohttp
import typing

class OpenGraphParser(html.parser.HTMLParser):
    def __init__(self, *, convert_charrefs: bool = ...) -> None:
        super().__init__(convert_charrefs=convert_charrefs)
        self.tags = {}

    def handle_starttag(self, tag, attrs):
        if tag != 'meta':
            return
        k = v = None
        for attr in attrs:
            if attr[0].lower() == 'name' or attr[0].lower() == 'property' and attr[1].startswith('og:'):
                k = attr[1]
            if attr[0].lower() == 'content':
                v = attr[1]
        if k and v:
            self.tags[k] = v

class RestOptions:
    def __init__(self, method='GET', headers=None, data=None, auth=None, returns: typing.Union[str, typing.Tuple[str]] = 'json') -> None:
        self.method = method
        self.headers = headers
        self.data = data
        self.auth = auth
        self.returns = returns

async def rest(url: str, opts: RestOptions = RestOptions()) -> typing.Union[object, typing.List[object]]:
    async with aiohttp.ClientSession() as s:
        async with s.request(opts.method, url, headers=opts.headers, data=opts.data, auth=opts.auth) as r:
            temp = []

            for out in opts.returns:
                if out == 'json':
                    try:
                        j = await r.json()
                    except aiohttp.ContentTypeError:
                        j = None
                    finally:
                        temp.append(j)
                elif out == 'status':
                    temp.append(r.status)
                elif out == 'raw':
                    temp.append(await r.read())
                elif out == 'text':
                    temp.append(await r.text())
                elif out == 'object':
                    temp.append(r)

            if not temp:
                raise NotImplementedError('Invalid rest return type ' + opts.returns)
            if len(temp) == 1:
                return temp[0]
            return temp

def escape_url(url: str) -> str:
    return urllib.parse.quote(url)
