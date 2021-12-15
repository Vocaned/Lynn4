import tempfile
import os
import hikari
import lightbulb
import lynn
import helpers

try:
    import yt_dlp as yt_dl
except ImportError:
    import youtube_dl as yt_dl

plugin = lightbulb.Plugin('media', 'Commands related to media')

# TODO: timeout commands after n seconds
@lightbulb.add_cooldown(10, 1, lightbulb.UserBucket)
@lightbulb.option('link', 'Link to the video')
@plugin.command
@lightbulb.command('youtubedl', 'Downloads a video', aliases=['youtube-dl', 'ytdl', 'dl', 'download'], auto_defer=True)
@lightbulb.implements(lightbulb.PrefixCommand)
async def youtubedl(ctx: lightbulb.Context):
    """insert usage here"""
    ydl_opts = {
        'geo_bypass': True,
        'no_color': True,
        'restrictfilenames': True,
        'quiet': True
    }

    try:
        tmp = lynn.TemporaryFile()
        ydl_opts['outtmpl'] = tmp.directory.name + '/%(id)s.%(ext)s'
        with yt_dl.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(ctx.options.link, download=False)
            if 'is_live' in info and info['is_live']:
                raise lynn.Error('Cannot download a livestream')
            ydl.download(ctx.options.link)

        file = tmp.directory.name + '/' + info['id'] + '.' + info['ext']
        tmp.filename = info['id'] + '.' + info['ext']
        size = os.path.getsize(file)
        if size > 8000000:
            if not helpers.is_vip(ctx.app, ctx.author.id):
                tmp.close()
                raise lynn.Error('File over 8MB!', 'File is ' + helpers.bytes2human(size) + '.\nVIP is required to upload files over 8MB.')

            # TODO: upload to fam.rip
            tmp.close()

        return lynn.Message(files=[tmp,])
    except FileNotFoundError as e:
        raise yt_dl.DownloadError('Could not download video.') from e

def load(bot: lynn.Bot):
    bot.add_plugin(plugin)

def unload(bot: lynn.Bot):
    bot.remove_plugin(plugin)