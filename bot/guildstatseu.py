import asyncio
import re
import time
import datetime
import aiohttp

from bs4 import BeautifulSoup

class GuildStats:

    URL_CHARACTER_ONLINE_TIME = "https://guildstats.eu/character?nick={0}#tab2"
    URL_CHARACTER_EXPERIENCE_CHANGE = "https://guildstats.eu/character?nick={0}#tab7"

    async def getTimeOnline(name):
        onlineTable = None
        if name is not None:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(GuildStats.URL_CHARACTER_ONLINE_TIME.format(name)) as resp:
                        content = await resp.text()
            except Exception as e:
                print(e)
                pass
            finally: 
                soup = BeautifulSoup(content, 'html.parser')
                table_div = soup.find('div' , {'id': 'tab2'})
                if table_div:
                    table = table_div.find("table", { "id" : "myTable", "class" : "tablesorter" })
                    if table:
                        onlineTable = {}
                        for row in table.findAll("tr"):
                            cells = row.findAll("td")
                            onlineTable['Last month'] = cells[0].find(text=True)
                            onlineTable['Current month'] = cells[1].find(text=True)
                            onlineTable['Current week'] = cells[2].find(text=True)
                            onlineTable['Mon'] = cells[3].find(text=True)
                            onlineTable['Tue'] = cells[4].find(text=True)
                            onlineTable['Wed'] = cells[5].find(text=True)
                            onlineTable['Thu'] = cells[6].find(text=True)
                            onlineTable['Fri'] = cells[7].find(text=True)
                            onlineTable['Sat'] = cells[8].find(text=True)
                            onlineTable['Sun'] = cells[9].find(text=True)
        return onlineTable

    async def getExperienceChange(name):
        expTable = None
        if name is not None:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(GuildStats.URL_CHARACTER_EXPERIENCE_CHANGE.format(name)) as resp:
                        content = await resp.text()
            except:
                pass
            finally: 
                soup = BeautifulSoup(content, 'lxml')
                table_div = soup.find('div' , {'id': 'tab7'})
                if table_div:
                    table = table_div.find("table", {"class" : "shadow" })
                    if table:
                        expTable = []
                        for row in table.findAll("tr"):
                            expRow = {}
                            cells = row.findAll("td")
                            expRow['Date'] = cells[0].find(text=True)
                            expRow['Exp change'] = cells[1].find(text=True)
                            expRow['Rank'] = cells[2].find(text=True)
                            expRow['Lvl'] = cells[3].find(text=True)
                            expRow['Experience'] = cells[4].find(text=True)
                            expTable.append(expRow) 
                        expTable.reverse()
        return expTable
