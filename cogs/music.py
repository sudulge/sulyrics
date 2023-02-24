# 뮤직봇 전용 채널 ui + 슬래시커맨드 완성본
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
log 기록
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
from discord.ui import Select, Button, Modal, View, InputText
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from ytmusicapi import YTMusic
import pickle
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

from .data.data import playlist

cid = os.getenv("spotipy_client_id")
secret = os.getenv("spotipy_client_secret")
client_credentials_manager = SpotifyClientCredentials(client_id=cid, client_secret=secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

url_rx = re.compile(r'https?://(?:www\.)?.+')
spotify_rx = re.compile('.+open.spotify.com/.+')


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


async def get_all_data(type):
    try:
        with open(f"cogs/data/music_{type}.pickle", 'rb') as f:
            return pickle.load(f)
    except:
        return {}


async def add_channel(guild_id, channel_id, message_id):
    data = await get_all_data('channel')
    data[guild_id] = {"channel_id": channel_id, "message_id": message_id}
    with open('cogs/data/music_channel.pickle', 'wb') as f:
        pickle.dump(data, f)

async def add_log(guild_id, title, uri, requester, date):
    data = await get_all_data('log')
    dic = {'title': title, 'uri': uri, 'requester': requester, 'date': date}
    try:
        data[guild_id].append(dic)
    except KeyError:
        data[guild_id] = [dic]
    with open('cogs/data/music_log.pickle', 'wb') as f: 
        pickle.dump(data, f)    
    
async def get_data(guild_id, type):
    data = await get_all_data(type)
    return data[guild_id]

async def idlePlayerEmbed():
    embed = discord.Embed(color=0xf5a9a9)
    embed.title = '수리릭 노래봇'
    embed.description = '이 채널에서는 커맨드를 사용하지 않아도 노래를 틀 수 있습니다\n`/list` 커맨드로 플레이리스트를 고를 수 있습니다\n모든 커맨드는 다른 채널에서도 사용 가능 합니다'
    embed.set_image(url='https://cdn.discordapp.com/attachments/1033149773504593921/1033712101354651678/main.png')
    return embed

async def idleListEmbed():
    embed = discord.Embed(color=0xf5a9a9)
    embed.title = '재생목록'
    embed.description = '텅텅.'
    return embed


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        if not hasattr(bot, 'lavalink'):  # This ensures the client isn't overwritten during cog reloads.
            bot.lavalink = lavalink.Client(731538324170342461)
            bot.lavalink.add_node('127.0.0.1', 2333, 'password', 'ko', 'default-node')  # Host, Port, Password, Region, Name

        lavalink.add_event_hook(self.track_hook)

        self.shuffle = False

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
            # await ctx.respond(error.original, delete_after=1)
            # sulyrics.py 에서 on_application_command_error 로 처리.
            pass
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
        should_connect = ctx.command.name in ('play', '재생', 'list', '플레이리스트', 'search', '검색') #봇을 들어오게 하는 커맨드인듯 ? 
        normal_command = ctx.command.name in ('setting', 'log', '기록', 'updateview') # 봇 클라이언트와 관련 없는 커맨드 (임의로 만듦)

        if not ctx.author.voice or not ctx.author.voice.channel:
            # Our cog_command_error handler catches this and sends it to the voicechannel.
            # Exceptions allow us to "short-circuit" command invocation via checks so the
            # execution state of the command goes no further.
            raise commands.CommandInvokeError('먼저 음성채널에 입장해주세요') # Join a voicechannel first.

        v_client = ctx.voice_client
        if not v_client: # 보이스 클라이언트가 없고
            if not should_connect: # 봇을 들어오게 하는 커맨드가 아니라면
                if not normal_command: # 봇 클라이언트와 관련이 있는 커맨드라면
                    raise commands.CommandInvokeError('봇이 연결되어있지 않습니다') # Not connected.
                else: #봇 클라이언트와 관련이 없는 커맨드라면 -> 경고 띄우지 않고 커맨드 실행
                    return

            permissions = ctx.author.voice.channel.permissions_for(ctx.me)

            if not permissions.connect or not permissions.speak:  # Check user limit too?
                raise commands.CommandInvokeError('`연결` `말하기` 권한이 필요합니다') # I need the `CONNECT` and `SPEAK` permissions.
            try:
                data = await get_data(ctx.guild.id, 'channel')
            except KeyError:
                raise commands.CommandInvokeError('노래 채널이 없습니다.\n`/setting` 커맨드로 채널을 만들어주세요')
            player.store('channel_id', data["channel_id"])
            player.store('message_id', data["message_id"])
            player.store('page', 1)
            await ctx.author.voice.channel.connect(cls=LavalinkVoiceClient)
        else:
            if v_client.channel.id != ctx.author.voice.channel.id:
                raise commands.CommandInvokeError('봇과 같은 음성채널에 있어야 합니다') # You need to be in my voicechannel.


    async def ensure_voice_chat(self, message):
        """ This check ensures that the bot and command author are in the same voicechannel. """
        player = self.bot.lavalink.player_manager.create(message.guild.id)
        
        if not message.author.voice or not message.author.voice.channel:
            await message.channel.send('먼저 음성채널에 입장해주세요', delete_after=1)
            raise commands.CommandInvokeError('먼저 음성채널에 입장해주세요')

        v_client = message.guild.voice_client
        if not v_client: # 보이스 클라이언트가 없고
            data = await get_data(message.guild.id, 'channel')
            player.store('channel_id', data["channel_id"])
            player.store('message_id', data["message_id"])
            player.store('page', 1)
            await message.author.voice.channel.connect(cls=LavalinkVoiceClient)
        else:
            if v_client.channel.id != message.author.voice.channel.id:
                await message.channel.send('봇과 같은 음성채널에 있어야 합니다', delete_after=1)
                raise commands.CommandInvokeError('봇과 같은 음성채널에 있어야 합니다')

    async def track_hook(self, event):
        if isinstance(event, lavalink.events.QueueEndEvent):
            # When this track_hook receives a "QueueEndEvent" from lavalink.py
            # it indicates that there are no tracks left in the player's queue.
            # To save on resources, we can tell the bot to disconnect from the voicechannel.
            guild_id = event.player.guild_id
            guild = self.bot.get_guild(guild_id)
            await guild.voice_client.disconnect(force=True)

            channel = await self.bot.fetch_channel(event.player.fetch('channel_id'))
            msg = await channel.fetch_message(event.player.fetch('message_id'))
            listembed = await idleListEmbed()
            playerembed = await idlePlayerEmbed()
            await msg.edit(embeds=[listembed, playerembed])

        elif isinstance(event, lavalink.events.TrackStartEvent):
            player = event.player
            await add_log(player.guild_id, player.current.title, player.current.uri, self.bot.get_guild(player.guild_id).get_member(player.current.requester).display_name, datetime.now().strftime("%m/%d %H:%M"))
            duration_min = int(player.current.duration//60000)
            duration_sec = int(player.current.duration/1000%60)
            playerembed = discord.Embed(color=0xf5a9a9)
            playerembed.title = '지금 재생 중'
            playerembed.description = f'[{player.current.title}]({player.current.uri})\n`[00:00/{duration_min:02d}:{duration_sec:02d}`\n\nRequested by: <@{player.current.requester}>'
            playerembed.set_image(url=f'https://i.ytimg.com/vi/{player.current.identifier}/maxresdefault.jpg')

            listembed = discord.Embed(color=0xf5a9a9)
            listembed.title = '재생 목록'
            if not player.queue:
                listembed.description = f'**지금 재생 중**: [{player.current.title}]({player.current.uri})\n\n**텅텅.**'
            else:
                page = 1
                tracks_per_page = 5
                pages = math.ceil(len(player.queue) / tracks_per_page) # queue 올림해서 페이지 수 계산
                start = (page - 1) * tracks_per_page
                end = start + tracks_per_page
                queue_list = ''
                for index, track in enumerate(player.queue[start:end], start=start+1):
                    queue_list += f'**{index}**. [{track.title}]({track.uri})\n'
                listembed.description = f'**지금 재생 중**: [{player.current.title}]({player.current.uri})\n\n{queue_list}'
                listembed.set_footer(text=f"{page}/{pages} page")

            channel = await self.bot.fetch_channel(player.fetch('channel_id'))
            msg = await channel.fetch_message(player.fetch('message_id'))
            await msg.edit(embeds=[listembed, playerembed])
            player.store('page', 1)


    @slash_command(name='setting', description="create music channel")
    async def setting(self, ctx):
        channel = await ctx.guild.create_text_channel(name='노래채널_수리릭', topic='수리릭 노래 채널입니다. 버그있거나 추가하고 싶은 플레이리스트 있으면 말해주삼')
        listembed = await idleListEmbed()
        playerembed = await idlePlayerEmbed()
        message = await channel.send(embeds=[listembed, playerembed], view=MyView())
        await add_channel(ctx.guild.id, channel.id, message.id)
        await ctx.respond('노래 채널 추가 완료 \n채널 알림은 꺼놓는 것을 추천합니다')


    @slash_command(name='재생', description="play")
    async def play_(self, ctx, query: Option(str, '노래 제목, 유튜브/스포티파이 링크')):
        await self.play(ctx, query)

    @slash_command(name='play', description="play")
    async def play(self, ctx, query: Option(str, '노래 제목, 유튜브/스포티파이 링크')):
        if isinstance(ctx, discord.Message): # on_message 에서 호출 됐을 경우. 
            send = ctx.channel.send
            await self.ensure_voice_chat(ctx)
            player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        else:
            send = ctx.respond
            player = self.bot.lavalink.player_manager.get(ctx.guild.id) 
        """ Searches and plays a song from a given query. """
        # Get the player for this guild from cache.
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
            return await send('결과를 찾을 수 없습니다.', delete_after=1)

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

            # /list, /플레이리스트 명령어로 넣었을때는 self.shuffle을 True로 바꿔줘서 셔플하기. 
            # 그냥 링크로 넣었을때는 셔플 x 
            if self.shuffle:
                random.shuffle(tracks)
                self.shuffle = False
            else:
                pass

            for track in tracks:
                # Add all of the tracks from the playlist to the queue.
                player.add(requester=ctx.author.id, track=track)

            embed.title = '플레이리스트 추가'
            embed.description = f'[{results.playlist_info.name}]({query}) - {len(tracks)} tracks'
            embed.set_thumbnail(url=f'https://i.ytimg.com/vi/{first.identifier}/maxresdefault.jpg')
            await send(embed=embed, delete_after=1)            

        else:
            track = results.tracks[0]
            duration_min = int(track.duration//60000)
            duration_sec = int(track.duration/1000%60)
            embed.set_thumbnail(url=f'https://i.ytimg.com/vi/{track.identifier}/maxresdefault.jpg')

            if not player.is_playing:
                embed.title = '지금 재생 중'
                embed.description = f'[{track.title}]({track.uri})\n`00:00 / {duration_min:02d}:{duration_sec:02d}`\n\nRequested by <@{ctx.author.id}>'
                await send(embed=embed, delete_after=1)
            else:
                embed.title = '노래 추가'
                embed.description = f'[{track.title}]({track.uri})\n`{duration_min:02d}:{duration_sec:02d}`\n\nRequested by <@{ctx.author.id}>'
                await send(embed=embed, delete_after=1)

            player.add(requester=ctx.author.id, track=track)


        # We don't want to call .play() if the player is playing as that will effectively skip
        # the current track.
        if not player.is_playing:
            await player.play()
        else: # 플레이어가 재생중일 때 리스트 임베드 업데이트 . 
            listembed = discord.Embed(color=0xf5a9a9)
            listembed.title = '재생 목록'
            page = 1
            tracks_per_page = 5
            pages = math.ceil(len(player.queue) / tracks_per_page) # queue 올림해서 페이지 수 계산
            start = (page - 1) * tracks_per_page
            end = start + tracks_per_page
            queue_list = ''
            for index, track_ in enumerate(player.queue[start:end], start=start+1):
                queue_list += f'**{index}**. [{track_.title}]({track_.uri})\n'
            listembed.description = f'**지금 재생 중**: [{player.current.title}]({player.current.uri})\n\n{queue_list}'
            listembed.set_footer(text=f"{page}/{pages} page")
            if isinstance(ctx, discord.Message):
                msg = await ctx.channel.fetch_message(player.fetch('message_id'))
            else:
                channel = await self.bot.fetch_channel(player.fetch('channel_id'))
                msg = await channel.fetch_message(player.fetch('message_id'))
            await msg.edit(embeds=[listembed, msg.embeds[1]])
            player.store('page', 1)


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
            return await ctx.respond('결과를 찾을 수 없습니다.', delete_after=1)

        embed = discord.Embed(color=0xf5a9a9)
        embed.title = '검색 결과'
        result_list = ''
        for i in range(5):
            result_list += f'**{i+1}**. [{results.tracks[i].title}]({results.tracks[i].uri})\n'
        embed.description = result_list
        await ctx.respond(embed=embed, delete_after=5)


    @slash_command(name='일시정지', description="pause resume")
    async def pause_(self, ctx):
        await self.pause(ctx)

    @slash_command(name='pause', description="pause resume")
    async def pause(self, ctx):
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        embed = discord.Embed(color=0xf5a9a9)

        if not player.is_playing:
            embed.title = "재생 중인 곡이 없습니다"
            return await ctx.respond(embed=embed, delete_after=1)

        if player.paused:
            await player.set_pause(False)
            embed.title = '⏯ | 재생'
        else:
            await player.set_pause(True)
            embed.title = '⏯ | 일시정지'
        await ctx.respond(embed=embed, delete_after=1)


    @slash_command(name='스킵', description="skip")
    async def skip_(self, ctx):
        await self.skip(ctx)

    @slash_command(name='skip', description="skip")
    async def skip(self, ctx):
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        if not player.is_playing:
            embed = discord.Embed(color=0xf5a9a9)
            embed.title = "재생 중인 곡이 없습니다"
            return await ctx.respond(embed=embed, delete_after=1)

        title = player.current.title
        await player.skip()
        await ctx.respond(f"`스킵:: {title}`", delete_after=1)


    @slash_command(name='정지', description="stop")
    async def stop_(self, ctx):
        await self.stop(ctx)

    @slash_command(name='stop', description="stop")
    async def stop(self, ctx):
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        embed = discord.Embed(color=0xf5a9a9)

        if not player.is_playing:
            embed.title = "플레이어 종료"
            await ctx.voice_client.disconnect(force=True)
            return await ctx.respond(embed=embed, delete_after=1)

        player.queue.clear()
        await player.stop()
        await ctx.voice_client.disconnect(force=True)
        embed.title = "플레이어 종료"
        await ctx.respond(embed=embed, delete_after=1)

        msg = await ctx.fetch_message(player.fetch('message_id'))
        listembed = await idleListEmbed()
        playerembed = await idlePlayerEmbed()
        await msg.edit(embeds=[listembed, playerembed])


    @slash_command(name='탐색', description="seek")
    async def seek_(self, ctx, seconds: Option(int, "+/- 초 (정수)")):
        await self.seek(ctx, seconds)

    @slash_command(name='seek', description="seek")
    async def seek(self, ctx, seconds: Option(int, "+/- 초 (정수)")):
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        embed = discord.Embed(color=0xf5a9a9)

        if not player.is_playing:
            embed.title = "재생 중인 곡이 없습니다"
            return await ctx.respond(embed=embed, delete_after=1)

        track_time = player.position + (seconds * 1000)
        await player.seek(track_time)
        if seconds >= 0:
            embed.title = f"앞으로 {seconds}초 이동"
        else:
            embed.title = f"뒤로 {-seconds}초 이동"
        await ctx.respond(embed=embed, delete_after=1)


    @slash_command(name='반복', description="loop")
    async def loop_(self, ctx):
        await self.loop(ctx)

    @slash_command(name='loop', description="loop")
    async def loop(self, ctx):
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        embed = discord.Embed(color=0xf5a9a9)

        if not player.is_playing:
            embed.title = "재생 중인 곡이 없습니다"
            return await ctx.respond(embed=embed, delete_after=1)

        if player.loop == 0:
            player.set_loop(1)
            embed.title = f"{player.current.title}\n반복을 켭니다"
        elif player.loop == 1:
            player.set_loop(2)
            embed.title = "플레이리스트 전체 반복을 켭니다"
        elif player.loop == 2:
            player.set_loop(0)
            embed.title = "반복을 끕니다"
        await ctx.respond(embed=embed, delete_after=1)


    @slash_command(name='제거', description="remove")
    async def remove_(self, ctx, index: Option(int, "노래 번호 index")):
        await self.remove(ctx, index)

    @slash_command(name='remove', description="remove")
    async def remove(self, ctx, index: Option(int, "노래 번호 index")):
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        if not player.queue:
            embed = discord.Embed(color=0xf5a9a9)
            embed.title = "재생 목록이 비어있습니다"
            return await ctx.respond(embed=embed, delete_after=1)

        if index > len(player.queue) or index < 1:
            return await ctx.respond(f'1 부터 {len(player.queue)} 사이의 정수를 입력해주세요', delete_after=1)
        removed = player.queue.pop(index - 1)
        await ctx.respond(f'`제거:: {index}. {removed.title}`', delete_after=1)

        listembed = discord.Embed(color=0xf5a9a9)
        listembed.title = '재생 목록'
        if not player.queue:
            listembed.description = f'**지금 재생 중**: [{player.current.title}]({player.current.uri})\n\n**텅텅.**'
        else:
            page = 1
            tracks_per_page = 5
            pages = math.ceil(len(player.queue) / tracks_per_page) # queue 올림해서 페이지 수 계산
            start = (page - 1) * tracks_per_page
            end = start + tracks_per_page
            queue_list = ''
            for index, track in enumerate(player.queue[start:end], start=start+1):
                queue_list += f'**{index}**. [{track.title}]({track.uri})\n'
            listembed.description = f'**지금 재생 중**: [{player.current.title}]({player.current.uri})\n\n{queue_list}'
            listembed.set_footer(text=f"{page}/{pages} page")

        msg = await ctx.fetch_message(player.fetch('message_id'))
        await msg.edit(embeds=[listembed, msg.embeds[1]])
        player.store('page', 1)


    @slash_command(name='now_playing', description="now playing")
    async def now_playing(self, ctx):
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        embed = discord.Embed(color=0xf5a9a9)

        if not player.is_playing:
            embed.title = "재생 중인 곡이 없습니다"
            return await ctx.respond(embed=embed, delete_after=1)

        now_min = int(int(player.position)//60000)
        now_sec = int(int(player.position)/1000%60)
        duration_min = int(player.current.duration//60000)
        duration_sec = int(player.current.duration/1000%60)

        embed.title = '지금 재생 중'
        embed.description = f'[{player.current.title}]({player.current.uri}&t={now_min}m{now_sec}s)\n`[{now_min:02d}:{now_sec:02d}/{duration_min:02d}:{duration_sec:02d}`\n\nRequested by: <@{player.current.requester}>'
        embed.set_thumbnail(url=f'https://i.ytimg.com/vi/{player.current.identifier}/mqdefault.jpg')
        await ctx.respond(embed=embed, delete_after=5)


    @slash_command(name='큐', description="queue")
    async def queue_(self, ctx, page: Option(int, "페이지 번호 index", default=1)):
        await self.queue(ctx, page)

    @slash_command(name='queue', description="queue")
    async def queue(self, ctx, page: Option(int, "페이지 번호 index", default=1)):
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        embed = discord.Embed(color=0xf5a9a9)

        if not player.is_playing:
            embed.title = "재생 중인 곡이 없습니다"
            return await ctx.respond(embed=embed, delete_after=1)

        embed.title = '재생 목록'

        if not player.queue:
            embed.description = f'**지금 재생 중**: [{player.current.title}]({player.current.uri})\n\n**재생 목록이 비어있습니다**'
            return await ctx.respond(embed=embed, delete_after=3)

        tracks_per_page = 10
        pages = math.ceil(len(player.queue) / tracks_per_page) # queue 올림해서 페이지 수 계산
        if page > pages: # 최대 페이지 보다 더 큰 수 입력시 마지막 페이지 보여주기
            page = pages
        start = (page - 1) * tracks_per_page
        end = start + tracks_per_page
        queue_list = ''

        for index, track in enumerate(player.queue[start:end], start=start+1):
            queue_list += f'**{index}**. [{track.title}]({track.uri})\n'
        embed.description = f'**지금 재생 중**: [{player.current.title}]({player.current.uri})\n\n{queue_list}'
        embed.set_footer(text=f"{page}/{pages} page")
        await ctx.respond(embed=embed, delete_after=5)


    @slash_command(name="플레이리스트", description="플레이리스트")
    async def playlist_(self, ctx):
        await self.playlist(ctx)

    @slash_command(name="list", description="플레이리스트")
    async def playlist(self, ctx):
        select = discord.ui.Select(placeholder='플레이 리스트 선택', options=[discord.SelectOption(label=title) for title in playlist])
        async def callback(interaction):
            self.shuffle = True
            await self.play(ctx, playlist[select.values[0]])
            await interaction.response.edit_message(delete_after=0)

        select.callback = callback

        view=discord.ui.View()
        view.add_item(select)
        await ctx.respond('```플레이리스트는 자동으로 셔플됩니다.\n원하는 플레이리스트가 있으면 혁수s연구실 채널에 남겨주세요```', view=view)


    @slash_command(name='기록', description="노래 재생 기록")
    async def log_(self, ctx, limit: Option(int, "표시할 노래 개수", default=10)):
        await self.log(ctx, limit)

    @slash_command(name="log", description="노래 재생 기록")
    async def log(self, ctx, limit: Option(int, "표시할 노래 개수", default=10)):
        data = await get_data(ctx.guild.id, 'log')
        embed = discord.Embed(color=0xf5a9a9)
        embed.title = "📜 Music History"
        embed.description = ''
        for index, log in enumerate(data[:-limit-1:-1], start=1):
            embed.description += f'**{index}**. [{log["title"]}]({log["uri"]}) {log["requester"]} {log["date"]}\n'
        embed.set_footer(text="기록은 최근 10개만 출력됩니다. 더 많은 기록은 /기록 명령어를 사용해주세요.")
        await ctx.respond(embed=embed, delete_after=10)


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
        await ctx.respond('Bye', delete_after=1)


    @slash_command(name="updateview", description="노래 채널 View 수정")
    async def updateview(self, ctx):
        if await self.bot.is_owner(ctx.user):
            with open('cogs/data/music_channel.pickle', 'rb') as f:
                dict = pickle.load(f)
            for i in dict.values():
                try:
                    channel = await self.bot.fetch_channel(i['channel_id'])
                    msg = await channel.fetch_message(i['message_id'])
                    await msg.edit(view=MyView())
                except:
                    pass
            await ctx.respond('View 업데이트 완료', delete_after=1)
        else:
            await ctx.respond('사용할 수 없습니다', delete_after=1)


class MyView(View):
    def __init__(self):
        super().__init__(timeout=None)
    
    async def ensure_voice_chat(self, interaction):
        """ This check ensures that the bot and command author are in the same voicechannel. """
        # player = interaction.client.lavalink.player_manager.create(interaction.guild.id)
        
        if not interaction.user.voice or not interaction.user.voice.channel:
            await interaction.response.send_message('먼저 음성채널에 입장해주세요', delete_after=1)
            raise commands.CommandInvokeError('먼저 음성채널에 입장해주세요')

        v_client = interaction.guild.voice_client
        if not v_client: # 보이스 클라이언트가 없고
            await interaction.response.send_message('봇이 연결되어 있지 않습니다', delete_after=1)
            raise commands.CommandInvokeError('봇이 연결되어 있지 않습니다')
        else:
            if v_client.channel.id != interaction.user.voice.channel.id:
                await interaction.response.send_message('봇과 같은 음성채널에 있어야 합니다', delete_after=1)
                raise commands.CommandInvokeError('봇과 같은 음성채널에 있어야 합니다')

    @discord.ui.button(label="일시정지", emoji="⏯️", style=discord.ButtonStyle.secondary, custom_id="persistent_view:pause")
    async def pause(self, button:discord.ui.Button, interaction: discord.Interaction):
        await self.ensure_voice_chat(interaction)
        player = interaction.client.lavalink.player_manager.get(interaction.guild.id)
        embed = discord.Embed(color=0xf5a9a9)

        if not player or not player.is_playing:
            embed.title = "재생 중인 곡이 없습니다"
            return await interaction.response.send_message(embed=embed, delete_after=1)

        if player.paused:
            await player.set_pause(False)
            embed.title = '⏯ | 재생'
        else:
            await player.set_pause(True)
            embed.title = '⏯ | 일시정지'
        await interaction.response.send_message(embed=embed, delete_after=1)


    @discord.ui.button(label="다음 곡", emoji=discord.PartialEmoji.from_str('<:wakCut:1030483562765504592>'), style=discord.ButtonStyle.secondary, custom_id="persistent_view:skip")
    async def skip(self, button:discord.ui.Button, interaction: discord.Interaction):
        await self.ensure_voice_chat(interaction)
        player = interaction.client.lavalink.player_manager.get(interaction.guild.id)

        if not player or not player.is_playing:
            embed = discord.Embed(color=0xf5a9a9)
            embed.title = "재생 중인 곡이 없습니다"
            return await interaction.response.send_message(embed=embed, delete_after=1)

        title = player.current.title
        await player.skip()
        await interaction.response.send_message(f"`스킵:: {title}`", delete_after=1)


    @discord.ui.button(label="10초 뒤로", emoji="⏪", style=discord.ButtonStyle.secondary, custom_id="persistent_view:back")
    async def back(self, button:discord.ui.Button, interaction: discord.Interaction):
        await self.ensure_voice_chat(interaction)
        player = interaction.client.lavalink.player_manager.get(interaction.guild.id)
        embed = discord.Embed(color=0xf5a9a9)

        if not player or not player.is_playing:
            embed.title = "재생 중인 곡이 없습니다"
            return await interaction.response.send_message(embed=embed, delete_after=1)

        track_time = player.position - 10000
        await player.seek(track_time)

        embed.title = f"뒤로 10초 이동"
        await interaction.response.send_message(embed=embed, delete_after=1) 


    @discord.ui.button(label="10초 앞으로", emoji="⏩", style=discord.ButtonStyle.secondary, custom_id="persistent_view:forward")
    async def forward(self, button:discord.ui.Button, interaction: discord.Interaction):
        await self.ensure_voice_chat(interaction)
        player = interaction.client.lavalink.player_manager.get(interaction.guild.id)
        embed = discord.Embed(color=0xf5a9a9)

        if not player or not player.is_playing:
            embed.title = "재생 중인 곡이 없습니다"
            return await interaction.response.send_message(embed=embed, delete_after=1)

        track_time = player.position + 10000
        await player.seek(track_time)

        embed.title = f"앞으로 10초 이동"
        await interaction.response.send_message(embed=embed, delete_after=1) 


    @discord.ui.button(label="종료", style=discord.ButtonStyle.danger, custom_id="persistent_view:stop")        
    async def stop(self, button:discord.ui.Button, interaction: discord.Interaction):
        await self.ensure_voice_chat(interaction)
        player = interaction.client.lavalink.player_manager.get(interaction.guild.id)
        embed = discord.Embed(color=0xf5a9a9)

        if not player or not player.is_playing:
            embed.title = "플레이어 종료"
            await interaction.guild.voice_client.disconnect(force=True)
            return await interaction.response.send_message(embed=embed, delete_after=1)

        player.queue.clear()
        await player.stop()
        await interaction.guild.voice_client.disconnect(force=True)
        embed.title = "플레이어 종료"
        await interaction.response.send_message(embed=embed, delete_after=1)

        channel = await interaction.client.fetch_channel(player.fetch('channel_id'))
        msg = await channel.fetch_message(player.fetch('message_id'))
        listembed = await idleListEmbed()
        playerembed = await idlePlayerEmbed()
        await msg.edit(embeds=[listembed, playerembed])
    

    @discord.ui.button(label="이전 페이지", style=discord.ButtonStyle.secondary, custom_id="persistent_view:previous_page")
    async def previous(self, button:discord.ui.Button, interaction: discord.Interaction):
        await self.ensure_voice_chat(interaction)
        player = interaction.client.lavalink.player_manager.get(interaction.guild.id)

        if not player or not player.is_playing:
            embed = discord.Embed(color=0xf5a9a9)
            embed.title = "재생 중인 곡이 없습니다"
            return await interaction.response.send_message(embed=embed, delete_after=1)

        listembed = discord.Embed(color=0xf5a9a9)
        listembed.title = '재생 목록'
        page = player.fetch('page')
        tracks_per_page = 5
        pages = math.ceil(len(player.queue) / tracks_per_page) # queue 올림해서 페이지 수 계산
        if page == 1:
            embed = discord.Embed(color=0xf5a9a9)
            embed.title = '첫 페이지입니다'
            return await interaction.response.send_message(embed=embed, delete_after=1)
        page -= 1
        player.store('page', page)
        start = (page - 1) * tracks_per_page
        end = start + tracks_per_page
        queue_list = ''
        for index, track_ in enumerate(player.queue[start:end], start=start+1):
            queue_list += f'**{index}**. [{track_.title}]({track_.uri})\n'
        listembed.description = f'**지금 재생 중**: [{player.current.title}]({player.current.uri})\n\n{queue_list}'
        listembed.set_footer(text=f"{page}/{pages} page")

        channel = await interaction.client.fetch_channel(player.fetch('channel_id'))
        msg = await channel.fetch_message(player.fetch('message_id'))
        await msg.edit(embeds=[listembed, msg.embeds[1]])
        embed = discord.Embed(color=0xf5a9a9)
        embed.title = ('이전 페이지')
        await interaction.response.send_message(embed=embed, delete_after=0)

    @discord.ui.button(label="다음 페이지", style=discord.ButtonStyle.secondary, custom_id="persistent_view:next_page")
    async def next(self, button:discord.ui.Button, interaction: discord.Interaction):
        await self.ensure_voice_chat(interaction)
        player = interaction.client.lavalink.player_manager.get(interaction.guild.id)

        if not player or not player.is_playing:
            embed = discord.Embed(color=0xf5a9a9)
            embed.title = "재생 중인 곡이 없습니다"
            return await interaction.response.send_message(embed=embed, delete_after=1)

        listembed = discord.Embed(color=0xf5a9a9)
        listembed.title = '재생 목록'
        page = player.fetch('page')
        tracks_per_page = 5
        pages = math.ceil(len(player.queue) / tracks_per_page) # queue 올림해서 페이지 수 계산
        if page == pages: 
            embed = discord.Embed(color=0xf5a9a9)
            embed.title = '마지막 페이지입니다'
            return await interaction.response.send_message(embed=embed, delete_after=1)
        page += 1
        player.store('page', page)
        start = (page - 1) * tracks_per_page
        end = start + tracks_per_page
        queue_list = ''
        for index, track_ in enumerate(player.queue[start:end], start=start+1):
            queue_list += f'**{index}**. [{track_.title}]({track_.uri})\n'
        listembed.description = f'**지금 재생 중**: [{player.current.title}]({player.current.uri})\n\n{queue_list}'
        listembed.set_footer(text=f"{page}/{pages} page")
            
        channel = await interaction.client.fetch_channel(player.fetch('channel_id'))
        msg = await channel.fetch_message(player.fetch('message_id'))
        await msg.edit(embeds=[listembed, msg.embeds[1]])
        embed = discord.Embed(color=0xf5a9a9)
        embed.title = ('다음 페이지')
        await interaction.response.send_message(embed=embed, delete_after=0)


    @discord.ui.button(label="반복", emoji="🔁", style=discord.ButtonStyle.secondary, custom_id="persistent_view:loop")
    async def loop(self, button:discord.ui.Button, interaction: discord.Interaction):
        await self.ensure_voice_chat(interaction)
        player = interaction.client.lavalink.player_manager.get(interaction.guild.id)
        embed = discord.Embed(color=0xf5a9a9)

        if not player or not player.is_playing:
            embed.title = "재생 중인 곡이 없습니다"
            return await interaction.response.send_message(embed=embed, delete_after=1)

        if player.loop == 0:
            player.set_loop(1)
            embed.title = f"{player.current.title}\n반복을 켭니다"
        elif player.loop == 1:
            player.set_loop(2)
            embed.title = "플레이리스트 전체 반복을 켭니다"
        elif player.loop == 2:
            player.set_loop(0)
            embed.title = "반복을 끕니다"
        await interaction.response.send_message(embed=embed, delete_after=1)


    @discord.ui.button(label="플레이리스트 생성", style=discord.ButtonStyle.secondary, custom_id="persistent_view:make_playlist")
    async def make_playlist(self, button:discord.ui.Button, interaction: discord.Interaction):
        await self.ensure_voice_chat(interaction)
        player = interaction.client.lavalink.player_manager.get(interaction.guild.id)
        embed = discord.Embed(color=0xf5a9a9)

        if not player or not player.is_playing:
            embed.title = "재생 중인 곡이 없습니다"
            return await interaction.response.send_message(embed=embed, delete_after=1)

        embed.title = "플레이리스트를 생성 중입니다..."
        embed.description = f"<@310691116049629184> 유튜브 뮤직 기준이므로 이세돌이 있을 수 있음 🤪"
        await interaction.response.send_message(embed=embed, delete_after=1)

        title = player.current.title

        ytmusic = YTMusic('cogs/data/headers_auth.json')
        search_results = ytmusic.search(query=title)
        playlist = ytmusic.get_watch_playlist(videoId=search_results[0]['videoId'])['tracks']

        li = [ i['videoId'] for i in playlist[1:] ]

        playlistId = ytmusic.create_playlist(title=f"{title} - 관련 트랙", description="tmp playlist for sulyrics", privacy_status='PUBLIC', video_ids=li)
        
        url = f"https://www.youtube.com/playlist?list={playlistId}"
        results = await player.node.get_tracks(url)
        tracks = results.tracks
        first = tracks[0]

        for track in tracks:
            player.add(requester=interaction.user.id, track=track)
        
        embed.title = '플레이리스트 추가'
        embed.description = f'[{results.playlist_info.name}]({url}) - {len(tracks)} tracks'
        embed.set_thumbnail(url=f'https://i.ytimg.com/vi/{first.identifier}/maxresdefault.jpg')
        await interaction.channel.send(embed=embed, delete_after=1)            

        listembed = discord.Embed(color=0xf5a9a9)
        listembed.title = '재생 목록'
        page = 1
        tracks_per_page = 5
        pages = math.ceil(len(player.queue) / tracks_per_page) # queue 올림해서 페이지 수 계산
        start = (page - 1) * tracks_per_page
        end = start + tracks_per_page
        queue_list = ''
        for index, track_ in enumerate(player.queue[start:end], start=start+1):
            queue_list += f'**{index}**. [{track_.title}]({track_.uri})\n'
        listembed.description = f'**지금 재생 중**: [{player.current.title}]({player.current.uri})\n\n{queue_list}'
        listembed.set_footer(text=f"{page}/{pages} page")

        channel = await interaction.client.fetch_channel(player.fetch('channel_id'))
        msg = await channel.fetch_message(player.fetch('message_id'))
        await msg.edit(embeds=[listembed, msg.embeds[1]])
        player.store('page', 1)

        ytmusic.delete_playlist(playlistId)


    @discord.ui.button(label="로그", emoji="📜", style=discord.ButtonStyle.secondary, custom_id="persistent_view:log")
    async def log(self, button:discord.ui.Button, interaction: discord.Interaction):
        data = await get_data(interaction.guild.id, 'log')
        embed = discord.Embed(color=0xf5a9a9)
        embed.title = "📜 Music History"
        embed.description = ''
        for index, log in enumerate(data[:-11:-1], start=1):
            embed.description += f'**{index}**. [{log["title"]}]({log["uri"]}) {log["requester"]} {log["date"]}\n'
        embed.set_footer(text="기록은 최근 10개만 출력됩니다. 더 많은 기록은 /기록 명령어를 사용해주세요.")
        await interaction.response.send_message(embed=embed, delete_after=10)


def setup(bot):
    bot.add_cog(Music(bot))