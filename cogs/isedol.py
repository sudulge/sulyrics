import discord
from discord.ext import commands
from discord.commands import slash_command, Option
import os
import requests
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()


member = [49045679, 702754423, 237570548, 169700336, 203667951, 707328484, 195641865]

url = "https://api.twitch.tv/helix/streams"
headers = {
    'client-id' : os.getenv("twitch_client_id"),
    'Authorization' : os.getenv("twitch_app_access_token"),
}

class Isedol(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_info(self):
        info = []
        for id in member:
            params = {"user_id": id}
            response = requests.get(url, headers=headers, params=params)
            contents = json.loads(response.content)

            try:
                if contents["data"][0]["type"] == 'live':
                    info.append(contents["data"][0]["title"])
            except:
                info.append(None)
                
        return info

    def make_embed(self, list):
        embed = discord.Embed(color=0xf4f4ec)
        embed.title = "이세돌 뱅온 정보"
        embed.add_field(name="우왁굳", value= list[0] if list[0] else "offline", inline=False)
        embed.add_field(name="아이네", value= list[1] if list[1] else "offline", inline=True)
        embed.add_field(name="징버거", value= list[2] if list[2] else "offline", inline=True)
        embed.add_field(name="릴파", value= list[3] if list[3] else "offline", inline=True)
        embed.add_field(name="주르르", value= list[4] if list[4] else "offline", inline=True)
        embed.add_field(name="고세구", value= list[5] if list[5] else "offline", inline=True)
        embed.add_field(name="비챤", value= list[6] if list[6] else "offline", inline=True)
        embed.set_image(url="https://cdn.discordapp.com/attachments/1033149773504593921/1060293166114287676/isedol.jpg")
        return embed


    @slash_command(name="이세돌", description="이세돌 뱅온 정보")
    async def isedol(self, ctx):
        info = self.get_info()
        embed = self.make_embed(info)
        await ctx.respond(embed=embed)

def setup(bot):
    bot.add_cog(Isedol(bot))