# with pycord

import discord
from discord.ext import commands
from datetime import datetime, timedelta, timezone
import asyncio
import random
import os

from config import EXTENSIONS
from saying import sayinglist

today_saying = random.choice(sayinglist)

embed = discord.Embed(color=0x87cefa)
embed.set_author(name='오늘의 명언', icon_url='https://cdn.discordapp.com/attachments/731547490347909120/972639147170873344/unknown.png')
embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/731547490347909120/972639446744842281/unknown.png')
embed.title = today_saying[0]
embed.description = today_saying[1]
embed.set_footer(text=f'{today_saying[2]} | {today_saying[3]}')

class Sulyrics(commands.Bot):
    def __init__(self):
        super().__init__()
        for i in EXTENSIONS:
            self.load_extension(i)
            print(f"{i}로드 완료")

    async def on_ready(self):
        print(f'We have logged in as {bot.user}')
        game = discord.Game("/help")
        await bot.change_presence(status = discord.Status.online, activity=game)
        await bot.get_channel(731547490347909120).send("이 몸 등 장 !")    # 아잉방 연구실
        # await bot.get_channel(896418649244573717).send("이 몸 등 장 !")  # 놀이터
        await self.schedule_daily_message()
    
    async def on_message(self, message):
        if message.author.bot:
            return
        else:
            await self.process_commands(message)

    async def schedule_daily_message(self):
        now = datetime.now(tz=timezone(timedelta(hours=9)))
        then = now.replace(hour=7, minute=00)
        wait_time = (then-now).total_seconds()
        await asyncio.sleep(wait_time)
        channel = bot.get_channel(723894009856131132)
        await channel.send("좋은 아침 !", embed=embed)


bot = Sulyrics()
bot_token = os.environ["BOT_TOKEN"]
bot.run(bot_token)
