import discord
from discord.ext import commands
import json
import sqlite3


def config():
    with open('Config.json', 'r') as read_file:
        return json.load(read_file)


def lang():
    with open('Language.json', 'r', encoding='utf-8') as read_file:
        return json.load(read_file)


bot = commands.Bot(command_prefix=config()["prefix"])


class BotEngine(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx):
        Ping = round(bot.latency * 1000, 2)
        if Ping < 300:
            Color = 0x00ff00
        else:
            Color = 0xff0000
        embed = discord.Embed(title=f"{lang()['ru']['Pong']}!", description=f"{lang()['ru']['Ping']}: `{Ping}ms`", color=Color)
        await ctx.send(embed=embed)

    @bot.event
    async def on_ready():
        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="ts!help"))
        print('TimeSlow инициализирован')

    @bot.event
    async def on_command_error(ctx, error):
        disagree_emoji = bot.get_emoji(765152575557074955)
        if isinstance(error, commands.CommandNotFound):
            await ctx.send(str(lang()["ru"]["UnKnCommand"]))
            await ctx.message.add_reaction(disagree_emoji)

        if isinstance(error, commands.BadArgument):
            await ctx.send(str(lang()["ru"]["BArg"]))
            await ctx.message.add_reaction(disagree_emoji)

        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(str(lang()["ru"]["MissReqArg"]))
            await ctx.message.add_reaction(disagree_emoji)

        if isinstance(error, commands.CheckFailure):
            await ctx.send(str(lang()["ru"]["AccessDenied"]))
            await ctx.message.add_reaction(disagree_emoji)


bot.add_cog(BotEngine(bot))
bot.run(config()["token"])
