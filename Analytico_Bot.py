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


# Configurable Parameters
COMMAND_PREFIX = '$aco '
POST_COLOUR = 0x03BDAB


main_dir = os.path.dirname(__file__)
token_path = '/Parameters/Bot_Token.txt'
token_file = main_dir + token_path

bot_token = open(token_file, 'r').read()

bot = commands.Bot(command_prefix=COMMAND_PREFIX)


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

    help_text = """```

Analytico Commands: (Note - All commands must be prefixed with '{prefix}')

    Graph Commands: (These commands will generate a graph image)

        graph messagecount user

            Returns bar chart of messages posted by user

        graph messagecount channel

            Returns bar chart of messages posted by channel

        graph wordcount

            Returns bar chart of word count posted by user 

        graph wordcount <your_word>

            Returns bar chart of specific word posted by user
            Replace <your_word> with word to search

        graph emojicount

            Returns bar chart of count of times emoji posted
    
    Other Commands:

        messagecount <unit> <value>

            Returns count of messages posted within the specified time period
            Replace <unit> and <value> with preferred time period

            Valid for <unit>: minutes, hours, days, weeks, years
            Valid for <value>: Any positive integer

        test
            Bot will respond if online.
    ```"""

    help_text = help_text.format(prefix=COMMAND_PREFIX)

    await ctx.channel.send(help_text)


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
    message_list = []

    for chan in bot.guilds[0].text_channels:
        channel_messages = await chan.history(limit=50000).flatten()
        message_list += channel_messages

    messages = []

    for msg in message_list:
        message_data = [msg.author.name, msg.channel.name, msg.content]
        messages.append(message_data)
    
    #df = pd.DataFrame(messages, columns=['User', 'Channel', 'Message'])

    # Assign Filename for Image
    filename = date_filename()    
    graph_path = main_dir + '/' + filename

    if args[0] == "messagecount":

        df = pd.DataFrame(messages, columns=['User', 'Channel', 'Message'])

        try:
            if args[1] == "user":

                # Transform Data
                grouped = df.groupby('User').size().reset_index(name='Count')
                
                # Plot Chart and Save Image
                sns.barplot(x='User', y='Count', data=grouped)
                plt.savefig(filename, dpi=200)
                plt.clf()

                # Construct Embedded Message
                embed = discord.Embed(
                    title="Message Count Graph",
                    description="Number of messages posted per user",
                    colour=POST_COLOUR
                    )

                graph_file = discord.File(graph_path, filename=filename)
                attach_path = "attachment://" + filename
                embed.set_image(url=attach_path)
                embed.set_footer(text="Chart generated using Seaborn")

                # Post Message
                await ctx.channel.send(file=graph_file, embed=embed)

                # Delete Image
                os.remove(graph_path)

            elif args[1] == "channel":
                
                # Transform Data
                grouped = df.groupby('Channel').size().reset_index(name='Count')

                # Plot Chart and Save Image
                sns.barplot(x='Channel', y='Count', data=grouped)
                plt.savefig(filename, dpi=200)
                plt.clf()

                # Construct Embedded Message
                embed = discord.Embed(
                    title="Message Count Graph",
                    description="Number of messages posted per channel",
                    colour=POST_COLOUR
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
            pass


    elif args[0] == "wordcount":

        df = pd.DataFrame(messages, columns=['User', 'Channel', 'Message'])

        try:
            # Transform Data
            search_word = str(args[1]).lower()
            df['Lower'] = df['Message'].str.lower()
            df['Wordcount'] = df['Lower'].str.count(search_word)
            grouped = df.groupby('User', as_index=False)['Wordcount'].apply(sum).sort_values(by='Wordcount', ascending=False)

            # Plot Chart and Save Image
            sns.barplot(x='User', y='Wordcount', data=grouped)
            plt.savefig(filename, dpi=200)
            plt.clf()

            # Construct Embedded Message
            embed_title = "Word Count Graph ( " + str(args[1]) + " )"
            embed_descr = "Number of times word '" + str(args[1]) + "' was posted per user"

            embed = discord.Embed(
                title=embed_title,
                description=embed_descr,
                colour=POST_COLOUR
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
            plt.clf()

            # Construct Embedded Message
            embed = discord.Embed(
                title="Word Count Graph",
                description="Number of words posted per user",
                colour=POST_COLOUR
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

        # TODO - Specific Emoji by Users
        # TODO - Specific User Emojis Used

        # Transform Data
        emoji_list = []

        for emoji in bot.guilds[0].emojis:
            emoji_data = [emoji.name, 0] 
            emoji_list.append(emoji_data)

        found_list = []
        for msg in messages:
            content = msg[2]
            found_emojis = re.findall(r'<:\w*:\d*>', content)
            for f in found_emojis:
                found_list.append(f)

        emoji_used = []
        for found in found_list:
            emoji_used.append(found.split(':')[1])

        for emoji in emoji_list:
            for used in emoji_used:
                if emoji[0] in used:
                    emoji[1] += 1

        df = pd.DataFrame(emoji_list, columns=['Emoji', 'Count'])

        # Plot Chart and Save Image
        sns.barplot(x='Emoji', y='Count', data=df)
        plt.savefig(filename, dpi=200)
        plt.clf()

        # Construct Embedded Message
        embed = discord.Embed(
            title="Emoji Count Graph",
            description="Number of emojis posted",
            colour=POST_COLOUR
            )

        graph_file = discord.File(graph_path, filename=filename)
        attach_path = "attachment://" + filename
        embed.set_image(url=attach_path)
        embed.set_footer(text="Chart generated using Seaborn")

        # Post Message
        await ctx.channel.send(file=graph_file, embed=embed)

        # Delete Image
        os.remove(graph_path)


    elif args[0] == "reactcount":

        # TODO - Count of reactions used

        pass

    elif args[0] == "imagecount":

        # TODO - Count of images posted

        pass

    else:
        print("\nInvalid Input\n")


# Run the bot

bot.run(bot_token)
