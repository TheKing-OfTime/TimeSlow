import discord
import asyncio
from datetime import datetime
from discord.ext import commands
from Lib import db_valid_cheker, get_guild_language, data, disagree_emoji, lang, is_Moderator, db_load_req, agree_emoji, warning_emoji, db_dump_req


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

                    elif guild_data[2] == 3:
                        mute_role = message.guild.get_role(int(guild_data[5]))
                        if int(member_data[2]) == 1:
                            pass
                        else:
                            await db_dump_req(
                                f"UPDATE mutemembers SET in_interval = {bool(1)} WHERE id = {message.author.id} AND guild_id = {message.guild.id}")
                            await message.author.add_roles(mute_role)
                            await asyncio.sleep(member_data[4])
                            await db_dump_req(
                                f"UPDATE mutemembers SET in_interval = {bool(0)} WHERE id = {message.author.id} AND guild_id = {message.guild.id}")
                            await message.author.remove_roles(mute_role)

    @commands.command(aliases=['Slowdown', 'sd'])
    @commands.check(is_Moderator)
    async def slowdown(self, ctx, member: discord.Member, interval, unmute_in='0'):
        if await db_load_req(
                f"SELECT COUNT(*) as count FROM mutemembers WHERE id = {member.id} AND guild_id = {ctx.guild.id}") == 0:
            membervalues = (member.id, str(member), False, datetime.now(), int(interval), int(unmute_in), ctx.guild.id,
                            str(ctx.guild.id) + str(member.id))
            cur = data.cursor()
            cur.execute("INSERT INTO mutemembers VALUES(?, ?, ?, ?, ?, ?, ?, ?);", membervalues)
            data.commit()
            if unmute_in == '0':
                unmute_in = 'Permanent'
            Bot = ctx.guild.get_member(750415350348382249)
            if Bot.guild_permissions.manage_messages and Bot.guild_permissions.manage_roles:
                await ctx.message.add_reaction(agree_emoji())
                embed = discord.Embed(title=f"Медленный режим у {member} включён", color=discord.Colour.blurple(),
                                      description=f'Интервал: `{interval}` секунд \nМедленный режим отключется через: `{unmute_in}` минут')
                await ctx.send(embed=embed)
            else:
                await ctx.message.add_reaction(warning_emoji())
                embed = discord.Embed(
                    title=f"Медленный режим у {member} включён, но некотороые необходимые права отсутствуют",
                    color=discord.Colour.blurple(),
                    description=f'Интервал: `{interval}` секунд \nМедленный режим отключется через: `{unmute_in}` минут \nОтсутствуент право "Управлять сообщениями". Медленный режим не будет работать корректно')
                await ctx.send(embed=embed)
        else:
            await ctx.message.add_reaction(disagree_emoji())
            embed = discord.Embed(title=f"{disagree_emoji()} Ошибка",
                                  description="Невозможно включить медленный режим пользователю дважды.",
                                  color=discord.Colour.red())
            await ctx.send(embed=embed)
        await asyncio.sleep(int(unmute_in) * 60)
        if await db_load_req(
                f"SELECT COUNT(*) as count FROM mutemembers WHERE id = {member.id} AND guild_id = {ctx.guild.id}") == 1 and unmute_in != 'Permanent':
            cur = data.cursor()
            cur.execute(f"DELETE FROM mutemembers WHERE id = {member.id} AND guild_id = {ctx.guild.id}")
            data.commit()
            await ctx.message.add_reaction(agree_emoji())
            embed = discord.Embed(title=f"Медленный режим у {member} отключён", color=discord.Colour.blurple())
            await ctx.send(embed=embed)

    @commands.command(aliases=['Unslowdown', 'usd'])
    @commands.check(is_Moderator)
    async def unslowdown(self, ctx, member: discord.Member):
        if await db_load_req(
                f"SELECT COUNT(*) as count FROM mutemembers WHERE id = {member.id} AND guild_id = {ctx.guild.id}") == 1:
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
    async def memberinfo(self, ctx, *, member: discord.Member = None):
        if await db_valid_cheker(ctx):
            if member is None:
                member = ctx.author
            if await db_load_req(
                    f"SELECT COUNT(*) as count FROM mutemembers WHERE id = {member.id} AND guild_id = {ctx.guild.id}") == 1:
                language = str(await get_guild_language(ctx))
                cur = data.cursor()
                cur.execute(f"SELECT * FROM mutemembers WHERE id = {member.id} AND guild_id = {ctx.guild.id}")
                member_data = cur.fetchone()
                embed = discord.Embed(title=f"{lang[language]['InfoAbout']} {lang[language]['Member']}",
                                      color=discord.Colour.blurple())
                embed.add_field(name=f"{lang[language]['Parameter']}",
                                value="Имя пользователя: \nID: \nИнтервал: \nОтключение через:", inline=True)
                embed.add_field(name=f"{lang[language]['Value']}",
                                value=f'{member_data[1]}\n{member_data[0]}\n{member_data[4]}\n{member_data[5]}')
                embed.set_footer(text=ctx.author, icon_url=ctx.author.avatar_url)
                embed.set_author(name=str(member), icon_url=member.avatar_url)
                await ctx.send(embed=embed)
            else:
                await ctx.send("У пользователя не включен медленный режим")
                await ctx.message.add_reaction(disagree_emoji())


def setup(bot):
    bot.add_cog(WorkWithMemberDB(bot))
