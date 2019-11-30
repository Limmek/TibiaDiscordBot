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
        self._activity_task = bot.loop.create_task(self.activity_task())

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
            char = await Tibia.get_character(name)
            self.sql.addWhitelist(char.name, char.world, int(char.level))

    async def online_task(self):
        await self.bot.wait_until_ready()
                  
        async def start_task(self):
            self.tibia_online_list = []
            
            for name in self.sql.getWhitelistNames():
                try:
                    # Get player info from tibia.com
                    character = await Tibia.get_character(name) 
                    if character is None: return True
                    # Get world data from tibia.com
                    world = await Tibia.get_world(character.world) 
                    if world is None: return True
                
                except Exception as e:
                    print("online_task exception (whitelist): " + e)
                    pass

                finally:
                    # Update whitelist player level
                    self.sql.updateWhitelistLevel(character.name, int(character.level))
                    
                    if character.former_names is not None:
                        for former_name in character.former_names:
                            if former_name in self.sql.getWhitelistNames():
                                self.sql.removeWhitelist(former_name)
                                print("Removed former name " + former_name)
                            
                            if former_name in self.sql.getOnlinelistNames():
                                self.sql.removeOnlinelist(former_name)
                                print("Removed former name " + former_name)

                    for online_player in world.online_players:
                        # Adds name and level from world online list if player is online
                        if online_player.name == character.name:
                            self.sql.addOnlinelist(name=character.name, level=online_player.level, world=character.world)
                            #if not online_player.name in [player.get('name') for player in self.tibia_online_list]:
                            if not self.check_tibia_online_list(self.tibia_online_list, online_player.name):
                                self.tibia_online_list.append({"name":online_player.name, "level":online_player.level, "world":character.world})
                                        
                    # Send online message
                    if (self.check_tibia_online_list(self.tibia_online_list, character.name) and self.sql.getOnlinelistOnline(character.name) and not self.sql.getOnlinelistStatus(character.name)):
                        print("Discord: {name} ".format(name=character.name) + ONLINE_MESSAGE.format(level=character.level, voc=character.vocation, world=character.world))
                        try:
                            embed = discord.Embed(
                                title=character.name,
                                url=character.url,
                                description=ONLINE_MESSAGE.format(level=character.level, voc=character.vocation, world=character.world),
                                color=Utils.colors['GREEN'],
                            )
                            
                            # Check if user has a custom tumbnail image and add it to embed message
                            Utils.add_thumbnail(embed, character.name, self.config["DEFAULT_WHITELIST"])
                            
                            # Add function send to multiplie channels
                            # list of channel ids stored in config
                            
                            await self.bot.get_channel(int(self.config["CHANNEL_ID"])).trigger_typing()
                            msg = await self.bot.get_channel(int(self.config["CHANNEL_ID"])).send(embed=embed)
                        finally:
                            self.sql.updateOnlinelist(character.name, character.level, 1, 1)

                            # Adds Higescores if on top 300
                            await highscore_check(character, embed, msg)

                    # Send level advance message
                    if (self.check_tibia_online_list(self.tibia_online_list, character.name) and int(self.sql.getOnlinelistLevel(character.name)) < int([x["level"] for x in self.tibia_online_list if x["name"] == character.name][0])):    
                        print("Discord: {name} ".format(name=character.name) + LEVEL_ADVANCE_MESSAGE.format(level=[x["level"] for x in self.tibia_online_list if x["name"] == character.name][0]))
                        try:                    
                            embed = discord.Embed(
                                title=character.name,
                                url=character.url,
                                description=LEVEL_ADVANCE_MESSAGE.format(level=[x["level"] for x in self.tibia_online_list if x["name"] == character.name][0]),
                                color=Utils.colors['GOLD'],
                            )
                            
                            # Check if user has a custom tumbnail image and add it to embed message
                            Utils.add_thumbnail(embed, character.name, self.config["DEFAULT_WHITELIST"])
                            
                            # Add function send to multiplie channels
                            # list of channel ids stored in config

                            await self.bot.get_channel(int(self.config["CHANNEL_ID"])).trigger_typing()
                            msg = await self.bot.get_channel(int(self.config["CHANNEL_ID"])).send(embed=embed)
                        finally:
                            self.sql.updateOnlinelist(character.name, [x["level"] for x in self.tibia_online_list if x["name"] == character.name][0], 1, 1)

                            # Adds Higescores if on top 300
                            await highscore_check(character, embed, msg)

                    # Send death message
                    for num, item in enumerate(character.deaths):
                        self.sql.addLastDeath(name=character.name, deathdate=Utils.utc_to_local(item.time))
                        lastdeath, status = self.sql.getLastDeath(character.name)
                        if status == 0 or lastdeath != Utils.utc_to_local(item.time):
                            print("Discord: {name} ".format(name=character.name) + KILL_MESSAGE.format(date=Utils.utc_to_local(item.time), level=character.level, killers=", ".join([killer.name for killer in item.killers if killer.name != item.name]), assists=", ".join([killer.name for killer in item.assists if killer.name != item.name]) if item.assists else EMBED_BLANK))
                            try:
                                embed = discord.Embed(
                                    title=character.name,
                                    url=character.url,
                                    colour=Utils.colors['DARK_BUT_NOT_BLACK']
                                )

                                embed.description = KILL_MESSAGE.format(date=Utils.utc_to_local(item.time), level=item.level, killers=", ".join([killer.name for killer in item.killers if killer.name != item.name]), assists=", ".join([killer.name for killer in item.assists if killer.name != item.name]) if item.assists else EMBED_BLANK)
                                
                                # Check if user has a custom tumbnail image and add it to embed message
                                Utils.add_thumbnail(embed, character.name, self.config["DEFAULT_WHITELIST"])

                                # Add function send to multiplie channels
                                # list of channel ids stored in config

                                await self.bot.get_channel(int(self.config["CHANNEL_ID"])).trigger_typing()
                                msg = await self.bot.get_channel(int(self.config["CHANNEL_ID"])).send(embed=embed)
                            finally:
                                self.sql.updateLastDeath(name=character.name, deathdate=Utils.utc_to_local(item.time), status=1)
                                
                                await highscore_check(character, embed, msg)
                        break

            #print(LOADING_TIBIA_ONLINELIST.format(self.tibia_online_list))
            
            for name, level, world, online, status, date in self.sql.getOnlineList():
                try:
                    # Get player info from tibia.com
                    character = await Tibia.get_character(name) 
                    if character is None: return True
                
                except Exception as e:
                    print("online_task exception (onlinelist): " + e)
                    pass
                
                finally:
                    # Update online list if player is offline
                    if not self.check_tibia_online_list(self.tibia_online_list, character.name):
                        self.sql.updateOnlinelist(character.name, character.level, 0, 1)
                    
                    # Send offline message
                    if not self.check_tibia_online_list(self.tibia_online_list, character.name) and not self.sql.getOnlinelistOnline(character.name) and self.sql.getOnlinelistStatus(character.name):
                        print("Discord: {name} ".format(name=character.name) + OFFLINE_MESSAGE.format(level=character.level, voc=character.vocation, world=character.world))
                        try:
                            embed = discord.Embed(
                                title=character.name,
                                url=character.url,
                                description=OFFLINE_MESSAGE.format(level=character.level, voc=character.vocation, world=character.world),
                                color=Utils.colors['DARK_RED'],
                            )
                            
                            # Check if user has a custom tumbnail image and add it to embed message
                            Utils.add_thumbnail(embed, character.name, self.config["DEFAULT_WHITELIST"])
                            
                            # Add function send to multiplie channels
                            # list of channel ids stored in config
                            
                            await self.bot.get_channel(int(self.config["CHANNEL_ID"])).trigger_typing()
                            msg = await self.bot.get_channel(int(self.config["CHANNEL_ID"])).send(embed=embed)
                        finally:
                            self.sql.removeOnlinelist(character.name)               

                            # Adds Higescores if on top 300
                            await highscore_check(character, embed, msg)

            #print(LOADING_ONLINELIST.format(self.sql.getOnlineList()))

        while True:
            asyncio.create_task(start_task(self)) # Fix for loop breaking if any error ocurred while runing online_task??
            await asyncio.sleep(60) # run task in seperate thread every 60 seconds

    async def activity_task(self):
        await self.bot.wait_until_ready()
        while True:
            await self.bot.change_presence(status=discord.Status.online, activity=discord.Game(name=ACTIVITY_TITLE.format(online=self.sql.onlineCount())))
            await asyncio.sleep(15) # task runs every 15 seconds

def setup(bot):
    bot.add_cog(Core(bot))
