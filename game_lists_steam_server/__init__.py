from os import getenv

from flask import Flask

from game_lists_steam_server import views
from game_lists_steam_server.models import Player, Game, Playtime
from game_lists_steam_server.steam_api import SteamAPI


steam_api_key = getenv('STEAM_API_KEY', None)
steam_api = SteamAPI(steam_api_key)


def create_table_if_not_exist(model):
    if not model.table_exists():
        model.create_table()


create_table_if_not_exist(Player)
create_table_if_not_exist(Game)
create_table_if_not_exist(Playtime)
app = Flask(__name__)
