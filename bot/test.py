import asyncio

import discord
from discord.ext import commands

from constants import *
from utils import *
from sqlite import Sql
from tibia import *
from guildstatseu import GuildStats

class Test(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = Config.load_config()
        self.sql = Sql()

    @commands.command(name='tibiaData', aliases=['td'], brief="TibiaData test", pass_context=True)
    async def tibiaData(self, ctx, *, name):  
        name_from_msg = ctx.message.content[len(ctx.prefix) + len(ctx.invoked_with) + 1:] # not used alternativ way
        embed = discord.Embed(
            title='Tibia Discord Bot Test',
            description=LOGIN_MESSAGE.format(self.bot.user.name, self.bot.user.id, self.config["PREFIX"])+"\n"+LOADING_DEFAULT_WHITELIST.format(self.config["DEFAULT_WHITELIST"]),
            colour=0xffffff
        )
        msg = await ctx.send(content=LOADING_MESSAGE, embed=embed)
        
        # Get character information from tibiadata.com
        character = await TibiaData.get_character(name)
        print(character.to_json())

        embed.add_field(name="Name", value=character.name, inline=True)
        embed.add_field(name="World", value=character.world, inline=True)
        embed.add_field(name="Level", value=character.level, inline=True)
        
        if character.house is not None:
            embed.add_field(name="House", value=HOUSE.format(name=character.house.name, town=character.house.town), inline=True)

        # Check if user has a custom tumbnail image and add it to embed message
        Utils.add_thumbnail(embed, character.name, self.config["DEFAULT_WHITELIST"])
        await msg.edit(content="Done", embed=embed)
        
        emoji1 = '\N{THUMBS UP SIGN}'
        emoji2 = '\N{THUMBS DOWN SIGN}'
        await msg.add_reaction(emoji1)
        await msg.add_reaction(emoji2)
        
        reaction, user = await self.bot.wait_for('reaction_add', check=lambda reaction, user: user != self.bot.user)
        
        await ctx.send(content="You responded with {}".format(reaction.emoji))


    @commands.command(name='tibia', aliases=['t'], brief="Tibia test", pass_context=True)
    async def tibia(self, ctx, *, name):
        embed = discord.Embed(
            title='Tibia Discord Bot Test',
            description=LOGIN_MESSAGE.format(self.bot.user.name, self.bot.user.id, self.config["PREFIX"])+"\n"+LOADING_DEFAULT_WHITELIST.format(self.config["DEFAULT_WHITELIST"]),
            colour=0xffffff
        )
        
        msg = await ctx.send(content=LOADING_MESSAGE, embed=embed)
        
        # Get character information from tibiadata.com
        character = await Tibia.get_character(name)
        print(character.to_json())

        embed.add_field(name="Name", value=character.name, inline=True)
        embed.add_field(name="World", value=character.world, inline=True)
        embed.add_field(name="Level", value=character.level, inline=True)
        
        if character.house is not None:
            embed.add_field(name="House", value=HOUSE.format(name=character.house.name, town=character.house.town), inline=True)

        emoji1 = '\N{THUMBS UP SIGN}'
        await msg.add_reaction(emoji1)

        reaction, user = await self.bot.wait_for('reaction_add', check=lambda reaction, user: user != self.bot.user)

        # Check if user has a custom tumbnail image and add it to embed message
        Utils.add_thumbnail(embed, character.name, self.config["DEFAULT_WHITELIST"])
        
        await msg.edit(content="Done", embed=embed)
    
    @commands.command(name='test', aliases=['te'], brief="Test command", pass_context=True)
    async def tibia(self, ctx, *, name):
        embed = discord.Embed(
            #title='Tibia Discord Bot Test',
            colour=0xffffff
        )
        
        msg = await ctx.send(content=LOADING_MESSAGE, embed=embed)
        
        # Get character information from tibiadata.com
        character = await Tibia.get_character(name)
        print(character.to_json())
        
        embed.set_author(name=character.name, url=character.url)

        if character.deaths:
            for num, item in enumerate(character.deaths):            
                embed.description = KILL_MESSAGE.format(date=Utils.utc_to_local(item.time), level=item.level, killers=", ".join([killer.name for killer in item.killers if killer.name != item.name]), assists=", ".join([killer.name for killer in item.assists if killer.name != item.name]) if item.assists else EMBED_BLANK)
                #embed.add_field(name="Deaths" if num == 0 else EMBED_BLANK, value=kill_message if num == 0 else EMBED_BLANK, inline=True)    
                break
        
        await msg.edit(content="Done", embed=embed)
    
    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if str(reaction.emoji) == "\N{THUMBS UP SIGN}":
            print(str(reaction.emoji))
            pass
        if str(reaction.emoji) == "\N{SMILE}":
            print(str(reaction.emoji))
            pass

def setup(bot):
    bot.add_cog(Test(bot))
