# with pycord

import discord
from discord.ext import commands
from datetime import datetime, timedelta, timezone, time
import asyncio
import random
import os
import re

from config import EXTENSIONS
from saying import sayinglist

intents = discord.Intents.all()

imoji_rx =  re.compile('^<a?:.+?:\d+>$')

morning = time(7, 0, 0)

def sayingEmbed():
    today_saying = random.choice(sayinglist)
    embed = discord.Embed(color=0x87cefa)
    embed.set_author(name='오늘의 명언', icon_url='https://cdn.discordapp.com/attachments/731547490347909120/972639147170873344/unknown.png')
    embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/731547490347909120/972639446744842281/unknown.png')
    embed.title = today_saying[0]
    embed.description = today_saying[1]
    embed.set_footer(text=f'{today_saying[2]} | {today_saying[3]}')
    return embed


class Sulyrics(commands.Bot):
    def __init__(self):
        super().__init__(intents=intents)
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
        elif message.channel.id == 954249440552697907 and imoji_rx.match(message.content):
            await message.delete()
            user = await self.fetch_user(message.author.id)
            embed = discord.Embed(color=0x2f3136)
            embed.set_author(name=message.author.display_name, icon_url=message.author.display_avatar)
            embed.set_image(url=f'https://cdn.discordapp.com/emojis/{message.content.split(":")[2].split(">")[0]}') 
            await message.channel.send(embed=embed)
        else:
            await self.process_commands(message)

    async def schedule_daily_message(self):
        while True: 
            now = datetime.now()
            if now.time() > morning:
                target_time = datetime.combine(now.date() + timedelta(days=1), morning)
            else:
                target_time = datetime.combine(now.date(), morning)
            wait_time = (target_time - now).total_seconds()
            await asyncio.sleep(wait_time)
            embed = sayingEmbed()
            channel = bot.get_channel(723894009856131132)
            await channel.send("좋은 아침 !", embed=embed)
            channel = bot.get_channel(954249440552697907)
            await channel.send("굿뭘닌 !", embed=embed)


bot = Sulyrics()
bot_token = os.environ["BOT_TOKEN"]
bot.run(bot_token)
