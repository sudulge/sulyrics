import discord
from discord.ext import commands
from discord.commands import slash_command, Option
import os
import requests
import json
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()


class Tetrio(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @slash_command(name="테트리오랭크", description="테트리오 랭크컷")
    async def tetrio_ranks(self, ctx):
        url = "https://tetrio.team2xh.net/?t=ranks"
        response = requests.get(url=url)
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')
        rankrow = soup.find_all('div', 'rank-row')
        updated_date = rankrow[0].find('small', 'last-updated').text
        del rankrow[0]
        del rankrow[-1]
        ranklist = ['X', 'U', 'SS', 'S+', 'S', 'S-', 'A+', 'A', 'A-', 'B+', 'B','B-', 'C+', 'C', 'C-', 'D+', 'D']

        embed = discord.Embed(color=0xf5a9a9)
        embed.title = "TETR.IO RANKS"
        embed.set_thumbnail(url="https://media.discordapp.net/attachments/1033149773504593921/1114231066916569229/t_spin.gif")
        embed.set_footer(text=updated_date)

        for index, rank in enumerate(rankrow):
            required_tr = rank.find('div', 'required-tr').text
            embed.add_field(name=ranklist[index], value=f'{required_tr} TR', inline=True)
        embed.add_field(name='', value='', inline=True)

        await ctx.respond(embed=embed)

    
    @slash_command(name="테트리오", description="테트리오 유저 정보 검색")
    async def tetrio_user(self, ctx, name: Option(str, "닉네임 입력")):
        url = f"https://ch.tetr.io/api/users/{name}"
        response = requests.get(url=url)
        contents = json.loads(response.content)
        user = contents['data']['user']
        league = user['league']

        embed = discord.Embed(color=0xf5a9a9)
        embed.title = user['username'].upper()
        embed.url = f"https://ch.tetr.io/u/{user['username']}"
        embed.add_field(name='APM', value=league['apm'])
        embed.add_field(name='PPS', value=league['pps'])
        embed.add_field(name='VS', value=league['vs'])
        embed.add_field(name='RANK', value=league['rank'].upper())
        embed.add_field(name='TR', value=round(league['rating']))
        embed.add_field(name='GLICKO', value=f"{round(league['glicko'])}±{round(league['rd'])}")
        embed.add_field(name='GAMES WON', value=f"{league['gameswon']}/{league['gamesplayed']} ({(league['gameswon']/league['gamesplayed'])*100:.2f}%)")
        embed.add_field(name='POSITION', value=f"{league['standing']}/{league['standing_local']}")
        embed.set_thumbnail(url=f"https://tetr.io/user-content/avatars/{user['_id']}.jpg?rv={user['avatar_revision']}" if 'avatar_revision' in user else '')
        
        await ctx.respond(embed=embed)


def setup(bot):
    bot.add_cog(Tetrio(bot))
