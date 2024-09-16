import discord
from discord.ext import commands
from discord.commands import slash_command, Option
import random
import re


num_rx = re.compile('^[0-9]{4}$')

def start():
    global HRnumber, tried_number, log_message
    HRnumber = list(map(str, random.sample(range(0, 9), 4)))
    tried_number = []
    log_message = ''
    return 


def checkInput(input):
    print(input, type(input))
    if not num_rx.match(input):
        return "네 자리 정수를 입력해 주세요"
    if len(set(input)) != 4:
        return "중복되지 않게 입력해 주세요"
    if input in tried_number:
        return "이미 시도한 숫자입니다."

    return True


def hit(input, ctx):
    global log_message
    while len(input) == 3: # ex) int(0123) -> 123 
        input = '0' + input

    valid = checkInput(input)
    
    if type(valid)==str:
        return valid
    
    tried_number.append(input)
    strike = 0
    ball = 0

    for index, number in enumerate(input):
        if number == HRnumber[index]:
            strike += 1
        elif number in HRnumber:
            ball += 1

    if strike == 4:
        result = f"홈런! {len(tried_number)}회 만에 맞추셨습니다"
        end()
    elif strike == 0 and ball == 0:
        result = "아웃"
    else:
        result = f"{input}: {strike}S {ball}B"
    
    log_message += f"{input}: {strike}S {ball}B ⠀({ctx.author.display_name})\n"

    return result


def end():
    global HRnumber # tried_number, log_message 는 홈런메시지에 출력해줘야해서 지우면 안됨.
    del HRnumber

class NBbaseball(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(name="숫자야구", description="숫자야구")
    async def numBaseball(self, ctx, choice: Option(str, "숫자야구", choices=["시작", "도움말"])):
        if choice == "시작":
            start()
            print(HRnumber)
            await ctx.respond("`숫자를 초기화했습니다.\n/야 명령어를 통해 숫자를 입력해 주세요.`")
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


    @slash_command(name="야", description="숫자야구")
    async def numBaseballInput(self, ctx, input: Option(int, "네자리 숫자 입력")):
        try:
            result = hit(str(input), ctx)
            embed = discord.Embed(color=0xf5a9a9)
            embed.title = result
            embed.description = "=========================="
            embed.add_field(name="로그", value=f"```{log_message}```")

            try:
                await msg.delete_original_message()
            finally:
                msg = await ctx.respond(embed=embed)

        except NameError as e:
            if 'msg' in str(e): # 처음 시작 하면 msg가 없음
                pass
            else:               # 홈런으로 끝난 후 다시 /야 칠떄 HRnumber가 없음
                await ctx.respond("`/숫자야구 명령어를 통해 숫자를 초기화 해주세요.`")


def setup(bot):
    bot.add_cog(NBbaseball(bot))
