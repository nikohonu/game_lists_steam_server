# pyright: reportGeneralTypeIssues=false
from steam.steamid import SteamID
from steam.webapi import WebAPI
from requests import get


class SteamAPI:
    def __init__(self, steam_api_key) -> None:
        self.steam_api_key = steam_api_key
        self.web_api = WebAPI(key=self.steam_api_key)

    def get_owned_games(self, steam_id):
        print('call get_owned_games')
        return self.web_api.IPlayerService.GetOwnedGames(steamid=steam_id, appids_filter=[], include_appinfo=True, include_free_sub=True, include_played_free_games=True)

    def get_steam_id_from_url(self, profile_url: str):
        print('call get_steam_id_from_url')
        return SteamID.from_url(profile_url)

    def get_player_summaries(self, steam_id):
        print('call get_player_summaries')
        return self.web_api.ISteamUser.GetPlayerSummaries(steamids=steam_id)

    @staticmethod
    def get_app_details(app_id):
        print('call get_appdetails')
        response = get(
            "https://store.steampowered.com/api/appdetails", params={'appids': app_id})
        print(response.url)
        return response.json()
