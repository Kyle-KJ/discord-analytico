# Analytico
# Discord Bot

import os
import re
import datetime
import discord
from discord.ext import commands
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


def date_filename():
    # Create image filename using current datetime
    return re.sub(r'\ |\.|\:|\-', '_', str(datetime.datetime.utcnow())) + ".png"
    

main_dir = os.path.dirname(__file__)
token_path = '/Parameters/Bot_Token.txt'
token_file = main_dir + token_path

bot_token = open(token_file, 'r').read()

bot = commands.Bot(command_prefix='$aco ')

post_colour= 0x03BDAB

@bot.event
async def on_ready():
    print("\n")
    print(f"Logged in as {bot.user}")
    print("\n")

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
async def helpme(ctx):
    # TODO - Provide help text containing list of available functions
    # TODO - Add optional extra argument to give deeper detail and examples for specific functions 
    await ctx.channel.send("Help text.")


@bot.command()
async def messagecount(ctx, unit, value):
    # TODO - Add optional arguments for username/channel
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
        await ctx.channel.send("``` messagecount requires a positive integer argument.```")


@bot.command()
async def graph(ctx, *args):
    # TODO - Add date filters

    # Get Message History (as DataFrame)
    message_list = await ctx.channel.history().flatten()

    messages = []

    for msg in message_list:
        message_data = [msg.author.name, msg.content]
        messages.append(message_data)
    
    df = pd.DataFrame(messages, columns=['User', 'Message'])

    # Assign Filename for Image
    filename = date_filename()    
    graph_path = main_dir + '/' + filename

    if args[0] == "messagecount":

        # Plot Chart and Save Image
        sns.countplot(x='User', data=df)
        plt.savefig(filename, dpi=200)

        # Construct Embedded Message
        embed = discord.Embed(
            title="Message Count Graph",
            description="Number of messages posted per user",
            colour=post_colour
            )

        graph_file = discord.File(graph_path, filename=filename)
        attach_path = "attachment://" + filename
        embed.set_image(url=attach_path)
        embed.set_footer(text="Chart generated using Seaborn")

        # Post Message
        await ctx.channel.send(file=graph_file, embed=embed)

        # Delete Image
        os.remove(graph_path)


    elif args[0] == "wordcount":

        try:
            # Transform Data
            search_word = str(args[1]).lower()
            df['Lower'] = df['Message'].str.lower()
            df['Wordcount'] = df['Lower'].str.count(search_word)
            grouped = df.groupby('User', as_index=False)['Wordcount'].apply(sum).sort_values(by='Wordcount', ascending=False)

            # Plot Chart and Save Image
            sns.barplot(x='User', y='Wordcount', data=grouped)
            plt.savefig(filename, dpi=200)

            # Construct Embedded Message
            embed_title = "Word Count Graph ( " + str(args[1]) + " )"
            embed_descr = "Number of times word '" + str(args[1]) + "' was posted per user"

            embed = discord.Embed(
                title=embed_title,
                description=embed_descr,
                colour=post_colour
                )

            graph_file = discord.File(graph_path, filename=filename)
            attach_path = "attachment://" + filename
            embed.set_image(url=attach_path)
            embed.set_footer(text="Chart generated using Seaborn")

            # Post Message
            await ctx.channel.send(file=graph_file, embed=embed)

            # Delete Image
            os.remove(graph_path)

        except:
            # Transform Data
            df['Wordcount'] = df['Message'].str.split().str.len()
            grouped = df.groupby('User', as_index=False)['Wordcount'].apply(sum).sort_values(by='Wordcount', ascending=False)

            # Plot Chart and Save Image
            sns.barplot(x='User', y='Wordcount', data=grouped)
            plt.savefig(filename, dpi=200)

            # Construct Embedded Message
            embed = discord.Embed(
                title="Word Count Graph",
                description="Number of words posted per user",
                colour=post_colour
                )

            graph_file = discord.File(graph_path, filename=filename)
            attach_path = "attachment://" + filename
            embed.set_image(url=attach_path)
            embed.set_footer(text="Chart generated using Seaborn")

            # Post Message
            await ctx.channel.send(file=graph_file, embed=embed)

            # Delete Image
            os.remove(graph_path)
    
    elif args[0] == "emojicount":
        pass

    elif args[0] == "reactcount":
        pass

    elif args[0] == "imagecount":
        pass

    else:
        print("\nInvalid Input\n")



bot.run(bot_token)
