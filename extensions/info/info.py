import hikari
import lightbulb
import lynn

@lightbulb.option('snowflake', 'Snowflake to get information from', hikari.Snowflake)
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
@lightbulb.command('color', 'Get information about a color', aliases=['col', 'hex'])
@lightbulb.implements(lightbulb.PrefixCommand)
async def color(ctx: lightbulb.Context):
    embed = hikari.Embed(title=ctx.options.color.hex_code, color=ctx.options.color)
    embed.add_field('Red', f'{ctx.options.color.rgb[0]} ({ctx.options.color.rgb_float[0]*100:.2f}%)')
    embed.add_field('Green', f'{ctx.options.color.rgb[1]} ({ctx.options.color.rgb_float[1]*100:.2f}%)')
    embed.add_field('Blue', f'{ctx.options.color.rgb[2]} ({ctx.options.color.rgb_float[2]*100:.2f}%)')
    return lynn.Message(embed=embed)

PLUGIN_NAME = 'info'
PLUGIN_DESC = 'All kinds of information about all kinds of things'
COMMANDS = [
    snowflake, color
]
LISTENERS = {}
