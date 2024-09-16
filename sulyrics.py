#sulyrics 코드정리 ver. 2024.09.16

import discord
import dotenv
import os
import sqlite3
from cogs.music import MusicView

cog_list = [
    'cogs.alarm',
    'cogs.isedol',
    'cogs.lunch',
    'cogs.music',
    'cogs.numberbaseball',
    'cogs.others',
    'cogs.tetrio'
]

dotenv.load_dotenv()

class Sulyrics(discord.Bot):
    def __init__(self):
        super().__init__(intents=discord.Intents.all())
        for cog in cog_list:
            self.load_extension(cog)
            print(f"{cog} 로드 완료")

    async def on_ready(self):
        print(f"we have logged in as {bot.user}")
        game = discord.Game("/help")
        await bot.change_presence(status=discord.Status.online, activity=game)

        bot.add_view(MusicView())

    async def on_message(self, message):
        if message.author.bot:
            return
        else:
            con = sqlite3.connect(os.path.dirname(os.path.abspath(__file__)) + '/cogs/data/sulyrics.db')
            cur = con.cursor()
            cur.execute(f"SELECT ChannelID FROM MUSIC WHERE GuildID = {message.guild.id}")
            data = cur.fetchall()

            if data and data[0][0] == message.channel.id:
                await message.delete()
                Music = self.get_cog("Music")
                await Music.play(message, message.content)


bot = Sulyrics()
token = os.getenv("bot_token")
bot.run(token)