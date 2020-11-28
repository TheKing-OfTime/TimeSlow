from Lib import *
import discord
import asyncio
from datetime import datetime
from discord.ext import commands


class WorkWithGuildsDB(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['Guildinfo', 'ginfo'])
    async def guildinfo(self, ctx):
        if await db_valid_cheker(ctx):
            language = await get_guild_language(ctx)
            cur = data.cursor()
            cur.execute(f"SELECT * FROM guilds WHERE id={ctx.guild.id}")
            guild_data = cur.fetchone()
            if guild_data[5] != 0:
                mute_role = f'<@&{guild_data[5]}>'
            else:
                mute_role = disagree_emoji()

            if guild_data[6] != 0:
                log_channel = f'<#{guild_data[6]}>'
            else:
                log_channel = disagree_emoji()
            embed = discord.Embed(title=f"{lang()[language]['InfoAbout']} {lang()[language]['Guild']}",
                                  colour=discord.Colour.blurple())
            embed.add_field(name="Параметр",
                            value=f'Id \nРежим \nДата первого включения \nРоль мута \nКанал логирования \nЯзык',
                            inline=True)
            embed.add_field(name="Значение",
                            value=f'{guild_data[0]} \n{guild_data[2]} \n{guild_data[3]} \n{mute_role} \n{log_channel} \n{language}',
                            inline=True)
            embed.set_footer(text=ctx.author, icon_url=ctx.author.avatar_url)
            embed.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon_url)
            await ctx.send(embed=embed)

    @commands.command()
    @commands.check(is_developer)
    async def setup(self, ctx):
        embed = discord.Embed(title="Инициализация", description="Пожалуйста подождите...",
                              colour=discord.Colour.blurple())
        emb_message = await ctx.send(embed=embed)
        await asyncio.sleep(1)
        embed = discord.Embed(title="Инициализация завершена")
        count = await db_load_req(f"SELECT COUNT(*) as count FROM guilds WHERE id = {ctx.guild.id}")
        if count == 0:
            if str(ctx.guild.region) == "russia":
                language = "ru"
            else:
                language = "en"
            guildvalues = (ctx.guild.id, str(ctx.guild.name), 1, datetime.now(), bool(1), 0, 0, language)
            cur = data.cursor()
            cur.execute("INSERT INTO guilds VALUES(?, ?, ?, ?, ?, ?, ?, ?);", guildvalues)
            data.commit()
            embed.add_field(name=f"База данных: {agree_emoji()}", value="Данные занесены в базу данных")
            if embed.colour != discord.Colour.orange() and embed.colour != discord.Colour.red():
                embed.colour = discord.Colour.green()
        elif count == 1:
            embed.add_field(name=f"База данных: {agree_emoji()}", value="Всё в порядке")
            if embed.colour != discord.Colour.orange() and embed.colour != discord.Colour.red():
                embed.colour = discord.Colour.green()
        else:
            print('DataBaseError', ctx.guild.name, ctx.guild.id, datetime.now())
            await developer().send(f'DataBaseError {ctx.guild.name} {ctx.guild.id} {datetime.date()}')
            embed.add_field(name=f"База данных: {disagree_emoji()}", value="Критическая ошибка")
            embed.colour = discord.Colour.red()
            await ctx.send("Критическая ошибка базы данных, разработчик уже извещён о проблеме")

        Bot = ctx.guild.get_member(750415350348382249)
        if Bot.guild_permissions.manage_messages and Bot.guild_permissions.manage_roles:
            embed.add_field(name=f"Права: {agree_emoji()}", value="Всё в порядке")
            if embed.colour != discord.Colour.orange() and embed.colour != discord.Colour.red():
                embed.colour = discord.Colour.green()
        else:
            embed.add_field(name=f"Права: {warning_emoji()}", value="Отсутствуют некоторые необходимые права")
            if embed.colour != discord.Colour.red():
                embed.colour = discord.Colour.orange()
            await ctx.send(
                "Проверте права бота, возможно у него отсутствуют права: Управление сообщениями, Управление ролями")
        await emb_message.edit(embed=embed)

    @commands.command(aliases=['Settings', 's'])
    @commands.check(is_Admin)
    async def settings(self, ctx, option, value):
        mod_possible_value = [1, 2, 3]
        language_possible_value = ['ru', 'en']
        if await db_valid_cheker(ctx):
            language = await get_guild_language(ctx)
            if option == config()["db_guild_possible_options"][0]:
                if mod_possible_value.count(int(value)) == 1:
                    await db_dump_req(f"UPDATE guilds SET mod = {int(value)} WHERE id = {ctx.guild.id};")
                    await ctx.message.add_reaction(agree_emoji())
                else:
                    await ctx.send(
                        f"{lang()[language]['Parameter']} `{option}` {lang()[language]['CannotSet']} `{value}`")
                    await ctx.message.add_reaction(disagree_emoji())

            elif option == config()["db_guild_possible_options"][1]:
                if value != '0':
                    role = convert_to_role(ctx.guild, value)
                    if role is not None:
                        role_id = role.id
                    else:
                        await ctx.send(
                            f"{lang()[language]['Parameter']} `{option}` {lang()[language]['CannotSet']} `{value}`")
                        await ctx.message.add_reaction(disagree_emoji())
                else:
                    role_id = 0
                await db_dump_req(f"UPDATE guilds SET mute_role_id = {int(role_id)} WHERE id = {ctx.guild.id};")
                await ctx.message.add_reaction(agree_emoji())

            elif option == config()["db_guild_possible_options"][2]:
                if value != '0':
                    txtchannel = convert_to_channel(value)
                    if txtchannel is not None:
                        channelid = txtchannel.id
                    else:
                        await ctx.send(
                            f"{lang()[language]['Parameter']} `{option}` {lang()[language]['CannotSet']} `{value}`")
                        await ctx.message.add_reaction(disagree_emoji())
                else:
                    channelid = 0
                await db_dump_req(f"UPDATE guilds SET log_channel_id = {int(channelid)} WHERE id = {ctx.guild.id};")
                await ctx.message.add_reaction(agree_emoji())

            elif option == config()["db_guild_possible_options"][3]:
                if language_possible_value.count(str(value)) == 1:
                    await db_dump_req(f'UPDATE guilds SET language = "{value}" WHERE id = {ctx.guild.id};')
                    await ctx.message.add_reaction(agree_emoji())
                else:
                    await ctx.send(
                        f"{lang()[language]['Parameter']} `{option}` {lang()[language]['CannotSet']} `{value}`")
                    await ctx.message.add_reaction(disagree_emoji())

            else:
                await ctx.send(f"{lang()[language]['Parameter']} `{option}` {lang()[language]['NotFound']}")
                await ctx.message.add_reaction(disagree_emoji())


class WorkWithMemberDB(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if str(message.channel.type) == 'text':
            if await db_load_req(f"SELECT COUNT(*) as count FROM guilds WHERE id = {message.guild.id}"):
                cur = data.cursor()
                cur.execute(f"SELECT * FROM guilds WHERE id={message.guild.id}")
                guild_data = cur.fetchone()
                if await db_load_req(
                        f"SELECT COUNT(*) as count FROM mutemembers WHERE id = {message.author.id} AND guild_id = {message.guild.id}"):
                    cur.execute(
                        f"SELECT * FROM mutemembers WHERE id = {message.author.id} AND guild_id = {message.guild.id}")
                    member_data = cur.fetchone()
                    if guild_data[2] == 1:
                        if int(member_data[2]) == 1:
                            await message.delete()
                        else:
                            await db_dump_req(
                                f"UPDATE mutemembers SET in_interval = {bool(1)} WHERE id = {message.author.id} AND guild_id = {message.guild.id}")
                            await asyncio.sleep(member_data[4])
                            await db_dump_req(
                                f"UPDATE mutemembers SET in_interval = {bool(0)} WHERE id = {message.author.id} AND guild_id = {message.guild.id}")

                    elif guild_data[2] == 2:
                        if int(member_data[2]) == 1:
                            await message.delete()
                            try:
                                await message.author.send(
                                    f"Вы отправляете сообщения слишком быстро \nУдаленно сообщение: {message.content}")
                            except:
                                pass
                        else:
                            await db_dump_req(
                                f"UPDATE mutemembers SET in_interval = {bool(1)} WHERE id = {message.author.id} AND guild_id = {message.guild.id}")
                            await asyncio.sleep(member_data[4])
                            await db_dump_req(
                                f"UPDATE mutemembers SET in_interval = {bool(0)} WHERE id = {message.author.id} AND guild_id = {message.guild.id}")

                    elif guild_data[3] == 3:
                        pass

    @commands.command(aliases=['Slowdown', 'sd'])
    @commands.check(is_Moderator)
    async def slowdown(self, ctx, member: discord.Member, interval, unmute_in):
        if await db_load_req(f"SELECT COUNT(*) as count FROM mutemembers WHERE id = {member.id} AND guild_id = {ctx.guild.id}") == 0:
            membervalues = (member.id, str(member), False, datetime.now(), int(interval), int(unmute_in), ctx.guild.id, str(ctx.guild.id) + str(member.id))
            cur = data.cursor()
            cur.execute("INSERT INTO mutemembers VALUES(?, ?, ?, ?, ?, ?, ?, ?);", membervalues)
            data.commit()
            await ctx.message.add_reaction(agree_emoji())
            embed = discord.Embed(title=f"Медленный режим у {member} включён", color=discord.Colour.blurple(),
                                  description=f'Интервал: `{interval}` секунд \nМедленный режим отключется через: `{unmute_in}` минут')
            await ctx.send(embed=embed)
        else:
            await ctx.message.add_reaction(disagree_emoji())
            embed = discord.Embed(title=f"{disagree_emoji()} Ошибка",
                                  description="Невозможно включить медленный режим пользователю дважды.",
                                  color=discord.Colour.red())
            await ctx.send(embed=embed)
        await asyncio.sleep(int(unmute_in) * 60)
        if await db_load_req(f"SELECT COUNT(*) as count FROM mutemembers WHERE id = {member.id} AND guild_id = {ctx.guild.id}") == 1:
            cur = data.cursor()
            cur.execute(f"DELETE FROM mutemembers WHERE id = {member.id} AND guild_id = {ctx.guild.id}")
            data.commit()
            await ctx.message.add_reaction(agree_emoji())
            embed = discord.Embed(title=f"Медленный режим у {member} отключён", color=discord.Colour.blurple())
            await ctx.send(embed=embed)

    @commands.command(aliases=['Unslowdown', 'usd'])
    @commands.check(is_Moderator)
    async def unslowdown(self, ctx, member: discord.Member):
        if await db_load_req(f"SELECT COUNT(*) as count FROM mutemembers WHERE id = {member.id} AND guild_id = {ctx.guild.id}") == 1:
            cur = data.cursor()
            cur.execute(f"DELETE FROM mutemembers WHERE id = {member.id} AND guild_id = {ctx.guild.id}")
            data.commit()
            await ctx.message.add_reaction(agree_emoji())
            embed = discord.Embed(title=f"Медленный режим у {member} отключён", color=discord.Colour.blurple())
            await ctx.send(embed=embed)
        else:
            await ctx.message.add_reaction(disagree_emoji())
            embed = discord.Embed(title=f"{disagree_emoji()} Ошибка",
                                  description="Невозможно отключить медленный режим у пользователя, ведь он уже отключён.",
                                  color=discord.Colour.red())
            await ctx.send(embed=embed)

    @commands.command(aliases=["Memberinfo", "minfo"])
    async def memberinfo(self, ctx, *, member: discord.Member):
        if await db_valid_cheker(ctx):
            if await db_load_req(f"SELECT COUNT(*) as count FROM mutemembers WHERE id = {member.id} AND guild_id = {ctx.guild.id}") == 1:
                language = str(await get_guild_language(ctx))
                cur = data.cursor()
                cur.execute(f"SELECT * FROM mutemembers WHERE id = {member.id} AND guild_id = {ctx.guild.id}")
                member_data = cur.fetchone()
                embed = discord.Embed(title=f"{lang()[language]['InfoAbout']} {lang()[language]['Member']}", color=discord.Colour.blurple())
                embed.add_field(name=f"{lang()[language]['Parameter']}", value="Имя пользователя: \nID: \nИнтервал: \nОтключение через:", inline=True)
                embed.add_field(name=f"{lang()[language]['Value']}", value=f'{member_data[1]}\n{member_data[0]}\n{member_data[4]}\n{member_data[5]}')
                embed.set_footer(text=ctx.author, icon_url=ctx.author.avatar_url)
                embed.set_author(name=str(member), icon_url=member.avatar_url)
                await ctx.send(embed=embed)
            else:
                await ctx.send("У пользователя не включен медленный режим")
                await ctx.message.add_reaction(disagree_emoji())


class MainCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx):
        if await db_valid_cheker(ctx):
            language = await get_guild_language(ctx)
            ping = round(bot.latency * 1000, 2)
            if ping < 180:
                color = discord.Colour.green()
            elif ping < 300:
                color = discord.Colour.orange()
            else:
                color = discord.Colour.red()
            embed = discord.Embed(title=f"{lang()[language]['Pong']}!",
                                  description=f"{lang()[language]['Ping']}: `{ping}ms`", color=color)
            await ctx.send(embed=embed)

    @bot.event
    async def on_ready():
        await bot.change_presence(
            activity=discord.Activity(type=discord.ActivityType.listening,
                                      name=f"{config()['prefix']}help | Серверов: {len(bot.guilds)}"))
        print('TimeSlow инициализирован')

    @bot.event
    async def on_command_error(ctx, error):
        try:
            language = await get_guild_language(ctx)
        except TypeError:
            language = 'en'
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


bot.add_cog(WorkWithMemberDB(bot))
bot.add_cog(MainCog(bot))
bot.add_cog(WorkWithGuildsDB(bot))
bot.run(config()["token"])
