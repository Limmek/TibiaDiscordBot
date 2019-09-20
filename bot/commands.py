import discord
from discord.ext import commands

from constants import *
from utils import *
from sqlite import Sql
from tibia import *
from guildstatseu import GuildStats

class Commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = Config.load_config()
        self.sql = Sql()

    @commands.command(name='whitelist', aliases=['wl', 'wlist'], brief="Show whitelist")
    async def whitelist(self, ctx):
        whitelist = self.sql.getWhitelist()
        embed = discord.Embed(
            title=LOADING_WHITELIST_MESSAGE,
            colour=0xffffff
        )
        msg = await ctx.send(LOADING_WHITELIST_MESSAGE)
        embed.title = TITLE_WHITELIST
        for name, world in whitelist:
            character = await TibiaData.get_character(name) # Get character information from tibiadata.com
            text = "{} {} on {}".format(character.level, character.vocation, character.world)
            embed.add_field(name=name, value=text, inline=False)
            await msg.edit(content=LOADING_WHITELIST_MESSAGE, embed=embed)
        await msg.edit(content=LOADING_DONE, embed=embed)
    
    @commands.command(name='add', aliases=[], brief="Add player to whitelist")
    async def add(self, ctx, *, name):
        msg = await ctx.send(LODING_CHARACTER_DATA)
        character = await TibiaData.get_character(name) # Get character information from tibiadata.com
        if character is not None:
            whitelist = self.sql.addWhitelist(character.name, character.world)
            await msg.edit(content=ADD_WHITELIST_MESSAGE.format(name=character.name, level=character.level, voc=character.vocation, world=character.world))
        else:
            await msg.edit(content=ERROR_LOADING_DATA)
            
    @commands.command(name='remove', aliases=[], brief="Remove player from whitelist")
    async def remove(self, ctx, *, name):
        msg = await ctx.send(LODING_CHARACTER_DATA)
        character = await TibiaData.get_character(name) # Get character information from tibiadata.com
        whitelist = self.sql.removeFromWhitelist(character.name)
        await msg.edit(content=REMOVE_WHITELIST_MESSAGE.format(name=character.name, level=character.level, voc=character.vocation, world=character.world)) 

    @commands.command(name='pg', aliases=['time'], brief="Show players online time")
    async def pg(self, ctx, *, name):
        msg = await ctx.send(LODING_CHARACTER_DATA)
        character = await TibiaData.get_character(name) # Get character information from tibiadata.com
        if character is None:
            await msg.edit(content=ERROR_LOADING_DATA)
        else:
            timeOnline = await GuildStats.getTimeOnline(name)
            if not timeOnline:
                await msg.edit(content=ERROR_LOADING_DATA)        
            else:
                embed = discord.Embed(
                    title=TITLE_ONLINE_TIME,
                    description=DESCRIPTION_ONLINE_TIME.format(name=character.name, level=character.level, voc=character.vocation, world=character.world, url=character.url),
                    colour=0xffffff,
                )
                embed.add_field(name="Last month", value=str(timeOnline["Last month"]), inline=True)
                embed.add_field(name="Current month", value=str(timeOnline["Current month"]), inline=True)
                embed.add_field(name="Current week", value=str(timeOnline["Current week"]), inline=True)
                embed.add_field(name="Mon", value=str(timeOnline["Mon"]), inline=True)
                embed.add_field(name="Tue", value=str(timeOnline["Tue"]), inline=True)
                embed.add_field(name="Wed", value=str(timeOnline["Wed"]), inline=True)
                embed.add_field(name="Thu", value=str(timeOnline["Thu"]), inline=True)
                embed.add_field(name="Fri", value=str(timeOnline["Fri"]), inline=True)
                embed.add_field(name="Sat", value=str(timeOnline["Sat"]), inline=True)
                embed.add_field(name="Sun", value=str(timeOnline["Sun"]), inline=True)

                # Check if user has a custom tumbnail image and add it to embed message
                Utils.add_thumbnail(embed, character.name, self.config["DEFAULT_WHITELIST"])
                
                await msg.edit(content=LOADING_DONE, embed=embed)

    @commands.command(name='exp', aliases=['xp'], brief="Show players experience change if player is on top 300")
    async def exp(self, ctx, *, name):
        msg = await ctx.send(LODING_CHARACTER_DATA)
        character = await TibiaData.get_character(name) # Get character information from tibiadata.com
        if character is None:
            await msg.edit(content=ERROR_LOADING_DATA)
        else:
            expChange = await GuildStats.getExperienceChange(name)
            if not expChange:
                await msg.edit(content=ERROR_LOADING_DATA)        
            else:
                embed = discord.Embed(title=TITLE_EXPERIENCE_CHANGE, description="", colour=0xffffff)
                
                for item in expChange:
                    embed.add_field(name=item["Date"], value=EXP_MESSAGE.format(item["Exp change"]), inline=True)

                # Check if user has a custom tumbnail image and add it to embed message
                Utils.add_thumbnail(embed, character.name, self.config["DEFAULT_WHITELIST"])            
                
                await msg.edit(content=LOADING_DONE, embed=embed)

    @commands.command(name='player', aliases=['name', 'n'], brief="Get information about player by name", pass_context=True)
    async def player(self, ctx, *, name):  
        msg = await ctx.send(content=LOADING_MESSAGE)
        character = await TibiaData.get_character(name) # Get character information from tibiadata.com
        if character is None:
            await msg.edit(content=ERROR_LOADING_DATA)
        else:
            embed = discord.Embed(colour=0xffffff)
            
            embed.set_author(name=character.name, url=character.url)
            
            embed.add_field(name="Level", value=character.level, inline=True)
            embed.add_field(name="Vocation", value=character.vocation, inline=True)
            embed.add_field(name="Sex", value=str(character.sex).capitalize(), inline=True)
            embed.add_field(name="Married to", value=character.married_to, inline=True)
            embed.add_field(name="World", value=character.world, inline=True)
            embed.add_field(name="Residence", value=character.residence, inline=True)        
            embed.add_field(name="House", value=HOUSE.format(name=character.house.name, town=character.house.town) if character.house is not None else EMBED_NONE, inline=False)  
            embed.add_field(name="Guild", value=GUILD.format(guild=character.guild_membership.name, url=character.guild_membership.url) if character.guild_membership is not None else EMBED_NONE, inline=True)
            embed.add_field(name="Rank", value=character.guild_membership.rank if character.guild_membership is not None else EMBED_NONE, inline=True)    
            embed.add_field(name="Comment", value=character.comment, inline=False)
            embed.add_field(name="Account Created", value=Utils.utc_to_local(character.account_information.created) if character.account_information is not None else EMBED_NONE, inline=True)
            embed.add_field(name="Account Status", value=character.account_status, inline=True)
            embed.add_field(name="Loyalty Title", value=character.account_information.loyalty_title if character.account_information is not None else EMBED_NONE, inline=True)
            embed.add_field(name="Achievement points", value=character.achievement_points, inline=True)
            embed.add_field(name="Achievements", value=str(",".join([achievement.name for achievement in character.achievements if character.achievements is not None])).replace(",","\n") if character.achievements else EMBED_NONE, inline=True)
            
            await msg.edit(embed=embed)
            
            if character.deaths:
                for num, item in enumerate(character.deaths):
                    kill_message = KILL_MESSAGE.format(date=Utils.utc_to_local(item.time), level=item.level, killers=", ".join([killer.name for killer in item.killers if killer.name != item.name]), assists=", ".join([killer.name for killer in item.assists if killer.name != item.name]) if item.assists else EMBED_BLANK)
                    embed.add_field(name="Deaths" if num == 0 else EMBED_BLANK , value=kill_message, inline=True)    
                    await msg.edit(embed=embed)
            
            # Check if user has a custom tumbnail image and add it to embed message
            Utils.add_thumbnail(embed, character.name, self.config["DEFAULT_WHITELIST"])

            await msg.edit(content=LOADING_DONE, embed=embed)

def setup(bot):
    bot.add_cog(Commands(bot))