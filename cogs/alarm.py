import discord
from discord.ext import commands
from discord.commands import slash_command, Option
from discord.ui import Select, Button, View
from datetime import datetime, timedelta, timezone, time
import asyncio


async def set_alarm(ampm, hour, minute): #정수값으로 보내주기
    now = datetime.now(tz=timezone(timedelta(hours=9))).replace(tzinfo=None)
    print(ampm)
    if ampm == "오전" and hour == 12:
        hour = 0
    if ampm == "오후" and hour < 12:
        hour = hour + 12

    time_ = time(hour, minute, 0)
    print(now.time(), time_)
    if now.time() > time_:
        target_time = datetime.combine(now.date() + timedelta(days=1), time_)
    else:
        target_time = datetime.combine(now.date(), time_)
    wait_time = (target_time - now).total_seconds()
    print(target_time, wait_time)
    await asyncio.sleep(wait_time)






class Alarm(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @slash_command(name="알람", guild_ids=[723892698435551324, 896398625163345931], description="알람을 설정합니다.")
    async def alarm(self, ctx):

        ampm = Select(placeholder = "오전/오후", options=[
            discord.SelectOption(label = "오전"),
            discord.SelectOption(label = "오후"),
        ])

        hour = Select(placeholder = "시", options=[
            discord.SelectOption(label = 1),
            discord.SelectOption(label = 2),
            discord.SelectOption(label = 3),
            discord.SelectOption(label = 4),
            discord.SelectOption(label = 5),
            discord.SelectOption(label = 6),
            discord.SelectOption(label = 7),
            discord.SelectOption(label = 8),
            discord.SelectOption(label = 9),
            discord.SelectOption(label = 10),
            discord.SelectOption(label = 11),
            discord.SelectOption(label = 12),
        ])

        minute = Select(placeholder = "분", options=[
            discord.SelectOption(label = 0),
            discord.SelectOption(label = 5),
            discord.SelectOption(label = 10),
            discord.SelectOption(label = 15),
            discord.SelectOption(label = 20),
            discord.SelectOption(label = 25),
            discord.SelectOption(label = 30),
            discord.SelectOption(label = 35),
            discord.SelectOption(label = 40),
            discord.SelectOption(label = 45),
            discord.SelectOption(label = 50),
            discord.SelectOption(label = 55),
        ])

        button = Button(label = "확인", style=discord.ButtonStyle.success)
        
        async def button_callback(interaction):
            if ampm.values and hour.values and minute.values:
                embed = discord.Embed(color=0xf5a9a9)
                embed.title = f"{ampm.values[0]} {hour.values[0]}시 {minute.values[0]}분 알람 설정"
                embed.description = f"{ctx.author.display_name}"
                embed.set_footer(text="설정된 시각 이전에 봇이 껏다 켜질 경우 알람이 초기화 됩니다.\n너무 긴 시간은 설정하지 않는게 좋습니다.")
                await interaction.response.edit_message(view=None, embed=embed)
                await set_alarm(str(ampm.values[0]), int(hour.values[0]), int(minute.values[0]))
                user = await self.bot.fetch_user(ctx.author.id)
                await user.send(f"{ampm.values[0]} {hour.values[0]}시 {minute.values[0]}분 입니다!")

            else:
                await interaction.response.send_message("항목을 모두 채워주세요")
        
        button.callback = button_callback

        view = View()
        view.add_item(ampm)
        view.add_item(hour)
        view.add_item(minute)
        view.add_item(button)

        await ctx.respond("알람 `오전 12시 = 새벽 / 오후 12시 = 낮`", view=view)


def setup(bot):
    bot.add_cog(Alarm(bot))