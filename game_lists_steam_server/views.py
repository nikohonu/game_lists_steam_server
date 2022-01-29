from datetime import date, datetime
from os import abort, getenv

from flask import jsonify, abort
import flask

from game_lists_steam_server.__main__ import app
from game_lists_steam_server.steam_api import SteamAPI
from game_lists_steam_server.models import Player

steam_api_key = getenv('STEAM_API_KEY', None)
steam_api = SteamAPI(steam_api_key)


def check_date(dt: datetime, max_delta=28):
    if dt:
        now = datetime.now()
        return (now-dt).days <= max_delta
    else:
        return False


@app.route('/get-steam-id/<profile_url_id>', methods=['GET'])
def get_steam_id(profile_url_id: str):
    profile_url = f'https://steamcommunity.com/id/{profile_url_id}/'
    result = steam_api.get_steam_id_from_url(profile_url)
    if result:
        id = int(result)
        player, _ = Player.get_or_create(
            id=id,
        )
        player.profile_url = profile_url
        player.save()
        return jsonify(id)
    else:
        flask.abort(404)

    # if player and check_date(player.update_time):
    #    return jsonify(player.id)
    # else:
    #    player, created = Player.get_or_create(id=int(result), )


@app.route('/get-player/<id>')
def get_player(id: int):
    player = Player.get_or_none(Player.id == id)
    if not player or not check_date(player.update_time):
        players = steam_api.get_player_summaries(id)['response']['players']
        if players:
            player, _ = Player.get_or_create(id=id)
            player.id = int(players[0]['steamid'])
            player.name = players[0]['personaname']
            player.profile_url = players[0]['profileurl']
            player.is_public = True if players[0]['communityvisibilitystate'] == 3 else False
            player.update_time = datetime.now()
            player.save()
        else:
            flask.abort(404)
    return jsonify(player.__dict__)


@app.route("/get-player-summaries/<steam_id>")
@app.route('/steam-api-key', methods=['GET'])
def get_steam_api_key():
    return steam_api_key
