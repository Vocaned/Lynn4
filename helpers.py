import hikari
import base64
import uuid

from utils.navigation import DynamicButtonNavigator
from utils.rest import OpenGraphParser, RestOptions, rest, escape_url
from utils import formatting

def is_vip(bot, user: hikari.Snowflakeish):
    if isinstance(user) == hikari.PartialUser:
        user = user.id

    vips = bot.config.get('vips')
    if not vips:
        return False
    return str(user) in vips

def random_name(length: int = 8):
    return base64.urlsafe_b64encode(uuid.uuid4().bytes).decode("ascii")[:length]