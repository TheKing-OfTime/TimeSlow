import math
import discord
import time
import aiohttp
import mmh3

from Lib import agree_emoji, disagree_emoji
from discord.ext import commands
from discord.ext.tasks import loop


class RolloutManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.rollouts_data = None
        self.rollouts_last_receive = None
        self.update_data.start()

    @commands.command(aliases=["r"])
    async def rollout(self, ctx:commands.Context, r_code:int = None, target_id:int = None):
        data = self.rollouts_data
        counter = 0
        embed = discord.Embed(title=f"List of rollouts", colour=discord.Colour.blurple())
        target_name = ''
        description = ''

        if r_code is None:
            for item in data:
                r_d = item['rollout'][3][0][0][0][1][0]
                description += f"`{counter}: `{item['data']['title']}\n"
                counter+=1
            embed.description = description
            embed.description+=f"The data has been updated <t:{self.rollouts_last_receive}:R>"

        else:
            try:
                r_code = int(r_code)
            except ValueError:
                await ctx.send("Invalid target number")
                return
            else:
                target_name = data[r_code]['data']['id']

            c_data = data[r_code]
            if not target_id:
                if c_data['data']['type'] == 'guild':
                    target_id = ctx.guild.id
                    embed.set_thumbnail(url=ctx.guild.icon_url)
                else:
                    target_id = ctx.author.id
                    embed.set_thumbnail(url=ctx.author.icon_url)
            pos = mmh3.hash(f"{target_name}:{target_id}", signed=False) % 10000

            embed.title = f"{c_data['data']['title']} rollout"
            embed.add_field(name="Position in 'queue'", value=pos, inline=False)

            enabled = False
            rollout_data_dict = {}

            for i in c_data['rollout'][3][0][0]:
                rollout_data_dict[i[0]] = i[1]
            for i in c_data['data']['buckets']:
                pr = 0
                if rollout_data_dict.get(i):
                    for item in rollout_data_dict[i]:
                        if not enabled:
                            enabled = item['s'] < pos < item['e']
                        pr += item['e'] - item['s']

                if i and pr/100 != 0:
                    embed.add_field(name=c_data['data']['description'][i].split(':')[1], value=f"{agree_emoji() if enabled else disagree_emoji()} {pr/100}%")

            #embed.set_footer(text=f"The feature rolled out on {math.floor((rollout_preview[0]['e'] - rollout_preview[0]['s'])/100)}% of all Discord {c_data['data']['type']}s")

        await ctx.send(embed=embed)

    @loop(minutes=15)
    async def update_data(self):
        async with aiohttp.ClientSession() as session:
            async with session.get('https://rollouts.advaith.workers.dev/') as r:
                if r.status == 200:
                    self.rollouts_data = await r.json()
                    self.rollouts_last_receive = math.floor(time.time())
                    print(self.rollouts_last_receive, ':', 'received')
                else:
                    print('Receiving failed')

def setup(bot):
    bot.add_cog(RolloutManager(bot))