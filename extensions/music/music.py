# pylint: disable=no-member

import hikari
import lightbulb
import lynn
import lavasnek_rs
import logging

class EventHandler:
    """Events from the Lavalink server"""

    async def track_start(self, _: lavasnek_rs.Lavalink, event: lavasnek_rs.TrackStart):
        logging.debug('Track started on guild %s', event.guild_id)

    async def track_finish(self, _: lavasnek_rs.Lavalink, event: lavasnek_rs.TrackFinish):
        logging.debug('Track finished on guild %s', event.guild_id)

    async def track_exception(self, lavalink: lavasnek_rs.Lavalink, event: lavasnek_rs.TrackException):
        logging.warning('Track exception event happened on guild %s', event.guild_id)

        # If a track was unable to be played, skip it
        skip = await lavalink.skip(event.guild_id)
        node = await lavalink.get_guild_node(event.guild_id)

        if skip:
            if not node.queue and not node.now_playing:
                await lavalink.stop(event.guild_id)


class Music(lynn.Plugin):
    """pepeJAM"""

    async def _join(self, ctx: lightbulb.Context):
        states = self.bot.cache.get_voice_states_view_for_guild(ctx.get_guild())
        voice_state = [state async for state in states.iterator().filter(lambda i: i.user_id == ctx.author.id)]

        if not voice_state:
            raise lynn.Error(title='Failed to join voice channel', text='Please connect to a voice channel first.')

        channel_id = voice_state[0].channel_id

        try:
            connection_info = await self.bot.data.lavalink.join(ctx.guild_id, channel_id)
        except TimeoutError as e:
            raise lynn.Error(title='Failed to join voice channel', 
                text='I was unable to connect to the voice channel, maybe missing permissions? or some internal issue.'
            ) from e

        await self.bot.data.lavalink.create_session(connection_info)

        return channel_id

    @lightbulb.listener(hikari.ShardReadyEvent)
    async def start_lavalink(self, _: hikari.ShardReadyEvent) -> None:
        """Event that triggers when the hikari gateway is ready."""

        builder = (
            lavasnek_rs.LavalinkBuilder(self.bot.get_me().id, lynn.config.get('token'))
            .set_host(lynn.config.get('lavalink_host')).set_password(lynn.config.get('lavalink_pass'))
        )

        lava_client = await builder.build(EventHandler())
        self.bot.data.lavalink = lava_client

    @lightbulb.check(lightbulb.guild_only)
    @lightbulb.command()
    async def join(self, ctx: lightbulb.Context) -> None:
        """Joins the voice channel you are in."""
        channel_id = await self._join(ctx)

        if channel_id:
            await lynn.Response(f'Joined <#{channel_id}>').send(ctx)

    @lightbulb.check(lightbulb.guild_only)
    @lightbulb.command()
    async def leave(self, ctx: lightbulb.Context) -> None:
        """Leaves the voice channel the bot is in, clearing the queue."""

        await self.bot.data.lavalink.destroy(ctx.guild_id)
        await self.bot.data.lavalink.leave(ctx.guild_id)

        # Destroy nor leave remove the node nor the queue loop, you should do this manually.
        await self.bot.data.lavalink.remove_guild_node(ctx.guild_id)
        await self.bot.data.lavalink.remove_guild_from_loops(ctx.guild_id)

        await lynn.Response('Left voice channel.').send(ctx)

    @lightbulb.check(lightbulb.guild_only)
    @lightbulb.command()
    async def play(self, ctx: lightbulb.Context, *, query: str) -> None:
        """Searches the query on youtube, or adds the URL to the queue."""

        con = await self.bot.data.lavalink.get_guild_gateway_connection_info(ctx.guild_id)
        # Join the user's voice channel if the bot is not in one.
        if not con:
            await self._join(ctx)

        # Search the query, auto_search will get the track from a url if possible, otherwise,
        # it will search the query on youtube.
        query_information = await self.bot.data.lavalink.auto_search_tracks(query)

        if not query_information.tracks:  # tracks is empty
            raise lynn.Error(title='Failed to play music', text='Could not find any video that matches the search query.')

        try:
            # `.requester()` To set who requested the track, so you can show it on now-playing or queue.
            # `.queue()` To add the track to the queue rather than starting to play the track now.
            await self.bot.data.lavalink.play(ctx.guild_id, query_information.tracks[0]).requester(
                ctx.author.id
            ).queue()
        except lavasnek_rs.NoSessionPresent as e:
            raise lynn.Error(title='Failed to play music', text=f'Use `{ctx.clean_prefix}join` first') from e

        await lynn.Response(f'Added to queue: {query_information.tracks[0].info.title}').send(ctx)

    @lightbulb.check(lightbulb.guild_only)
    @lightbulb.command()
    async def stop(self, ctx: lightbulb.Context) -> None:
        """Stops the current song (skip to continue)."""

        await self.bot.data.lavalink.stop(ctx.guild_id)
        await ctx.message.add_reaction('\N{BLACK SQUARE FOR STOP}')

    @lightbulb.check(lightbulb.guild_only)
    @lightbulb.command()
    async def skip(self, ctx: lightbulb.Context) -> None:
        """Skips the current song."""

        skip = await self.bot.data.lavalink.skip(ctx.guild_id)
        node = await self.bot.data.lavalink.get_guild_node(ctx.guild_id)

        if not skip:
            await lynn.Response('Nothing to skip').send(ctx)
        else:
            # If the queue is empty, the next track won't start playing (because there isn't any),
            # so we stop the player.
            if not node.queue and not node.now_playing:
                await self.bot.data.lavalink.stop(ctx.guild_id)

            await lynn.Response(f'Skipped: {skip.track.info.title}')
            await ctx.message.add_reaction('\N{BLACK RIGHT-POINTING DOUBLE TRIANGLE WITH VERTICAL BAR}')

    @lightbulb.check(lightbulb.guild_only)
    @lightbulb.command()
    async def pause(self, ctx: lightbulb.Context) -> None:
        """Pauses the current song."""

        await self.bot.data.lavalink.pause(ctx.guild_id)
        await ctx.message.add_reaction('\N{DOUBLE VERTICAL BAR}')

    @lightbulb.check(lightbulb.guild_only)
    @lightbulb.command()
    async def resume(self, ctx: lightbulb.Context) -> None:
        """Resumes playing the current song."""

        await self.bot.data.lavalink.resume(ctx.guild_id)
        await lynn.Response('Resumed player').send(ctx)
        await ctx.message.add_reaction('\N{BLACK RIGHT-POINTING TRIANGLE WITH DOUBLE VERTICAL BAR}')

    @lightbulb.check(lightbulb.guild_only)
    @lightbulb.command(aliases=["np"])
    async def nowplaying(self, ctx: lightbulb.Context) -> None:
        """Gets the song that's currently playing."""

        node = await self.bot.data.lavalink.get_guild_node(ctx.guild_id)
        if not node or not node.now_playing:
            raise lynn.Error(text='Nothing is playing at the moment.')

        embed = hikari.Embed(title='Now playing')
        embed.set_author(name=node.now_playing.track.info.author, url=node.now_playing.track.info.uri)
        embed.description = f'{node.now_playing.track.info.position} / {node.now_playing.track.info.length}'
        await lynn.Response(embed=embed).send(ctx)

    #@lightbulb.check(lightbulb.guild_only)
    #@lightbulb.command(aliases['q'])
    async def queue(self, ctx: lightbulb.Context):
        """Gets the song queue"""
        node = await self.bot.data.lavalink.get_guild_node(ctx.guild_id)
        if not node or not node.now_playing:
            raise lynn.Error(text='Nothing is playing at the moment.')

        for song in node.queue:
            # navigation menu here
            # for queue, iterate over `node.queue`, where index 0 is now_playing.
            pass

    @lightbulb.check(lightbulb.guild_only)
    @lightbulb.check(lightbulb.owner_only)  # Optional
    @lightbulb.command()
    async def data(self, ctx: lightbulb.Context, *args) -> None:
        """Load or read data from the node.
        If just `data` is ran, it will show the current data, but if `data <key> <value>` is ran, it
        will insert that data to the node and display it."""

        node = await self.bot.data.lavalink.get_guild_node(ctx.guild_id)

        if not args:
            await lynn.Response(await node.get_data()).send(ctx)
        else:
            if len(args) == 1:
                await node.set_data({args[0]: args[0]})
            else:
                await node.set_data({args[0]: args[1]})
            await lynn.Response(await node.get_data()).send(ctx)


def load(bot: lynn.Bot):
    if lynn.config.get('lavalink_host'):
        bot.add_plugin(Music(bot))

def unload(bot: lynn.Bot):
    bot.remove_plugin('Music')
