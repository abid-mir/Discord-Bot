import os

import discord
from dotenv import load_dotenv

# Load all the key value pair from .env into environment variables.
load_dotenv() 

# Fetches the DISCORD_TOKEN value from the environment.
TOKEN = os.getenv('DISCORD_TOKEN')  
GUILD = os.getenv('DISCORD_SERVER')

# Enable necessary intents (what events bot recieves from Discord)
intents = discord.Intents.default() 
intents.message_content = True  # Allows bot to read messages
intents.members = True  # This allows the bot to see all server members

# Initialize the bot
client = discord.Client(intents = intents)

@client.event
async def on_ready():   # Runs on_ready event when Client has established connection to Discord
    for guild in client.guilds:
        if guild == GUILD:
            break

    print(f'{client.user} is connected to the following guild:\n{guild.name}(id:{guild.id})')

    # METHOD 1:
    # members = '\n - '.join([member.name for member in guild.members])
    # print(f'Guild Members:\n - {members}')

    # METHOD 2:
    members = []
    for member in guild.members:
        members.append(member.name)
    
    members = '\n - '.join(members)
    print(f'Guild members:\n - {members}')

    #METHOD 3 (USING UTILITY FUNCTION):

# Run Client using bot's token
client.run(TOKEN)