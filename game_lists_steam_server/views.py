from datetime import datetime

from flask import abort, jsonify
from requests.exceptions import HTTPError

from game_lists_steam_server.__init__ import steam_api
from game_lists_steam_server.__main__ import app
from game_lists_steam_server.models import (Game, GameGenre, GameTag, Genre,
                                            Player, Playtime, Tag)


def check_date(dt: datetime, max_delta=1):
    dt = None if dt == '0000-00-00 00:00:00' else dt
    if dt:
        now = datetime.now()
        return (now-dt).days < max_delta
    else:
        return False


@app.route('/get-steam-id/<profile_url_id>', methods=['GET'])
def get_steam_id(profile_url_id: str):
    profile_url = f'https://steamcommunity.com/id/{profile_url_id}/'
    player = Player.get_or_none(Player.profile_url == profile_url)
    if player:
        return jsonify(player.id)
    else:
        data = steam_api.get_steam_id_from_url(profile_url)
        if data:
            player, _ = Player.get_or_create(id=int(data))
            player.profile_url = profile_url
            player.save()
            return jsonify(player.id)
        else:
            abort(404)


@app.route('/get-player/<id>')
def get_player(id: int):
    player = Player.get_or_none(Player.id == id)
    if player and check_date(player.update_time):
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


def generate_game_json(game: Game):

    genres = [game_genre.genre.__dict__ for game_genre in GameGenre.select().where(
        GameGenre.game == game)]  # type: ignore
    tags = [game_tag.__dict__ for game_tag in GameTag.select().where(
        GameTag.game == game)]  # type: ignore
    return jsonify({
        'id': game.id,
        'name': game.name,
        'genres': genres,
        'tags': tags,
    })


@app.route('/get-game/<id>')
def get_game(id: int):
    game = Game.get_or_none(Game.id == id)
    if game and check_date(game.update_time):
        return generate_game_json(game)
    else:
        data = steam_api.get_app_details(id)
        if data and data[id]['success']:
            data = data[id]['data']
            game, _ = Game.get_or_create(id=id)
            tags = steam_api.get_app_tags(id)
            genres = data['genres']
            GameTag.delete().where(GameTag.game == game).execute()  # type: ignore
            for i in range(len(tags)):
                tag, _ = Tag.get_or_create(name=tags[i])
                tag.save()
                coefficient = 2.1111  # tag value from 0.955 to 0.10 for 20 tags
                value = round((1-(i/coefficient*0.1))*100)/100
                GameTag.get_or_create(game=game, tag=tag, value=value)
            GameGenre.delete().where(GameGenre.game == game).execute()  # type: ignore
            for g in genres:
                genre, _ = Genre.get_or_create(id=g['id'])
                genre.name = g['description']
                genre.save()
                GameGenre().get_or_create(game=game, genre=genre)
            game.name = data['name']
            game.update_time = datetime.now()
            game.save()
            return generate_game_json(game)
        else:
            abort(404)


def genetate_playtime_json(player: Player):
    result = []
    for playtime in Playtime.select().where(Playtime.player == player):  # type: ignore
        result.append({
            'game_id': playtime.game.id,
            'game_name': playtime.game.name,
            'minutes': playtime.minutes,
        })
    return jsonify(result)


@app.route("/get-playtime/<id>")
def get_playtime(id: int):
    player, _ = Player.get_or_create(id=id)
    if check_date(player.playtime_update_time):
        return genetate_playtime_json(player)
    try:
        data = steam_api.get_owned_games(id)
        if 'response' in data and 'games' in data['response']:
            for g in [g for g in data['response']['games'] if g['playtime_forever'] > 0]:
                game, _ = Game.get_or_create(id=g['appid'], name=g['name'])
                game.name = g['name']
                game.save()
                playtime, _ = Playtime.get_or_create(player=player, game=game)
                playtime.minutes = g['playtime_forever']
                playtime.save()
            player.playtime_update_time = datetime.now()
            player.is_game_details_public = True
            player.save()
            return genetate_playtime_json(player)
        else:
            player.is_game_details_public = False
            player.save()
    except HTTPError:
        pass
    abort(404)
