import discord
from discord.ext import commands

#
#   Constants
#

bot = commands.Bot(command_prefix='.')
bot.remove_command('help')

SERVER_ID = 702970602427777024
CHANNEL_ACCUEIL_ID = 702986042604781630
CHANNEL_PRESENTATIONS_ID = 702979184565420032
ROLE_TMP = 703011182491205652
ROLE_PARTICIPANT = 702976876003590276
ROLE_ORGANIZER = 702976196173889557

WELCOME_DM = ''.join(open('welcome_text').readlines())

#
#   Basics
#


@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game('42'))
    print('Bot is ready')


@bot.event
async def on_member_join(member):
    server = bot.get_guild(SERVER_ID)
    role_tmp = discord.utils.get(server.roles, id=ROLE_TMP)
    await member.add_roles(role_tmp)

#
#   Handling reactions on welcome message
#


@bot.event
async def on_raw_reaction_add(payload):
    channel = bot.get_channel(payload.channel_id)
    username = bot.get_user(payload.user_id)
    reaction = payload.emoji
    print(f"{username} added a {reaction.name} react.")
    if channel.id == CHANNEL_ACCUEIL_ID:
        if reaction.name == "👌":
            await username.send(WELCOME_DM)

#
#   Transfer DM presentation to correct private channel
#


@bot.event
async def on_message(message):
    if message.author == bot.user or message.guild is not None:
        return

    server = bot.get_guild(SERVER_ID)
    role_participant = discord.utils.get(server.roles, id=ROLE_PARTICIPANT)
    role_organizer = discord.utils.get(server.roles, id=ROLE_ORGANIZER)
    member = server.get_member(message.author.id)
    if not member:
        await message.author.send('Vous n\'avez pas le droit de m\'ecrire...')
        return

    if role_participant in member.roles or role_organizer in member.roles:
        await message.author.send("Cela ne sert plus a rien de me parler !")
        return

    embed = discord.Embed(title='', colour=discord.Colour.green())
    embed.set_author(name=message.author)
    embed.add_field(name='Presentation', value=message.content, inline=False)

    channel = bot.get_channel(CHANNEL_PRESENTATIONS_ID)
    msg = await channel.send(embed=embed)
    await msg.add_reaction("✅")
    await msg.add_reaction("❌")

#
#   Main code for bot
#

if __name__ == '__main__':
    with open('tok.en') as f:
        token = f.read()

    bot.run(token)
