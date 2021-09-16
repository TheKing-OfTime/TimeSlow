import discord
import aiohttp
from discord.ext import commands
from Lib import loading_emoji

    
class Discord_status(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    @commands.command(aliases=["Discord_status", "Discordstatus", "discordstatus", "dstats", "ds"])
    async def discord_status(self, ctx, arg=None, arg2: int = 0, arg3=None):
        mymess = await ctx.send(loading_emoji())
        aliases1_arg1 = ["detail", "more", "d", "m"]
        aliases2_arg1 = ["last", "l"]

        aliases1_arg3 = ["detail", "more", "updates", "d", "m", "u"]

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
            if last_incident["impact"] == "none":
                colour = discord.Colour.green()
            elif last_incident["impact"] == "minor":
                colour = discord.Colour.orange()
            elif last_incident["impact"] == "major":
                colour = discord.Colour.red()
            else:
                colour = 0xff0000
            embed.color = colour
            embed.add_field(name="Name", value=last_incident["name"], inline=False)
            embed.add_field(name="Impact", value=last_incident["impact"], inline=False)
            embed.add_field(name="Status", value=last_incident["status"], inline=False)
            if arg3 in aliases1_arg3:
                for incident in last_incident["incident_updates"]:
                    embed.add_field(name=incident["status"], value=incident["body"], inline=False)
            embed.add_field(name="Incident ID", value=last_incident["id"], inline=False)
        embed.set_thumbnail(url="https://dka575ofm4ao0.cloudfront.net/pages-transactional_logos/retina/15011/logo.png")
        await mymess.edit(content=None, embed=embed)


    @commands.command(aliases=["Status", "stats"])
    async def status(self, ctx, url="srhpyqt94yxb", arg=None, arg2: int = 0, arg3=None):
        mymess = await ctx.send(loading_emoji())
        aliases1_arg1 = ["detail", "more", "d", "m"]
        aliases2_arg1 = ["last", "l"]

        aliases1_arg3 = ["detail", "more", "updates", "d", "m", "u"]

        async with aiohttp.ClientSession() as session:
            if arg not in aliases2_arg1:
                res = await session.get(url=f"https://{url}.statuspage.io/api/v2/status.json")
                data_status = await res.json()
                res = await session.get(url=f"https://{url}.statuspage.io/api/v2/components.json")
                data_components = await res.json()
            else:
                if int(arg2) > 50 or int(arg2) < 0:
                    await mymess.delete()
                    raise commands.BadArgument
                res = await session.get(url=f"https://{url}.statuspage.io/api/v2/incidents.json")
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

        embed = discord.Embed(description=f"[More info](https://{url}.statuspage.io)")
        if arg not in aliases2_arg1:
            embed.title = f'{data_status["page"]["name"]}: {data_status["status"]["description"]}'
            embed.colour = colour
            for component in data_components["components"]:
                if component["status"] != "operational" or arg in aliases1_arg1:
                    embed.add_field(name=component["name"], value=component["status"])
        else:
            embed.title = f"{data_incidents['page']['name']}: Last incident"
            embed.description = f"[More info]({last_incident['shortlink']})"
            if last_incident["impact"] == "none":
                colour = discord.Colour.green()
            elif last_incident["impact"] == "minor":
                colour = discord.Colour.orange()
            elif last_incident["impact"] == "major":
                colour = discord.Colour.red()
            else:
                colour = 0xff0000
            embed.color = colour
            embed.add_field(name="Name", value=last_incident["name"], inline=False)
            embed.add_field(name="Impact", value=last_incident["impact"], inline=False)
            embed.add_field(name="Status", value=last_incident["status"], inline=False)
            if arg3 in aliases1_arg3:
                for incident in last_incident["incident_updates"]:
                    embed.add_field(name=incident["status"], value=incident["body"], inline=False)
            embed.add_field(name="Incident ID", value=last_incident["id"], inline=False)
        await mymess.edit(content=None, embed=embed)


def setup(bot):
    bot.add_cog(Discord_status(bot))
