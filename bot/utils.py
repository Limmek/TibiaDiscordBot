from datetime import datetime, timezone
from constants import *

import ssl

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    # Legacy Python that doesn't verify HTTPS certificates by default
    pass
else:
    # Handle target environment that doesn't support HTTPS verification
    ssl._create_default_https_context = _create_unverified_https_context


class Utils:
    colors = {
        'DEFAULT': 0x000000,
        'WHITE': 0xFFFFFF,
        'AQUA': 0x1ABC9C,
        'GREEN': 0x2ECC71,
        'GREEN_OLD': 0x00c95d,
        'BLUE': 0x3498DB,
        'PURPLE': 0x9B59B6,
        'LUMINOUS_VIVID_PINK': 0xE91E63,
        'GOLD': 0xF1C40F,
        'ORANGE': 0xE67E22,
        'RED': 0xE74C3C,
        'GREY': 0x95A5A6,
        'NAVY': 0x34495E,
        'DARK_AQUA': 0x11806A,
        'DARK_GREEN': 0x1F8B4C,
        'DARK_BLUE': 0x206694,
        'DARK_PURPLE': 0x71368A,
        'DARK_VIVID_PINK': 0xAD1457,
        'DARK_GOLD': 0xC27C0E,
        'DARK_ORANGE': 0xA84300,
        'DARK_RED': 0x992D22,
        'DARK_GREY': 0x979C9F,
        'DARKER_GREY': 0x7F8C8D,
        'LIGHT_GREY': 0xBCC0C0,
        'DARK_NAVY': 0x2C3E50,
        'BLURPLE': 0x7289DA,
        'GREYPLE': 0x99AAB5,
        'DARK_BUT_NOT_BLACK': 0x2C2F33,
        'NOT_QUITE_BLACK': 0x23272A
    }

    def utc_to_local(utc_dt):
        return utc_dt.replace(tzinfo=timezone.utc).astimezone(tz=None).strftime("%Y-%m-%d %H:%M:%S")

    def add_thumbnail(embed, player_name, default_whitelist):
        if player_name in default_whitelist:
            embed.set_thumbnail(url=default_whitelist[player_name])
        return embed

    def lastlogin(lastlogin):
        if lastlogin == None:
            return str(LASTLOGIN_NONE)
        return Utils.utc_to_local(lastlogin)
    
import os
import json
class Config:
    def create_config(file):
        config = {
            'TOKEN': '',
            'CHANNEL_ID': '',
            'PREFIX': "! -",
            'GUILD_NAME': "",
            'TIBIA_ROLE': "",
            'DEFAULT_WHITELIST': {}
        }
        with open(file, 'w') as json_file:
            json.dump(config, json_file, indent=4)

    def load_config(file='config.json'):
        data = None
        if not os.path.isfile(file):
            Config.create_config(file)
        with open(file) as json_data_file:
            data = json.load(json_data_file)
        return data
