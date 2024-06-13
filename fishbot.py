import asyncio
import os
import discord
import yt_dlp
import phrases
import nacl
from dotenv import load_dotenv
from discord.ext import commands

# stating intents for bot
intents = discord.Intents.all()
intents.message_content = True
intents.presences = True
intents.members = True

# overwriting default help command
help_command = commands.DefaultHelpCommand(no_category='Commands')

# creating instance of client and bot to connect with discord
client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix=commands.when_mentioned_or('!'), intents=intents, help_command=help_command)

# loading environment variables from .env
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

# youtube setup
yt_dlp.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio',
    'noplaylist': True
}

ffmpeg_options = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

ytdl = yt_dlp.YoutubeDL(ytdl_format_options)


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = ""

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]
        filename = data['title'] if stream else ytdl.prepare_filename(data)
        return filename


# global vars for playing music
queue = []


# global functions
def check_permission(ctx):
    return any(role.name == 'gago' for role in ctx.author.roles)


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


@bot.command(name='clear', help='I clear a given amount of chat messages')
async def clear(ctx, amount):
    print('Running Command: clear')

    await ctx.channel.purge(limit=int(amount))


@bot.command(name='join', help='I join your voice channel')
async def join(ctx):
    print('Running Command: join')

    if not ctx.author.voice:
        await ctx.send('You are not connected to a voice channel!')
        return
    else:
        v_client = ctx.voice_client
        channel = ctx.author.voice.channel
        if v_client and v_client.is_connected:
            await v_client.move_to(channel)
        else:
            await channel.connect()


@bot.command(name='leave', help='I leave the voice channel')
async def leave(ctx):
    print('Running Command: leave')

    v_client = ctx.voice_client
    if v_client and v_client.is_connected:
        await v_client.disconnect()
    else:
        ctx.send('I am not connected to a voice channel!')


@bot.command(name='play', help='I play the given music')
async def play(ctx, url=None):
    print('Running Command: play')

    discord.opus.load_opus('/opt/homebrew/Cellar/opus/1.5.2/lib/libopus.0.dylib')

    if check_permission(ctx):
        try:
            v_client = ctx.voice_client

            if not v_client.is_playing():

                if url is None:

                    if queue[0] is None:
                        ctx.send('You didn´t provide a link')
                        return
                    else:
                        yt_url = queue[0]

                else:
                    if not ("youtube.com/watch?" in url or "https:youtu.be/" in url):
                        ctx.send('This is not music from Youtube')
                        return
                    info = ytdl.extract_info(url, download=False)
                    yt_url = info['url']

                # after= needed to keep playing the queue
                v_client.play(discord.FFmpegPCMAudio(yt_url, **ffmpeg_options))
                v_client.is_playing()
                queue.remove(queue[0])
                await ctx.send('Bot is playing')

            else:
                await ctx.send('I am already playing music, use !queue to add to queue')
                return

        except Exception as e:
            print(e)
            print(e.__context__)
            await ctx.send("I am not connected to a voice channel, please use !join first.")

    else:
        await ctx.send(f'{ctx.author.mention}: You are not allowed to use this command.')
        return


@bot.command(name='stop', help='I stop the current music')
async def stop(ctx):
    print('Running Command: stop')

    if check_permission(ctx):
        v_client = ctx.voice_client

        if v_client.is_playing:
            v_client.stop()
        else:
            await ctx.send('I am not playing music')


@bot.command(name='queue', help='I queue the given music')
async def queue(ctx, url=None):
    print('Running Command: queue')

    if check_permission(ctx):
        if url is None:
            ctx.send('You have to provide a url for me to queue it')
            return

        if not ("youtube.com/watch?" in url or "https:youtu.be/" in url):
            ctx.send('This is not music from Youtube')
            return

        info = ytdl.extract_info(url, download=False)
        yt_url = info['url']
        queue.append(yt_url)

        await ctx.send('Song queued')


bot.run(TOKEN)
