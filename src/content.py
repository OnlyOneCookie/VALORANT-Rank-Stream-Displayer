import requests
import shutil
import os

from src.constants import ICONS

class Content():
    def __init__(self, Requests, log):
        self.Requests = Requests
        self.log = log

    def get_content(self):
        content = self.Requests.fetch("custom", f"https://shared.{self.Requests.region}.a.pvp.net/content-service/v3/content", "get")
        return content

    def get_latest_season_id(self, content):
        for season in content["Seasons"]:
            if season["IsActive"]:
                self.log(f"retrieved season id: {season['ID']}")
                return season["ID"]

    def get_all_agents(self):
        rAgents = requests.get("https://valorant-api.com/v1/agents?isPlayableCharacter=true").json()
        agent_dict = {}
        agent_dict.update({None: None})
        for agent in rAgents["data"]:
            agent_dict.update({agent['uuid'].lower(): agent['displayName']})
        self.log(f"retrieved agent dict: {agent_dict}")
        return agent_dict

    def set_values_in_file(self, directory, type, value):
        if type == "rank" or type == "peakRank" or type == "agent":
            url = ""
            if type == "rank" or type == "peakRank":
                url = ICONS.get("Ranks").get(value, ICONS.get("Ranks").get("None"))
            if type == "agent":
                url = ICONS.get("Agents").get(value, ICONS.get("Agents").get("None"))
            r = requests.get(url, stream=True)

            if r.status_code == 200:
                r.raw.decode_content = True

                with open(f"{directory}{type}.png", 'wb+') as f:
                    shutil.copyfileobj(r.raw, f)
                    f.close()
            else:
                self.log("Image couldn\'t be retrieved")
        else:
            file = f"{directory}{type}.txt"

            if not os.path.exists(directory):
                os.makedirs(directory)
            with open(file, 'w+', encoding='utf-8') as f:
                f.write(f"{value}")
                f.close()