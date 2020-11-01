import discord
from discord.ext import commands
import json
import sqlite3
from datetime import datetime


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


def convert_to_member(value: discord.Member):
    return value


def convert_to_channel(value: discord.TextChannel):
    return value


def convert_to_role(value: discord.Role):
    return value


def agree_emoji():
    return bot.get_emoji(764938637862371348)


def disagree_emoji():
    return bot.get_emoji(765152575557074955)


async def is_developer(ctx):
    return ctx.author.id == config()["devID"]


class BotEngine(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.check(is_developer)
    async def setup(self, ctx):
        dev = developer()
        count = await db_load_req(f"SELECT COUNT(*) as count FROM guilds WHERE id = {ctx.guild.id}")
        if count == 0:
            print(ctx.guild.region)
            if str(ctx.guild.region) == "russia":
                language = "ru"
            else:
                language = "en"
            guildvalues = (ctx.guild.id, str(ctx.guild.name), 2, None, bool(1), 0, 0, language)
            cur = data.cursor()
            cur.execute("INSERT INTO guilds VALUES(?, ?, ?, ?, ?, ?, ?, ?);", guildvalues)
            data.commit()
            await ctx.message.add_reaction(agree_emoji())
        elif count == 1:
            await ctx.send("Действия не требуются")
        else:
            print('DataBaseError', ctx.guild.name, ctx.guild.id, datetime)
            await dev.send('DataBaseError', ctx.guild.name, ctx.guild.id, datetime)
            await ctx.send('Критическая ошибка базы данных, разработчик уже извёщен об ошибке')
            await ctx.message.add_reaction(disagree_emoji())

    @commands.command(aliases=['Settings', 's'])
    @commands.check(is_developer)
    async def settings(self, ctx, option, value):
        dev = developer()
        mod_possible_value = [1, 2, 3]
        language_possible_value = ['ru', 'en']
        count = await db_load_req(f"SELECT COUNT(*) as count FROM guilds WHERE id = {ctx.guild.id};")
        language = await db_load_req(f"SELECT language FROM guilds WHERE id = {ctx.guild.id};")
        if count == 1:
            if option == config()["db_guild_possible_options"][0]:
                if mod_possible_value.count(int(value)) == 1:
                    await db_dump_req(f"UPDATE guilds SET mod = {int(value)} WHERE id = {ctx.guild.id};")
                    await ctx.message.add_reaction(agree_emoji())
                else:
                    await ctx.send(f"{lang()[language]['Parameter']} `{option}` {lang()[language]['CannotSet']} {value}")
                    await ctx.message.add_reaction(disagree_emoji())

            elif option == config()["db_guild_possible_options"][1]:
                role = convert_to_role(value)
                await db_dump_req(f"UPDATE guilds SET mute_role_id = {int(role.id)} WHERE id = {ctx.guild.id};")
                await ctx.message.add_reaction(agree_emoji())

            elif option == config()["db_guild_possible_options"][2]:
                if value != 0:
                    txtchannel = convert_to_channel(value)
                    channelid = txtchannel.id
                else:
                    channelid = 0
                await db_dump_req(f"UPDATE guilds SET log_channel_id = {int(channelid)} WHERE id = {ctx.guild.id};")
                await ctx.message.add_reaction(agree_emoji())

            elif option == config()["db_guild_possible_options"][3]:
                if language_possible_value.count(str(value)) == 1:
                    await db_dump_req(f'UPDATE guilds SET language = "{value}" WHERE id = {ctx.guild.id};')
                    await ctx.message.add_reaction(agree_emoji())
                else:
                    await ctx.send(f"{lang()[language]['Parameter']} `{option}` {lang()[language]['CannotSet']} {value}")
                    await ctx.message.add_reaction(disagree_emoji())

            else:
                await ctx.send(f"{lang()[language]['Parameter']} `{option}` {lang()[language]['NotFound']}")
                await ctx.message.add_reaction(disagree_emoji())

        elif count == 0:
            await ctx.send(f"Что то пошло не так. Я не смог дбавить сервер в базу данных автоматически, но вы можете сделать это вручную с помощью команды `{config()['prefix']}setup`")
            await ctx.message.add_reaction(disagree_emoji())
        else:
            print('DataBaseError', ctx.guild.name, ctx.guild.id, datetime)
            await dev.send('DataBaseError', ctx.guild.name, ctx.guild.id, datetime)
            await ctx.send('Критическая ошибка базы данных, разработчик уже извёщен об ошибке')
            await ctx.message.add_reaction(disagree_emoji())

    @commands.command()
    async def ping(self, ctx):
        language = await db_load_req(f"SELECT language FROM guilds WHERE id = {ctx.guild.id};")
        print(language)
        ping = round(bot.latency * 1000, 2)
        if ping < 300:
            color = 0x00ff00
        else:
            color = 0xff0000
        embed = discord.Embed(title=f"{lang()[language]['Pong']}!", description=f"{lang()[language]['Ping']}: `{ping}ms`", color=color)
        await ctx.send(embed=embed)

    @bot.event
    async def on_ready():
        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=f"{config()['prefix']}help"))
        print('TimeSlow инициализирован')

    @bot.event
    async def on_command_error(ctx, error):
        language = await db_load_req(f"SELECT language FROM guilds WHERE id = {ctx.guild.id};")
        if isinstance(error, commands.CommandNotFound):
            await ctx.send(str(lang()[language]["UnKnCommand"]))
            await ctx.message.add_reaction(disagree_emoji())

        if isinstance(error, commands.BadArgument):
            await ctx.send(str(lang()[language]["BArg"]))
            await ctx.message.add_reaction(disagree_emoji())

        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(str(lang()[language]["MissReqArg"]))
            await ctx.message.add_reaction(disagree_emoji())

        if isinstance(error, commands.CheckFailure):
            await ctx.send(str(lang()[language]["AccessDenied"]))
            await ctx.message.add_reaction(disagree_emoji())


bot.add_cog(BotEngine(bot))
bot.run(config()["token"])
