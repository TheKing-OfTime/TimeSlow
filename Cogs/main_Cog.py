import asyncio
import requests
import mmh3
import discord
import time
import random
import math
import sdc_api_py as sdc_api
from datetime import datetime
from discord.ext import commands
from discord.ext.tasks import loop
from Lib import get_guild_language, disagree_emoji, lang, config, about_message, help_list, help_settings, db_load_req, data, developer, is_Admin, agree_emoji

lst_of_pr = []

class MainCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.uptime = time.time()
        self.update_presence.start()
        self.urls = ["https://cdn.discordapp.com/attachments/478984255377113095/866459741059809320/go_fuck_yourself.mp4", "https://thecore.city/ping.webm"]
        self.rollouts_data = requests.get("https://rollouts.advaith.workers.dev/").json()

    @commands.command(aliases=["Help", "h"])
    async def help(self, ctx, arg1=None):
        if arg1 == None:
            await help_list(ctx)
        elif arg1 == "settings":
            await help_settings(ctx)

    @commands.command()
    async def ping(self, ctx:commands.Context):
        glang = await get_guild_language(ctx)
        uptime = time.gmtime(time.time() - self.uptime)
        ping = round(self.bot.latency * 1000, 2)
        if ping < 160:
            color = discord.Colour.green()
        elif ping < 200:
            color = discord.Colour.orange()
        else:
            color = discord.Colour.red()
        message = await ctx.send("Определяю")
        ping2 = message.created_at - ctx.message.created_at

        embed = discord.Embed(title=f"{lang[glang]['Pong']}!",
                              description=f"{lang[glang]['Ping']}:\n`{ping}ms`\n`{ping2.microseconds/2000}ms`\nUptime {uptime.tm_hour + ((uptime.tm_mday - 1) * 24)}h {uptime.tm_min}m {uptime.tm_sec}s",
                              color=color)

        await message.edit(content='', embed=embed)

    @commands.command(aliases=["Invite", "i"])
    async def invite(self, ctx):
        embed = discord.Embed(title=lang[await get_guild_language(ctx)]['Invite'], url=config["invite"],
                              color=0x7289da)
        embed.set_author(name=ctx.author, icon_url=ctx.author.avatar_url)
        await ctx.send(embed=embed)

    @commands.command(aliases=["About", "a"])
    async def about(self, ctx):
        await about_message(ctx)

    @commands.command(aliases=["d", 'Donate'])
    async def donate(self, ctx):
        language = await get_guild_language(ctx)
        if language == "ru":
            embed = discord.Embed(title="Донат",
                                  description="Если вам вдруг захочется поддержать автора проекта, то вы смело можете это сделать:\n[QIWI](https://qiwi.com/n/THEKINGOFTIME)\nНа карту: 4276400029387983",
                                  colour=discord.Colour.from_rgb(217, 171, 42))
            embed.set_footer(text=ctx.author, icon_url=ctx.author.avatar_url)
        else:
            embed = discord.Embed(title="Donate",
                                  description="Donation unavailable in your country",
                                  colour=discord.Colour.from_rgb(217, 171, 42))
            embed.set_footer(text=ctx.author, icon_url=ctx.author.avatar_url)
        await ctx.send(embed=embed)

    @commands.command(aliases=["rc"])
    @commands.check(is_Admin)
    async def regionchanger(self, ctx: commands.Context, region=None):
        try:
            await ctx.guild.edit(region=discord.VoiceRegion.us_west)
        except Exception as e:
            await ctx.send(e)
        else:
            await ctx.send("Done")


    @commands.Cog.listener()
    async def on_ready(self):
        print('TimeSlow инициализирован')
        print(self.bot.user.name, self.bot.command_prefix)
        bots = sdc_api.Bots(self.bot, config["SDCtoken"])
        bots.create_loop()
        await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=f"ts!help | Серверов: {len(self.bot.guilds)}"))
        #self.get_rollout_data.start()

    # @commands.Cog.listener()
    # async def on_message(self, message):
    #    current_content = message.content.lower()
    #    current_content = current_content.replace(" ", "")
    #    if (("пидор" in current_content) or ("пидар" in current_content)) and developer() in message.mentions and is_pidor():
    #        try:
    #            await message.add_reaction("🇳")
    #            await message.add_reaction("🇴")
    #            await message.add_reaction("⬛")
    #            await message.add_reaction("🇺")
    #        except:
    #            await message.reply(":regional_indicator_n::regional_indicator_o:⬛🇺")

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        try:
            language = await get_guild_language(ctx)
        except TypeError:
            language = 'ru'
        if isinstance(error, commands.CommandNotFound):
            pass
            # await ctx.send(str(lang()[language]["UnKnCommand"]))
            # await ctx.message.add_reaction(disagree_emoji())

        if isinstance(error, commands.MissingPermissions):
            pass

        if isinstance(error, discord.Forbidden):
            pass

        if isinstance(error, commands.BadArgument):
            await ctx.send(str(lang[language]["BArg"]))
            await ctx.message.add_reaction(disagree_emoji())

        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(str(lang[language]["MissReqArg"]))
            await ctx.message.add_reaction(disagree_emoji())

        if isinstance(error, commands.CheckFailure):
            await ctx.send(str(lang[language]["AccessDenied"]))
            await ctx.message.add_reaction(disagree_emoji())
        if isinstance(error, commands.BotMissingPermissions):
            await ctx.send(str(lang[language]["Bot_hvnt_perm"]))
            await ctx.message.add_reaction(disagree_emoji())

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        try:
            embed = discord.Embed(title=f"Вошёл в  {guild.name} ({guild.id})", colour=discord.Colour.blurple())
            embed.set_author(name=guild.name, icon_url=guild.icon_url)
            await self.bot.get_channel(810967184397434921).send(embed=embed)
        except Exception as error:
            await self.bot.get_channel(810967184397434921).send(f'Logger error: {error}')
        count = await db_load_req(f"SELECT COUNT(*) as count FROM guilds WHERE id = {guild.id}")
        if count == 0:
            if str(guild.region) == "russia":
                language = "ru"
            else:
                language = "en"
            guildvalues = (guild.id, str(guild.name), 2, time.time(), bool(1), 0, 0, language)
            cur = data.cursor()
            cur.execute("INSERT INTO guilds VALUES(?, ?, ?, ?, ?, ?, ?, ?);", guildvalues)
            data.commit()
        elif count == 1:
            pass

        else:
            await developer().send(f'DataBaseError {guild.name} {guild.id} {datetime.now()}')

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        try:
            embed = discord.Embed(title=f"Вышел с  {guild.name} ({guild.id})", colour=discord.Colour.blurple())
            embed.set_author(name=guild.name, icon_url=guild.icon_url)
            await self.bot.get_channel(810967184397434921).send(embed=embed)
        except Exception as error:
            await self.bot.get_channel(810967184397434921).send(f'Logger error: {error}')

    @commands.Cog.listener()
    async def on_command(self, ctx):
        args = ctx.args[2:]
        embed = discord.Embed(title=f"Использованна команда", colour=discord.Colour.blurple(),
                              description=ctx.message.content)
        embed.set_footer(text=f"{ctx.author} ({ctx.author.id})", icon_url=ctx.author.avatar_url)
        embed.set_author(name=f"{ctx.guild.name} ({ctx.guild.id})", icon_url=ctx.guild.icon_url)
        await self.bot.get_channel(810967123752255518).send(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, msg: discord.Message):
        if msg.mention_everyone:
            await msg.channel.send(f"<:KoloPing:866512728829722654> {random.choice(self.urls)}")

    @loop(minutes=10)
    async def update_presence(self):
        await asyncio.sleep(10)
        await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=f"ts!help | Серверов: {len(self.bot.guilds)}"))



def setup(bot):
    bot.add_cog(MainCog(bot))
