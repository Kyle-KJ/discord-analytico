# Analytico
# Discord Bot

import os
import datetime
import discord
from discord.ext import commands


main_dir = os.path.dirname(__file__)
token_path = '/Parameters/Bot_Token.txt'
token_file = main_dir + token_path

bot_token = open(token_file, 'r').read()

bot = commands.Bot(command_prefix='$aco ')

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    if message.content.startswith("Analytico"):
        await message.channel.send("Noted.")
    
    await bot.process_commands(message)

@bot.command()
async def test(ctx):
    await ctx.channel.send("Online.")

@bot.command()
async def msgcount(ctx, unit, value):
    if value.isnumeric():
        value = int(value)
        today = datetime.datetime.utcnow()
        if unit == "minutes":
            target_date = today - datetime.timedelta(minutes=value)
        elif unit == "hours":
            target_date = today - datetime.timedelta(hours=value)
        elif unit == "days":
            target_date = today - datetime.timedelta(days=value)
        elif unit == "weeks":
            target_date = today - datetime.timedelta(weeks=value)
        elif unit == "years":
            value = value * 365
            target_date = today - datetime.timedelta(days=value)
        else:
            pass

        msg_count = 0
        async for msg in ctx.channel.history(after=target_date):
            msg_count = msg_count + 1
        output_value = f"``` {msg_count}.```"
        await ctx.channel.send(output_value)
    else:
        await ctx.channel.send("``` msgcount requires a positive integer argument.")

bot.run(bot_token)