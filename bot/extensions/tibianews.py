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
        self._table = self.sql.createTable('''CREATE TABLE IF NOT EXISTS tibia_news
                        (title text UNIQUE, content text UNIQUE, datetime text, status int)''')
        self._news_ticker = bot.loop.create_task(self.update_news_ticker())
        self._news_ticker = bot.loop.create_task(self.update_news())

    async def get_latest_news(self):
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
    
    async def update_news_ticker(self):
        async def start_news_ticker(self):
            # News
            #data = await Tibia.get_news()
            #print(data.title) print(data.date) print(data.content)
            
            content = await self.get_latest_news()
            datetime, content = self.tibia_news_ticker(content)

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
                        colour=Utils.colors['RED'],
                        url="https://www.tibia.com/news/?subtopic=latestnews"
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
                    
                    await msg.pin()

                    tibia_role = discord.utils.get(msg.guild.roles, name=self.config["TIBIA_ROLE"])
                    if tibia_role is not None:
                        await msg.edit(content=f'{tibia_role.mention}')
        while True:
            await self.bot.wait_until_ready()
            asyncio.create_task(start_news_ticker(self))
            await asyncio.sleep(600)

    def tibia_news_ticker(self, content):
        if content is None:
            return
 
        soup = BeautifulSoup(content, 'lxml')
        
        news_ticker = soup.find("div", id="NewsTicker")
        
        text = news_ticker.find("div", class_="NewsTickerFullText").find("p").text
        date = news_ticker.find("span", class_="NewsTickerDate").getText("p")
        time = news_ticker.find("span", class_="NewsTickerTime").getText("p")
        
        return date + time, str(text)

    # Latest news
    async def update_news(self):
        async def start_news(self):
            # News
            #data = await Tibia.get_news()
            #print(data.title) print(data.date) print(data.content)
            
            content = await self.get_latest_news()
            datetime, title, content = self.tibia_news(content)

            query = 'INSERT OR IGNORE INTO tibia_news values (?,?,?,?)'
            sql = self.sql.executeQuery(query, [title, content, datetime, 0])
            
            data = self.sql.executeQuery('SELECT * FROM tibia_news WHERE status=0', []).fetchone()
            if data is None:
                return True
            
            old_title, old_content, old_datetime, status = data
            if status == 0 and datetime == old_datetime:
                print("DISCORD NEWS: " + content)
                try:
                    embed = discord.Embed(
                        title=title,
                        colour=Utils.colors['RED'],
                        url="https://www.tibia.com/news/?subtopic=latestnews"
                    )
                    x=2000
                    res=[content[y-x:y] for y in range(x, len(content)+x,x)]
                    embed.description = res[0] + "..."
                    msg = await self.bot.get_channel(int(self.config["CHANNEL_ID"])).send(embed=embed)
                except:
                    pass
                finally:
                    embed.set_footer(
                        text=f'Posted: {datetime}',
                    )
                    await msg.edit(embed=embed)

                    self.sql.executeQuery("UPDATE tibia_news SET status=? WHERE datetime=?", [1, old_datetime])
                    
                    await msg.pin()
                    
                    tibia_role = discord.utils.get(msg.guild.roles, name=self.config["TIBIA_ROLE"])
                    if tibia_role is not None:
                        await msg.edit(content=f'{tibia_role.mention}')
        while True:
            await self.bot.wait_until_ready()
            asyncio.create_task(start_news(self))
            await asyncio.sleep(600)
    
    def tibia_news(self, content):
        if content is None:
            return
 
        soup = BeautifulSoup(content, 'lxml')
        
        news_ticker = soup.find("div", id="News")
    
        date = news_ticker.find("div", class_="NewsHeadlineDate").getText("p")
        title = news_ticker.find("div", class_="NewsHeadlineText").find("p").text
        content = news_ticker.find("table", class_="").find("tr").text
        return date, str(title), content

def setup(bot):
    bot.add_cog(TibiaNews(bot))
