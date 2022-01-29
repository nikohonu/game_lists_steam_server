from os import getenv

from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler

from game_lists_steam_server import views
from game_lists_steam_server.models import Player, Game
from game_lists_steam_server.steam_api import SteamAPI


steam_api_key = getenv('STEAM_API_KEY', None)
steam_api = SteamAPI(steam_api_key)


def get_game_list():
    i = 0
    apps = steam_api.get_app_list()['applist']['apps']
    for app in apps:
        game, _ = Game.get_or_create(id=app['appid'])
        game.name = app['name']
        game.save()
        i += 1
        if i % 1000 == 0:
            print(f'updated {i} games')


def create_table_if_not_exist(model, callback=lambda _: _):
    if not model.table_exists():
        model.create_table()
        callback()


create_table_if_not_exist(Player)
create_table_if_not_exist(Game, get_game_list)
sched = BackgroundScheduler(daemon=True)
sched.add_job(get_game_list, 'interval', hours=24)
sched.start()
app = Flask(__name__)
