import discord
from datetime import datetime
from discord.ext import commands
import json
import sqlite3
from sys import version_info
import re


def Config():
    with open('Config.json', 'r') as read_file:
        return json.load(read_file)


def Lang():
    with open('Language.json', 'r', encoding='utf-8') as read_file:
        return json.load(read_file)


config = Config()
lang = Lang()

data = sqlite3.connect("Data.db")
bot = commands.Bot(command_prefix=config["prefix"],
                   intents=discord.Intents(guilds=True, messages=True, typing=False, emojis=True, members=True))


def developer():
    return bot.get_user(config["devID"])


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
        await ctx.send(
            f"Что то пошло не так. Я не смог дбавить сервер в базу данных автоматически, но вы можете сделать это вручную с помощью команды `{config['prefix']}setup`")
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
    return ctx.author.id == config["devID"]


async def is_Moderator(ctx):
    return ctx.author.id == config["devID"] or ctx.author.guild_permissions.manage_guild


async def is_Admin(ctx):
    return ctx.author.id == config["devID"] or ctx.author.guild_permissions.administrator


async def help_list(ctx):
    embed = discord.Embed(title=f'{lang[await get_guild_language(ctx)]["Help"]}', color=discord.Colour.blurple(),
                          description="Структура команд `имя[Псевдонимы]{обязательный аргумент}(не обязатнльный аргумент)`\n Если у вас остались вопросы, то можете смело заходить на [сервер поддержки](https://discord.gg/8epHXKA)")
    embed.add_field(name=f"Общие:",
                    value="`ping`   Вывод задержки \n`guildinfo[serverinfo, sinfo, ginfo]`   Информация о сервере \n`memberinfo[minfo]{member}`   Информация о пользователе \n`invite[i]`   Пригласить бота к себе на сервер\n`about[d]`   Краткое описание и техническая информация\n`donate[d]`   Если вдруг захочеся поддержать автора",
                    inline=False)
    if await is_Moderator(ctx):
        embed.add_field(name=f"Доступные модераторам:",
                        value="`slowdown[sd]{member}{interval}(minutes)`   Включить медленный режим у пользователя \n`unslowdown[usd]{member}`   Выключить медленный режим у пользователя\n`channelslowdown[chsd]{member}{interval}(minutes)`   Включить медленный режим в канале \n`channelunslowdown[chusd]{member}`   Выключить медленный режим в канале",
                        inline=False)
    if await is_Admin(ctx):
        embed.add_field(name=f"Доступные администраторам:",
                        value="`settings[s]{option}{value}`   Изменить параметры работы бота *больше информации ts!help settings* \n`setup`   Команда для первой инициализации, если она не смогла пройти автоматически",
                        inline=False)
    embed.set_footer(text=ctx.author, icon_url=ctx.author.avatar_url)
    await ctx.send(embed=embed)


async def help_settings(ctx):
    embed = discord.Embed(title=f'{lang[await get_guild_language(ctx)]["Help"]}', color=discord.Colour.blurple(),
                          description='settings[s]{option}{value}')
    embed.add_field(name=f"Режим работы",
                    value='`ts!settings mod {value}`\n`1`: При выходе за таймер сообщение удаляется\n`2`: Первый режим + отправка удалённого сообщения в ЛС\n`3`: Выдача мута пользовтелю на время таймера',
                    inline=False)
    embed.add_field(name=f"Канал логирования",
                    value='`ts!settings log_channel {value}`\n`Канал`: Установка заданного канала как "Канала логирования"',
                    inline=False)
    embed.add_field(name=f"Роль мута",
                    value='`ts!settings mute_role {value}`\n`Роль`: Установка заданной роли как "Роли мута"',
                    inline=False)
    embed.add_field(name=f"Язык",
                    value='`ts!settings language {value}`\n`ru`: Установка русского языка\n`en`: Установка английского языка **НЕ рекомендуется**',
                    inline=False)
    await ctx.send(embed=embed)


async def about_message(ctx):
    embed = discord.Embed(title="О приложении",
                          description="Основной задачей бота на данный момент является борьба с оверпостерами.",
                          colour=discord.Colour.blurple())
    embed.add_field(name="Версия бота", value=config["bot_version"])
    embed.add_field(name="Версия discord.py", value=discord.__version__)
    embed.add_field(name="Версия Python", value=f"{version_info.major}.{version_info.minor}.{version_info.micro}")
    embed.set_footer(text=f"Разработчик: TheKingOfTime#5595", icon_url="https://images-ext-2.discordapp.net/external/ymzuQwwUcu76ZYHHGtkwbln1ijE025FCtqgtZfrsmIM/%3Fsize%3D2048/https/cdn.discordapp.com/avatars/500020124515041283/e8364a838285245b1af76b9250ec2d55.webp")
    await ctx.send(embed=embed)
