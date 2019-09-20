import asyncio
import aiohttp
import tibiapy

# tibiadata.com
class TibiaData:
    # Character info
    async def get_character(name):
        character = None
        url = tibiapy.Character.get_url_tibiadata(name)
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    content = await resp.text()
            character = tibiapy.Character.from_tibiadata(content)
        except Exception as e:
            print(str(e))
            pass
        return character

    # World info
    async def get_world(name):
        world = None
        world_url = tibiapy.World.get_url_tibiadata(name)
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(world_url) as resp:
                    world_content = await resp.text()     
            world = tibiapy.World.from_tibiadata(world_content)
        except Exception as e:
            print(str(e))
            pass
        return world

    # Highscores
    async def get_highscores(world):
        highscores = None
        url = tibiapy.Highscores.get_url_tibiadata(world)
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    content = await resp.text()
            highscores = tibiapy.Highscores.from_tibiadata(content)
        except Exception as e:
            print(str(e))
            pass
        return highscores

    # Check player name against tibiadata Highscores
    async def check_player_highscore(name, world):
        entrie = None
        highscores = await TibiaData.get_highscores(world = world)
        for entrie in highscores.entries:
            if (entrie.name == name):
                return entrie
        return entrie

# tibia.com
class Tibia:
    # Character info
    async def get_character(name):
        character = None
        url = tibiapy.Character.get_url(name)
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    content = await resp.text()
            character = tibiapy.Character.from_content(content)
        except Exception as e:
            print(str(e))
            pass
        return character

    # World info
    async def get_world(name):
        world = None
        world_url = tibiapy.World.get_url(name)
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(world_url) as resp:
                    world_content = await resp.text()     
            world = tibiapy.World.from_content(world_content)
        except Exception as e:
            print(str(e))
            pass
        return world

    # Highscores
    async def get_highscores(world, page=1):
        highscores = None
        url = tibiapy.Highscores.get_url(world, page=page)
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    content = await resp.text()
            highscores = tibiapy.Highscores.from_content(content)
        except Exception as e:
            print(str(e))
            pass
        return highscores

    # Check player against tibia.com Highscores
    async def check_player_highscore(name, world):
        entrie = None
        test = await Tibia.get_highscores(world)
        if test is not None:
            for page in range(test.page, test.total_pages):
                test = await Tibia.get_highscores(world, page=page)
                for entrie in test.entries:
                    if (entrie.name == name):
                        return entrie
        return entrie

async def CheckHighscore(name, world):
    msg = ""
    highscore = await TibiaData.check_player_highscore(name, world)
    if highscore is not None:
        msg="\nRanked {} on the Experience list".format(highscore.rank)
    return msg