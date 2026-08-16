from discord import (
    AllowedMentions,
    ApplicationContext,
    Bot,
    ButtonStyle,
    Color,
    File,
    Interaction,
    SeparatorSpacingSize,
    User,
    PartialEmoji,
    UnfurledMediaItem,
    Message
)

from discord.ui import (
    ActionRow,
    Button,
    Container,
    DesignerView,
    MediaGallery,
    Section,
    Select,
    Separator,
    TextDisplay,
    Thumbnail,
    button,
)

from lavalink import LoadType, LoadResult


from .spotify import sulyrics_spotify
from .db import get_data, add_new_guild


class MusicView(DesignerView):
    def __init__(self, pause_callback, skip_callback, loop_callback, stop_callback):
        super().__init__(timeout=None)

        listcontainer = Container()
        playercontainer = Container()
        
        pause_btn = Button(label="일시정지", emoji="⏯️", style=ButtonStyle.secondary, custom_id="persistent_view:pause")
        skip_btn = Button(label="다음 곡", emoji=PartialEmoji.from_str('<:wakCut:1030483562765504592>'), style=ButtonStyle.secondary, custom_id="persistent_view:skip")
        loop_btn = Button(label="반복", emoji="🔁", style=ButtonStyle.secondary, custom_id="persistent_view:loop")
        stop_btn = Button(label="종료", style=ButtonStyle.danger, custom_id="persistent_view:stop")
        pause_btn.callback = pause_callback
        skip_btn.callback = skip_callback
        loop_btn.callback = loop_callback
        stop_btn.callback = stop_callback

        self.actionrow = ActionRow(pause_btn, skip_btn, loop_btn, stop_btn)

        self.add_item(listcontainer)
        self.add_item(playercontainer)
        self.add_item(self.actionrow)

    def rebuild_view(self, listcontainer, playercontainer):
        self.clear_items()
        self.add_item(listcontainer)
        self.add_item(playercontainer)
        self.add_item(self.actionrow)


class ViewManager:
    def __init__(self, bot, pause_callback, skip_callback, loop_callback, stop_callback):
        self.bot = bot
        self.musicview = None
        self.pause_callback = pause_callback
        self.skip_callback = skip_callback
        self.loop_callback = loop_callback
        self.stop_callback = stop_callback

    def get_musicview(self):
        if self.musicview is None:
            self.musicview = MusicView(self.pause_callback, self.skip_callback, self.loop_callback, self.stop_callback)
        return self.musicview

    async def make_container(
        self,
        title: str | None = None,
        items: list | None = None,
        image: str | None = None
        ):
        
        container = Container()
        container.add_item(TextDisplay(title))
        for item in items:
            container.add_item(TextDisplay(item))
        if image:
            container.add_item(MediaGallery().add_item(image))
        container.color = 0xf5a9a9

        return container

    async def addTrackView(self, results: LoadResult, query=None):
        if results.load_type == LoadType.PLAYLIST:
            section = Section(TextDisplay("### 플레이리스트 추가"), TextDisplay(f"### [{results.playlist_info.name}]({query}) - {len(results.tracks)} tracks"))
        else:
            duration_min = int(results.tracks[0].duration//60000)
            duration_sec = int(results.tracks[0].duration/1000%60)
            section = Section(TextDisplay("### 노래 추가"), TextDisplay(f"### [{results.tracks[0].title}]({results.tracks[0].uri})"), TextDisplay(f"`00:00 / {duration_min:02d}:{duration_sec:02d}`"))

        view = DesignerView(Container(section.set_thumbnail(f"https://i.ytimg.com/vi/{results.tracks[0].identifier}/maxresdefault.jpg?"), color=0xf5a9a9))

        return view

        
    async def idlePlayerContainer(self):
        return await self.make_container("### 수리릭 노래봇", ["이 채널에서는 커맨드를 사용하지 않아도 노래를 틀 수 있습니다\n`/list` 커맨드로 플레이리스트를 고를 수 있습니다\n모든 커맨드는 다른 채널에서도 사용 가능 합니다"], "https://cdn.discordapp.com/attachments/1033149773504593921/1033712101354651678/main.png?")
    
    async def idleListContainer(self):
        return await self.make_container("### 재생목록", ["**텅텅.**"])

    async def playerContainer(self, player):
        duration_min = int(player.current.duration//60000)
        duration_sec = int(player.current.duration/1000%60)
        thumbnail_url = f"https://wsrv.nl/?url=https://i.ytimg.com/vi/{player.current.identifier}/maxresdefault.jpg&w=400&h=225"
        if len(player.current.identifier) > 15: # 15보다 길면 스포티파이 identifier, 스포티파이 썸네일 못가져와서 유튜브꺼 가져오기..
            try:
                sp = sulyrics_spotify()
                youtube_query = await sp.get_query_from_spotify(player.current.identifier)
                results = await player.node.get_tracks(youtube_query)
                track = results.tracks[0]
                thumbnail_url = f"https://wsrv.nl/?url=https://i.ytimg.com/vi/{track.identifier}/maxresdefault.jpg&w=400&h=225"
            except:
                pass

        content = [
            f"### [{player.current.title}]({player.current.uri})\n"
            f"`[00:00/{duration_min:02d}:{duration_sec:02d}]`\n\n"
            f"Requested by: <@{player.current.requester}>"
        ]

        return await self.make_container("### 지금 재생 중", content, thumbnail_url)
    
    async def listContainer(self, player):
        if not player.queue:
            return await self.idleListContainer()
        
        pages = ((len(player.queue)-1) // 5) + 1
        queue_list = ""
        for index, track in enumerate(player.queue[0:5]):
            queue_list += f"**{index+1}**. [{track.title}]({track.uri})\n"
        
        return await self.make_container("### 재생목록", [queue_list, f"-# 1/{pages} page"])

    async def updateContainer(self, player):
        if player.is_playing:
            listcontainer = await self.listContainer(player)
            playercontainer = await self.playerContainer(player)

        else:
            listcontainer = await self.idleListContainer()
            playercontainer = await self.idlePlayerContainer()

        view = self.get_musicview()
        view.rebuild_view(listcontainer, playercontainer)
        
        channel =  await self.bot.fetch_channel(player.fetch('channel_id'))
        msg = await channel.fetch_message(player.fetch('message_id'))
        await msg.edit(view=view, allowed_mentions=AllowedMentions.none())

    
    async def setting(self, ctx):
        channel = await ctx.guild.create_text_channel(name="노래채널_수리릭", topic="수리릭 노래 채널입니다. 버그있거나 추가하고 싶은 플레이리스트 있으면 말해주삼")
        view = self.get_musicview()
        view.rebuild_view(await self.idleListContainer(), await self.idlePlayerContainer())
        message = await channel.send(view=view)
        add_new_guild(ctx.guild.id, ctx.guild.name, channel.id, message.id)
        await ctx.respond("노래 채널 추가 완료 \n채널 알림은 꺼놓는 것을 추천합니다")

    async def reloadview(self, ctx):
        data = get_data(f"SELECT ChannelID, MessageID FROM MUSIC WHERE GuildID = {ctx.guild.id}")
        channel = await self.bot.fetch_channel(data[0][0])
        msg = await channel.fetch_message(data[0][1])
        view = self.get_musicview()
        view.rebuild_view(await self.idleListContainer(), await self.idlePlayerContainer())
        await msg.edit(view=view)
        await ctx.respond("view 업데이트 완료")
