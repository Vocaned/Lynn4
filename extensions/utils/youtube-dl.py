import tempfile
import os
import hikari
import lightbulb
import lynn
import helpers

if True: # TODO: config switch
    import yt_dlp
else:
    pass
    #import youtube_dl

class YoutubeDL(lynn.Plugin):

    @lightbulb.cooldown(10, 1, lightbulb.UserBucket)
    @lightbulb.command(aliases=['youtube-dl', 'ytdl', 'dl', 'download'])
    async def youtubedl(self, ctx: lightbulb.Context, link, *, args=None):
        """Downloads a video
        insert usage here"""
        ydl_opts = {
            'geo_bypass': True,
            'no_color': True,
            'quiet': False, # TODO: for debugging, use True in production
            'restrictfilenames': True
        }

        try:
            with tempfile.TemporaryDirectory() as tmp:
                ydl_opts['outtmpl'] = tmp + '%(id)s.%(ext)s'
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(link)
                    if 'is_live' in info and info['is_live']:
                        raise lynn.Error('Cannot download a livestream')

                file = tmp + info['id'] + '.' + info['ext']
                size = os.path.getsize(file)
                if size > 8000000:
                    if not helpers.is_vip(self.bot, ctx.author.id):
                        raise lynn.Error('File over 8MB!', 'File is ' + helpers.bytes2human(size) + '.\nVIP is required to upload files over 8MB, ping the bot owner for more information.')

                    # TODO: upload to fam.rip

                hikari.File(file)
                lynn.Response(attachment=file).send(ctx)
        except FileNotFoundError as e:
            raise yt_dlp.DownloadError('Could not download video.') from e





def load(bot: lynn.Bot):
    bot.add_plugin(YoutubeDL(bot))

def unload(bot: lynn.Bot):
    bot.remove_plugin('YoutubeDL')
