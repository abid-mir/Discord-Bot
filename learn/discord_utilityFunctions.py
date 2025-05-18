# bot.py
import os

import discord
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

client = discord.Client()

@client.event
async def on_ready():
    # Method 1:
    # for guild in client.guilds:
    #     if guild == GUILD:
    #         break

    # METHOD 2 (using Utility Functions --> find()):
    # guild = discord.utilis.find(lambda g : g.name == GUILD, client.guilds)

    # discord.utils.find(function, iterable)-->function is applied to each element of iterable(list)-->{returns first match}.
    # find function takes two inputs.
    # find searches through client.guilds, applying the lambda function to each guild (g) in client.guilds.
    
    # METHOD 3 (using Utility Functions --> get()):
    guild = discord.utils.get(client.guilds, name=GUILD)
    
    # discord.utils.get(iterable, **attributes) --> could have multiple attributes
    # Searches inside client.guilds (list of all servers the bot is in).
    # Finds the first guild where guild.name == GUILD.

    print(
        f'{client.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})'
    )

client.run(TOKEN)