import urllib
import aiohttp

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

def escapeURL(url: str) -> str:
    return urllib.parse.quote(url)