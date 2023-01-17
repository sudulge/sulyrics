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


async def set_alarm(interaction, name, ampm, hour, minute): #정수값으로 보내주기
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

    await asyncio.sleep(wait_time)

    user = await interaction.client.fetch_user(interaction.user.id)
    embed = discord.Embed(color=0xf5a9a9)
    embed.title = f"⏰ {name}"
    embed.description = f"{ampm} {hour}시 {minute}분입니다! {random.choice(alarm_text)}"
    await user.send(embed=embed)


class Alarm(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @slash_command(name="알람", description="알람을 설정합니다")
    async def alarm(self, ctx):
        await ctx.respond(view=AlarmView())


class AlarmView(View):
    @discord.ui.select(placeholder="오전/오후", custom_id="ampm", options=[
        discord.SelectOption(label = "오전"),
        discord.SelectOption(label = "오후"),
    ])

    async def ampm_callback(self, select, interaction):
        await interaction.response.defer()

    @discord.ui.select(placeholder="시", custom_id="hour", options=[
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

    async def hour_callback(self, select, interaction):
        await interaction.response.defer()

    @discord.ui.select(placeholder = "분", custom_id="minute", options=[
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

    async def minute_callback(self, select, interaction):
        await interaction.response.defer()

    @discord.ui.button(label="이름 변경", style=discord.ButtonStyle.primary)
    async def changeName(self, button, interaction):
        name_input_modal = Modal(title="알람 이름 변경")
        name_input_modal.add_item(discord.ui.InputText(label="알람 이름", placeholder="알람", value=self.name if hasattr(self, "name") else None))
        async def name_input_modal_callback(interaction):
            await interaction.response.send_message(f"알람 이름 변경됨: {name_input_modal.children[0].value}", delete_after=1)
            self.name = name_input_modal.children[0].value
        name_input_modal.callback = name_input_modal_callback
        await interaction.response.send_modal(name_input_modal)

    @discord.ui.button(label="확인", style=discord.ButtonStyle.success)
    async def ok(self, button, interaction):
        ampm = self.get_item(custom_id="ampm").values[0]
        hour = self.get_item(custom_id="hour").values[0]
        minute = self.get_item(custom_id="minute").values[0]
        name = self.name if hasattr(self, "name") else "알람"

        if ampm and hour and minute:
            embed = discord.Embed(color=0xf5a9a9)
            embed.title = f"⏰ {ampm} {hour}시 {minute}분 | {name}"
            embed.description = f"{interaction.user.display_name}"
            embed.set_footer(text="알람이 설정되었습니다\n설정된 시각에 dm이 발송됩니다")             
            await interaction.response.edit_message(view=None, embed=embed)
            await set_alarm(interaction, name, ampm, int(hour), int(minute))
        else:
            await interaction.response.send_message("항목을 모두 채워주세요", delete_after=1)

def setup(bot):
    bot.add_cog(Alarm(bot))
    