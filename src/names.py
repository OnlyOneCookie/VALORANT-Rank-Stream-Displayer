import requests

class Names:
    def __init__(self, Requests, log):
        self.Requests = Requests
        self.log = log

    def get_multiple_names_from_puuid(self, puuids):
        response = requests.put(self.Requests.pd_url + "/name-service/v2/players", headers=self.Requests.get_headers(), json=puuids, verify=False)
        name_dict = {player["Subject"]: f"{player['GameName']}#{player['TagLine']}"
                     for player in response.json()}
        return name_dict

    def get_names_from_puuids(self, players):
        players_puuid = []
        for player in players:
            players_puuid.append(player["Subject"])
        return self.get_multiple_names_from_puuid(players_puuid)

    def get_players_puuid(self, Players):
        return [player["Subject"] for player in Players]