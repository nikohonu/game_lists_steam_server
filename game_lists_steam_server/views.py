from datetime import datetime
from os import abort, getenv

from flask import jsonify, abort
import flask

from game_lists_steam_server.__main__ import app
from game_lists_steam_server.steam_api import SteamAPI
from game_lists_steam_server.models import Player

steam_api_key = getenv('STEAM_API_KEY', None)
steam_api = SteamAPI(steam_api_key)


def check_date(dt: datetime, max_delta=28):
    now = datetime.now()
    return (now-dt).days <= max_delta


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


@ app.route('/player/<steam_id>')
def get_user(steam_id: int):
    return jsonify(steam_api.get_player_summaries(steam_id))


@ app.route("/get-player-summaries/<steam_id>")
@ app.route('/steam-api-key', methods=['GET'])
def get_steam_api_key():
    return steam_api_key
