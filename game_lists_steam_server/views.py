from datetime import datetime

from flask import jsonify, abort

from game_lists_steam_server.__main__ import app
from game_lists_steam_server.__init__ import steam_api
from game_lists_steam_server.models import Game, Player, Playtime

exclude = [8230, 43110, 836620]


def check_date(dt: datetime, max_delta=1):
    if dt:
        now = datetime.now()
        return (now-dt).days < max_delta
    else:
        return False


@app.route('/get-steam-id/<profile_url_id>', methods=['GET'])
def get_steam_id(profile_url_id: str):
    profile_url = f'https://steamcommunity.com/id/{profile_url_id}/'
    player = Player.get_or_none(Player.profile_url == profile_url)
    if player and check_date(player.update_time):
        return jsonify(player.id)
    else:
        data = steam_api.get_steam_id_from_url(profile_url)
        if data:
            player, _ = Player.get_or_create(id=int(data))
            player.profile_url = profile_url
            player.update_time = datetime.now()
            player.save()
            return jsonify(player.id)
        else:
            abort(404)


@app.route('/get-player/<id>')
def get_player(id: int):
    player = Player.get_or_none(Player.id == id)
    if player and check_date(player.update_time) and player.name:
        return jsonify(player.__dict__)
    else:
        data = steam_api.get_player_summaries(id)['response']['players']
        if data:
            data = data[0]
            player, _ = Player.get_or_create(id=id)
            player.name = data['personaname']
            player.profile_url = data['profileurl']
            player.is_public = True if data['communityvisibilitystate'] == 3 else False
            player.update_time = datetime.now()
            player.save()
            return jsonify(player.__dict__)
        else:
            abort(404)


@app.route('/get-game/<id>')
def get_game(id: int):
    game = Game.get_or_none(Game.id == id)
    if game and check_date(game.update_time):
        return jsonify(game.__dict__)
    else:
        data = steam_api.get_app_details(id)
        if data and data[id]['success']:
            data = data[id]['data']
            game, _ = Game.get_or_create(id=id)
            game.name = data['name']
            game.update_time = datetime.now()
            game.save()
            return jsonify(game.__dict__)
        else:
            abort(404)


@app.route("/get-playtime/<id>")
def get_playtime(id: int):
    player = None
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
