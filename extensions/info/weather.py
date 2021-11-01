import datetime
import hikari
import lightbulb
import lynn
from helpers import rest, escapeURL

class Weather(lynn.Plugin):

    @lightbulb.check(lightbulb.has_guild_permissions(hikari.Permissions.MANAGE_MESSAGES))
    @lightbulb.command()
    async def weather(self, ctx: lightbulb.Context, *, city: str):
        """Is it raining today?"""
        geocoding = await rest('https://nominatim.openstreetmap.org/search?format=json&limit=1&accept-language=en&q='+escapeURL(city))
        data = await rest(f"https://api.darksky.net/forecast/{self.bot.config.get_secret('darksky')}/{geocoding[0]['lat']},{geocoding[0]['lon']}?exclude=minutely,hourly,daily,flags&units=si")

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
        embed.set_footer(text='Powered by Dark Sky and OpenStreetMap')
        embed.timestamp = datetime.datetime.fromtimestamp(data['currently']['time'], tz=datetime.timezone.utc)
        await lynn.Response(embed=embed).send(ctx)

def load(bot: lynn.Bot):
    bot.add_plugin(Weather(bot))

def unload(bot: lynn.Bot):
    bot.remove_plugin('Weather')
