import discord
import asyncio
import time
from datetime import datetime
from discord.ext import commands
from Lib import db_valid_cheker, get_guild_language, data, disagree_emoji, lang, is_Admin, loading_emoji, db_load_req, agree_emoji, developer, warning_emoji, db_dump_req, convert_to_role, convert_to_channel, is_developer


class WorkWithGuildsDB(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['Guildinfo', 'ginfo', 'Serverinfo', 'sinfo', 'serverinfo'])
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
            embed = discord.Embed(title=f"{lang[language]['InfoAbout']} {lang[language]['Guild']}",
                                  colour=discord.Colour.blurple())
            embed.add_field(name=lang[language]['Parameter'],
                            value=f'ID \n{lang[language]["Mod"]} \n{lang[language]["DOLsetup"]} \n{lang[language]["MRole"]} \n{lang[language]["LChann"]} \n{lang[language]["Lang"]}',
                            inline=True)
            embed.add_field(name=lang[language]['Value'],
                            value=f'{guild_data[0]} \n{guild_data[2]} \n{guild_data[3]} \n{mute_role} \n{log_channel} \n{language}',
                            inline=True)
            embed.set_footer(text=ctx.author, icon_url=ctx.author.avatar_url)
            embed.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon_url)
            await ctx.send(embed=embed)

    @commands.command()
    @commands.check(is_Admin)
    async def setup(self, ctx):
        try:
            guild_language = await get_guild_language(ctx)
        except:
            guild_language = "en"
        embed = discord.Embed(title=f"{loading_emoji()} Инициализация", description="Пожалуйста подождите...",
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
            guildvalues = (ctx.guild.id, str(ctx.guild.name), 1, time.time(), bool(1), 0, 0, language)
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
            await developer().send(f'DataBaseError {ctx.guild.name} {ctx.guild.id} {datetime.now()}')
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
        cur = data.cursor()
        cur.execute(f"SELECT * FROM guilds WHERE id={ctx.guild.id}")
        guild_data = cur.fetchone()
        db_guild_possible_options = ["mod", "mute_role", "log_channel", "language"]
        mod_possible_value = [1, 2, 3]
        language_possible_value = ['ru', 'en']
        if await db_valid_cheker(ctx):
            language = await get_guild_language(ctx)
            if option in db_guild_possible_options:
                if option == db_guild_possible_options[0]:
                    if int(value) in mod_possible_value:
                        await db_dump_req(f"UPDATE guilds SET mod = {int(value)} WHERE id = {ctx.guild.id};")
                        if int(value) == 3 and ctx.guild.get_role(int(guild_data[5])) is None:
                            await ctx.message.add_reaction(warning_emoji())
                            await ctx.send("Роль мута не назначена, данный режим не сможет рабоать без неё.\nЧтобы установить роль мута используйте `ts!settings mute_role {роль}` (в качестве аргумента комманды нужно использовать упоминание или ID).")
                        else:
                            await ctx.message.add_reaction(agree_emoji())
                    else:
                        await ctx.send(
                            f"{lang[language]['Parameter']} `{option}` {lang[language]['CannotSet']} `{value}`")
                        await ctx.message.add_reaction(disagree_emoji())

                elif option == db_guild_possible_options[1]:
                    if value != '0':
                        role = convert_to_role(ctx.guild, value)
                        if role is not None:
                            role_id = role.id
                        else:
                            role_id = 0
                            await ctx.send(
                                f"{lang[language]['Parameter']} `{option}` {lang[language]['CannotSet']} `{value}`")
                            await ctx.message.add_reaction(disagree_emoji())
                    else:
                        role_id = 0
                    await db_dump_req(f"UPDATE guilds SET mute_role_id = {int(role_id)} WHERE id = {ctx.guild.id};")
                    await ctx.message.add_reaction(agree_emoji())

                elif option == db_guild_possible_options[2]:
                    if value != '0':
                        txtchannel = convert_to_channel(value)
                        if txtchannel is not None:
                            channelid = txtchannel.id
                        else:
                            channelid = 0
                            await ctx.send(
                                f"{lang[language]['Parameter']} `{option}` {lang[language]['CannotSet']} `{value}`")
                            await ctx.message.add_reaction(disagree_emoji())
                    else:
                        channelid = 0
                    await db_dump_req(f"UPDATE guilds SET log_channel_id = {int(channelid)} WHERE id = {ctx.guild.id};")
                    await ctx.message.add_reaction(agree_emoji())

                elif option == db_guild_possible_options[3]:
                    if value in language_possible_value:
                        await db_dump_req(f'UPDATE guilds SET language = "{value}" WHERE id = {ctx.guild.id};')
                        await ctx.message.add_reaction(agree_emoji())
                    else:
                        await ctx.send(
                            f"{lang[language]['Parameter']} `{option}` {lang[language]['CannotSet']} `{value}`")
                        await ctx.message.add_reaction(disagree_emoji())

            else:
                await ctx.send(f"{lang[language]['Parameter']} `{option}` {lang[language]['NotFound']}")
                await ctx.message.add_reaction(disagree_emoji())

    @commands.command(aliases=['sql'])
    @commands.check(is_developer)
    async def sql_request(self, ctx, *, request):
        cur = data.cursor()
        try:
            cur.execute(str(request))
            await ctx.send(cur.fetchall() or 0)
            data.commit()
        except Exception as error:
            await ctx.send(error)


def setup(bot):
    bot.add_cog(WorkWithGuildsDB(bot))
