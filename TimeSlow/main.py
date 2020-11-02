from Lib import *
import discord
from datetime import datetime
from discord.ext import commands


class WorkWithGuildsDB(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['Guildinfo', 'ginfo'])
    @commands.check(is_developer)
    async def guildinfo(self, ctx):
        if await db_valid_cheker(ctx):
            language = await get_guild_language(ctx.guild)
            cur = data.cursor()
            cur.execute(f"SELECT * FROM guilds WHERE id={ctx.guild.id}")
            guild_data = cur.fetchone()
            print(guild_data)
            if guild_data[5] != 0:
                mute_role = convert_to_role(guild_data[5])
            else:
                mute_role = disagree_emoji()

            if guild_data[6] != 0:
                log_channel = convert_to_channel(guild_data[6])
            else:
                log_channel = disagree_emoji()
            embed = discord.Embed(title=f"{lang()[language]['InfoAbout']} {lang()[language]['Guild']}", colour=discord.Colour.blurple())
            embed.add_field(name="Parameter", value=f'''
Id
Mod
Join time
Mute role
Log channel
Language''', inline=True)

            embed.add_field(name="Value", value=f'''
{guild_data[0]} 
{guild_data[2]} 
{guild_data[3]} 
{mute_role} 
{log_channel} 
{language} ''', inline=True)
            embed.set_author(name=ctx.author, icon_url=ctx.author.avatar_url)
            embed.set_footer(text=f'{ctx.guild.name}', icon_url=ctx.guild.icon_url)
            await ctx.send(embed=embed)

    @commands.command()
    @commands.check(is_developer)
    async def setup(self, ctx):
        count = await db_load_req(f"SELECT COUNT(*) as count FROM guilds WHERE id = {ctx.guild.id}")
        if count == 0:
            print(ctx.guild.region)
            if str(ctx.guild.region) == "russia":
                language = "ru"
            else:
                language = "en"
            guildvalues = (ctx.guild.id, str(ctx.guild.name), 2, datetime, bool(1), 0, 0, language)
            cur = data.cursor()
            cur.execute("INSERT INTO guilds VALUES(?, ?, ?, ?, ?, ?, ?, ?);", guildvalues)
            data.commit()
            await ctx.message.add_reaction(agree_emoji())
        elif count == 1:
            await ctx.send("Действия не требуются")
        else:
            print('DataBaseError', ctx.guild.name, ctx.guild.id, datetime)
            await developer().send('DataBaseError', ctx.guild.name, ctx.guild.id, datetime)
            await ctx.send('Критическая ошибка базы данных, разработчик уже извёщен об ошибке')
            await ctx.message.add_reaction(disagree_emoji())

    @commands.command(aliases=['Settings', 's'])
    @commands.check(is_developer)
    async def settings(self, ctx, option, value):
        mod_possible_value = [1, 2, 3]
        language_possible_value = ['ru', 'en']
        if await db_valid_cheker(ctx):
            language = await get_guild_language(ctx.guild)
            if option == config()["db_guild_possible_options"][0]:
                if mod_possible_value.count(int(value)) == 1:
                    await db_dump_req(f"UPDATE guilds SET mod = {int(value)} WHERE id = {ctx.guild.id};")
                    await ctx.message.add_reaction(agree_emoji())
                else:
                    await ctx.send(f"{lang()[language]['Parameter']} `{option}` {lang()[language]['CannotSet']} `{value}`")
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
                    await ctx.send(f"{lang()[language]['Parameter']} `{option}` {lang()[language]['CannotSet']} `{value}`")
                    await ctx.message.add_reaction(disagree_emoji())

            else:
                await ctx.send(f"{lang()[language]['Parameter']} `{option}` {lang()[language]['NotFound']}")
                await ctx.message.add_reaction(disagree_emoji())


class MainCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx):
        if await db_valid_cheker(ctx):
            language = await get_guild_language(ctx.guild)
            ping = round(bot.latency * 1000, 2)
            if ping < 300:
                color = 0x00ff00
            else:
                color = 0xff0000
            embed = discord.Embed(title=f"{lang()[language]['Pong']}!",
                                  description=f"{lang()[language]['Ping']}: `{ping}ms`", color=color)
            await ctx.send(embed=embed)

    @bot.event
    async def on_ready():
        await bot.change_presence(
            activity=discord.Activity(type=discord.ActivityType.listening, name=f"{config()['prefix']}help"))
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


bot.add_cog(MainCog(bot))
bot.add_cog(WorkWithGuildsDB(bot))
bot.run(config()["token"])
