import os
import random

import discord
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Enable necessary intents
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

client = discord.Client(intents = intents)

# Bot connection message
@client.event
async def on_ready():
    print(f'{client.user.name} has connected to Discord!')

# Welcoming new members
@client.event
async def on_member_join(member):
    await member.create_dm()
    await member.dm_channel.send(
        f'Hi {member.name}, welcome to my Discord server!'
    )

# Responding to Events
@client.event
async def on_message(message):
    # Check if message is sent by bot itself
    if message.author == client.user:
        return

    brooklyn_99_quotes = [
        'I\'m the human form of the 💯 emoji.',
        'Bingpot!',
        (
            'Cool. Cool cool cool cool cool cool cool, '
            'no doubt no doubt no doubt no doubt.'
        ),
    ]

    # Return random string if input = 99!
    if message.content == '99!':
        response = random.choice(brooklyn_99_quotes)
        await message.channel.send(response)
    elif message.content == 'raise-exception':
        raise discord.DiscordException


# Store error in a file 
@client.event
async def on_error(event, *args, **kwargs):
    # Create err file
    with open('err.log', 'a') as file:
        if event == 'on_message':
            file.write(f'Unhandled message: {args[0]}\n')
        else:
            raise
# event is the event at which error occured
# args contains all the input parameters passed to event

client.run(TOKEN)