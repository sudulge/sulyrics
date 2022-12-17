import discord
from discord.ext import commands
from discord.commands import slash_command, Option
from datetime import datetime
from pytz import timezone
from neispy import Neispy
import os
import sys
from dotenv import load_dotenv

load_dotenv()

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from config import guild_ids

class Lunch(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(name="급식", description="급식")
    async def lunch(self, ctx, school: Option(str, "학교 이름 입력")):
        today = str(datetime.now())[:10].replace('-', '')
        neis_key = os.getenv["neis_api_key"]

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

def setup(bot):
    bot.add_cog(Lunch(bot))
