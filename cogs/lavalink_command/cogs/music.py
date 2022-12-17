# 뮤직봇 only 슬래시 커맨드 완성본
''' 
커맨드 리스트 

play 재생
skip 스킵
stop 정지
pause 일시정지
seek 탐색
loop 반복
now_playing
queue 큐
remove 제거
list 플레이리스트
search 검색
disconnect 
'''


import re
import os
import sys
import math
import random
import discord
import lavalink
from discord.ext import commands
from discord.commands import slash_command, Option
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from config import guild_ids

cid = os.environ["SPOTIPY_CLIENT_ID"]
secret = os.environ["SPOTIPY_CLIENT_SECRET"]
client_credentials_manager = SpotifyClientCredentials(client_id=cid, client_secret=secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

url_rx = re.compile(r'https?://(?:www\.)?.+')
spotify_rx = re.compile('.+open.spotify.com/.+')


playlist = {
    'ALL(왁타버스) : MUSIC': 'https://youtube.com/playlist?list=PLWTycz4el4t7ZCxkGYyekoP1iBxmOM4zZ',
    'ISEGYE IDOL : MUSIC': 'https://youtube.com/playlist?list=PLWTycz4el4t4l6uuriz3OhqR2aKy86EEP',
    '아이네': 'https://www.youtube.com/playlist?list=PLJWTWXJ7iqXctxVu1Fd3ZkF-WWD8kOzMb',
    '징버거': 'https://www.youtube.com/playlist?list=PLio0a5EPF6j099Af5uBaK6V25RtTvK4kq',
    '릴파': 'https://www.youtube.com/playlist?list=PLLPGQs-RNQXnFl55WissjQylZbInOK81P',
    '주르르': 'https://www.youtube.com/playlist?list=PLqE7uvTHaH31Wl8lCe3SYslZvoCnTD-JS',
    '고세구': 'https://www.youtube.com/playlist?list=PLZNwpHxpI4EjDSv3v_HY7udxDEqj4C7PL',
    '비챤': 'https://www.youtube.com/playlist?list=PLhaJuLneKo5FdYnMZ1Jc5BaV7y26KvmD1'
}

class LavalinkVoiceClient(discord.VoiceClient):
    """
    This is the preferred way to handle external voice sending
    This client will be created via a cls in the connect method of the channel
    see the following documentation:
    https://discordpy.readthedocs.io/en/latest/api.html#voiceprotocol
    """

    def __init__(self, client: discord.Client, channel: discord.abc.Connectable):
        self.client = client
        self.channel = channel
        # ensure a client already exists
        if hasattr(self.client, 'lavalink'):
            self.lavalink = self.client.lavalink
        else:
            self.client.lavalink = lavalink.Client(client.user.id)
            self.client.lavalink.add_node(
                'localhost',
                2333,
                'password',
                'ko',
                'default-node'
            )
            self.lavalink = self.client.lavalink

    async def on_voice_server_update(self, data):
        # the data needs to be transformed before being handed down to
        # voice_update_handler
        lavalink_data = {
            't': 'VOICE_SERVER_UPDATE',
            'd': data
        }
        await self.lavalink.voice_update_handler(lavalink_data)

    async def on_voice_state_update(self, data):
        # the data needs to be transformed before being handed down to
        # voice_update_handler
        lavalink_data = {
            't': 'VOICE_STATE_UPDATE',
            'd': data
        }
        await self.lavalink.voice_update_handler(lavalink_data)

    async def connect(self, *, timeout: float, reconnect: bool, self_deaf: bool = False, self_mute: bool = False) -> None:
        """
        Connect the bot to the voice channel and create a player_manager
        if it doesn't exist yet.
        """
        # ensure there is a player_manager when creating a new voice_client
        self.lavalink.player_manager.create(guild_id=self.channel.guild.id)
        await self.channel.guild.change_voice_state(channel=self.channel, self_mute=self_mute, self_deaf=self_deaf)

    async def disconnect(self, *, force: bool = False) -> None:
        """
        Handles the disconnect.
        Cleans up running player and leaves the voice client.
        """
        player = self.lavalink.player_manager.get(self.channel.guild.id)

        # no need to disconnect if we are not connected
        if not force and not player.is_connected:
            return

        # None means disconnect
        await self.channel.guild.change_voice_state(channel=None)

        # update the channel_id of the player to None
        # this must be done because the on_voice_state_update that would set channel_id
        # to None doesn't get dispatched after the disconnect
        player.channel_id = None
        self.cleanup()


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        if not hasattr(bot, 'lavalink'):  # This ensures the client isn't overwritten during cog reloads.
            bot.lavalink = lavalink.Client(731538324170342461)
            bot.lavalink.add_node('127.0.0.1', 2333, 'password', 'ko', 'default-node')  # Host, Port, Password, Region, Name

        lavalink.add_event_hook(self.track_hook)

    def cog_unload(self):
        """ Cog unload handler. This removes any event hooks that were registered. """
        self.bot.lavalink._event_hooks.clear()

    async def cog_before_invoke(self, ctx):
        """ Command before-invoke handler. """
        guild_check = ctx.guild is not None
        #  This is essentially the same as `@commands.guild_only()`
        #  except it saves us repeating ourselves (and also a few lines).

        if guild_check:
            await self.ensure_voice(ctx)
            #  Ensure that the bot and command author share a mutual voicechannel.

        return guild_check

    async def cog_command_error(self, ctx, error):
        if isinstance(error, commands.CommandInvokeError):
            await ctx.respond(error.original)
            # The above handles errors thrown in this cog and shows them to the user.
            # This shouldn't be a problem as the only errors thrown in this cog are from `ensure_voice`
            # which contain a reason string, such as "Join a voicechannel" etc. You can modify the above
            # if you want to do things differently.

    async def ensure_voice(self, ctx):
        """ This check ensures that the bot and command author are in the same voicechannel. """
        player = self.bot.lavalink.player_manager.create(ctx.guild.id)
        # Create returns a player if one exists, otherwise creates.
        # This line is important because it ensures that a player always exists for a guild.

        # Most people might consider this a waste of resources for guilds that aren't playing, but this is
        # the easiest and simplest way of ensuring players are created.

        # These are commands that require the bot to join a voicechannel (i.e. initiating playback).
        # Commands such as volume/skip etc don't require the bot to be in a voicechannel so don't need listing here.
        should_connect = ctx.command.name in ('play', '재생', 'list', '플레이리스트', 'search')

        if not ctx.author.voice or not ctx.author.voice.channel:
            # Our cog_command_error handler catches this and sends it to the voicechannel.
            # Exceptions allow us to "short-circuit" command invocation via checks so the
            # execution state of the command goes no further.
            raise commands.CommandInvokeError('먼저 음성채널에 입장해주세요.') # Join a voicechannel first.

        v_client = ctx.voice_client
        if not v_client:
            if not should_connect:
                raise commands.CommandInvokeError('봇이 연결되어있지 않습니다') # Not connected.

            permissions = ctx.author.voice.channel.permissions_for(ctx.me)

            if not permissions.connect or not permissions.speak:  # Check user limit too?
                raise commands.CommandInvokeError('`연결` `말하기` 권한이 필요합니다') # I need the `CONNECT` and `SPEAK` permissions.

            player.store('channel', ctx.channel.id)
            await ctx.author.voice.channel.connect(cls=LavalinkVoiceClient)
        else:
            if v_client.channel.id != ctx.author.voice.channel.id:
                raise commands.CommandInvokeError('봇과 같은 음성채널에 있어야 합니다') # You need to be in my voicechannel.

    async def track_hook(self, event):
        if isinstance(event, lavalink.events.QueueEndEvent):
            # When this track_hook receives a "QueueEndEvent" from lavalink.py
            # it indicates that there are no tracks left in the player's queue.
            # To save on resources, we can tell the bot to disconnect from the voicechannel.
            guild_id = event.player.guild_id
            guild = self.bot.get_guild(guild_id)
            await guild.voice_client.disconnect(force=True)

############################################################################################################            

    @slash_command(name='재생', description="play")
    async def play_(self, ctx, query: Option(str, '노래 제목, 유튜브/스포티파이 링크')):
        await self.play(ctx, query)

    @slash_command(name='play', description="play")
    async def play(self, ctx, query: Option(str, '노래 제목, 유튜브/스포티파이 링크')):
        """ Searches and plays a song from a given query. """
        # Get the player for this guild from cache.
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        # Remove leading and trailing <>. <> may be used to suppress embedding links in Discord.
        query = query.strip('<>')

        # Check if the user input might be a URL. If it isn't, we can Lavalink do a YouTube search for it instead.
        # SoundCloud searching is possible by prefixing "scsearch:" instead.
        if url_rx.match(query):
            if spotify_rx.search(query):
                trackid = query.split('?')[0].split('/')[-1]
                result = sp.track(trackid)
                query = f'ytsearch:{result["artists"][0]["name"]} {result["name"]}'
        else:
            query = f'ytsearch:{query}'

        # Get the results for the query from Lavalink.
        results = await player.node.get_tracks(query)

        # Results could be None if Lavalink returns an invalid response (non-JSON/non-200 (OK)).
        # ALternatively, resullts.tracks could be an empty array if the query yielded no tracks.
        if not results or not results.tracks:
            return await ctx.respond('결과를 찾을 수 없습니다.')

        embed = discord.Embed(color=0xf5a9a9)

        # Valid loadTypes are:
        #   TRACK_LOADED    - single video/direct URL)
        #   PLAYLIST_LOADED - direct URL to playlist)
        #   SEARCH_RESULT   - query prefixed with either ytsearch: or scsearch:.
        #   NO_MATCHES      - query yielded no results
        #   LOAD_FAILED     - most likely, the video encountered an exception during loading.
        if results.load_type == 'PLAYLIST_LOADED':
            tracks = results.tracks
            first = tracks[0]
            random.shuffle(tracks)

            for track in tracks:
                # Add all of the tracks from the playlist to the queue.
                player.add(requester=ctx.author.id, track=track)

            embed.title = '플레이리스트 추가'
            embed.description = f'[{results.playlist_info.name}]({query}) - {len(tracks)} tracks'
            embed.set_thumbnail(url=f'https://i.ytimg.com/vi/{first.identifier}/maxresdefault.jpg')

        else:
            track = results.tracks[0]
            duration_min = int(track.duration//60000)
            duration_sec = int(track.duration/1000%60)
            embed.set_thumbnail(url=f'https://i.ytimg.com/vi/{track.identifier}/maxresdefault.jpg')

            if not player.is_playing:
                embed.title = '지금 재생 중'
                embed.description = f'[{track.title}]({track.uri})\n`00:00 / {duration_min:02d}:{duration_sec:02d}`\n\nRequested by <@{ctx.author.id}>'
            else:
                embed.title = '노래 추가'
                embed.description = f'[{track.title}]({track.uri})\n`{duration_min:02d}:{duration_sec:02d}`\n\nRequested by <@{ctx.author.id}>'

            player.add(requester=ctx.author.id, track=track)

        await ctx.respond(embed=embed)

        # We don't want to call .play() if the player is playing as that will effectively skip
        # the current track.
        if not player.is_playing:
            await player.play()


    @slash_command(name='검색', description="search")
    async def search_(self, ctx, query: Option(str, '검색')):
        await self.search(ctx, query)
    
    @slash_command(name='search', description="search")
    async def search(self, ctx, query: Option(str, '노래 제목, 유튜브/스포티파이 링크')):
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        query = query.strip('<>')

        if url_rx.match(query):
            if spotify_rx.search(query):
                trackid = query.split('?')[0].split('/')[-1]
                result = sp.track(trackid)
                query = f'ytsearch:{result["artists"][0]["name"]} {result["name"]}'
        else:
            query = f'ytsearch:{query}'

        results = await player.node.get_tracks(query)

        if not results or not results.tracks:
            return await ctx.respond('결과를 찾을 수 없습니다.')

        embed = discord.Embed(color=0xf5a9a9)
        embed.title = '검색 결과'
        result_list = ''
        for i in range(5):
            result_list += f'**{i+1}**. [{results.tracks[i].title}]({results.tracks[i].uri})\n'
        embed.description = result_list
        await ctx.respond(embed=embed)


    @slash_command(name='일시정지', description="pause resume")
    async def pause_(self, ctx):
        await self.pause(ctx)

    @slash_command(name='pause', description="pause resume")
    async def pause(self, ctx):
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        embed = discord.Embed(color=0xf5a9a9)

        if not player.is_playing:
            embed.title = "재생 중인 곡이 없습니다"
            return await ctx.respond(embed=embed)

        if player.paused:
            await player.set_pause(False)
            embed.title('⏯ | 재생')
        else:
            await player.set_pause(True)
            embed.title('⏯ | 일시정지')
        await ctx.respond(embed=embed)


    @slash_command(name='스킵', description="skip")
    async def skip_(self, ctx):
        await self.skip(ctx)

    @slash_command(name='skip', description="skip")
    async def skip(self, ctx):
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        if not player.is_playing:
            embed = discord.Embed(color=0xf5a9a9)
            embed.title = "재생 중인 곡이 없습니다"
            return await ctx.respond(embed=embed)

        title = player.current.title
        await player.skip()
        await ctx.respond(f"`스킵:: {title}`")



    @slash_command(name='정지', description="stop")
    async def stop_(self, ctx):
        await self.stop(ctx)

    @slash_command(name='stop', description="stop")
    async def stop(self, ctx):
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        embed = discord.Embed(color=0xf5a9a9)

        if not player.is_playing:
            embed.title = "재생 중인 곡이 없습니다"
            return await ctx.respond(embed=embed)

        player.queue.clear()
        await player.stop()
        await ctx.voice_client.disconnect(force=True)
        embed.title = "플레이어 종료"
        await ctx.respond(embed=embed)


    @slash_command(name='탐색', description="seek")
    async def seek_(self, ctx, seconds: Option(int, "+/- 초 (정수)")):
        await self.seek(ctx, seconds)

    @slash_command(name='seek', description="seek")
    async def seek(self, ctx, seconds: Option(int, "+/- 초 (정수)")):
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        embed = discord.Embed(color=0xf5a9a9)

        if not player.is_playing:
            embed.title = "재생 중인 곡이 없습니다"
            return await ctx.respond(embed=embed)

        track_time = player.position + (seconds * 1000)
        await player.seek(track_time)
        if seconds >= 0:
            embed.title = f"앞으로 {seconds}초 이동"
        else:
            embed.title = f"뒤로 {-seconds}초 이동"
        await ctx.respond(embed=embed)


    @slash_command(name='반복', description="loop")
    async def loop_(self, ctx):
        await self.loop(ctx)

    @slash_command(name='loop', description="loop")
    async def loop(self, ctx):
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        embed = discord.Embed(color=0xf5a9a9)

        if not player.is_playing:
            embed.title = "재생 중인 곡이 없습니다"
            return await ctx.respond(embed=embed)

        if player.loop == 0:
            player.set_loop(1)
            embed.title = f"{player.current.title}\n반복을 켭니다"
        elif player.loop == 1:
            player.set_loop(2)
            embed.title = "플레이리스트 반복을 켭니다"
        elif player.loop == 2:
            player.set_loop(0)
            embed.title = "반복을 끕니다"
        await ctx.respond(embed=embed)


    @slash_command(name='제거', description="remove")
    async def remove_(self, ctx, index: Option(int, "노래 번호 index")):
        await self.remove(ctx, index)

    @slash_command(name='remove', description="remove")
    async def remove(self, ctx, index: Option(int, "노래 번호 index")):
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        if not player.queue:
            embed = discord.Embed(color=0xf5a9a9)
            embed.title = "재생 목록이 비어있습니다"
            return await ctx.respond(embed=embed)

        if index > len(player.queue) or index < 1:
            return await ctx.respond(f'1 부터 {len(player.queue)} 사이의 정수를 입력해주세요')
        removed = player.queue.pop(index - 1)
        await ctx.respond(f'`제거:: {index}. {removed.title}`')


    @slash_command(name='now_playing', description="now playing")
    async def now_playing(self, ctx):
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        embed = discord.Embed(color=0xf5a9a9)

        if not player.is_playing:
            embed.title = "재생 중인 곡이 없습니다"
            return await ctx.respond(embed=embed)

        now_min = int(int(player.position)//60000)
        now_sec = int(int(player.position)/1000%60)
        duration_min = int(player.current.duration//60000)
        duration_sec = int(player.current.duration/1000%60)

        embed.title = '지금 재생 중'
        embed.description = f'[{player.current.title}]({player.current.uri})\n`[{now_min:02d}:{now_sec:02d}/{duration_min:02d}:{duration_sec:02d}`\n\nRequested by: <@{player.current.requester}>'
        embed.set_thumbnail(url=f'https://i.ytimg.com/vi/{player.current.identifier}/maxresdefault.jpg')
        await ctx.respond(embed=embed)


    @slash_command(name='큐', description="queue")
    async def queue_(self, ctx, page: Option(int, "페이지 번호 index", default=1)):
        await self.queue(ctx, page)

    @slash_command(name='queue', description="queue")
    async def queue(self, ctx, page: Option(int, "페이지 번호 index", default=1)):
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        embed = discord.Embed(color=0xf5a9a9)

        if not player.is_playing:
            embed.title = "재생 중인 곡이 없습니다"
            return await ctx.respond(embed=embed)

        embed.title = '재생 목록'

        if not player.queue:
            embed.description = f'**지금 재생 중**: [{player.current.title}]({player.current.uri})\n\n**재생 목록이 비어있습니다**'
            return await ctx.respond(embed=embed)

        tracks_per_page = 10
        pages = math.ceil(len(player.queue) / tracks_per_page) # queue 올림해서 페이지 수 계산
        if page > pages: # 최대 페이지 보다 더 큰 수 입력시 마지막 페이지 보여주기
            page = pages
        start = (page - 1) * tracks_per_page
        end = start + tracks_per_page
        queue_list = ''

        for index, track in enumerate(player.queue[start:end], start=start+1):
            queue_list += f'**{index}**. [{track.title}]({track.uri})\n'
        embed.description = f'**Now Playing**: [{player.current.title}]({player.current.uri})\n\n{queue_list}'
        embed.set_footer(text=f"{page}/{pages} page")
        await ctx.respond(embed=embed)


    @slash_command(name="플레이리스트", description="플레이리스트")
    async def playlist_(self, ctx):
        await self.playlist(ctx)

    @slash_command(name="list", description="플레이리스트")
    async def playlist(self, ctx):
        select = discord.ui.Select(placeholder='플레이 리스트 선택', options=[
            discord.SelectOption(label='ALL(왁타버스) : MUSIC'),
            discord.SelectOption(label='ISEGYE IDOL : MUSIC'),
            discord.SelectOption(label='아이네'),
            discord.SelectOption(label='징버거'),
            discord.SelectOption(label='릴파'),
            discord.SelectOption(label='주르르'),
            discord.SelectOption(label='고세구'),
            discord.SelectOption(label='비챤')
        ])

        async def callback(interaction):
            await self.play(ctx, playlist[select.values[0]])
            await interaction.response.edit_message(delete_after=0)

        select.callback = callback
   

        view=discord.ui.View()
        view.add_item(select)
        await ctx.respond('```플레이리스트는 자동으로 셔플됩니다.\n원하는 플레이리스트가 있으면 혁수s연구실 채널에 남겨주세요```', view=view)


    @slash_command(description="disconnect")
    async def disconnect(self, ctx):
        """ Disconnects the player from the voice channel and clears its queue. """
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        # if not player.is_connected:
        #     return await ctx.respond('봇이 연결되어있지 않습니다')

        # if not ctx.author.voice or (player.is_connected and ctx.author.voice.channel.id != int(player.channel_id)):
        #     return await ctx.respond('봇과 같은 음성채널에 있어야 합니다')

        player.queue.clear()
        await player.stop()
        await ctx.voice_client.disconnect(force=True)
        await ctx.respond('Bye')


def setup(bot):
    bot.add_cog(Music(bot))