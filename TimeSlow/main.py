import discord
from discord.ext import commands
import json
import sqlite3


def config():
    with open('Config.json', 'r') as read_file:
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
        embed = discord.Embed(title="Понг!", description="Пинг: `{0}ms`".format(Ping), color=Color)
        await ctx.send(embed=embed)

    @bot.event
    async def on_ready():
        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="ts!help"))
        print('TimeSlow инициализирован')


bot.add_cog(BotEngine(bot))
bot.run(config()["token"])
