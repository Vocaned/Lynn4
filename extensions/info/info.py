import time
from datetime import datetime

import hikari
import lightbulb
import psutil
import lynn
import helpers

plugin = lightbulb.Plugin('info', 'Commands related to getting information')

@lightbulb.add_cooldown(60, 1, lightbulb.ChannelBucket)
@plugin.command
@lightbulb.command('ping', 'pong')
@lightbulb.implements(lightbulb.PrefixCommand)
async def ping_cmd(ctx: lightbulb.Context):
    embed = hikari.Embed(title='Pong!', color=lynn.EMBED_COLOR)

    embed.add_field('Current Time', f'\N{CLOCK FACE THREE OCLOCK} {datetime.now().isoformat()}')
    embed.add_field('Uptime',
                    f'\N{DESKTOP COMPUTER} **System**: {helpers.formatting.td_format(datetime.now() - datetime.fromtimestamp(psutil.boot_time()))}\n' +
                    f'\N{ROBOT FACE} **Bot**: {helpers.formatting.td_format(datetime.now() - datetime.fromtimestamp(ctx.app.startup_time))}')

    temperatures = []
    temps = psutil.sensors_temperatures()
    for k in temps:
        for v in temps[k]:
            temperatures.append(f'\N{FIRE} {k}_{v.label}: {v.current}°C')
    embed.add_field('Temperature', '\n'.join(temperatures))

    mem = psutil.virtual_memory()
    embed.add_field('Memory', f'\N{FLOPPY DISK} {helpers.formatting.bytes2human(mem.used)} used, {helpers.formatting.bytes2human(mem.total)} total')

    cpu = psutil.cpu_times_percent(interval=1, percpu=False)
    embed.add_field('CPU', f'\N{LEVEL SLIDER} {round(100-cpu.idle, 2)}%')

    start = time.time()
    firstmsg = await lynn.Message(embed=embed).send(ctx)
    end = time.time()

    embed.description = f'\N{BEATING HEART} Heartbeat Latency: **{int(ctx.app.heartbeat_latency * 1000)} ms**\n'
    embed.description += f'\N{ANTENNA WITH BARS} API Latency: **{int((end - start) * 1000)} ms**'

    await firstmsg.edit(embed=embed)

@lightbulb.option('snowflake', 'Snowflake to get information from', hikari.Snowflake)
@plugin.command
@lightbulb.command('snowflake', 'Get information from a snowflake')
@lightbulb.implements(lightbulb.PrefixCommand)
async def snowflake(ctx: lightbulb.Context):
    embed = hikari.Embed(title=ctx.options.snowflake, color=0x7289DA)
    embed.add_field('Timestamp', ctx.options.snowflake.created_at.strftime('%c'))
    embed.add_field('Internal worker ID', ctx.options.snowflake.internal_worker_id, inline=True)
    embed.add_field('Internal process ID', ctx.options.snowflake.internal_process_id, inline=True)
    embed.add_field('Increment', ctx.options.snowflake.increment, inline=True)
    return lynn.Message(embed=embed)

@lightbulb.option('color', 'Color to get information about', hikari.Color)
@plugin.command
@lightbulb.command('color', 'Get information about a color', aliases=['col', 'hex'])
@lightbulb.implements(lightbulb.PrefixCommand)
async def color(ctx: lightbulb.Context):
    embed = hikari.Embed(title=ctx.options.color.hex_code, color=ctx.options.color)
    embed.add_field('Red', f'{ctx.options.color.rgb[0]} ({ctx.options.color.rgb_float[0]*100:.2f}%)')
    embed.add_field('Green', f'{ctx.options.color.rgb[1]} ({ctx.options.color.rgb_float[1]*100:.2f}%)')
    embed.add_field('Blue', f'{ctx.options.color.rgb[2]} ({ctx.options.color.rgb_float[2]*100:.2f}%)')
    return lynn.Message(embed=embed)

def load(bot: lynn.Bot):
    bot.add_plugin(plugin)

def unload(bot: lynn.Bot):
    bot.remove_plugin(plugin)
