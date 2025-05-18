# bot.py
import os
import random
from dotenv import load_dotenv
import discord  # Import discord for Intents

# 1 (Provides tools to create command-based Discord bots)
from discord.ext import commands

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Define intents
intents = discord.Intents.default()  # Use default intents
intents.messages = True  # Enable message events 
intents.message_content = True

# 2 (Creates a bot instance that listens for messages with the prefix "!")
bot = commands.Bot(command_prefix='!', intents = intents)

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!') # Displays a message in the terminal when the bot is online.

@bot.command(name='99', help='Responds with a random quote from Brooklyn 99')
async def nine_nine(ctx):
    brooklyn_99_quotes = [
        'I\'m the human form of the 💯 emoji.',
        'Bingpot!',
        (
            'Cool. Cool cool cool cool cool cool cool, '
            'no doubt no doubt no doubt no doubt.'
        ),
    ]

    response = random.choice(brooklyn_99_quotes)
    await ctx.send(response)

bot.run(TOKEN)