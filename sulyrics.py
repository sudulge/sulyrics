# with pycord

import discord
from discord.ext import commands
from discord.commands import Option
from datetime import datetime
from pytz import timezone
from neispy import Neispy
import webbrowser
import time
import random
import pickle
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

def NBstart():
    HRnumber = list(map(str, random.sample(range(0, 9), 4)))
    tries = []
    tries_list = ''
    return HRnumber, tries, tries_list

def checkInput(input, tries):
    if len(input) != 4:
        return "4자리 수를 입력해 주세요"
    if len(set(input)) != 4:
        return "중복되지 않게 입력해 주세요"
    if input in tries:
        return "이미 시도한 숫자입니다."

    return True

def NBhit(HRnumber, input, tries, tries_list, ctx):
    valid = checkInput(input, tries)
    
    if type(valid)==str:
        return valid, ''
    
    tries.append(input)
    strike = 0
    ball = 0

    for index, number in enumerate(input):
        if number == HRnumber[index]:
            strike += 1
        elif number in HRnumber:
            ball += 1

    if strike == 4:
        result = f"홈런! {len(tries)}회 만에 맞추셨습니다"
        NBsolecheck(tries, tries_list, ctx)
        NBend()
    elif strike == 0 and ball == 0:
        result = "아웃"
    else:
        result = f"{input}: {strike}S {ball}B"
        
    return result, f"{input}: {strike}S {ball}B ⠀({ctx.author.display_name})\n"

def NBsolecheck(tries, tries_list, ctx):  # 마지막으로 입력한 사람이 혼자 했는지 체크 
    author = ctx.author.display_name
    if tries_list.count(author) == len(tries)-1:
        NBaddhistory(tries, ctx)
    return

def NBaddhistory(tries, ctx):
    with open("data/NBhistory.pickle", "rb") as f: # 깃허브에 올릴때는 sulyrics/ 빼기
        history = pickle.load(f)

    for dic in history: # 있던 사람
        if ctx.author.id in dic.values():
            if len(tries) in dic['로그']:
                dic['로그'][len(tries)] += 1
            else:
                dic['로그'][len(tries)] = 1
            dic['로그'] = dict(sorted(dic['로그'].items()))
            with open("data/NBhistory.pickle", "wb") as f:
                pickle.dump(history, f)
            return

    history.append({"id": ctx.author.id, "이름": ctx.author.name, "서버닉네임": ctx.author.display_name, "로그": {len(tries): 1}}) # 새로운 사람
    with open("data/NBhistory.pickle", "wb") as f:
        pickle.dump(history, f)
    return

def NBshowhistory(ctx):
    with open("data/NBhistory.pickle", "rb") as f:
        history = pickle.load(f)
    
    for dic in history:
        if ctx.author.id in dic.values():
            history = ''
            for key, value in dic['로그'].items():
                history += (f"{key}회:".ljust(4) + f" {value:2d}번\n")
            return history

    return False

def NBend():
    global HRnumber, tries
    del HRnumber, tries





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
    user = await bot.fetch_user(ctx.author.id)
    embed = discord.Embed(title="", color=user.accent_color)
    embed.add_field(name="이름", value=ctx.author.name, inline=True)
    embed.add_field(name="서버닉네임", value=ctx.author.display_name, inline=True)
    embed.add_field(name="가입일", value=str(date.year) + "년" + str(date.month) + "월" + str(date.day) + "일", inline=True)
    embed.add_field(name="아이디", value=ctx.author.id, inline=True)
    embed.set_thumbnail(url=ctx.author.display_avatar)
    await ctx.respond(embed=embed)

@bot.slash_command(name="삭제", guild_ids=[723892698435551324], description="메시지 삭제")
async def deleteMessage(ctx, limit: Option(int, "지울 개수 입력")):
    await ctx.channel.purge(limit=limit, check=lambda msg: not msg.pinned)


@bot.slash_command(name="고정", guild_ids=[723892698435551324], description="메시지 고정")
async def pinMessage(ctx, message_id: Option(str, "메시지 아이디 입력")):
    message = await ctx.fetch_message(int(message_id))
    await message.pin()

@bot.slash_command(name="구글", guild_ids=[723892698435551324], description="구글 검색")
async def googlesearch(ctx, query: Option(str, "검색 내용 입력")):
    await ctx.respond(f'https://www.google.co.kr/search?q={query.strip().replace(" ", "%20")}')

@bot.slash_command(name="브라우저열기", guild_ids=[723892698435551324], description="구글 검색")
async def googlesearch(ctx,):
    url = "https://www.google.co.kr/"
    webbrowser.open(url)

@bot.slash_command(name="오늘의라인", guild_ids=[723892698435551324], description="롤 라인 뽑기")
async def lolLane(ctx):
    lane = ["탑","미드","원딜","서폿","정글"]
    await ctx.respond(f"오늘의 라인은`{lane[random.randint(0, 4)]}`", ephemeral=True)

@bot.slash_command(name="급식", guild_ids=[723892698435551324], description="급식")
async def lunch(ctx, school: Option(str, "학교 이름 입력")):
    today = str(datetime.now(timezone('Asia/Seoul')))[:10].replace('-', '')
    neis_key = os.environ["NEIS_API_KEY"]

    async with Neispy(KEY=neis_key) as neis:
        try:
            scinfo = await neis.schoolInfo(SCHUL_NM=school)
            AE = scinfo[0].ATPT_OFCDC_SC_CODE
            SE = scinfo[0].SD_SCHUL_CODE
            SCHUL_NM = scinfo[0].SCHUL_NM

        except:
            await ctx.respond("학교를 찾을 수 없습니다")

        else:
            try:
                scmeal = await neis.mealServiceDietInfo(AE, SE, MLSV_YMD=f"{today}")
                meal = scmeal[0].DDISH_NM.replace("<br/>", "\n")

                replacelist = '01234567890./'

                for i in replacelist:
                    meal = meal.replace(i, '')
                lunchlist = meal

            except:
                lunchlist = '오늘의 점심은?'  # 오류 방지용 문구

            embed = discord.Embed(title=f"{SCHUL_NM} {today[4:6]}월 {today[6:8]}일 중식", color=0xf5a9a9)
            embed.add_field(name="​", value=f"{lunchlist}", inline=False)
            embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/769489028357160990.png?v=1")
            await ctx.respond(embed=embed)


@bot.slash_command(name="로또", guild_ids=[723892698435551324], description="로또")
async def lotto(ctx):
    myNumber, count, bonus = automatic(mainNumber, bonusNumber)
    ranking = rank(count, bonus)

    embed = discord.Embed(title="수리릭 로또", color=0xf5a9a9)
    embed.add_field(name="내 번호", value=f"{myNumber}", inline=False)
    embed.add_field(name="등수", value=f"{ranking}", inline=False)
    embed.set_footer(text="당첨 번호는 매일 바뀝니다")
    await ctx.respond(embed=embed)


@bot.slash_command(name="숫자야구", guild_ids=[723892698435551324], description="숫자야구")
async def numBaseball(ctx, choice: Option(str, "숫자야구", choices=["시작", "기록", "도움말"])):
    if choice == "시작":
        global HRnumber, tries, tries_list
        HRnumber, tries, tries_list = NBstart()
        print(HRnumber)
        await ctx.respond("`숫자를 초기화했습니다.\n/야 명령어를 통해 숫자를 입력해 주세요.`")
    elif choice == "기록":
        history = NBshowhistory(ctx)
        NBembed = discord.Embed(color=0xf5a9a9)
        NBembed.title = f"{ctx.author.display_name}"
        NBembed.description = "================================="
        if history:
            NBembed.add_field(name="기록", value=f"```{history}```")
        else:
            NBembed.add_field(name="기록", value=f"숫자야구 플레이 기록이 없습니다.")
        await ctx.respond(embed=NBembed)
    elif choice == "도움말":
        NBembed = discord.Embed(color=0xf5a9a9)
        NBembed.title = "숫자야구"
        NBembed.description = "================================="
        NBembed.add_field(name="규칙", value=
        "0~9 사이의 중복되지 않는 네자리 수\n\
        숫자는 맞지만 위치가 틀렸을 경우 '볼'\n\
        숫자와 위치가 모두 맞았을 경우 '스트라이크'\n\
        맞는 숫자가 한 개도 없을 경우 '아웃'\n")
        await ctx.respond(embed=NBembed)


@bot.slash_command(name="야", guild_ids=[723892698435551324], description="숫자야구")
async def numBaseballInput(ctx, input: Option(str, "숫자 입력")):
    try:
        global tries_list, msg
        result, log = NBhit(HRnumber, input, tries, tries_list, ctx)
        tries_list += log
        NBembed = discord.Embed(color=0xf5a9a9)
        NBembed.title = result
        NBembed.description = "=========================="
        NBembed.add_field(name="로그", value=f"```{tries_list}```")
        try:
            await msg.delete_original_message()
        finally:
            msg = await ctx.respond(embed=NBembed)
            print(tries_list)
    except NameError as e:
        if 'msg' in str(e): # 처음 시작 하면 msg가 없음
            pass
        else:
            await ctx.respond("`/숫자야구 명령어를 통해 숫자를 초기화 해주세요.`")


@bot.slash_command(name="help", guild_ids=[723892698435551324], description="수리릭 도움말")
async def help(ctx):
    Hembed = discord.Embed(color=0xf5a9a9)
    Hembed.title = "수리릭"
    Hembed.set_thumbnail(url="https://cdn.discordapp.com/attachments/731547490347909120/941329421552467998/c39add417a556179.png")
    Hembed.add_field(name="명령어 리스트", value="`정보` `자기소개` \n `삭제` `고정` \n `급식` `로또` `숫자야구` `오늘의라인` `구글`")
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


bot_token = os.environ["BOT_TOKEN"]
bot.run(bot_token)
