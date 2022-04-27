import re
import os
import math
import random
import discord
import lavalink
from discord.ext import commands
from discord.commands import slash_command, Option
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials


cid = os.environ["SPOTIPY_CLIENT_ID"]
secret = os.environ["SPOTIPY_CLIENT_SECRET"]
client_credentials_manager = SpotifyClientCredentials(client_id=cid, client_secret=secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

try:
    lavalinkIP = str(os.environ["LAVALINK_IP"])
except:
    lavalinkIP = 'localhost'

try:
    lavalinkPW = os.environ["LAVALINK_PW"]
except:
    lavalinkPW = 'password'

url_rx = re.compile(r'https?://(?:www\.)?.+')
spotify_rx = re.compile(r'open\.spotify')

playlist = {
    'ISEGYE IDOL : MUSIC': 'https://youtube.com/playlist?list=PLWTycz4el4t4l6uuriz3OhqR2aKy86EEP',
    'ALL(왁타버스) : MUSIC': 'https://youtube.com/playlist?list=PLWTycz4el4t7ZCxkGYyekoP1iBxmOM4zZ',

}


class LavalinkVoiceClient(discord.VoiceClient):
    def __init__(self, client: discord.Client, channel: discord.abc.Connectable):
        self.client = client
        self.channel = channel

        if hasattr(self.client, 'lavalink'):
            self.lavalink = self.client.lavalink
        else:
            self.client.lavalink = lavalink.Client(client.user.id)
            self.client.lavalink.add_node(
                    lavalinkIP,
                    8080,
                    lavalinkPW,
                    'eu',
                    'default-node')
            self.lavalink = self.client.lavalink

    async def on_voice_server_update(self, data):
        lavalink_data = {
                't': 'VOICE_SERVER_UPDATE',
                'd': data
                }
        await self.lavalink.voice_update_handler(lavalink_data)

    async def on_voice_state_update(self, data):
        lavalink_data = {
                't': 'VOICE_STATE_UPDATE',
                'd': data
                }
        await self.lavalink.voice_update_handler(lavalink_data)

    async def connect(self, *, timeout: float, reconnect: True):
        self.lavalink.player_manager.create(guild_id=self.channel.guild.id)
        await self.channel.guild.change_voice_state(channel=self.channel)

    async def disconnect(self, *, force: True):
        player = self.lavalink.player_manager.get(self.channel.guild.id)
        if not force and not player.is_connected:
            return
        await self.channel.guild.change_voice_state(channel=None)
        player.channel_id = None
        self.cleanup()

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        if not hasattr(bot, 'lavalink'):
            bot.lavalink = lavalink.Client(731538324170342461)
            bot.lavalink.add_node(lavalinkIP, 8080, lavalinkPW, 'eu', 'default-node')  # Host, Port, Password, Region, Name

        lavalink.add_event_hook(self.track_hook)

    def cog_unload(self):
        self.bot.lavalink._event_hooks.clear()

    async def cog_before_invoke(self, ctx):
        guild_check = ctx.guild is not None
        if guild_check:
            await self.ensure_voice(ctx)

        return guild_check

    async def cog_command_error(self, ctx, error):
        if isinstance(error, commands.CommandInvokeError):
            await ctx.respond(error.original)

    async def ensure_voice(self, ctx):
        player = self.bot.lavalink.player_manager.create(ctx.guild.id, endpoint=str(ctx.guild.region))
        should_connect = ctx.command.name in ('play','list')

        if not ctx.author.voice or not ctx.author.voice.channel:
            raise commands.CommandInvokeError('Join a voicechannel first.')

        if not player.is_connected:
            if not should_connect:
                raise commands.CommandInvokeError('봇이 연결되어 있지 않습니다') # Not connected.

            permissions = ctx.author.voice.channel.permissions_for(ctx.me)

            if not permissions.connect or not permissions.speak:
                raise commands.CommandInvokeError('"연결", "말하기" 권한이 필요합니다') # I need the `CONNECT` and `SPEAK` permissions.

            player.store('channel', ctx.channel.id)
            await ctx.author.voice.channel.connect(cls=LavalinkVoiceClient)
        else:
            if int(player.channel_id) != ctx.author.voice.channel.id:
                raise commands.CommandInvokeError('같은 음성 채널에 있어야합니다') # You need to be in my voicechannel.

    async def track_hook(self, event):
        if isinstance(event, lavalink.events.QueueEndEvent):
            guild_id = int(event.player.guild_id)
            guild = self.bot.get_guild(guild_id)
            await guild.voice_client.disconnect(force=True)


    @slash_command(guild_ids=[723892698435551324, 896398625163345931], description="play")
    async def play(self, ctx, search: Option(str, "노래 이름 입력")):
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        query = search.strip('<>')

        if url_rx.match(query):
            if spotify_rx.search(query):
                trackid = query.split('?')[0].split('/')[-1]
                result = sp.track(trackid)
                query = f'ytsearch:{result["artists"][0]["name"]} {result["name"]}'
        else:
            query = f'ytsearch:{query}'

        results = await player.node.get_tracks(query)

        if not results or not results['tracks']:
            return await ctx.respond('Nothing found!')

        embed = discord.Embed(color=0xf5a9a9)

        # Valid loadTypes are:
        #   TRACK_LOADED    - single video/direct URL)
        #   PLAYLIST_LOADED - direct URL to playlist)
        #   SEARCH_RESULT   - query prefixed with either ytsearch: or scsearch:.
        #   NO_MATCHES      - query yielded no results
        #   LOAD_FAILED     - most likely, the video encountered an exception during loading.
        if results['loadType'] == 'PLAYLIST_LOADED':
            tracks = results['tracks']
            info = tracks[0]['info']
            random.shuffle(tracks)

            for track in tracks:
                # Add all of the tracks from the playlist to the queue.
                player.add(requester=ctx.author.id, track=track)
            
            # list로 했을때 셔플
            embed.title = 'Playlist Enqueued'
            embed.description = f'{results["playlistInfo"]["name"]} - {len(tracks)} tracks'
        else:
            track = results['tracks'][0]
            info = track['info']

            player.add(requester=ctx.author.id, track=track)

            if not player.queue:
                embed.title = 'Now Playing'
                minutes = int(info['length']//60000)
                seconds = int(info['length']/1000%60)
                embed.description = f'[{info["title"]}]({info["uri"]})\n`[00:00 / {minutes:02d}:{seconds:02d}]`\n\n Requested by: <@{ctx.author.id}>'
            else:
                embed.title = 'Track Enqueued'
                embed.description = f'[{info["title"]}]({info["uri"]})\nRequested by: <@{ctx.author.id}>'

            # You can attach additional information to audiotracks through kwargs, however this involves
            # constructing the AudioTrack class yourself.

            # track = lavalink.models.AudioTrack(track, ctx.author.id)

        embed.set_thumbnail(url=f'https://i.ytimg.com/vi/{info["identifier"]}/0.jpg')
        await ctx.respond(embed=embed)

        # We don't want to call .play() if the player is playing as that will effectively skip
        # the current track.py.
        if not player.is_playing:
            await player.play()
        

    @slash_command(name="list", guild_ids=[723892698435551324, 896398625163345931], description="플레이리스트")
    async def playlist(self, ctx):
        select = discord.ui.Select(placeholder='플레이 리스트 선택', options=[
            discord.SelectOption(label='ISEGYE IDOL : MUSIC'),
            discord.SelectOption(label='ALL(왁타버스) : MUSIC'),

        ])

        async def callback(interaction):
            await self.play(ctx, playlist[select.values[0]])
            await interaction.response.edit_message(delete_after=0)

        select.callback = callback
   

        view=discord.ui.View()
        view.add_item(select)
        await ctx.respond('```플레이리스트는 자동으로 셔플됩니다.\n원하는 플레이리스트가 있으면 연구실에 남겨주세요```', view=view)


    @slash_command(guild_ids=[723892698435551324, 896398625163345931], description="skip")
    async def skip(self, ctx):
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        if not player.is_playing:
            embed = discord.Embed(color=0xf5a9a9)
            embed.title = "재생 중인 곡이 없습니다"
            return await ctx.respond(embed=embed)

        await player.skip()
        await ctx.respond("song skipped")

    
    @slash_command(guild_ids=[723892698435551324, 896398625163345931], description="stop")
    async def stop(self, ctx):
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        if not player.is_playing:
            embed = discord.Embed(color=0xf5a9a9)
            embed.title = "재생 중인 곡이 없습니다"
            return await ctx.respond(embed=embed)

        player.queue.clear()
        await player.stop()
        await ctx.respond("player stopped")
    
    @slash_command(guild_ids=[723892698435551324, 896398625163345931], description="seek")
    async def seek(self, ctx, seconds: Option(int, "정수 입력")):
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        if not player.is_playing:
            embed = discord.Embed(color=0xf5a9a9)
            embed.title = "재생 중인 곡이 없습니다"
            return await ctx.respond(embed=embed)

        track_time = player.position + (seconds * 1000)
        await player.seek(track_time)
        embed = discord.Embed(color=0xf5a9a9)
        embed.title = "player seek"
        if seconds >= 0:
            embed.description = f"앞으로 {seconds}초 이동"
        else:
            embed.description = f"뒤로 {-seconds}초 이동"
        await ctx.respond(embed=embed)
    

    @slash_command(guild_ids=[723892698435551324, 896398625163345931], description="repeat")
    async def repeat(self, ctx):
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        if not player.is_playing:
            embed = discord.Embed(color=0xf5a9a9)
            embed.title = "재생 중인 곡이 없습니다"
            return await ctx.respond(embed=embed)

        # player.repeat = not player.repeat
        embed = discord.Embed(color=0xf5a9a9)
        if not player.repeat:
            player.set_repeat(True)
            embed.title = "플레이리스트 반복을 켭니다"
        else:
            player.set_repeat(False)
            embed.title = "플레이리스트 반복을 끕니다"
        await ctx.respond(embed=embed)


    @slash_command(guild_ids=[723892698435551324, 896398625163345931], description="now playing")
    async def now_playing(self, ctx):
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        if not player.current:
            embed = discord.Embed(color=0xf5a9a9)
            embed.title = "재생 중인 곡이 없습니다"
            return await ctx.respond(embed=embed)

        now_minutes = int(int(player.position)//60000)
        now_seconds = int(int(player.position)/1000%60)
        minutes = int(player.current.duration//60000)
        seconds = int(player.current.duration/1000%60)

        embed = discord.Embed(color=0xf5a9a9)
        embed.title = 'Now Playing'
        embed.description = f'[{player.current.title}]({player.current.uri})\n`[{now_minutes:02d}:{now_seconds:02d}/{minutes:02d}:{seconds:02d}`\n\n Requested by: <@{player.current.requester}>'
        embed.set_thumbnail(url=f'https://i.ytimg.com/vi/{player.current.identifier}/0.jpg')
        await ctx.respond(embed=embed)


    @slash_command(guild_ids=[723892698435551324, 896398625163345931], description="queue")
    async def queue(self, ctx, page: int = 1):
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        if not player.queue:
            embed = discord.Embed(color=0xf5a9a9)
            embed.title = "재생 목록이 비어있습니다"
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
        embed = discord.Embed(color=0xf5a9a9)
        embed.title = 'Music Queue'
        embed.description = f'**Now Playing**: [{player.current.title}]({player.current.uri})\n\n{queue_list}'
        embed.set_footer(text=f"{page}/{pages} page")
        await ctx.respond(embed=embed)


    @slash_command(guild_ids=[723892698435551324, 896398625163345931], description="pause")
    async def pause(self, ctx):
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        if not player.is_playing:
            embed = discord.Embed(color=0xf5a9a9)
            embed.title = "재생 중인 곡이 없습니다"
            return await ctx.respond(embed=embed)

        if player.paused:
            await player.set_pause(False)
            await ctx.respond('⏯ | Resumed')
        else:
            await player.set_pause(True)
            await ctx.respond('⏯ | Paused')


    @slash_command(guild_ids=[723892698435551324, 896398625163345931], description="remove")
    async def remove(self, ctx, index: int):
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        if not player.queue:
            embed = discord.Embed(color=0xf5a9a9)
            embed.title = "재생목록이 비어있습니다"
            return await ctx.respond(embed=embed)

        if index > len(player.queue) or index < 1:
            return await ctx.respond(f'1 부터 {len(player.queue)} 사이의 정수를 입력해주세요')
        removed = player.queue.pop(index - 1)
        await ctx.respond(f'**{index}.{removed.title}** 가 제거되었습니다')




    @slash_command(guild_ids=[723892698435551324, 896398625163345931], description="disconnect")
    async def disconnect(self, ctx):
        """ Disconnects the player from the voice channel and clears its queue. """
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        if not player.is_connected:
            return
            # return await ctx.respond('Not connected.')

        if not ctx.author.voice or (player.is_connected and ctx.author.voice.channel.id != int(player.channel_id)):
            return
            # return await ctx.respond('You\'re not in my voicechannel!')

        player.queue.clear()
        await player.stop()
        await ctx.voice_client.disconnect(force=True)
        await ctx.respond('Bye')


def setup(bot):
    bot.add_cog(Music(bot))
