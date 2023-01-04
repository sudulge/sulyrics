import discord
from discord.ext import commands
from discord.commands import slash_command, Option
from discord.ui import Select, Button, Modal, View
from datetime import datetime, timedelta, timezone, time
import asyncio
import random
import os
import sys

from .data.data import alarm_text


async def set_alarm(ampm, hour, minute): #정수값으로 보내주기
    now = datetime.now(tz=timezone(timedelta(hours=9))).replace(tzinfo=None)

    if ampm == "오전" and hour == 12:
        hour = 0
    if ampm == "오후" and hour < 12:
        hour = hour + 12

    time_ = time(hour, minute, 0)

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
    
    @slash_command(name="알람", description="알람을 설정합니다.")
    async def alarm(self, ctx):

        ampm = Select(placeholder = "오전/오후", options=[
            discord.SelectOption(label = "오전"),
            discord.SelectOption(label = "오후"),
        ])
        hour = Select(placeholder = "시", options=[
            discord.SelectOption(label = '1'),
            discord.SelectOption(label = '2'),
            discord.SelectOption(label = '3'),
            discord.SelectOption(label = '4'),
            discord.SelectOption(label = '5'),
            discord.SelectOption(label = '6'),
            discord.SelectOption(label = '7'),
            discord.SelectOption(label = '8'),
            discord.SelectOption(label = '9'),
            discord.SelectOption(label = '10'),
            discord.SelectOption(label = '11'),
            discord.SelectOption(label = '12'),
        ])

        minute = Select(placeholder = "분", options=[
            discord.SelectOption(label = '0'),
            discord.SelectOption(label = '5'),
            discord.SelectOption(label = '10'),
            discord.SelectOption(label = '15'),
            discord.SelectOption(label = '20'),
            discord.SelectOption(label = '25'),
            discord.SelectOption(label = '30'),
            discord.SelectOption(label = '35'),
            discord.SelectOption(label = '40'),
            discord.SelectOption(label = '45'),
            discord.SelectOption(label = '50'),
            discord.SelectOption(label = '55'),
        ])

        name_button = Button(label = "이름 변경", style=discord.ButtonStyle.primary)
        ok_button = Button(label = "확인", style=discord.ButtonStyle.success)

        name_input_modal = Modal(title="알람 이름 변경")
        name_input_modal.add_item(discord.ui.InputText(label="이름", placeholder="알람", value = "알람"))


        async def name_button_callback(interaction):
            if interaction.user == ctx.author:
                await interaction.response.send_modal(name_input_modal)
        
        async def ok_button_callback(interaction):
            if interaction.user == ctx.author:
                if ampm.values and hour.values and minute.values:
                    embed = discord.Embed(color=0xf5a9a9)
                    embed.title = f"⏰ {ampm.values[0]} {hour.values[0]}시 {minute.values[0]}분 | {name_input_modal.children[0].value}"
                    embed.description = f"{ctx.author.display_name}"
                    embed.set_footer(text="알람이 설정되었습니다.\n설정된 시각에 dm이 발송됩니다.")
                    await interaction.response.edit_message(view=None, embed=embed)

                    await set_alarm(str(ampm.values[0]), int(hour.values[0]), int(minute.values[0]))

                    user = await self.bot.fetch_user(ctx.author.id)
                    embed = discord.Embed(color=0xf5a9a9)
                    embed.title =f"⏰ {name_input_modal.children[0].value}" 
                    embed.description = f"{ampm.values[0]} {hour.values[0]}시 {minute.values[0]}분 입니다! {random.choice(alarm_text)}"
                    await user.send(embed = embed)

                else:
                    await interaction.response.send_message("항목을 모두 채워주세요", delete_after=2)
        
        async def name_input_modal_callback(interaction):
            if interaction.user == ctx.author:
                await interaction.response.send_message(f'알림 이름 변경됨: {name_input_modal.children[0].value}', delete_after=2)

        async def ampm_callback(interaction):
            if interaction.user == ctx.author:
                await interaction.response.defer()
        async def hour_callback(interaction):
            if interaction.user == ctx.author:
                await interaction.response.defer()
        async def minute_callback(interaction):
            if interaction.user == ctx.author:
                await interaction.response.defer()

        ampm.callback = ampm_callback
        hour.callback = hour_callback
        minute.callback = minute_callback
        name_button.callback = name_button_callback
        ok_button.callback = ok_button_callback
        name_input_modal.callback = name_input_modal_callback

        view = View()
        view.add_item(ampm)
        view.add_item(hour)
        view.add_item(minute)
        view.add_item(name_button)
        view.add_item(ok_button)

        await ctx.respond(view=view)


def setup(bot):
    bot.add_cog(Alarm(bot))
