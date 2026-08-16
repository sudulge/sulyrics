import re

import discord
from discord.ext import commands
from discord.commands import slash_command, Option

import lavalink
from lavalink.events import TrackStartEvent, QueueEndEvent, TrackExceptionEvent, TrackEndEvent
from lavalink.server import LoadType

from .music_utils.lavalinkvoiceclient import LavalinkVoiceClient
from .music_utils.viewmanager import ViewManager
from .music_utils.db import get_data, add_log

url_rx = re.compile(r'https?://(?:www\.)?.+')
spotify_rx = re.compile('.+open.spotify.com/.+')

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.viewmanager = ViewManager(
            bot, 
            pause_callback = self.pause,
            skip_callback = self.skip,
            loop_callback = self.loop,
            stop_callback = self.stop)
        li = get_data(f"SELECT ChannelID FROM MUSIC")
        self.music_channel_list = set([i[0] for i in li])
        self.lavalink = None

    # 봇이 실행되기 전에 (이벤트 루프가 생기기 전에) aiohttp.ClientSession()이 생성되는 것을 방지하기 위해 분리.
    # 봇이 실행된 이후에 cog를 불러오면 slash_command가 작동하지 않음.
    @commands.Cog.listener()
    async def on_ready(self):
        if self.lavalink is not None:
            return
        
        if not hasattr(self.bot, 'lavalink'):
            self.bot.lavalink = lavalink.Client(self.bot.user.id)
            self.bot.lavalink.add_node(host='127.0.0.1', port=2333, password='password',
                                  region='ko', name='default-node')

        self.lavalink: lavalink.Client = self.bot.lavalink
        self.lavalink.add_event_hooks(self)

    def cog_unload(self):
        """
        This will remove any registered event hooks when the cog is unloaded.
        They will subsequently be registered again once the cog is loaded.

        This effectively allows for event handlers to be updated when the cog is reloaded.
        """
        self.lavalink._event_hooks.clear()

    async def cog_command_error(self, ctx, error):
        if isinstance(error, commands.CommandInvokeError):
            await ctx.send(error.original)
            # The above handles errors thrown in this cog and shows them to the user.
            # This shouldn't be a problem as the only errors thrown in this cog are from `ensure_voice`
            # which contain a reason string, such as "Join a voicechannel" etc. You can modify the above
            # if you want to do things differently.
        elif isinstance(error, commands.NoPrivateMessage):
            await ctx.respond("여기가 아닌데요?")

    @staticmethod
    async def create_player(ctx: commands.Context):
        """
        A check that is invoked before any commands marked with `@commands.check(create_player)` can run.

        This function will try to create a player for the guild associated with this Context, or raise
        an error which will be relayed to the user if one cannot be created.
        """
        if ctx.guild is None:
            raise commands.NoPrivateMessage()

        player = ctx.bot.lavalink.player_manager.create(ctx.guild.id)
        # Create returns a player if one exists, otherwise creates.
        # This line is important because it ensures that a player always exists for a guild.

        # Most people might consider this a waste of resources for guilds that aren't playing, but this is
        # the easiest and simplest way of ensuring players are created.

        # These are commands that require the bot to join a voicechannel (i.e. initiating playback).
        # Commands such as volume/skip etc don't require the bot to be in a voicechannel so don't need listing here.
        # should_connect = ctx.command.name in ('play', '재생')
        should_connect = getattr(ctx.command, "name", "play") in ("play", "재생")
        # 슬래시 커맨드로 노래를 재생했을때는 ctx.command.name이 play.
        # on_message 이벤트로 재생했을때는 ctx.command가 없기 때문에 play로 설정.

        voice_client = ctx.voice_client

        if not ctx.author.voice or not ctx.author.voice.channel:
            # Check if we're in a voice channel. If we are, tell the user to join our voice channel.
            if voice_client is not None:
                await ctx.channel.send("수리릭과 같은 음성채널에 있어야 합니다", delete_after=1)
                raise commands.CommandInvokeError('수리릭과 같은 음성채널에 있어야 합니다')

            # Otherwise, tell them to join any voice channel to begin playing music.
            await ctx.channel.send("먼저 음성채널에 입장해 주세요.", delete_after=1)
            raise commands.CommandInvokeError('먼저 음성채널에 입장해 주세요') 

        voice_channel = ctx.author.voice.channel

        if voice_client is None:
            if not should_connect:
                await ctx.channel.send("음악 재생중이 아닙니다", delete_after=1)
                raise commands.CommandInvokeError("음악 재생중이 아닙니다")

            permissions = voice_channel.permissions_for(ctx.me)

            if not permissions.connect or not permissions.speak:
                await ctx.channel.send("`연결` `말하기` 권한이 필요합니다", delete_after=1)
                raise commands.CommandInvokeError('`연결` `말하기` 권한이 필요합니다')

            if voice_channel.user_limit > 0:
                # A limit of 0 means no limit. Anything higher means that there is a member limit which we need to check.
                # If it's full, and we don't have "move members" permissions, then we cannot join it.
                if len(voice_channel.members) >= voice_channel.user_limit and not ctx.me.guild_permissions.move_members:
                    await ctx.channel.send("음성채널에 입장할 수 없습니다", delete_after=1)
                    raise commands.CommandInvokeError('음성채널에 입장할 수 없습니다')

            data = get_data(f"SELECT ChannelID, MessageID FROM MUSIC WHERE GuildID = {ctx.guild.id}")
            if not data:
                await ctx.channel.send("노래 채널이 없습니다.\n`/setting` 커맨드로 채널을 만들어주세요", delete_after=1)
                raise commands.CommandInvokeError('노래 채널이 없습니다.\n`/setting` 커맨드로 채널을 만들어주세요')
            
            player.store('channel_id', data[0][0])
            player.store('message_id', data[0][1])
            player.store('channel', ctx.channel.id)
            await ctx.author.voice.channel.connect(cls=LavalinkVoiceClient)
        elif voice_client.channel.id != voice_channel.id:
            await ctx.channel.send("수리릭과 같은 음성 채널에 있어야 합니다", delete_after=1)
            raise commands.CommandInvokeError('수리릭과 같은 음성 채널에 있어야 합니다')

        return True

    @lavalink.listener(TrackStartEvent)
    async def on_track_start(self, event: TrackStartEvent):
        guild_id = event.player.guild_id
        channel_id = event.player.fetch('channel')
        guild = self.bot.get_guild(guild_id)

        if not guild:
            return await self.lavalink.player_manager.destroy(guild_id)

        channel = guild.get_channel(channel_id)

        if channel:
            add_log(event.player.current.title, event.player.current.uri, self.bot.get_guild(event.player.guild_id).get_member(event.player.current.requester).display_name, event.player.guild_id)
            await self.viewmanager.updateContainer(event.player)

    @lavalink.listener(QueueEndEvent)
    async def on_queue_end(self, event: QueueEndEvent):
        guild_id = event.player.guild_id
        guild = self.bot.get_guild(guild_id)

        if guild is not None:
            await guild.voice_client.disconnect(force=True)

        await self.viewmanager.updateContainer(event.player)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        else:
            if message.channel.id in self.music_channel_list:
                await message.delete()
                ctx = await self.bot.get_context(message)
                await self.create_player(ctx)
                await self.play(message, message.content)

######명령어#########################################################################

    @slash_command(name="setting", description="음악 채널을 생성합니다.")
    async def setting(self, ctx):
        await self.viewmanager.setting(ctx)
        li = get_data(f"SELECT ChannelID FROM MUSIC")
        self.music_channel_list = set([i[0] for i in li])

    @slash_command(name="reloadmusicview", description="음악 패널을 다시 불러옵니다.")
    async def reloadmusicview(self, ctx):
        await self.viewmanager.reloadview(ctx)


    @slash_command(name='재생', description="play")
    @commands.check(create_player)
    async def play(self, ctx, query=Option(str, '노래 제목, 유튜브/스포티파이 링크')):
        if isinstance(ctx, discord.Message):
            send = ctx.channel.send
        else:
            send = ctx.respond

        player : lavalink.DefaultPlayer = self.bot.lavalink.player_manager.get(ctx.guild.id)
        
        query = query.strip('<>')

        if url_rx.match(query):
            pass
        else:
            query = f'ytsearch:{query}'

        results = await player.node.get_tracks(query)
        
        if results.load_type == LoadType.EMPTY:
            return await send("결과를 찾을 수 없습니다.", delete_after=1)

        else:
            for track in results.tracks:
                track.extra["requester"] = ctx.author.id
                player.add(track=track)

        addTrackView = await self.viewmanager.addTrackView(results, query if results.load_type == LoadType.PLAYLIST else None)

        await send(view=addTrackView, delete_after=1)

        if player.is_playing:
            await self.viewmanager.updateContainer(player)
        else:
            await player.play()


    @slash_command(name="일시정지", description="Pause")
    async def pause(self, ctx):
        player = self.bot.lavalink.player_manager.get(ctx.guild.id) 

        if not player:
            return await ctx.respond("노래 재생중이 아닙니다", delete_after=1)

        if player.paused:
            await player.set_pause(False)
            await ctx.respond("`재생`", delete_after=1)
        else:
            await player.set_pause(True)
            await ctx.respond("`일시정지`", delete_after=1)


    @slash_command(name="스킵", description="Skip")
    async def skip(self, ctx):
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        if not player:
            return await ctx.respond("노래 재생중이 아닙니다", delete_after=1)
        
        title = player.current.title
        await player.skip()
        await ctx.respond(f"`스킵:: {title}`", delete_after=1)
        

    @slash_command(name='반복', description="Loop")
    async def loop(self, ctx):
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        if not player:
            return await ctx.respond("노래 재생중이 아닙니다", delete_after=1)
        
        if player.loop == 0:
            player.set_loop(1)
            await ctx.respond("`현재 곡 반복을 켭니다`", delete_after=1)
        elif player.loop == 1:
            player.set_loop(2)
            await ctx.respond("`플레이리스트 전체 반복을 켭니다`", delete_after=1)
        elif player.loop == 2:
            player.set_loop(0)
            await ctx.respond("`반복을 끕니다`", delete_after=1)

    @slash_command(name="종료", description="Stop")
    async def stop(self, ctx):
        """ Disconnects the player from the voice channel and clears its queue. """
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        # The necessary voice channel checks are handled in "create_player."
        # We don't need to duplicate code checking them again.

        # Clear the queue to ensure old tracks don't start playing
        # when someone else queues something.

        if not player:
            return await ctx.respond("노래 재생중이 아닙니다", delete_after=1)
        
        player.queue.clear()
        # Stop the current track so Lavalink consumes less resources.
        await player.stop()
        # Disconnect from the voice channel.
        await ctx.guild.voice_client.disconnect(force=True)
        await ctx.respond("`플레이어 종료`", delete_after=1)
        await self.viewmanager.updateContainer(player)


def setup(bot):
    bot.add_cog(Music(bot))