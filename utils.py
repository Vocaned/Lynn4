import json
import os
import hikari
import lightbulb

def get_config(key: str) -> object:
    if not os.path.exists('config.json'):
        return None
    
    with open('config.json') as f:
        j = json.load(f)
        return j.get(key, None)

async def respond(ctx: lightbulb.Context, *args, **kwargs) -> hikari.Message:
    try:
        return await ctx.respond(reply=True, *args, **kwargs)
    except hikari.BadRequestError as e:
        try:
            if len(e.errors['message_reference']['_errors']) == 1 and e.errors['message_reference']['_errors'][0]['code'] == 'REPLIES_UNKNOWN_MESSAGE':
                # Resend the response without a reply, since the message no longer exists
                # TODO: Assumes args[0] is message, need to investigate if it can be something else as well
                msg = list(args)
                msg[0] = f'{ctx.author.mention}, {msg[0]}'
                return await ctx.respond(*msg, **kwargs)
        except KeyError:
            pass
        return None