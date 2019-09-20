from datetime import datetime, timezone
from constants import *
class Utils:
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
