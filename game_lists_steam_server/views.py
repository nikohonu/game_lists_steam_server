from datetime import datetime

from flask import jsonify, abort

from game_lists_steam_server.__main__ import app
from game_lists_steam_server.__init__ import steam_api
from game_lists_steam_server.models import Game, Player, Playtime

exclude = [8230, 43110, 836620]


def check_date(dt: datetime, max_delta=28):
    if dt:
        now = datetime.now()
        return (now-dt).days <= max_delta
    else:
        return False


def get_player_data(id):
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
            return None
    return player


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
        abort(404)


@app.route('/get-player/<id>')
def get_player(id: int):
    player = get_player_data(id)
    if player:
        return jsonify(player.__dict__)
    else:
        abort(404)


@app.route('/get-game/<id>')
def get_game(id: int):
    game = Game.get_or_none(Game.id == id)
    print(game)
    if not game:
        abort(404)
    return jsonify(game.__dict__)


@app.route("/get-playtime/<id>")
def get_playtime(id: int):
    player = get_player_data(id)
    if player and player.is_public:
        if not check_date(player.playtime_update_time):
            response = steam_api.get_owned_games(id)['response']
            if 'games' in response:
                for app in [app for app in response['games'] if app['appid'] not in exclude and app['playtime_forever'] > 0]:
                    game = Game.get(Game.id == app['appid'])
                    playtime, _ = Playtime.get_or_create(
                        player=player, game=game)
                    playtime.minutes = app['playtime_forever']
                    player.playtime_update_time = datetime.now()
                    playtime.save()
                    player.save()
            else:
                player.is_public = False
                player.save()
                abort(404)
        result = []
        for playtime in Playtime.select().where(Playtime.player == player):  # type: ignore
            result.append(playtime.__dict__)
        return jsonify(result)
    else:
        abort(404)
