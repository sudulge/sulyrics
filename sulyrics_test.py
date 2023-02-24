# 수리릭 테스트용 봇

# with pycord

# 음악 테스트 할때 1. sulyrics 경로부터 실행, 2. music.py 파일에 클라이언트 아이디 바꿔주기
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
from cogs.music import MyView

intents = discord.Intents.all()

async def get_all_data():
    try:
        with open("cogs/data/music_channel.pickle", 'rb') as f: # 로컬에서 실행시킬때는 project 폴더부터 경로 작성
            return pickle.load(f)
    except FileNotFoundError:
        return {}
    except EOFError:
        return {}

async def get_data(guild_id):
    data = await get_all_data()
    return data[guild_id]


class SulyricsTest(commands.Bot):
    def __init__(self):
        super().__init__(intents=intents)
        for i in EXTENSIONS:
            self.load_extension(i)
            print(f"{i} 로드 완료")
        self.persistent_views_added = False

    async def on_ready(self):
        print(f'We have logged in as {bot.user}')
        game = discord.Game("아무것도 안")
        await bot.change_presence(status = discord.Status.online, activity=game)

        if not self.persistent_views_added:
            bot.add_view(MyView())
            self.persistent_views_added = True

    async def on_message(self, message):
        if message.author.bot:
            return
        else:
            try:
                data = await get_data(message.guild.id)
                if message.channel.id == data['channel_id']:
                    await message.delete()
                    Music = self.get_cog("Music")
                    await Music.play(message, message.content)
                else:
                    await self.process_commands(message)
            except:
                await self.process_commands(message)

    async def on_application_command_error(self, ctx, exception):
        embed = discord.Embed(color=0xf5a9a9)
        embed.title = "다시 시도해주세요"
        embed.description = f"`/{ctx.command}`  {exception}"
        await ctx.respond(embed=embed, delete_after=3)

bot = SulyricsTest()
bot_token = os.getenv("test_bot_token")
bot.run(bot_token)