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
    async def get_highscores(world, category):
        highscores = None
        url = tibiapy.Highscores.get_url_tibiadata(world, category)
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
    async def check_player_highscore(name, world, category):
        highscores = await TibiaData.get_highscores(world, category)
        for entrie in highscores.entries:
            if (entrie.name == name):
                return entrie
        return None

    # Character info
    async def get_guild(name):
        guild = None
        url = tibiapy.Guild.get_url_tibiadata(name)
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    content = await resp.text()
            guild = tibiapy.Guild.from_tibiadata(content)
        except Exception as e:
            print(str(e))
            pass
        return guild

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
        test = await Tibia.get_highscores(world)
        if test is not None:
            for page in range(test.page, test.total_pages):
                test = await Tibia.get_highscores(world, page=page)
                for entrie in test.entries:
                    if (entrie.name == name):
                        return entrie
        return None

    # Get news from tibia.com
    async def get_news(news_id=1):
        url = tibiapy.News.get_url(news_id)
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    content = await resp.text()
            news = tibiapy.News.from_content(content, news_id)
        
        except Exception as e:
            print(str(e))
            pass
        return news

from constants import *
async def highscore_check(character, embed, msg):
    # Highscores
    # Check Experience
    experience = await TibiaData.check_player_highscore(character.name, character.world, tibiapy.Category.EXPERIENCE)
    if experience is not None:
        embed.add_field(name=HIGHSCORE_EXP_MESSAGE.format(experience.value), value=HIGHSCORE_RANK.format(experience.rank), inline=True)
        await msg.edit(content=LOADING_MESSAGE, embed=embed)

    # Check magic level if druid or sorcerer
    if (character.vocation in [tibiapy.Vocation.DRUID, tibiapy.Vocation.ELDER_DRUID, tibiapy.Vocation.SORCERER, tibiapy.Vocation.MASTER_SORCERER]):
        magic = await TibiaData.check_player_highscore(character.name, character.world, tibiapy.Category.MAGIC_LEVEL)
        if magic is not None:
            
            embed.add_field(name=HIGHSCORE_MAGIC_MESSAGE.format(magic.value), value=HIGHSCORE_RANK.format(magic.rank), inline=True)
            await msg.edit(content=LOADING_MESSAGE, embed=embed)

    # Check distance skill if paladin
    if (character.vocation in [tibiapy.Vocation.PALADIN, tibiapy.Vocation.ROYAL_PALADIN]):
        distance = await TibiaData.check_player_highscore(character.name, character.world, tibiapy.Category.DISTANCE_FIGHTING)
        if distance is not None:
            
            embed.add_field(name=HIGHSCORE_DISTANCE_MESSAGE.format(distance.value), value=HIGHSCORE_RANK.format(distance.rank), inline=True)
            await msg.edit(content=LOADING_MESSAGE, embed=embed)

    # Check mele skills if knight
    if (character.vocation in [tibiapy.Vocation.KNIGHT, tibiapy.Vocation.ELITE_KNIGHT]):
        # Sword skill
        sword = await TibiaData.check_player_highscore(character.name, character.world, tibiapy.Category.SWORD_FIGHTING)
        if sword is not None:
            
            embed.add_field(name=HIGHSCORE_SWORD_MESSAGE.format(sword.value), value=HIGHSCORE_RANK.format(sword.rank), inline=True)
            await msg.edit(content=LOADING_MESSAGE, embed=embed)

        # Axe skill
        axe = await TibiaData.check_player_highscore(character.name, character.world, tibiapy.Category.AXE_FIGHTING)
        if axe is not None:
            
            embed.add_field(name=HIGHSCORE_AXE_MESSAGE.format(axe.value), value=HIGHSCORE_RANK.format(axe.rank), inline=True)
            await msg.edit(content=LOADING_MESSAGE, embed=embed)

        # Club skill
        club = await TibiaData.check_player_highscore(character.name, character.world, tibiapy.Category.CLUB_FIGHTING)
        if club is not None:
            
            embed.add_field(name=HIGHSCORE_CLUB_MESSAGE.format(club.value), value=HIGHSCORE_RANK.format(club.rank), inline=True)
            await msg.edit(content=LOADING_MESSAGE, embed=embed)

    # Check Shielding all vocations
    shielding = await TibiaData.check_player_highscore(character.name, character.world, tibiapy.Category.SHIELDING)
    if shielding is not None:
        
        embed.add_field(name=HIGHSCORE_SHIELDING_MESSAGE.format(shielding.value), value=HIGHSCORE_RANK.format(shielding.rank), inline=True)
        await msg.edit(content=LOADING_MESSAGE, embed=embed)

    # Check Fist all vocations
    fist = await TibiaData.check_player_highscore(character.name, character.world, tibiapy.Category.FIST_FIGHTING)
    if fist is not None:
        
        embed.add_field(name=HIGHSCORE_FIST_MESSAGE.format(fist.value), value=HIGHSCORE_RANK.format(fist.rank), inline=True)
        await msg.edit(content=LOADING_MESSAGE, embed=embed)

    # Check Fishing all vocations
    fishing = await TibiaData.check_player_highscore(character.name, character.world, tibiapy.Category.FISHING)
    if fishing is not None:
        
        embed.add_field(name=HIGHSCORE_FISHING_MESSAGE.format(fishing.value), value=HIGHSCORE_RANK.format(fishing.rank), inline=True)
        await msg.edit(content=LOADING_MESSAGE, embed=embed)

    # Check Fishing all vocations
    achievements = await TibiaData.check_player_highscore(character.name, character.world, tibiapy.Category.ACHIEVEMENTS)
    if achievements is not None:
        
        embed.add_field(name=HIGHSCORE_ACHIEVEMENTS_MESSAGE.format(achievements.value), value=HIGHSCORE_RANK.format(achievements.rank), inline=True)
        await msg.edit(content=LOADING_MESSAGE, embed=embed)

    # Check Fishing all vocations
    loyalty = await TibiaData.check_player_highscore(character.name, character.world, tibiapy.Category.LOYALTY_POINTS)
    if loyalty is not None:
        embed.add_field(name=HIGHSCORE_LOYALTY_POINTS_MESSAGE.format(loyalty.value), value=HIGHSCORE_RANK.format(loyalty.rank), inline=True)
        await msg.edit(content=LOADING_MESSAGE, embed=embed)
    
    await msg.edit(content="")
