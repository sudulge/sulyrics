import discord
from discord.ext import commands
from discord.commands import slash_command, Option
from datetime import datetime
from neispy import Neispy
from bs4 import BeautifulSoup
import requests
import os
import sys
from dotenv import load_dotenv

load_dotenv()


class Lunch(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(name="급식", description="급식")
    async def lunch(self, ctx, school: Option(str, "학교 이름 입력")):
        today = datetime.now().strftime("%Y%m%d")
        neis_key = os.getenv("neis_api_key")

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

    
    @slash_command(name="학식", description="학식")
    async def lunch2(self, ctx):
        url = 'https://www.smu.ac.kr/ko/life/restaurantView.do'
        response = requests.get(url)
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')
        all_menu = soup.findAll('ul', {'class': 's-dot'})
        del all_menu[0] # 쓸모 없는 값 삭제
        # all_menu[n] 0~4: 월~금 자율학식, 5~9: 월~금 컵밥

        weekday = datetime.now().weekday() # 0~4: 월~금
        if weekday in range(5):
            lunchlist = all_menu[weekday].text
        else:
            lunchlist = '오늘은 주말' #오류 방지용 문구

        embed = discord.Embed(color=0xf5a9a9)
        embed.title = f"상명대 {datetime.today().month}월 {datetime.today().day}일 학식"
        embed.add_field(name="​", value=lunchlist)
        embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/769489028357160990.png")
        await ctx.respond(embed=embed)


def setup(bot):
    bot.add_cog(Lunch(bot))
