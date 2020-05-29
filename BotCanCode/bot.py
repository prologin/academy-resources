from discord.ext import commands
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from string import Template
import conf
import discord
import os
import smtplib
import strings


bot = commands.Bot(command_prefix='!')


#
#   Basics
#


@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game('Learning Python'))
    print('>>> Bot is ready.', flush=True)


@bot.event
async def on_member_join(member):
    server = bot.get_guild(conf.SERVER)
    role_tmp = server.get_role(conf.ROLE_TMP)
    print(f'>>> {member.nick} joined the server.', flush=True)
    await member.add_roles(role_tmp)


#
#   Handling reactions on welcome message
#


@bot.event
async def on_raw_reaction_add(payload):
    channel = bot.get_channel(payload.channel_id)
    username = bot.get_user(payload.user_id)
    reaction = payload.emoji
    if channel.id == conf.CHANNEL_ACCUEIL:
        print(f'>>> {username} added a {reaction.name} react.', flush=True)
        if reaction.name == '\N{OK HAND SIGN}':
            await username.send(strings.WELCOME_DM)


#
#   Transfer DM presentation to correct private channel
#


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.guild is not None:
        await bot.process_commands(message)
        return
	
    print(f'>>> {message.author} sent a message to the bot:\n"{message.content}".', flush=True)

    server = bot.get_guild(conf.SERVER)
    role_participant = server.get_role(conf.ROLE_PARTICIPANT)
    role_organizer = server.get_role(conf.ROLE_ORGANIZER)
    member = server.get_member(message.author.id)
    if not member:
        await message.author.send(strings.BANNED)
        await bot.process_commands(message)
        return

    if role_participant in member.roles or role_organizer in member.roles:
        await message.author.send(strings.ALREADY_ACCEPTED)
        await bot.process_commands(message)
        return

    embed = discord.Embed(title='', colour=discord.Colour.green())
    embed.set_author(name=message.author)
    embed.add_field(name='Présentation', value=message.content, inline=False)

    channel = bot.get_channel(conf.CHANNEL_PRESENTATIONS)
    msg = await channel.send(embed=embed)
    await msg.add_reaction('\N{WHITE HEAVY CHECK MARK}')
    await msg.add_reaction('\N{CROSS MARK}')
    await bot.process_commands(message)


#
#   Activity Mailing
#


def get_contacts(filename):
    contacts = {}

    try:
        with open(filename) as f:
            tmp_contacts = f.read().splitlines()
            for contact in tmp_contacts:
                name, email = contact.split(',')[0], contact.split(',')[1]
                contacts[name] = email
    except OSError as e:
        print(f"bot-can-code: {e.strerror}", file=sys.stderr)

    return contacts


def read_template(filename):
    try:
        with open(filename) as template_file:
            template_file_content = template_file.read()

    except OSError as e:
        print(f"bot-can-code: {e.strerror}", file=sys.stderr, flush=True)

    return Template(template_file_content)


@bot.command()
async def notif(ctx, activity, time):
    print('>>> Entered notif command', flush=True)

    if ctx.channel.id != conf.CHANNEL_BOT:
        print('>>> Invalid channel', flush=True)
        return

    msg = f'Session "{activity}" prévue à {time}'

    print(f'>>> Trying to send {msg}', flush=True)

    server = bot.get_guild(conf.SERVER)

    # ping @Organizer on #staff

    role_organizer = server.get_role(conf.ROLE_ORGANIZER)
    channel = bot.get_channel(conf.CHANNEL_STAFF)
    await channel.send(f'{role_organizer.mention} {msg}')


    # ping @Partipant on #general

    role_participant = server.get_role(conf.ROLE_PARTICIPANT)
    channel = bot.get_channel(conf.CHANNEL_NEWS)
    await channel.send(f'{role_participant.mention} {msg}')


    # Mailing
    conn = smtplib.SMTP(host=conf.MAIL_HOST, port=conf.MAIL_PORT)
    conn.starttls()
    conn.login(conf.MAIL_ADDRESS, conf.MAIL_PASSWORD)

    contacts = get_contacts('contacts.csv')
    message_template = read_template('message.txt')

    for name, email in contacts.items():
        print(f'>>> Trying to email {name}:{email}', flush=True)
        msg = MIMEMultipart()
        message = message_template.substitute(PERSON_NAME=name, ACTIVITY=activity, TIME=time)

        msg['From'] = conf.MAIL_ADDRESS
        msg['To'] = email
        msg['Subject'] = f'[Académie Prologin] Session "{activity}" à {time}'

        msg.attach(MIMEText(message, 'plain'))

        conn.send_message(msg)
        print('>>> msg should be sent', flush=True)

        del msg

    conn.quit()


#
#   Main code for bot
#

if __name__ == '__main__':
    bot.run(conf.BOT_TOKEN)
