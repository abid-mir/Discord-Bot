# bot.py
import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

# Load token from .env file
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Define intents
intents = discord.Intents.default()  # Use default intents
intents.message_content = True

# Create bot instance
bot = commands.Bot(command_prefix='!', intents = intents)

# Create a new text channel
@bot.command(name = 'create-channel')
@commands.has_role('admin') # Restrict to admins
async def create_channel(ctx, channel_name='real-python'):
    guild = ctx.guild
    existing_channel = discord.utils.get(guild.channels, name=channel_name)

    # Check if the channel already exists
    if not existing_channel:
        print(f'Creating a new channel: {channel_name}')
        await guild.create_text_channel(channel_name)

# Check if the bot has permission to create channels
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send('You do not have the correct role for this command.')

# Run the bot
bot.run(TOKEN)