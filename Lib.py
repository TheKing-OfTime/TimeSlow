import discord
from datetime import datetime
from discord.ext import commands
import json
import sqlite3
from sys import version_info
import re


def Config():
    with open('c:/Ya/DiscordBot/TimeSlow/Config.json', 'r') as read_file:
        return json.load(read_file)


def Lang():
    with open(f'c:/Ya/DiscordBot/TimeSlow/Language.json', 'r', encoding='utf-8') as read_file:
        return json.load(read_file)


config = Config()
lang = Lang()

data = sqlite3.connect("c:/Ya/DiscordBot/TimeSlow/Data.db")
bot = commands.Bot(command_prefix="ts!",
                   intents=discord.Intents(guilds=True, messages=True, typing=False, emojis=True, members=False))
console_log = 830490410778099752


def developer():
    return bot.get_user(config["devID"])


async def db_dump_req(sql_request):
    try:
        cur = data.cursor()
        cur.execute(sql_request)
        data.commit()
        cur.close()
    except Exception as error:
        print(error)


async def db_load_req(sql_request):
    try:
        cur = data.cursor()
        cur.execute(sql_request)
        return cur.fetchone()[0]
    except Exception as error:
        print(error)


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
    return bot.get_emoji(837961320107212810)


def loading_emoji():
    return bot.get_emoji(830796791837491210)


def is_developer(ctx):
    return ctx.author.id == config["devID"]


def is_Moderator(ctx):
    return ctx.author.id == config["devID"] or ctx.author.guild_permissions.manage_guild


def is_Admin(ctx):
    return ctx.author.id == config["devID"] or ctx.author.guild_permissions.administrator


async def help_list(ctx):
    guild_language = await get_guild_language(ctx)
    if guild_language == "ru":
        embed = discord.Embed(title=f'{lang[guild_language]["Help"]}', color=discord.Colour.blurple(),
                              description="Структура команд `имя[Псевдонимы]{обязательный аргумент}(не обязательный аргумент)`\n Если у вас остались вопросы, то можете смело заходить на [сервер поддержки](https://discord.gg/8epHXKA)")
        embed.add_field(name="Общие:",
                        value="`ping`   Вывод задержки \n`guildinfo[serverinfo, sinfo, ginfo]`   Информация о сервере \n`memberinfo[minfo]{member}`   Информация о пользователе \n`invite[i]`   Пригласить бота к себе на сервер\n`about[a]`   Краткое описание и техническая информация\n`donate[d]`   Если вдруг захочется поддержать автора",
                        inline=False)
        if is_Moderator(ctx):
            embed.add_field(name="Доступные модераторам:",
                            value="`slowdown[sd]{member}{interval}(minutes)`   Включить медленный режим у пользователя \n`unslowdown[usd]{member}`   Выключить медленный режим у пользователя\n`channelslowdown[chsd]{channel}{interval}(minutes)`   Включить медленный режим в канале \n`channelunslowdown[chusd]{channel}`   Выключить медленный режим в канале",
                            inline=False)
        if is_Admin(ctx):
            embed.add_field(name="Доступные администраторам:",
                            value="`settings[s]{option}{value}`   Изменить параметры работы бота *больше информации ts!help settings* \n`setup`   Команда для первой инициализации, если она не смогла пройти автоматически",
                            inline=False)
        embed.add_field(name="Экспериментальные:",
                        value='`rollout(target number)(target id)`   Показывает информацию о текущем развертываний новых функций.\n `discordstatus[ds](detail/last)(target id)(detail)`   Показывает информацию о текущем статусе серверов Discord')

        embed.set_footer(text=ctx.author, icon_url=ctx.author.avatar_url)
    else:
        embed = discord.Embed(title=f'{lang[guild_language]["Help"]}', color=discord.Colour.blurple(),
                              description="Command structure `name[aliases]{required arg}(optional arg)`\n If you still have questions, you can go to the [support server](https://discord.gg/8epHXKA)")
        embed.add_field(name="Common:",
                        value="`ping`   Latency output \n`guildinfo[serverinfo, sinfo, ginfo]`   server info \n`memberinfo[minfo]{member}`   member info \n`invite[i]`   Invite the bot in your own server\n`about[a]`   Brief description and technical information",
                        inline=False)
        if is_Moderator(ctx):
            embed.add_field(name=f"Available to Mods:",
                            value="`slowdown[sd]{member}{interval}(minutes)`   Enable slowmode for the member \n`unslowdown[usd]{member}`   Disable slowmode for the member\n`channelslowdown[chsd]{channel}{interval}(minutes)`   Enable slowmode in a channel \n`channelunslowdown[chusd]{channel}`   Disable slowmode in a channel",
                            inline=False)
        if is_Admin(ctx):
            embed.add_field(name=f"Available to Admins:",
                            value="`settings[s]{option}{value}`   Change the parameters of the bot *more information ts!help settings* \n`setup`   Command for first initialization, if it failed to pass automatically",
                            inline=False)
        embed.add_field(name="Experimental:",
                        value='`rollout(target number)(target id)`   Shows information about current feature rollouts.\n discordstatus[ds](detail/last)(target id)(detail)`   Shows information about current discord status.')

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
    guild_language = await get_guild_language(ctx)
    embed = discord.Embed(title=lang[guild_language]['About_title'],
                          description=lang[guild_language]['About_description'],
                          colour=discord.Colour.blurple())
    embed.add_field(name=lang[guild_language]['Bot_Version'], value=config["bot_version"])
    embed.add_field(name=lang[guild_language]['discord.py_Version'], value=discord.__version__)
    embed.add_field(name=lang[guild_language]['Python_version'], value=f"{version_info.major}.{version_info.minor}.{version_info.micro}")
    embed.add_field(name="Github", value="[click](https://github.com/TheKing-OfTime/TimeSlow/tree/main/TimeSlow)")
    embed.set_thumbnail(url="https://cdn.discordapp.com/avatars/750415350348382249/4f54a5942a53b3ae0495d1b640e55b2f.webp")
    embed.set_footer(text=f"{lang[guild_language]['Developer']}: TheKingOfTime#5595", icon_url=developer().avatar_url)
    await ctx.send(embed=embed)


async def sd_log(ctx, member, interval, aoff):
    try:
        channel = bot.get_channel(await db_load_req(f"SELECT log_channel_id FROM guilds WHERE id = {ctx.guild.id};"))
        embed = discord.Embed(title="Медленный режим включён", colour=discord.Color.red())
        embed.add_field(name="Пользователь", value=member)
        embed.add_field(name="Модератор", value=ctx.author)
        embed.add_field(name="Интервал", value=interval)
        embed.add_field(name="Отключение через", value=f"{aoff} минут")
        embed.set_footer(text=ctx.author, icon_url=ctx.author.avatar_url)
        embed.set_thumbnail(url=member.avatar_url)
        await channel.send(embed=embed)
    except Exception as error:
        print(error)


async def usd_log(ctx, member, moder):
    try:
        channel = bot.get_channel(await db_load_req(f"SELECT log_channel_id FROM guilds WHERE id = {ctx.guild.id};"))
        embed = discord.Embed(title="Медленный режим отключён", colour=discord.Color.green())
        embed.add_field(name="Пользователь", value=member)
        embed.add_field(name="Модератор", value=moder)
        embed.set_footer(text=ctx.author, icon_url=ctx.author.avatar_url)
        embed.set_thumbnail(url=member.avatar_url)
        await channel.send(embed=embed)
    except Exception as error:
        print(error)
