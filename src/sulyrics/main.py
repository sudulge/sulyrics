import discord
from discord.ext import commands
import os
import dotenv

dotenv.load_dotenv()

class SulyricsTest(commands.Bot):
    def __init__(self):
        super().__init__(intents=discord.Intents.all())

        self.cog_list = [
            'sulyrics.cogs.music',
        ]

        for cog in self.cog_list:
            self.load_extension(cog)
            print(f"{cog} 로드 완료")

    async def on_ready(self):
        print(f"{self.user} 로그인 완료")
        await self.change_presence(status=discord.Status.online, activity=discord.Game("/help"))

def main():
    bot = SulyricsTest()
    token = os.getenv("bot_token")
    bot.run(token)

if __name__ == "__main__":
    main()