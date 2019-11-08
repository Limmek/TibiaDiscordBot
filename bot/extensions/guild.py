import asyncio

import discord
from discord.ext import commands

from constants import *
from utils import *
from sqlite import Sql
from tibia import *

class Guild(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = Config.load_config()
        self.sql = Sql()
        self._guild = bot.loop.create_task(self.update_guild())

    async def update_guild(self):
        async def start_guild_task(self):
            if self.config["GUILD_NAME"] is None:
                return True

            guildlist = await TibiaData.get_guild(self.config["GUILD_NAME"])

            if guildlist is None: 
                return True
            
            for item in guildlist.members:
                if item.name not in self.sql.getWhitelistNames() :
                    print("Added " + item.name + " to whitelist")
                    await self.bot.get_channel(int(self.config["CHANNEL_ID"])).trigger_typing()
                    try:
                        character = await TibiaData.get_character(item.name) # Get character information from tibiadata.com
                        if character is None:
                            return True
                        msg = await self.bot.get_channel(int(self.config["CHANNEL_ID"])).send(LODING_CHARACTER_DATA)
                    except Exception as e:
                        print(str(e))
                        pass
                    finally:
                        whitelist = self.sql.addWhitelist(character.name, character.world, character.level)
                        for num, item in enumerate(character.deaths):
                            lastdeath = self.sql.addLastDeath(name=character.name, deathdate=Utils.utc_to_local(item.time), status=1)
                            break
                        await msg.edit(content=ADD_WHITELIST_MESSAGE.format(name=character.name, level=character.level, voc=character.vocation, world=character.world))
        
        await self.bot.wait_until_ready()
        while True:
            asyncio.create_task(start_guild_task(self))
            await asyncio.sleep(300)

def setup(bot):
    bot.add_cog(Guild(bot))
