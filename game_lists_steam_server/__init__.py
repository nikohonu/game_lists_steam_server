from flask import Flask

from game_lists_steam_server import views
from game_lists_steam_server.models import Player


def create_table_if_not_exist(model):
    if not model.table_exists():
        model.create_table()


create_table_if_not_exist(Player)
app = Flask(__name__)
