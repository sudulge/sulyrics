# with pycord

import discord
from discord.ext import commands
from discord.commands import Option
from datetime import datetime
# from pytz import timezone
# from neispy import Neispy
import time
import random
import os
import re

bot = commands.Bot()

url_rx = re.compile(r'https?://(?:www\.)?.+')

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


@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    game = discord.Game("/help")
    await bot.change_presence(status = discord.Status.online, activity=game)
    await bot.get_channel(731547490347909120).send("이 몸 등 장 !")  # 아잉방 연구실
    # await bot.get_channel(896418649244573717).send("이 몸 등 장 !")  # 놀이터


@bot.slash_command(guild_ids=[723892698435551324], description="check bot's response latency")
async def ping(ctx):
    embed = discord.Embed(title="Pong!", description=f"Delay: {bot.latency} seconds", color=0xf5a9a9)
    await ctx.respond(embed=embed)


# @bot.slash_command(name="으악이유튜브", guild_ids=[723892698435551324], description="영찬이 유튜브")
# async def _0chanYoutube(ctx):
#     embed = discord.Embed(title="게임채널으악이", description="https://www.youtube.com/channel/UC3I4Uf6SMxyQH81B2YLls8g", color=0xf5a9a9)
#     await ctx.respond(embed=embed)


@bot.slash_command(name="정보", guild_ids=[723892698435551324], description="수리릭 정보")
async def sulyricsInfo(ctx):
    embed = discord.Embed(title="Sulyrics", color=0xf5a9a9)
    embed.add_field(name="이름", value="수리릭", inline=True)
    embed.add_field(name="서버닉네임", value="sulyrics", inline=True)
    embed.add_field(name="생일", value="2020년 7월 12일", inline=True)
    embed.add_field(name="아이디", value="731538324170342461", inline=True)
    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/731547490347909120/941329421552467998/c39add417a556179.png")
    await ctx.respond(embed=embed)


@bot.slash_command(name="자기소개", guild_ids=[723892698435551324], description="사용자 정보")
async def userInfo(ctx):
    date = datetime.utcfromtimestamp(((int(ctx.author.id) >> 22) + 1420070400000) / 1000)
    embed = discord.Embed(title="", color=0xf5a9a9)
    embed.add_field(name="이름", value=ctx.author.name, inline=True)
    embed.add_field(name="서버닉네임", value=ctx.author.display_name, inline=True)
    embed.add_field(name="가입일", value=str(date.year) + "년" + str(date.month) + "월" + str(date.day) + "일", inline=True)
    embed.add_field(name="아이디", value=ctx.author.id, inline=True)
    embed.set_thumbnail(url=ctx.author.display_avatar)
    await ctx.respond(embed=embed)


@bot.slash_command(name="오늘의라인", guild_ids=[723892698435551324], description="롤 라인 뽑기")
async def lolLane(ctx):
    lane = ["탑","미드","원딜","서폿","정글"]
    await ctx.respond(f"오늘의 라인은`{lane[random.randint(0, 4)]}`", ephemeral=True)


@bot.slash_command(name="삭제", guild_ids=[723892698435551324], description="메시지 삭제")
async def deleteMessage(ctx, limit: Option(int, "지울 개수 입력")):
    await ctx.channel.purge(limit=limit, check=lambda msg: not msg.pinned)


@bot.slash_command(name="고정", guild_ids=[723892698435551324], description="메시지 고정")
async def pinMessage(ctx, message_id: Option(str, "메시지 아이디 입력")):
    message = await ctx.fetch_message(int(message_id))
    await message.pin()


# @bot.slash_command(name="급식", guild_ids=[723892698435551324], description="급식")
# async def lunch(ctx, school: Option(str, "학교 이름 입력")):
#     today = str(datetime.now(timezone('Asia/Seoul')))[:10].replace('-', '')
#     neis_key = os.environ["NEIS_API_KEY"]
#
#     async with Neispy(KEY=neis_key) as neis:
#         try:
#             scinfo = await neis.schoolInfo(SCHUL_NM=school)
#             AE = scinfo[0].ATPT_OFCDC_SC_CODE
#             SE = scinfo[0].SD_SCHUL_CODE
#             SCHUL_NM = scinfo[0].SCHUL_NM
#
#         except:
#             await ctx.respond("학교를 찾을 수 없습니다")
#
#         else:
#             try:
#                 scmeal = await neis.mealServiceDietInfo(AE, SE, MLSV_YMD=f"{today}")
#                 meal = scmeal[0].DDISH_NM.replace("<br/>", "\n")
#
#                 replacelist = '01234567890./'
#
#                 for i in replacelist:
#                     meal = meal.replace(i, '')
#                 lunchlist = meal
#
#             except:
#                 lunchlist = '오늘의 점심은?'  # 오류 방지용 문구
#
#             embed = discord.Embed(title=f"{SCHUL_NM} {today[4:6]}월 {today[6:8]}일 중식", color=0xf5a9a9)
#             embed.add_field(name="​", value=f"{lunchlist}", inline=False)
#             embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/769489028357160990.png?v=1")
#             await ctx.respond(embed=embed)

@bot.slash_command(name="로또", guild_ids=[723892698435551324], description="로또")
async def lotto(ctx):
    myNumber, count, bonus = automatic(mainNumber, bonusNumber)
    ranking = rank(count, bonus)

    embed = discord.Embed(title="수리릭 로또", color=0xf5a9a9)
    embed.add_field(name="내 번호", value=f"{myNumber}", inline=False)
    embed.add_field(name="등수", value=f"{ranking}", inline=False)
    embed.set_footer(text="당첨 번호는 매일 바뀝니다")
    await ctx.respond(embed=embed)

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


bot_token = os.environ["BOT_TOKEN"]
bot.run(bot_token)
