import tempfile
import os
import hikari
import lightbulb
import helpers
import lynn
import ffmpeg

try:
    import yt_dlp as yt_dl
except ImportError:
    import youtube_dl as yt_dl

# TODO: timeout commands after n seconds
@lightbulb.add_cooldown(10, 1, lightbulb.UserBucket)
@lightbulb.option('link', 'Link to the video')
@lightbulb.command('youtubedl', 'Downloads a video', aliases=['youtube-dl', 'ytdl', 'dl', 'download'], auto_defer=True)
@lightbulb.implements(lightbulb.PrefixCommand)
async def youtubedl(ctx: lightbulb.Context):
    """insert usage here"""
    return await download(ctx)

async def download(ctx: lightbulb.Context):
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
                raise lynn.Error('File over 8MB!', 'File is ' + helpers.formatting.bytes2human(size) + '.\nVIP is required to upload files over 8MB.')

            # TODO: upload to fam.rip
            tmp.close()

        return lynn.Message(files=[tmp,])
    except FileNotFoundError as e:
        raise yt_dl.DownloadError('Could not download video.') from e

# TODO: timeout commands after n seconds
@lightbulb.add_cooldown(10, 1, lightbulb.UserBucket)
@lightbulb.option('link', 'Link to the video', required=False)
@lightbulb.option('args', 'Arguments for the action')
@lightbulb.option('action', 'Action to make on the video')
@lightbulb.set_help(docstring=True)
@lightbulb.command('ffmpeg', 'Edits a video', aliases=['editvideo', 'videoedit'], auto_defer=True)
@lightbulb.implements(lightbulb.PrefixCommand)
async def edit(ctx: lightbulb.Context):
    """
    Possible actions:
        - format <format> | Re-encodes video as <format>. For example to turn the video into an mp4: format mp4
        - speed <speed> | Sets the video speed to <speed>. For example for 2x speed: speed 2
        - volume <vol> | Sers the video volume to <vol>. Use 0 to mute the video. For example for 200% loudness: volume 2
    """
    with tempfile.TemporaryDirectory() as tmp:
        fp = None
        if ctx.options.link:
            msg = await download(ctx)
            fp = os.path.join(tmp, msg.files[0].get_filename())
            os.rename(msg.files[0].get_path(), fp)
            msg.files[0].close()
        elif ctx.attachments.count == 1:
            fp = os.path.join(tmp, ctx.attachments[0].filename)
            with open(fp, 'wb') as f:
                f.write(await ctx.attachments[0].read())
        #elif ctx.event.message.referenced_message:
        #    msg = await ctx.app.rest.fetch_message(ctx.event.message.referenced_message.channel_id, ctx.event.message.referenced_message.id)
        #    print(msg)

        #    if msg.attachments.count == 1:
        #        fp = os.path.join(tmp, msg.attachments[0].filename)
        #        with open(fp, 'wb') as f:
        #            f.write(await msg.attachments[0].read())

        if not fp:
            raise lynn.Error('Could not find video to edit', 'Video can be passed as an attachment or a link') #or an attachment in reply

        out_format = os.path.splitext(fp)[1]
        inp = ffmpeg.input(fp)
        video = inp.video
        audio = inp.audio
        if ctx.options.action.lower() == 'format':
            out_format = ctx.options.args
        elif ctx.options.action.lower() == 'speed':
            speed = float(ctx.options.args)
            video = video.filter('setpts', f'{1/speed}*PTS')

            # https://trac.ffmpeg.org/wiki/How%20to%20speed%20up%20/%20slow%20down%20a%20video
            # The atempo filter is limited to using values between 0.5 and 2.0 (so it can slow it down to no less than half the original speed, and speed up to no more than double the input).
            # If you need to, you can get around this limitation by stringing multiple atempo filters together.
            while speed < 0.5:
                audio = audio.filter('atempo', 0.5)
                speed += 0.5
            while speed > 2:
                audio = audio.filter('atempo', 2)
                speed -= 2
            if speed != 0:
                audio = audio.filter('atempo', speed)
        elif ctx.options.action.lower() == 'volume':
            volume = float(ctx.options.args)
            audio = audio.filter('volume', volume)
        else:
            raise lynn.Error(f'Could not find action `{ctx.options.action}`')

        out_file = os.path.join(tmp, 'out.' + out_format)
        ffmpeg.output(video, audio, out_file).run()

        tmpfile = lynn.TemporaryFile()
        os.rename(out_file, os.path.join(tmpfile.directory.name, helpers.random_name() + '.' + out_format))

        return lynn.Message(files=[tmpfile,])


PLUGIN_NAME = 'media'
PLUGIN_DESC = 'Commands related to audio, video and images'
COMMANDS = [
    youtubedl, edit
]
LISTENERS = {}
