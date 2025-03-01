import os

import discord
from dotenv import load_dotenv

# Load all the key value pair from .env into environment variables.
load_dotenv() 

# Fetches the DISCORD_TOKEN value from the environment.
TOKEN = os.getenv('DISCORD_TOKEN')  

# Enable necessary intents (what events bot recieves from Discord)
intents = discord.Intents.default() 
intents.message_content = True  # Allows bot to read messages

# Initialize the bot
client = discord.Client(intents = intents)

@client.event
async def on_ready():   # Runs on_ready event when Client has established connection to Discord
    print(f'{client.user} has connected to Discord!')

print(f'Token = {TOKEN}')

# Run Client using bot's token
client.run(TOKEN)