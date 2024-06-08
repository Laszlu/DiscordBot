# This example requires the 'message_content' intent.
import os
import discord
import fish_commands as fish
from dotenv import load_dotenv

# stating intents for bot
intents = discord.Intents.default()
intents.message_content = True
intents.presences = True
intents.members = True

# creating instance of client to connect with discord
client = discord.Client(intents=intents)

# loading environment variables from .env
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')


@client.event
async def on_ready():
    for guild in client.guilds:
        if guild.name == GUILD:
            break
    print(f'We have logged in as {client.user}')
    print(f'Connected to {guild.name} (id: {guild.id})')


@client.event
async def on_message(message):
    if message.author == client.user:
        return
    else:
        print('Message received:')
        print(f'from {message.author} to {client.user} in {message.channel}')
        if message.content.startswith('--'):
            print('Getting commands')
            await fish.get_command(message)


client.run(TOKEN)
