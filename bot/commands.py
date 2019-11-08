import discord
from discord.ext import commands

from datetime import datetime
import random

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

    @commands.command(name='shutdown', aliases=[], brief="Shutdown", pass_context=True, hidden=True)
    async def shutdown(self, ctx):
        msg = await ctx.send("Shuting down....")
        await self.bot.logout()

    @commands.command(name='restart', aliases=[], brief="Restart", pass_context=True, hidden=True)
    async def restart(self, ctx):
        msg = await ctx.send("Shuting down")
        await ctx.trigger_typing()
        try:
            await self.bot.close()
        except:
            pass
        finally:
            os.system("py -3 " + os.path.dirname(os.path.realpath(__file__)) + "\\bot.py")
            

    @commands.command(name='whitelist', aliases=['wl', 'wlist'], brief="Show whitelist")
    async def whitelist(self, ctx):
        msg = await ctx.send(LOADING_WHITELIST_MESSAGE)
        await ctx.trigger_typing()
        whitelist = self.sql.getWhitelist()
        embed = discord.Embed(
            title=TITLE_WHITELIST,
            colour=Utils.colors['WHITE']
        )

        embed.set_footer(
            text=f'Requested by {ctx.message.author.name}',
            icon_url=ctx.message.author.avatar_url
        )

        for name, world, level in whitelist:
            character = await TibiaData.get_character(name) # Get character information from tibiadata.com
            text = "{} {} on {}".format(character.level, character.vocation, character.world)
            embed.add_field(name=name, value=text, inline=False)
            await msg.edit(content=LOADING_WHITELIST_MESSAGE, embed=embed)
        await msg.edit(content=LOADING_DONE, embed=embed)
    
    @commands.command(name='add', aliases=[], brief="Add player to whitelist")
    async def add(self, ctx, *, name):
        await ctx.trigger_typing()
        
        character = await TibiaData.get_character(name) # Get character information from tibiadata.com
        if character is None:
            await ctx.send(content=ERROR_LOADING_DATA)
            return True

        whitelist = self.sql.addWhitelist(character.name, character.world, character.level)
        msg = await ctx.send(LODING_CHARACTER_DATA)
        await msg.edit(content=ADD_WHITELIST_MESSAGE.format(name=character.name, level=character.level, voc=character.vocation, world=character.world)) 
            
    @commands.command(name='remove', aliases=[], brief="Remove player from whitelist")
    async def remove(self, ctx, *, name):
        await ctx.trigger_typing()

        character = await TibiaData.get_character(name) # Get character information from tibiadata.com
        if character is None:
            await ctx.send(content=ERROR_LOADING_DATA)
            return True
            
        whitelist = self.sql.removeFromWhitelist(character.name)
        msg = await ctx.send(LODING_CHARACTER_DATA)
        await msg.edit(content=REMOVE_WHITELIST_MESSAGE.format(name=character.name, level=character.level, voc=character.vocation, world=character.world)) 

    @commands.command(name='pg', aliases=['time'], brief="Show players online time")
    async def pg(self, ctx, *, name):
        await ctx.trigger_typing()
        
        character = await TibiaData.get_character(name) # Get character information from tibiadata.com
        if character is None:
            await ctx.send(content=ERROR_LOADING_DATA)
            return True
            
        timeOnline = await GuildStats.getTimeOnline(character.name)
        if not timeOnline:
            await ctx.send(content=ERROR_LOADING_DATA)  
            return True      

        embed = discord.Embed(
            title=TITLE_ONLINE_TIME,
            description=DESCRIPTION_ONLINE_TIME.format(name=character.name, level=character.level, voc=character.vocation, world=character.world, url=character.url),
            colour=Utils.colors['DARK_GREEN'],
        )

        embed.set_footer(
            text=f'Requested by {ctx.message.author.name}',
            icon_url=ctx.message.author.avatar_url
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
        
        msg = await ctx.send(LODING_CHARACTER_DATA)
        await msg.edit(content=LOADING_DONE, embed=embed)

    @commands.command(name='exp', aliases=['xp'], brief="Show players experience change if player is on top 300")
    async def exp(self, ctx, *, name):
        await ctx.trigger_typing()
        
        character = await TibiaData.get_character(name) # Get character information from tibiadata.com
        if character is None:
            await ctx.send(content=ERROR_LOADING_DATA)
            return True
        
        expChange = await GuildStats.getExperienceChange(name)
        if not expChange:
            await ctx.send(content=ERROR_LOADING_DATA)        
            return True

        msg = await ctx.send(LODING_CHARACTER_DATA)
        await ctx.trigger_typing()
        
        embed = discord.Embed(
            title=TITLE_EXPERIENCE_CHANGE,
            description="",
            colour=Utils.colors['DARK_GREEN']
        )

        embed.set_footer(
            text=f'Requested by {ctx.message.author.name}',
            icon_url=ctx.message.author.avatar_url
        )
        
        for item in expChange:
            embed.add_field(name=item["Date"], value=EXP_MESSAGE.format(item["Exp change"]), inline=True)

        # Check if user has a custom tumbnail image and add it to embed message
        Utils.add_thumbnail(embed, character.name, self.config["DEFAULT_WHITELIST"])            
        
        await msg.edit(content=LOADING_DONE, embed=embed)

    @commands.command(name='player', aliases=['name', 'n'], brief="Get information about player by name", pass_context=True)
    async def player(self, ctx, *, name):  
        await ctx.trigger_typing()
        
        character = await TibiaData.get_character(name) # Get character information from tibiadata.com
        if character is None:
            await ctx.send(content=ERROR_LOADING_DATA)
            return True
        
        embed = discord.Embed(
            colour=Utils.colors['ORANGE']
        )
        
        embed.set_footer(
            text=f'Requested by {ctx.message.author.name}',
            icon_url=ctx.message.author.avatar_url
        )
        
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
        
        msg = await ctx.send(content=LOADING_MESSAGE, embed=embed)
        await ctx.trigger_typing()
        
        if character.deaths:
            for num, item in enumerate(character.deaths):
                kill_message = KILL_MESSAGE.format(date=Utils.utc_to_local(item.time), level=item.level, killers=", ".join([killer.name for killer in item.killers if killer.name != item.name]), assists=", ".join([killer.name for killer in item.assists if killer.name != item.name]) if item.assists else EMBED_BLANK)
                embed.add_field(name="Deaths" if num == 0 else EMBED_BLANK , value=kill_message, inline=True)    
                await msg.edit(embed=embed)
        
        # Check if user has a custom tumbnail image and add it to embed message
        Utils.add_thumbnail(embed, character.name, self.config["DEFAULT_WHITELIST"])

        await msg.edit(content=LOADING_DONE, embed=embed)

    @commands.command(name='rank', aliases=['top'], brief="Get players highscore information", pass_context=True)
    async def rank(self, ctx, *, name):  
        await ctx.trigger_typing()

        # Get character information from tibia.com
        character = await Tibia.get_character(name)

        if character is None:
            await ctx.send(content=ERROR_LOADING_DATA)
            return True
        
        embed = discord.Embed(
            colour=Utils.colors['DARK_ORANGE'],
        )

        embed.set_footer(
            text=f'Requested by {ctx.message.author.name}',
            icon_url=ctx.message.author.avatar_url
        )

        embed.set_author(name=character.name, url=character.url)
        
        msg = await ctx.send(content=LOADING_MESSAGE)
        await ctx.trigger_typing()

        # Highscores
        await highscore_check(character, embed, msg)

    @commands.command(name='share', aliases=['s'], brief="Check experience level range of player or level", pass_context=True)
    async def share(self, ctx, *, name):  
        await ctx.trigger_typing()
        
        embed = discord.Embed(
            colour=Utils.colors['DARK_ORANGE']
        )
        
        embed.set_footer(
            text=f'Requested by {ctx.message.author.name}',
            icon_url=ctx.message.author.avatar_url
        )

        character = None
        level = 0
        
        if name.isdigit():
            # If a int value(levle) is entered instead for character name
            level = int(name)
        else:
            # Get character information from tibiadata.com
            character = await TibiaData.get_character(name)
            if character is not None:
                level = character.level
        
        if level == 0:
            await ctx.send(content=ERROR_LOADING_DATA)
            return
        
        level_min = round((level/3*2))
        level_max = round((level*3/2) + 0.5)

        embed.title = SHARE_MESSAGE.format(level=level, min=level_min, max=level_max) if name.isdigit() else SHARE_PLAYER_MESSAGE.format(name=character.name, level=character.level, min=level_min, max=level_max)
        
        msg = await ctx.send(content=EMBED_BLANK, embed=embed)

        # Check if whitelisted player is able to share exp
        update = False
        if not name.isdigit():
            for name, world, level in self.sql.getWhitelist():
                if level >= level_min and level <= level_max and world == character.world and name != character.name:
                    embed.add_field(name=name, value='Level: '+str(level), inline=True)
                    update = True
        
        if update:
            await msg.edit(embed=embed)

    @commands.command(name='rashid', aliases=['r'], brief="Tells where rashid can be found today", pass_context=True)
    async def rashid(self, ctx):  
        await ctx.trigger_typing()
        embed = discord.Embed(
            colour=Utils.colors['DARK_ORANGE']
        )
        
        embed.set_footer(
            text=f'Requested by {ctx.message.author.name}',
            icon_url=ctx.message.author.avatar_url
        )
        RASHID_MESSAGES = ["Rashid can be found in {town} today.", "Today Rashid will be found in {town}.", "Today you can find Rashid in {town}."]
        rashid = {
            1:"Svargrond",
            2:"Liberty Bay",
            3:"Port Hope",
            4:"Ankrahmun",
            5:"Darashia",
            6:"Edron",
            7:"Carlin"
        }
        if datetime.now() >= datetime.now().replace(hour=10, minute=00):
            rashid_day = datetime.now().isoweekday()
        else:
            rashid_day = datetime.now().isoweekday()-1

        embed.title = RASHID_MESSAGES[random.randrange(0,len(RASHID_MESSAGES))].format(town=rashid.get(rashid_day))
        msg = await ctx.send(content=EMBED_BLANK, embed=embed)

    @commands.command(name='check_yasir', aliases=['yasir', 'y'], brief="Yasir information from https://yasironline.tibiageeks.com", pass_context=True)
    async def check_yasir(self, ctx):

        embed = discord.Embed(
            colour=Utils.colors['WHITE']
        )

        embed.set_footer(
            text=f'Requested by {ctx.message.author.name}',
            icon_url=ctx.message.author.avatar_url
        )
        
        msg = await ctx.send(content='Yasir #TODO', embed=embed)

def setup(bot):
    bot.add_cog(Commands(bot))
