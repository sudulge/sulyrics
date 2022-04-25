# with pycord

import discord
from discord.ext import commands
import os

from config import EXTENSIONS


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
        # await bot.get_channel(731547490347909120).send("이 몸 등 장 !")  # 아잉방 연구실
        # await bot.get_channel(896418649244573717).send("이 몸 등 장 !")  # 놀이터
    
    async def on_message(self, message):
        if message.author.bot:
            return
        else:
            await self.process_commands(message)


bot = Sulyrics()
bot_token = os.environ["BOT_TOKEN"]
bot.run(bot_token)
