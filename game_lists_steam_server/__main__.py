from flask import Flask, jsonify
import os
from steam.steamid import SteamID
from steam.webapi import WebAPI

steam_api_key = os.getenv('STEAM_API_KEY', None)

companies = [{"id": 1, "name": "Company One"}, {"id": 2, "name": "Company Two"}]

app = Flask(__name__)

@app.route('/get-owned-games/<steam_id>', methods=['GET'])
def get_owned_games(steam_id: str):
    steam_id= SteamID.from_url(f'https://steamcommunity.com/id/{steam_id}')
    api = WebAPI(key=steam_api_key)
    data = api.IPlayerService.GetOwnedGames(steamid=steam_id, appids_filter=[], include_appinfo=True, include_free_sub=True, include_played_free_games=True)
    return jsonify(data)

@app.route("/get-player-summaries/<steam_id>")

@app.route('/steam-api-key', methods=['GET'])
def get_steam_api_key():
    return steam_api_key

def main():
    app.run()

if __name__ == '__main__':
    main()
