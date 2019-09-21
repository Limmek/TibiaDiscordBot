import discord
from discord.ext import commands

from constants import *
from utils import *
from sqlite import Sql
from tibia import *
from guildstatseu import GuildStats

class Core(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = Config.load_config()
        self.sql = Sql()
        self.tibia_online_list = []
        self._update_task = bot.loop.create_task(self.update_default_whitelist())
        self._online_task = bot.loop.create_task(self.online_task())
        self.activity_task = bot.loop.create_task(self.activity_task())

    # Returns list of names from onlinelist
    def get_tibia_onlinelist_names(self):
        return [player.get('name') for player in self.tibia_online_list] 
    
    # Returns True if name exist in onlinelist
    def check_tibia_online_list(self, onlinelist, name):
        if (name in [player.get("name") for player in onlinelist]): return True
        return False

    # Update Whitelist with default whitelist data
    async def update_default_whitelist(self):
        for name in self.config["DEFAULT_WHITELIST"]:
            char = await TibiaData.get_character(name)
            self.sql.addWhitelist(char.name, char.world)

    async def online_task(self):
        await self.bot.wait_until_ready()
        while True:
            self.tibia_online_list = []
            for name in self.sql.getWhitelistNames():
                # Get player info from tibiadata.com
                character = await Tibia.get_character(name) 
                if character is None: return True
                # Get world data from tibia.com
                world = await Tibia.get_world(character.world) 
                if world is None: return True
                
                for online_player in world.online_players:
                    # Adds name and level from world online list if player is online
                    if online_player.name == character.name:
                        self.sql.addToOnlinelist(name=character.name, level=online_player.level, world=character.world, deathdate=[Utils.utc_to_local(character.deaths[0].time) if character.deaths else ""][0])
                        #if not online_player.name in [player.get('name') for player in self.tibia_online_list]:
                        if not self.check_tibia_online_list(self.tibia_online_list, online_player.name):
                            self.tibia_online_list.append({"name":online_player.name, "level":online_player.level, "world":character.world})
                                     
                # Send online message
                if (self.check_tibia_online_list(self.tibia_online_list, character.name) and self.sql.getOnline(character.name) and not self.sql.getStatus(character.name)):
                    print("Discord: {name} ".format(name=character.name) + ONLINE_MESSAGE.format(level=character.level, voc=character.vocation, world=character.world))
                    try:                    
                        embed = discord.Embed(
                            title=character.name,
                            url=character.url,
                            description=ONLINE_MESSAGE.format(level=character.level, voc=character.vocation, world=character.world),
                            color=0x00c95d,
                        )
                        
                        # Removed due to not seen in notification message on android/ios
                        #embed.set_author(name=character.name, url=character.url)
                        
                        # Check if user has a custom tumbnail image and add it to embed message
                        Utils.add_thumbnail(embed, character.name, self.config["DEFAULT_WHITELIST"])
                        
                        # Add function send to multiplie channels
                        # list of channel ids stored in config
                        
                        await self.bot.get_channel(int(self.config["CHANNEL_ID"])).trigger_typing()
                        msg = await self.bot.get_channel(int(self.config["CHANNEL_ID"])).send(embed=embed)
                    finally:
                        self.sql.updateOnlinelist(character.name, character.level, 1, 1)
                    
                    await self.highscore_check(character, embed, msg)

                # Send level advance message
                if (self.check_tibia_online_list(self.tibia_online_list, character.name) and int(self.sql.getLevel(character.name)) < int([x["level"] for x in self.tibia_online_list if x["name"] == character.name][0])):    
                    print("Discord: {name} ".format(name=character.name) + LEVEL_ADVANCE_MESSAGE.format(level=[x["level"] for x in self.tibia_online_list if x["name"] == character.name][0]))
                    try:                    
                        embed = discord.Embed(
                            title=character.name,
                            url=character.url,
                            description=LEVEL_ADVANCE_MESSAGE.format(level=[x["level"] for x in self.tibia_online_list if x["name"] == character.name][0]),
                            color=0xF5A623,
                        )
                        
                        # Removed due to not seen in notification message on android/ios
                        #embed.set_author(name=character.name, url=character.url)
                        
                        # Check if user has a custom tumbnail image and add it to embed message
                        Utils.add_thumbnail(embed, character.name, self.config["DEFAULT_WHITELIST"])
                        
                        # Add function send to multiplie channels
                        # list of channel ids stored in config

                        await self.bot.get_channel(int(self.config["CHANNEL_ID"])).trigger_typing()
                        msg = await self.bot.get_channel(int(self.config["CHANNEL_ID"])).send(embed=embed)
                    finally:
                        self.sql.updateOnlinelist(character.name, [x["level"] for x in self.tibia_online_list if x["name"] == character.name][0], 1, 1)
                    
                    await self.highscore_check(character, embed, msg)

                # Send death message
                if (self.check_tibia_online_list(self.tibia_online_list, character.name) and len(character.deaths) >= 1 and (self.sql.getDeathdate(character.name) == None or self.sql.getDeathdate(character.name) != Utils.utc_to_local(character.deaths[0].time))):
                    print("Discord: {name} ".format(name=character.name) + KILL_MESSAGE.format(date=Utils.utc_to_local(item.time), level=item.level, killers=", ".join([killer.name for killer in item.killers if killer.name != item.name]), assists=", ".join([killer.name for killer in item.assists if killer.name != item.name]) if item.assists else EMBED_BLANK))
                    try:
                        embed = discord.Embed(
                            title=character.name,
                            url=character.url,
                            colour=0x992d22
                        )

                        # Removed due to not seen in notification message on android/ios
                        #embed.set_author(name=character.name, url=character.url)
                        
                        for num, item in enumerate(character.deaths):            
                            embed.description = KILL_MESSAGE.format(date=Utils.utc_to_local(item.time), level=item.level, killers=", ".join([killer.name for killer in item.killers if killer.name != item.name]), assists=", ".join([killer.name for killer in item.assists if killer.name != item.name]) if item.assists else EMBED_BLANK)
                            break
                        
                        # Check if user has a custom tumbnail image and add it to embed message
                        Utils.add_thumbnail(embed, character.name, self.config["DEFAULT_WHITELIST"])

                        # Add function send to multiplie channels
                        # list of channel ids stored in config

                        await self.bot.get_channel(int(self.config["CHANNEL_ID"])).trigger_typing()
                        msg = await self.bot.get_channel(int(self.config["CHANNEL_ID"])).send(embed=embed)
                    finally:
                        self.sql.addLastDeathTime(character.name, Utils.utc_to_local(character.deaths[0].time))
                    
                    await self.highscore_check(character, embed, msg)

            #print(LOADING_TIBIA_ONLINELIST.format(self.tibia_online_list))
            
            for name, level, world, deathdate, online, status, date in self.sql.getOnlineList():
                # Get player info from tibiadata.com
                character = await Tibia.get_character(name) 
                if character is None: return True

                # Update online list if player is offline
                if not self.check_tibia_online_list(self.tibia_online_list, character.name):
                    self.sql.updateOnlinelist(character.name, character.level, 0, 1)
                
                # Send offline message
                if not self.check_tibia_online_list(self.tibia_online_list, character.name) and not self.sql.getOnline(character.name) and self.sql.getStatus(character.name):
                    print("Discord: {name} ".format(name=character.name) + OFFLINE_MESSAGE.format(level=character.level, voc=character.vocation, world=character.world))
                    try:
                        embed = discord.Embed(
                            title=character.name,
                            url=character.url,
                            description=OFFLINE_MESSAGE.format(level=character.level, voc=character.vocation, world=character.world),
                            color=0xD0021B,
                        )
                        
                        # Removed due to not seen in notification message on android/ios
                        #embed.set_author(name=character.name, url=character.url)
                        
                        # Check if user has a custom tumbnail image and add it to embed message
                        Utils.add_thumbnail(embed, character.name, self.config["DEFAULT_WHITELIST"])
                        
                        # Add function send to multiplie channels
                        # list of channel ids stored in config
                        
                        await self.bot.get_channel(int(self.config["CHANNEL_ID"])).trigger_typing()
                        msg = await self.bot.get_channel(int(self.config["CHANNEL_ID"])).send(embed=embed)
                    finally:
                        self.sql.removeFromOnlinelist(character.name)               

                    await self.highscore_check(character, embed, msg)

            #print(LOADING_ONLINELIST.format(self.sql.getOnlineList()))
            await asyncio.sleep(30) # task runs every 30 seconds

    async def activity_task(self):
        await self.bot.wait_until_ready()
        while True:
            await self.bot.change_presence(status=discord.Status.online, activity=discord.Game(name=ACTIVITY_TITLE.format(online=self.sql.onlineCount())))
            await asyncio.sleep(15) # task runs every 15 seconds

    async def highscore_check(self, character, embed, msg):
        # Highscores
        # Check Experience
        experience = await TibiaData.check_player_highscore(character.name, character.world, tibiapy.Category.EXPERIENCE)
        if experience is not None:
            embed.add_field(name=HIGHSCORE_EXP_MESSAGE.format(experience.rank), value=str(experience.value), inline=True)
            await msg.edit(content=LOADING_MESSAGE, embed=embed)

        # Check magic level if druid or sorcerer
        if (character.vocation in [tibiapy.Vocation.DRUID, tibiapy.Vocation.ELDER_DRUID, tibiapy.Vocation.SORCERER, tibiapy.Vocation.MASTER_SORCERER]):
            magic = await TibiaData.check_player_highscore(character.name, character.world, tibiapy.Category.MAGIC_LEVEL)
            if magic is not None:
                
                embed.add_field(name=HIGHSCORE_MAGIC_MESSAGE.format(magic.rank), value=str(magic.value), inline=True)
                await msg.edit(content=LOADING_MESSAGE, embed=embed)

        # Check distance skill if paladin
        if (character.vocation in [tibiapy.Vocation.PALADIN, tibiapy.Vocation.ROYAL_PALADIN]):
            distance = await TibiaData.check_player_highscore(character.name, character.world, tibiapy.Category.DISTANCE_FIGHTING)
            if distance is not None:
                
                embed.add_field(name=HIGHSCORE_DISTANCE_MESSAGE.format(distance.rank), value=str(distance.value), inline=True)
                await msg.edit(content=LOADING_MESSAGE, embed=embed)

        # Check mele skills if knight
        if (character.vocation in [tibiapy.Vocation.KNIGHT, tibiapy.Vocation.ELITE_KNIGHT]):
            # Sword skill
            sword = await TibiaData.check_player_highscore(character.name, character.world, tibiapy.Category.SWORD_FIGHTING)
            if sword is not None:
                
                embed.add_field(name=HIGHSCORE_SWORD_MESSAGE.format(sword.rank), value=str(sword.value), inline=True)
                await msg.edit(content=LOADING_MESSAGE, embed=embed)

            # Axe skill
            axe = await TibiaData.check_player_highscore(character.name, character.world, tibiapy.Category.AXE_FIGHTING)
            if axe is not None:
                
                embed.add_field(name=HIGHSCORE_AXE_MESSAGE.format(axe.rank), value=str(axe.value), inline=True)
                await msg.edit(content=LOADING_MESSAGE, embed=embed)

            # Club skill
            club = await TibiaData.check_player_highscore(character.name, character.world, tibiapy.Category.CLUB_FIGHTING)
            if club is not None:
                
                embed.add_field(name=HIGHSCORE_CLUB_MESSAGE.format(club.rank), value=str(club.value), inline=True)
                await msg.edit(content=LOADING_MESSAGE, embed=embed)

        # Check Shielding all vocations
        shielding = await TibiaData.check_player_highscore(character.name, character.world, tibiapy.Category.SHIELDING)
        if shielding is not None:
            
            embed.add_field(name=HIGHSCORE_SHIELDING_MESSAGE.format(shielding.rank), value=str(shielding.value), inline=True)
            await msg.edit(content=LOADING_MESSAGE, embed=embed)

        # Check Fist all vocations
        fist = await TibiaData.check_player_highscore(character.name, character.world, tibiapy.Category.FIST_FIGHTING)
        if fist is not None:
            
            embed.add_field(name=HIGHSCORE_FIST_MESSAGE.format(fist.rank), value=str(fist.value), inline=True)
            await msg.edit(content=LOADING_MESSAGE, embed=embed)

        # Check Fishing all vocations
        fishing = await TibiaData.check_player_highscore(character.name, character.world, tibiapy.Category.FISHING)
        if fishing is not None:
            
            embed.add_field(name=HIGHSCORE_FISHING_MESSAGE.format(fishing.rank), value=str(fishing.value), inline=True)
            await msg.edit(content=LOADING_MESSAGE, embed=embed)

        # Check Fishing all vocations
        achievements = await TibiaData.check_player_highscore(character.name, character.world, tibiapy.Category.ACHIEVEMENTS)
        if achievements is not None:
            
            embed.add_field(name=HIGHSCORE_ACHIEVEMENTS_MESSAGE.format(achievements.rank), value=str(achievements.value), inline=True)
            await msg.edit(content=LOADING_MESSAGE, embed=embed)

        # Check Fishing all vocations
        loyalty = await TibiaData.check_player_highscore(character.name, character.world, tibiapy.Category.LOYALTY_POINTS)
        if loyalty is not None:
            embed.add_field(name=HIGHSCORE_LOYALTY_POINTS_MESSAGE.format(loyalty.rank), value=str(loyalty.value), inline=True)
            await msg.edit(content=LOADING_MESSAGE, embed=embed)
        
        await msg.edit(content="")

def setup(bot):
    bot.add_cog(Core(bot))
