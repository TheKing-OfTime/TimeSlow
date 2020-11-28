import discord
from datetime import datetime
from discord.ext import commands
import json
import sqlite3
import re


def config():
    with open('Config.json', 'r') as read_file:
        return json.load(read_file)


def lang():
    with open('Language.json', 'r', encoding='utf-8') as read_file:
        return json.load(read_file)


data = sqlite3.connect("Data.db")
bot = commands.Bot(command_prefix=config()["prefix"])


def developer():
    return bot.get_user(config()["devID"])


async def db_dump_req(sql_request):
    cur = data.cursor()
    cur.execute(sql_request)
    data.commit()
    cur.close()


async def db_load_req(sql_request):
    cur = data.cursor()
    cur.execute(sql_request)
    return cur.fetchone()[0]


async def db_valid_cheker(ctx):
    try:
        count = await db_load_req(f"SELECT COUNT(*) as count FROM guilds WHERE id = {ctx.guild.id}")
    except sqlite3.OperationalError:
        print('DataBaseError', ctx.guild.name, ctx.guild.id, datetime.now())
        await developer().send(f'DataBaseError {ctx.guild.name} {ctx.guild.id} {datetime.now()}')
        await ctx.send('Критическая ошибка базы данных, разработчик уже извёщен об ошибке')
        await ctx.message.add_reaction(disagree_emoji())
        return False

    if count == 1:
        return True
    elif count == 0:
        await ctx.send(f"Что то пошло не так. Я не смог дбавить сервер в базу данных автоматически, но вы можете сделать это вручную с помощью команды `{config()['prefix']}setup`")
        await ctx.message.add_reaction(disagree_emoji())
        return False
    else:
        print('DataBaseError', ctx.guild.name, ctx.guild.id, datetime)
        await developer().send(f'DataBaseError {ctx.guild.name} {ctx.guild.id} {datetime.now()}')
        await ctx.send('Критическая ошибка базы данных, разработчик уже извёщен об ошибке')
        await ctx.message.add_reaction(disagree_emoji())
        return False


async def get_guild_language(ctx):
    if await db_valid_cheker(ctx):
        language = await db_load_req(f"SELECT language FROM guilds WHERE id = {ctx.guild.id};")
        return language
    else:
        return "en"


def convert_to_member(value):
    print(value)
    return value


def convert_to_channel(value):
    try:
        channelid = re.sub("[^0-9]", "", str(value))
        channel = bot.get_channel(int(channelid))
    except:
        channel = None
    return channel


def convert_to_role(guild, value):
    try:
        roleid = re.sub("[^0-9]", "", str(value))
        role = guild.get_role(int(roleid))
    except:
        role = None
    return role


def agree_emoji():
    return bot.get_emoji(764938637862371348)


def warning_emoji():
    return bot.get_emoji(776432019940573244)


def disagree_emoji():
    return bot.get_emoji(765152575557074955)


async def is_developer(ctx):
    return ctx.author.id == config()["devID"]


async def is_Moderator(ctx):
    return ctx.author.id == config()["devID"] or ctx.author.guild_permissions.manage_guild


async def is_Admin(ctx):
    return ctx.author.id == config()["devID"] or ctx.author.guild_permissions.administrator
