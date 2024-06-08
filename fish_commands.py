import discord
import phrases


async def get_command(message):
    if 'hello' in message.content[2:9]:
        await introduce_self(message)
    if 'help' in message.content[2:9]:
        await get_help(message)
    if 'admins' in message.content[2:9]:
        await get_admins(message)


async def introduce_self(message):
    print('Running Command: say_hello')
    await message.channel.send(phrases.introduction_hello)
    await message.channel.send(phrases.introduction_help)


async def get_help(message):
    print('Running Command: get_help')
    await message.channel.send(phrases.help_introduction)
    await message.channel.send(phrases.help_hello)
    await message.channel.send(phrases.help_admins)


async def get_admins(message):
    print('Running Command: get_admins')
    await message.channel.send(phrases.admins_explanation)
    async for member in message.guild.fetch_members():
        for role in member.roles:
            if role.name == 'Admin':
                status = message.guild.get_member(member.id).status
                if status == discord.Status.online or status == discord.Status.idle:
                    icon = phrases.admins_online
                if status == discord.Status.offline:
                    icon = phrases.admins_offline
                adminMessage = f'{member.mention} {icon}'
                await message.channel.send(adminMessage)


