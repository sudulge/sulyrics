import discord
from discord.ext import commands
from discord.commands import slash_command, Option
from datetime import datetime
import random
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from config import guild_ids


def lotto():
    lottoNumber = random.sample(range(1, 46), 7)
    mainNumber = lottoNumber[0:6]
    bonusNumber = lottoNumber[6]
    mainNumber.sort()
    return mainNumber, bonusNumber


def automatic(mainNumber, bonusNumber):
    myNumber = random.sample(range(1, 46), 6)
    myNumber.sort()
    count = 0
    bonus = False

    for i in myNumber:
        if i in mainNumber:
            count += 1
    if bonusNumber in myNumber:
        bonus = True

    return myNumber, count, bonus


def rank(count, bonus):
    if count == 6:
        ranking = 1
    elif count == 5:
        if bonus:
            ranking = 2
        else:
            ranking = 3
    elif count == 4:
        ranking = 4
    elif count == 3:
        ranking = 5
    else:
        ranking = "꽝"

    return ranking

mainNumber, bonusNumber = lotto()


class Others(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(guild_ids=guild_ids, description="check bot's response latency")
    async def ping(self, ctx):
        embed = discord.Embed(title="Pong!", description=f"Delay: {self.bot.latency} seconds", color=0xf5a9a9)
        await ctx.respond(embed=embed)


    @slash_command(name="정보", guild_ids=guild_ids, description="수리릭 정보")
    async def sulyricsInfo(self, ctx):
        embed = discord.Embed(title="Sulyrics", color=0xf5a9a9)
        embed.add_field(name="이름", value="수리릭", inline=True)
        embed.add_field(name="서버닉네임", value="sulyrics", inline=True)
        embed.add_field(name="생일", value="2020년 7월 12일", inline=True)
        embed.add_field(name="아이디", value="731538324170342461", inline=True)
        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/731547490347909120/941329421552467998/c39add417a556179.png")
        await ctx.respond(embed=embed)


    @slash_command(name="자기소개", guild_ids=guild_ids, description="사용자 정보")
    async def userInfo(self, ctx):
        date = datetime.utcfromtimestamp(((int(ctx.author.id) >> 22) + 1420070400000) / 1000)
        user = await self.bot.fetch_user(ctx.author.id)
        embed = discord.Embed(title="", color=user.accent_color)
        embed.add_field(name="이름", value=ctx.author.name, inline=True)
        embed.add_field(name="서버닉네임", value=ctx.author.display_name, inline=True)
        embed.add_field(name="가입일", value=str(date.year) + "년" + str(date.month) + "월" + str(date.day) + "일", inline=True)
        embed.add_field(name="아이디", value=ctx.author.id, inline=True)
        embed.set_thumbnail(url=ctx.author.display_avatar)
        await ctx.respond(embed=embed)


    @slash_command(name="삭제", guild_ids=guild_ids, description="메시지 삭제")
    async def deleteMessage(self, ctx, limit: Option(int, "지울 개수 입력")):
        await ctx.channel.purge(limit=limit, check=lambda msg: not msg.pinned)


    @slash_command(name="고정", guild_ids=guild_ids, description="메시지 고정")
    async def pinMessage(self, ctx, message_id: Option(str, "메시지 아이디 입력")):
        message = await ctx.fetch_message(int(message_id))
        await message.pin()


    @slash_command(name="구글", guild_ids=guild_ids, description="구글 검색")
    async def googlesearch(self, ctx, query: Option(str, "검색 내용 입력")):
        await ctx.respond(f'https://www.google.co.kr/search?q={query.strip().replace(" ", "%20")}')


    @slash_command(name="오늘의라인", guild_ids=guild_ids, description="롤 라인 뽑기")
    async def lolLane(self, ctx):
        lane = ["탑","미드","원딜","서폿","정글"]
        await ctx.respond(f"오늘의 라인은`{lane[random.randint(0, 4)]}`", ephemeral=True)


    @slash_command(name="로또", guild_ids=guild_ids, description="로또")
    async def lotto(self, ctx):
        myNumber, count, bonus = automatic(mainNumber, bonusNumber)
        ranking = rank(count, bonus)


        embed = discord.Embed(title="수리릭 로또", color=0xf5a9a9)
        embed.add_field(name="내 번호", value=f"{myNumber}", inline=False)
        embed.add_field(name="등수", value=f"{ranking}", inline=False)
        embed.set_footer(text="당첨 번호는 매일 바뀝니다")
        await ctx.respond(embed=embed)


    @slash_command(name="help", guild_ids=guild_ids, description="수리릭 도움말")
    async def help(self, ctx):
        Hembed = discord.Embed(color=0xf5a9a9)
        Hembed.title = "수리릭 명령어"
        Hembed.set_thumbnail(url="https://cdn.discordapp.com/attachments/731547490347909120/941329421552467998/c39add417a556179.png")
        Hembed.add_field(name="정보", value="`정보` `자기소개`", inline=False)
        Hembed.add_field(name="채팅", value="`삭제` `고정`", inline=False)
        Hembed.add_field(name="음악", value="`play` `list` `skip` `stop` `now_playing` `queue` `seek` `pause` `repeat` `remove`", inline=False)
        Hembed.add_field(name="기타", value="`알람` `급식` `로또` `숫자야구` `야` `오늘의라인` `구글`", inline=False)
        await ctx.respond(embed=Hembed)

    #
    # @bot.slash_command(name="", guild_ids=[723892698435551324], description="")
    # ephemeral = True


    # @bot.slash_command(guild_ids=[723892698435551324], description="hello world 출력")
    # async def helloworld(ctx):
    #     await ctx.respond("hello world")
    #
    #
    # @bot.slash_command(guild_ids=[723892698435551324], description="입력한 문자열 반환")
    # async def option(ctx,
    #                  text: Option(str, "문자열 입력하기"),
    #                  ):
    #     await ctx.respond(f"입력된 문자열: {text}")
    #
    #
    # @bot.slash_command(guild_ids=[723892698435551324], description="옵션 선택하기")
    # async def choice(ctx,
    #                  text: Option(str, "다음 중 고르세요.", choices=["하나", "둘", "셋"]),
    #                  ):
    #     await ctx.respond(f"선택된 문자열: {text}")
    #
    #
    # @bot.slash_command(guild_ids=[723892698435551324], description="hello world 출력하고 수정하기")
    # async def edit(ctx):
    #     respondMessage = await ctx.respond("hello world!")
    #     time.sleep(0.5)
    #     await respondMessage.edit_original_message(content = "hello korea")
    #
    #
    # @bot.slash_command(guild_ids=[723892698435551324], description="나만 보이는 메시지")
    # async def private(ctx):
    #     await ctx.respond("private message", ephemeral=True)
    #
    #
    # @bot.slash_command(guild_ids=[723892698435551324], description="버튼을 표시합니다.")
    # async def button(ctx):
    #     class Button(discord.ui.View):
    #             @discord.ui.button(label="primary", style=discord.ButtonStyle.primary)
    #             async def primary(self, button: discord.ui.Button, interaction: discord.Interaction):
    #                 await ctx.respond(f"<@!{interaction.user.id}> 님이 primary 버튼을 눌렀어요!")
    #
    #             @discord.ui.button(label="green", style=discord.ButtonStyle.green)
    #             async def green(self, button: discord.ui.Button, interaction: discord.Interaction):
    #                 await ctx.respond(f"<@!{interaction.user.id}> 님이 green 버튼을 눌렀어요!")
    #
    #             @discord.ui.button(label="gray", style=discord.ButtonStyle.gray)
    #             async def gray(self, button: discord.ui.Button, interaction: discord.Interaction):
    #                 await ctx.respond(f"<@!{interaction.user.id}> 님이 gray 버튼을 눌렀어요!")
    #
    #     await ctx.respond("버튼을 누르세요.", view=Button())

def setup(bot):
    bot.add_cog(Others(bot))
