import discord
from discord.ext import commands
from discord.commands import slash_command, Option
import random
import pickle
import re


num_rx = re.compile('^[0-9]{4}')

def NBstart():
    HRnumber = list(map(str, random.sample(range(0, 9), 4)))
    tries = []
    tries_list = ''
    return HRnumber, tries, tries_list


def checkInput(input, tries):
    if not num_rx.match(input):
        return "네 자리 정수를 입력해 주세요"
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
    with open("cogs/data/NBhistory.pickle", "rb") as f: # 깃허브에 올릴때는 sulyrics/ 빼기
        history = pickle.load(f)

    for dic in history: # 있던 사람
        if ctx.author.id in dic.values():
            if len(tries) in dic['로그']:
                dic['로그'][len(tries)] += 1
            else:
                dic['로그'][len(tries)] = 1
            dic['로그'] = dict(sorted(dic['로그'].items()))
            with open("cogs/data/NBhistory.pickle", "wb") as f:
                pickle.dump(history, f)
            return

    history.append({"id": ctx.author.id, "이름": ctx.author.name, "서버닉네임": ctx.author.display_name, "로그": {len(tries): 1}}) # 새로운 사람
    with open("cogs/data/NBhistory.pickle", "wb") as f:
        pickle.dump(history, f)
    return


def NBshowhistory(ctx):
    with open("cogs/data/NBhistory.pickle", "rb") as f:
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

class NBbaseball(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(name="숫자야구", guild_ids=[723892698435551324, 896398625163345931], description="숫자야구")
    async def numBaseball(self, ctx, choice: Option(str, "숫자야구", choices=["시작", "기록", "도움말"])):
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


    @slash_command(name="야", guild_ids=[723892698435551324, 896398625163345931], description="숫자야구")
    async def numBaseballInput(self, ctx, input: Option(int, "네자리 숫자 입력")):
        try:
            global tries_list, msg
            result, log = NBhit(HRnumber, str(input), tries, tries_list, ctx)
            tries_list += log
            NBembed = discord.Embed(color=0xf5a9a9)
            NBembed.title = result
            NBembed.description = "=========================="
            NBembed.add_field(name="로그", value=f"```{tries_list}```")
            try:
                await msg.delete_original_message()
            finally:
                msg = await ctx.respond(embed=NBembed)
        except NameError as e:
            if 'msg' in str(e): # 처음 시작 하면 msg가 없음
                pass
            else:
                await ctx.respond("`/숫자야구 명령어를 통해 숫자를 초기화 해주세요.`")

def setup(bot):
    bot.add_cog(NBbaseball(bot))