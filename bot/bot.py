import asyncio

import discord
from discord.ext import commands

from constants import *
from utils import *
from sqlite import Sql

config = Config.load_config()
sql = Sql()

startup_extensions = ["core", "commands"] + config["EXTENTIONS"]
bot = commands.Bot(command_prefix=(config["PREFIX"].split(" ")))

@bot.event
async def on_ready():
    await bot.change_presence(status=discord.Status.do_not_disturb, activity=discord.Game(LOADING_MESSAGE))
    print(LOGIN_MESSAGE.format(bot.user.name, bot.user.id, config["PREFIX"], config["EXTENTIONS"]))
    print(LOADING_DEFAULT_WHITELIST.format(config["DEFAULT_WHITELIST"]))
    print(LOADING_WHITELIST.format(sql.getWhitelist()))
    print(LOADING_ONLINELIST.format(sql.getOnlineList()))
    print(BOT_READY.format(bot.user.name))

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.MissingRequiredArgument):
        await ctx.send(ERROR_MISSING_ARGUMENT)

if __name__ == "__main__":
    for extension in startup_extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            exc = '{}: {}'.format(type(e).__name__, e)
            print('Failed to load extension {}\n{}'.format(extension, exc))
    
    bot.run(config["TOKEN"])
