import os
import discord
import youtube_dl
import phrases
from dotenv import load_dotenv
from discord.ext import commands

# stating intents for bot
intents = discord.Intents.all()
intents.message_content = True
intents.presences = True
intents.members = True


help_command = commands.DefaultHelpCommand(no_category='Commands')

# creating instance of client and bot to connect with discord
client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix=commands.when_mentioned_or('!'), intents=intents, help_command=help_command)

# loading environment variables from .env
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')


@bot.event
async def on_ready():
    for guild in bot.guilds:
        if guild.name == GUILD:
            break
    print(f'We have logged in as {bot.user}')
    print(f'Connected to {guild.name} (id: {guild.id})')


@bot.event
async def on_message(message):
    if message.author == client.user:
        return
    else:
        await bot.process_commands(message)
        print('Message received:')
        print(f'from {message.author} to {client.user} in {message.channel}')
        if str(message.content).lower == 'hello' or str(message.content).lower() == 'hi':
            print('Greeting')
            await message.channel.send('Hello!')


@bot.command(name='introduction', help='I introduce myself', cog='Utility')
async def introduce(ctx):
    print('Running Command: say_hello')

    await ctx.send(phrases.introduction_hello)
    await ctx.send(phrases.introduction_help)


@bot.command(name='admins', help='I display all server admins')
async def get_admins(ctx):
    print('Running Command: get_admins')

    await ctx.send(phrases.admins_explanation)
    async for member in ctx.guild.fetch_members():
        for role in member.roles:
            if role.name == 'Admin':
                status = ctx.guild.get_member(member.id).status
                if status == discord.Status.online or status == discord.Status.idle:
                    icon = phrases.admins_online
                if status == discord.Status.offline:
                    icon = phrases.admins_offline
                admin_message = f'{member.mention} {icon}'
                await ctx.send(admin_message)


@bot.command(name='server', help='I display all essential server information')
async def get_server_info(ctx):
    print('Running Command: get_server_info')

    name = ctx.guild.name
    owner = ctx.guild.owner.mention
    guild_id = ctx.guild.id
    member_count = ctx.guild.member_count
    icon = ctx.guild.icon
    description = ctx.guild.description
    creation_date = str(ctx.guild.created_at)[:10]

    embed = discord.Embed(
        title=f'{name} Server Information',
        description=description,
        colour=discord.Colour.red()
    )

    embed.set_thumbnail(url=icon)
    embed.add_field(name='Owner', value=owner, inline=True)
    embed.add_field(name='Created', value=creation_date, inline=True)
    embed.add_field(name='Server ID', value=guild_id, inline=False)
    embed.add_field(name='Member Count', value=member_count, inline=False)

    await ctx.send(embed=embed)


@bot.command(name='join', help='I join your voice channel')
async def join(ctx):
    print('Running Command: join')

    if not ctx.author.voice:
        await ctx.send('You are not connected to a voice channel!')
        return
    else:
        channel = ctx.author.voice.channel
        await channel.connect()


@bot.command(name='play', help='I play the given music')
async def play(ctx, url):
    print('Running Command: play')

    if not ctx.author.role == 'gago':
        await ctx.send('You are not allowed to use this command.')
        return
    #else:


bot.run(TOKEN)
