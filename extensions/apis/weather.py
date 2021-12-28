import datetime
import hikari
import lightbulb
import lynn
from helpers import rest, escape_url

@lightbulb.option('city', 'City to search weather in', modifier=lightbulb.commands.OptionModifier.CONSUME_REST)
@lightbulb.command('weather', 'Is it raining today?', auto_defer=True)
@lightbulb.implements(lightbulb.PrefixCommand)
async def weather(ctx: lightbulb.Context):
    city, out = lynn.typeparser(ctx.options.city, lynn.MessageOutput.embed, lynn.MessageOutput.content | lynn.MessageOutput.image | lynn.MessageOutput.embed)

    geocoding = await rest('https://nominatim.openstreetmap.org/search?format=json&limit=1&accept-language=en&q='+escape_url(city))
    if not geocoding:
        raise lynn.Error('Location not found.')
    data = await rest(f"https://api.darksky.net/forecast/{ctx.app.config.get_secret('darksky')}/{geocoding[0]['lat']},{geocoding[0]['lon']}?exclude=minutely,hourly,daily,flags&units=si")

    if 'alerts' in data and data['alerts']:
        col = 0xff0000
    else:
        col = 0xffb347

    embed = hikari.Embed(title=geocoding[0]['display_name'], color=col)
    embed.set_thumbnail(f"https://darksky.net/images/weather-icons/{data['currently']['icon']}.png")

    if 'alerts' in data:
        alerts = []
        for alert in data['alerts']:
            if len(alerts) > 3:
                continue
            if alert['title'] not in alerts:
                embed.add_field(name=alert['title'], value=alert['description'][:1024])
                alerts.append(alert['title'])

    embed.add_field(name=data['currently']['summary'], value=str(round(data['currently']['temperature'], 2)) + '°C (' + str(round(data['currently']['temperature'] * (9/5) + 32, 2)) + '°F)\n' \
        + 'Feels Like: ' + str(round(data['currently']['apparentTemperature'], 2)) + '°C (' + str(round(data['currently']['apparentTemperature'] * (9/5) + 32, 2)) + '°F)\n' \
        + 'Humidity: ' + str(round(data['currently']['humidity'] * 100, 2)) + '%\n' \
        + 'Clouds: ' + str(round(data['currently']['cloudCover'] * 100, 2)) + '%\n' \
        + 'Wind: ' + str(data['currently']['windSpeed']) + ' m/s (' + str(round(int(data['currently']['windSpeed']) * 2.2369362920544, 2)) + ' mph)', inline=False)
    embed.set_footer('Powered by Dark Sky and OpenStreetMap')
    embed.timestamp = datetime.datetime.fromtimestamp(data['currently']['time'], tz=datetime.timezone.utc)
    return lynn.Message(content=f"{geocoding[0]['display_name']}: {str(round(data['currently']['temperature']))}°C",
                        embed=embed, image=f"https://wttr.in/{geocoding[0]['lat']},{geocoding[0]['lon']}.png", output=out)


PLUGIN_NAME = 'apis'
PLUGIN_DESC = 'Getting data from APIs around the internet'
COMMANDS = [
    weather
]
LISTENERS = {}
