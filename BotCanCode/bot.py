import conf
import discord
import os
import strings

bot = discord.Client()

#
#   Basics
#


@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game('42'))
    print('>>> Bot is ready.')


@bot.event
async def on_member_join(member):
    server = bot.get_guild(conf.SERVER_ID)
    role_tmp = server.get_role(conf.ROLE_TMP)
    print('>>> {member.nick} joined the server.')
    await member.add_roles(role_tmp)

#
#   Handling reactions on welcome message
#


@bot.event
async def on_raw_reaction_add(payload):
    channel = bot.get_channel(payload.channel_id)
    username = bot.get_user(payload.user_id)
    reaction = payload.emoji
    if channel.id == conf.CHANNEL_ACCUEIL_ID:
        print('>>> {username} added a {reaction.name} react.')
        if reaction.name == '\N{OK HAND SIGN}':
            await username.send(strings.WELCOME_DM)

#
#   Transfer DM presentation to correct private channel
#


@bot.event
async def on_message(message):
    if message.author == bot.user or message.guild is not None:
        return

    print('>>> {message.author} sent a message to the bot:\n"{message.content}".')

    server = bot.get_guild(conf.SERVER_ID)
    role_participant = server.get_role(conf.ROLE_PARTICIPANT)
    role_organizer = server.get_role(conf.ROLE_ORGANIZER)
    member = server.get_member(message.author.id)
    if not member:
        await message.author.send(strings.BANNED)
        return

    if role_participant in member.roles or role_organizer in member.roles:
        await message.author.send(strings.ALREADY_ACCEPTED)
        return

    embed = discord.Embed(title='', colour=discord.Colour.green())
    embed.set_author(name=message.author)
    embed.add_field(name='Présentation', value=message.content, inline=False)

    channel = bot.get_channel(conf.CHANNEL_PRESENTATIONS_ID)
    msg = await channel.send(embed=embed)
    await msg.add_reaction('\N{WHITE HEAVY CHECK MARK}')
    await msg.add_reaction('\N{CROSS MARK}')

#
#   Main code for bot
#

if __name__ == '__main__':
    bot.run(conf.BOT_TOKEN)
