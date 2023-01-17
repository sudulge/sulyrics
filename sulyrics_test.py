# 수리릭 테스트용 봇

# with pycord

import discord
from discord.ext import commands
from discord.commands import slash_command
from datetime import datetime, timedelta, timezone, time
import asyncio
import random
import os
import re
import pickle
from dotenv import load_dotenv

load_dotenv()
from config import EXTENSIONS

intents = discord.Intents.all()


class SulyricsTest(commands.Bot):
    def __init__(self):
        super().__init__(intents=intents)
        for i in EXTENSIONS:
            self.load_extension(i)
            print(f"{i} 로드 완료")

    async def on_ready(self):
        print(f'We have logged in as {bot.user}')
        game = discord.Game("아무것도 안")
        await bot.change_presence(status = discord.Status.online, activity=game)


bot = SulyricsTest()
bot_token = os.getenv("test_bot_token")
bot.run(bot_token)