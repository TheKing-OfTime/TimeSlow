import discord
import asyncio
from datetime import datetime
from discord.ext import commands
from Lib import is_Moderator, db_load_req, data, disagree_emoji, warning_emoji, agree_emoji, db_valid_cheker, lang, get_guild_language, db_dump_req


class Roles(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if str(message.channel.type) == 'text':
            if await db_load_req(f"SELECT COUNT(*) as count FROM guilds WHERE id = {message.guild.id}"):
                cur = data.cursor()
                cur.execute(f"SELECT * FROM guilds WHERE id={message.guild.id}")
                guild_data = cur.fetchone()
                cur.execute(f"SELECT id FROM muteroles WHERE guild_id = {message.guild.id}")
                allcasesinguild = cur.fetchall()[0]
                checker = 0
                for role in message.author.roles:
                    if role.id in allcasesinguild:
                        checker = role
                if checker != 0:
                    cur.execute(
                        f"SELECT * FROM mutemembers WHERE id = {message.author.id} AND guild_id = {message.guild.id}")
                    member_data = cur.fetchone()
                    cur.execute(
                        f"SELECT * FROM rolemutemembers WHERE id = {checker.id} AND guild_id = {message.guild.id} ")
                    role_data = cur.fetchone()
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

    @commands.command(aliases=['Roleslowdown', 'rsd'])
    @commands.check(is_Moderator)
    async def roleslowdown(self, ctx, role: discord.Role, interval, subchannel: discord.TextChannel = None,
                           unmute_in=0):
        if await db_load_req(
                f"SELECT COUNT(*) as count FROM muteroles WHERE id = {role.id} AND guild_id = {ctx.guild.id} AND channel_id = {subchannel.id if subchannel is not None else None}") == 0:
            membervalues = (
                role.id, subchannel.id if subchannel is not None else None, str(role), False, datetime.now(),
                int(interval),
                int(unmute_in), ctx.guild.id,
                str(ctx.guild.id) + str(role.id))
            cur = data.cursor()
            cur.execute("INSERT INTO muteroles VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?);", membervalues)
            data.commit()
            if unmute_in == '0':
                unmute_in = 'Permanent'
            Bot = ctx.guild.get_member(750415350348382249)
            if Bot.guild_permissions.manage_messages and Bot.guild_permissions.manage_roles:
                await ctx.message.add_reaction(agree_emoji())
                embed = discord.Embed(title=f"Медленный режим у @{role} включён", color=discord.Colour.blurple(),
                                      description=f'Интервал: `{interval}` секунд \n{f"Канал: {subchannel}" if subchannel is not None else ""}\nМедленный режим отключется через: `{unmute_in}` минут')
                await ctx.send(embed=embed)
            else:
                await ctx.message.add_reaction(warning_emoji())
                embed = discord.Embed(
                    title=f"Медленный режим у @{role} включён, но некотороые необходимые права отсутствуют",
                    color=discord.Colour.blurple(),
                    description=f'Интервал: `{interval}` секунд \nМедленный режим отключется через: `{unmute_in}` минут\n{f"Канал: {subchannel}" if subchannel is not None else ""} \nОтсутствуент право "Управлять сообщениями". Медленный режим не будет работать корректно')
                await ctx.send(embed=embed)
        else:
            await ctx.message.add_reaction(disagree_emoji())
            embed = discord.Embed(title=f"{disagree_emoji()} Ошибка",
                                  description="Невозможно включить медленный режим роли с одинаковыми настройками дважды.",
                                  color=discord.Colour.red())
            await ctx.send(embed=embed)
        await asyncio.sleep(int(unmute_in) * 60)
        if await db_load_req(
                f"SELECT COUNT(*) as count FROM mutemembers WHERE id = {role.id} AND guild_id = {ctx.guild.id} AND channel_id = {subchannel.id if subchannel is not None else None}") == 1 and unmute_in != 'Permanent':
            cur = data.cursor()
            cur.execute(f"DELETE FROM muteroles WHERE id = {role.id} AND guild_id = {ctx.guild.id} AND channel_id = {subchannel.id if subchannel is not None else None}")
            data.commit()
            await ctx.message.add_reaction(agree_emoji())
            embed = discord.Embed(title=f"Медленный режим у @{role} отключён", color=discord.Colour.blurple())
            await ctx.send(embed=embed)

    @commands.command(aliases=["Roleinfo", "rinfo"])
    async def roleinfo(self, ctx, role: discord.Role, subchannel: discord.TextChannel = None):
        if await db_valid_cheker(ctx):
            if await db_load_req(
                    f"SELECT COUNT(*) as count FROM muteroles WHERE id = {role.id} AND guild_id = {ctx.guild.id} AND channel_id = {subchannel.id if subchannel is not None else None}") == 1:
                language = str(await get_guild_language(ctx))
                cur = data.cursor()
                cur.execute(f"SELECT * FROM muteroles WHERE id = {role.id} AND guild_id = {ctx.guild.id} AND channel_id = {subchannel.id if subchannel is not None else None}")
                member_data = cur.fetchone()
                embed = discord.Embed(title=f"{lang[language]['InfoAbout']} {lang[language]['Member']}",
                                      color=discord.Colour.blurple())
                embed.add_field(name=f"{lang[language]['Parameter']}",
                                value="Имя пользователя: \nRole ID:\nChannel ID: \nИнтервал: \nОтключение через:", inline=True)
                embed.add_field(name=f"{lang[language]['Value']}",
                                value=f'{member_data[2]}\n{member_data[0]}\n{member_data[1]}\n{member_data[5]}\n{member_data[6]}')
                embed.set_footer(text=ctx.author, icon_url=ctx.author.avatar_url)
                await ctx.send(embed=embed)
            else:
                await ctx.send("У роли не включен медленный режим")
                await ctx.message.add_reaction(disagree_emoji())

    @commands.command(aliases=['Roleunslowdown', 'rusd'])
    @commands.check(is_Moderator)
    async def roleunslowdown(self, ctx, role: discord.Role, subchannel: discord.TextChannel = None):
        if await db_load_req(
                f"SELECT COUNT(*) as count FROM muteroles WHERE id = {role.id} AND guild_id = {ctx.guild.id} AND channel_id = {subchannel.id if subchannel is not None else None}") == 1:
            cur = data.cursor()
            cur.execute(f"DELETE FROM muteroles WHERE id = {role.id} AND guild_id = {ctx.guild.id} AND channel_id = {subchannel.id if subchannel is not None else None}")
            data.commit()
            await ctx.message.add_reaction(agree_emoji())
            embed = discord.Embed(title=f"Медленный режим у {role} отключён", color=discord.Colour.blurple())
            await ctx.send(embed=embed)
        else:
            await ctx.message.add_reaction(disagree_emoji())
            embed = discord.Embed(title=f"{disagree_emoji()} Ошибка",
                                  description="Невозможно отключить медленный режим у пользователя, ведь он уже отключён.",
                                  color=discord.Colour.red())
            await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Roles(bot))
