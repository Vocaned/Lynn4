import hikari
import lightbulb
import asyncio
import lynn
import sys
import time
from datetime import datetime
import psutil
import utils

class Ping(lynn.Plugin):

    @lightbulb.cooldown(60, 1, lightbulb.ChannelBucket)
    @lightbulb.command()
    async def ping(self, ctx: lightbulb.Context):
        embed = hikari.Embed(title='Pong!', color=lynn.EMBED_COLOR)

        embed.add_field('Current Time', f'\N{CLOCK FACE THREE OCLOCK} {datetime.now().isoformat()}')
        embed.add_field('Uptime',
                       f'\N{DESKTOP COMPUTER} **System**: {utils.td_format(datetime.now() - datetime.fromtimestamp(psutil.boot_time()))}\n' +
                       f'\N{ROBOT FACE} **Bot**: {utils.td_format(datetime.now() - datetime.fromtimestamp(lynn.startup_time))}')

        temperatures = []
        temps = psutil.sensors_temperatures()
        for k in temps:
            for v in temps[k]:
                temperatures.append(f'\N{FIRE} {k}_{v.label}: {v.current}°C')
        embed.add_field('Temperature', '\n'.join(temperatures))

        mem = psutil.virtual_memory()
        embed.add_field('Memory', f'\N{FLOPPY DISK} {utils.bytes2human(mem.used)} used, {utils.bytes2human(mem.total)} total')

        cpu = psutil.cpu_times_percent(interval=1, percpu=False)
        embed.add_field('CPU', f'\N{LEVEL SLIDER} {round(100-cpu.idle, 2)}%')

        start = time.time()
        firstmsg = await lynn.Response(embed=embed).send(ctx)
        end = time.time()

        embed.description = f'\N{BEATING HEART} Heartbeat Latency: **{int(self.bot.heartbeat_latency * 1000)} ms**\n'
        embed.description += f'\N{ANTENNA WITH BARS} API Latency: **{int((end - start) * 1000)} ms**'

        await firstmsg.edit(embed=embed)

def load(bot: lynn.Bot):
    bot.add_plugin(Ping(bot))

def unload(bot: lynn.Bot):
    bot.remove_plugin('Ping')
