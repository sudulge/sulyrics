# 뮤직봇 only 슬래시 커맨드용

# with pycord

import discord
from discord.ext import commands
from datetime import datetime, timedelta, timezone, time
import asyncio
import random
import os
import re
from dotenv import load_dotenv

load_dotenv()
from config import EXTENSIONS

intents = discord.Intents.all()

imoji_rx =  re.compile('^<a?:.+?:\d+>$')


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
    
    async def on_message(self, message):
        if message.author.bot:
            return
        else:
            await self.process_commands(message)

    async def on_application_command_error(self, ctx, exception):
        embed = discord.Embed(color=0xf5a9a9)
        embed.title = "다시 시도해주세요"
        embed.description = f"`/{ctx.command}`  {exception.original}"
        await ctx.respond(embed=embed)

bot = Sulyrics()
bot_token = os.getenv("bot_token")
bot.run(bot_token)
