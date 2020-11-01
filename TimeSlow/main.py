import discord
from discord.ext import commands
import json
import sqlite3
from datetime import datetime

data = sqlite3.connect("Data.db")
bot = commands.Bot(command_prefix=config()["prefix"])

def config():
    with open('Config.json', 'r') as read_file:
        return json.load(read_file)


def lang():
    with open('Language.json', 'r', encoding='utf-8') as read_file:
        return json.load(read_file)


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


def disagree_emoji():
    return bot.get_emoji(765152575557074955)


async def is_developer(ctx):
    return ctx.author.id == config()["devID"]


class BotEngine(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def setup(self, ctx):
        if ctx.guild.region == "russia0":
            language = "ru"
        else:
            language = "en"
        guildvalues = (ctx.guild.id, ctx.guild.name, 2, datetime, 1, 0, 0, language)
        cur = data.cursor()
        cur.execute(f"INSERT INTO guilds VALUES(?, ?, ?, ?, ?, ?, ?, ?);", guildvalues)
        data.commit()
        cur.close()
        await ctx.add_reaction(disagree_emoji())

    @commands.command(aliases=['Settings', 's'])
    async def settings(self, ctx, option, value):
        mod_possible_value = [1, 2, 3]
        if option == config()["db_guild_possible_options"][0]:
            if mod_possible_value.count(value) == 1:
                await db_dump_req(f"UPDATE guilds SET mod = {int(value)} WHERE id = {ctx.guild.id};")
            else:
                await ctx.send(f"{lang()['ru']['Parameter']} `{option}` {lang()['ru']['CannotSet']} {value}")
                await ctx.add_reaction(disagree_emoji())

        elif option == config()["db_guild_possible_options"][1]:
            role = convert_to_role(value)
            await db_dump_req(f"UPDATE guilds SET mute_role_id = {int(role.id)} WHERE id = {ctx.guild.id};")

        elif option == config()["db_guild_possible_options"][2]:
            if value != 0:
                txtchannel = convert_to_channel(value)
                Id = txtchannel.id
            else:
                Id = 0
            await db_dump_req(f"UPDATE guilds SET log_channel_id = {int(Id)} WHERE id = {ctx.guild.id};")
        else:
            await ctx.send(f"{lang()['ru']['Parameter']} `{option}` {lang()['ru']['NotFound']}")
            await ctx.add_reaction(disagree_emoji())

    @commands.command()
    async def ping(self, ctx):
        ping = round(bot.latency * 1000, 2)
        if ping < 300:
            color = 0x00ff00
        else:
            color = 0xff0000
        embed = discord.Embed(title=f"{lang()['ru']['Pong']}!", description=f"{lang()['ru']['Ping']}: `{ping}ms`", color=color)
        await ctx.send(embed=embed)

    @bot.event
    async def on_ready():
        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=f"{config()['prefix']}help"))
        print('TimeSlow инициализирован')

    @bot.event
    async def on_command_error(ctx, error):
        if isinstance(error, commands.CommandNotFound):
            await ctx.send(str(lang()["ru"]["UnKnCommand"]))
            await ctx.message.add_reaction(disagree_emoji())

        if isinstance(error, commands.BadArgument):
            await ctx.send(str(lang()["ru"]["BArg"]))
            await ctx.message.add_reaction(disagree_emoji())

        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(str(lang()["ru"]["MissReqArg"]))
            await ctx.message.add_reaction(disagree_emoji())

        if isinstance(error, commands.CheckFailure):
            await ctx.send(str(lang()["ru"]["AccessDenied"]))
            await ctx.message.add_reaction(disagree_emoji())


bot.add_cog(BotEngine(bot))
bot.run(config()["token"])
