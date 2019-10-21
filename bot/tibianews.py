import asyncio
import aiohttp

import discord
from discord.ext import commands

from constants import *
from utils import *
from sqlite import Sql
from bs4 import BeautifulSoup

class TibiaNews(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = Config.load_config()
        self.sql = Sql()
        self._table = self.sql.createTable('''CREATE TABLE IF NOT EXISTS tibia_news_ticker
                        (content text UNIQUE, datetime text, status int)''')
        self._news_ticker = bot.loop.create_task(self.update_news_ticker())

    async def update_news_ticker(self):
        async def start_news_ticker(self):
            # News
            #data = await Tibia.get_news()
            #print(data.title) print(data.date) print(data.content)
            
            content = await self.get_latest_news_ticker()
            datetime, content = self.from_tibia_data(content)

            query = 'INSERT OR IGNORE INTO tibia_news_ticker values (?,?,?)'
            sql = self.sql.executeQuery(query, [content, datetime, 0])
            
            data = self.sql.executeQuery('SELECT * FROM tibia_news_ticker WHERE status=0', []).fetchone()
            if data is None:
                return True
            
            old_content, old_datetime, status = data
            if status == 0 and datetime == old_datetime:
                print("DISCORD NEWS TICKER: " + content)
                try:
                    embed = discord.Embed(
                        title="Tibia News Ticker",
                        colour=Utils.colors['RED']
                    )
                    embed.description = content
                    embed.set_footer(
                        text=f'Posted: {datetime}',
                    )
                    msg = await self.bot.get_channel(int(self.config["CHANNEL_ID"])).send(embed=embed)
                except:
                    pass
                finally:
                    self.sql.executeQuery("UPDATE tibia_news_ticker SET status=? WHERE datetime=?", [1, old_datetime])
                    
                    tibia_role = discord.utils.get(msg.guild.roles, name="Tibia")
                    if tibia_role is not None:
                        await msg.edit(content=f'{tibia_role.mention}')
        while True:
            await self.bot.wait_until_ready()
            asyncio.create_task(start_news_ticker(self))
            await asyncio.sleep(10)

    async def get_latest_news_ticker(self):
        content = None
        url = "https://www.tibia.com/news/?subtopic=latestnews"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    content = await resp.text()
        except Exception as e:
            print(str(e))
            pass
        return content

    def from_tibia_data(self, content):
        if content is None:
            return
 
        soup = BeautifulSoup(content, 'lxml')
        
        news_ticker = soup.find("div", id="NewsTicker")
        
        text = news_ticker.find("div", class_="NewsTickerFullText").find("p").text
        date = news_ticker.find("span", class_="NewsTickerDate").getText("p")
        time = news_ticker.find("span", class_="NewsTickerTime").getText("p")
        
        return date + time, str(text)

def setup(bot):
    bot.add_cog(TibiaNews(bot))
