import discord
import asyncio
import aiohttp
import time
from datetime import datetime
from discord.ext import commands
from discord.ext.tasks import loop
from Lib import get_guild_language, data, disagree_emoji, lang, config, loading_emoji, db_load_req, help_list, developer, help_settings, about_message


class MainCog(commands.Cog):
    print("Инициализация")

    def __init__(self, bot):
        self.bot = bot
        self.uptime = time.time()
        self.monitorings.start()

    @commands.command(aliases=["Help", "h"])
    async def help(self, ctx, arg1=None):
        if arg1 == None:
            await help_list(ctx)
        elif arg1 == "settings":
            await help_settings(ctx)

    @commands.command()
    async def ping(self, ctx):
        glang = await get_guild_language(ctx)
        uptime = time.gmtime(time.time() - self.uptime)
        ping = round(self.bot.latency * 1000, 2)
        if ping < 160:
            color = discord.Colour.green()
        elif ping < 200:
            color = discord.Colour.orange()
        else:
            color = discord.Colour.red()
        embed = discord.Embed(title=f"{lang[glang]['Pong']}!",
                              description=f"{lang[glang]['Ping']}: `{ping}ms`\nUptime {uptime.tm_hour + ((uptime.tm_mday - 1) * 24)}h {uptime.tm_min}m {uptime.tm_sec}s",
                              color=color)
        await ctx.send(embed=embed)

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

    @commands.command(aliases=["Discord_status", "Discordstatus", "discordstatus", "dstats", "ds"])
    async def discord_status(self, ctx, arg=None, arg2: int = 0):
        mymess = await ctx.send(loading_emoji())
        aliases1_arg1 = ["detail", "more", "d", "m"]
        aliases2_arg1 = ["last", "l"]

        async with aiohttp.ClientSession() as session:
            if arg not in aliases2_arg1:
                res = await session.get(url="https://srhpyqt94yxb.statuspage.io/api/v2/status.json")
                data_status = await res.json()
                res = await session.get(url="https://srhpyqt94yxb.statuspage.io/api/v2/components.json")
                data_components = await res.json()
            else:
                if int(arg2) > 50 or int(arg2) < 0:
                    await mymess.delete()
                    raise commands.BadArgument
                res = await session.get(url="https://srhpyqt94yxb.statuspage.io/api/v2/incidents.json")
                data_incidents = await res.json()
                last_incident = data_incidents["incidents"][int(arg2)]
        if arg not in aliases2_arg1:
            if data_status["status"]['indicator'] == "none":
                colour = discord.Colour.green()
            elif data_status["status"]['indicator'] == ("minor" or "major"):
                colour = discord.Colour.orange()
            else:
                colour = discord.Colour.red()
        else:
            colour = discord.Colour.blurple()

        embed = discord.Embed(description="[More info](https://discordstatus.com)")
        if arg not in aliases2_arg1:
            embed.title = data_status["status"]["description"]
            embed.colour = colour
            for component in data_components["components"]:
                if component["status"] != "operational" or arg in aliases1_arg1:
                    embed.add_field(name=component["name"], value=component["status"])
        else:
            embed.title = "Last incident"
            embed.description = f"[More info]({last_incident['shortlink']})"
            embed.colour = discord.Colour.blurple()
            embed.add_field(name="Name", value=last_incident["name"], inline=False)
            embed.add_field(name="Status", value=last_incident["status"], inline=False)
            embed.add_field(name="ID", value=last_incident["id"], inline=False)
        embed.set_thumbnail(url="https://dka575ofm4ao0.cloudfront.net/pages-transactional_logos/retina/15011/logo.png")
        await mymess.edit(content=None, embed=embed)

    @commands.Cog.listener()
    async def on_ready(self):
        print('TimeSlow инициализирован')

    #@commands.Cog.listener()
    #async def on_message(self, message):
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

        if isinstance(error, commands.BadArgument):
            await ctx.send(str(lang[language]["BArg"]))
            await ctx.message.add_reaction(disagree_emoji())

        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(str(lang[language]["MissReqArg"]))
            await ctx.message.add_reaction(disagree_emoji())

        if isinstance(error, commands.CheckFailure):
            await ctx.send(str(lang[language]["AccessDenied"]))
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
        embed = discord.Embed(title=f"Использованна команда", colour=discord.Colour.blurple(), description="ts!{0} {1}".format(ctx.command, args))
        embed.set_footer(text=f"{ctx.author} ({ctx.author.id})", icon_url=ctx.author.avatar_url)
        embed.set_author(name=f"{ctx.guild.name} ({ctx.guild.id})", icon_url=ctx.guild.icon_url)
        await self.bot.get_channel(810967123752255518).send(embed=embed)

    @loop(hours=1)
    async def monitorings(self):
        await asyncio.sleep(5)
        try:
            async with aiohttp.ClientSession() as session:
                res = await session.post(f"https://api.server-discord.com/v2/bots/{750415350348382249}/stats",
                                         headers={"Authorization": f"SDC {config['SDCtoken']}"},
                                         data={"shards": self.bot.shard_count or 1, "servers": len(self.bot.guilds)})
                await self.bot.get_channel(810967184397434921).send(f"SDC Status updated: {await res.json()}")
                await session.close()
            await asyncio.sleep(1)
            await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching,
                                                                     name=f"{config['prefix']}help | Серверов: {len(self.bot.guilds)}"))
            await self.bot.get_channel(810967184397434921).send("Presence updated")
        except Exception as error:
            await self.bot.get_channel(810967184397434921).send("Error in presence update:")
            await self.bot.get_channel(810967184397434921).send(error)


def setup(bot):
    bot.add_cog(MainCog(bot))
