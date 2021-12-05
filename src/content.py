import requests
import re

class Content():
    def __init__(self, Requests, log):
        self.Requests = Requests
        self.log = log
        self.gameContent = {}

    def get_content(self):
        content = self.Requests.fetch("custom", f"https://shared.{self.Requests.region}.a.pvp.net/content-service/v3/content", "get")
        self.gameContent = content
        self.log(f"content: {self.gameContent}")
        return content

    def get_latest_season_id(self):
        for season in self.gameContent["Seasons"]:
            if season["IsActive"]:
                self.log(f"[Content] Retrieved season id: {season['ID']}")
                return season["ID"]

    def get_current_season(self): 
        return self.get_current_act() + " - " + self.get_current_episode()

    def get_current_act(self):
        act = ""
        for season in self.gameContent["Seasons"]:
            if season["IsActive"] and season["Type"] == "act":
                act = season["Name"].capitalize()
                break
        return act

    def get_current_episode(self):
        episode = ""
        for season in self.gameContent["Seasons"]:
            if season["IsActive"] and season["Type"] == "episode":
                episode = season["Name"].capitalize()
                break
        return episode

    def get_all_maps(self):
        rMaps = requests.get("https://valorant-api.com/v1/maps").json()
        map_dict = {}
        for map in rMaps["data"]:
            url = map["mapUrl"]
            name = map["displayName"]
            map_dict.update({url: name})
        self.log(f"[Content] Retrieved maps: {map_dict}")
        return map_dict

    def get_all_modes(self):
        rModes = requests.get("https://valorant-api.com/v1/gamemodes").json()
        mode_dict = {}
        for mode in rModes["data"]:
            path = mode["assetPath"].replace("ShooterGame/Content/", "/Game/").split("_", 1)[0]
            name = mode["displayName"].capitalize()
            mode_dict.update({path: name})
        self.log(f"[Content] Retrieved modes: {mode_dict}")
        return mode_dict

    def get_all_ranks(self, episode):
        rRanks = requests.get("https://valorant-api.com/v1/competitivetiers").json()
        rank_arr = []
        for data in rRanks["data"]:
            episode_value = re.sub(r"\s+", "", episode)
            obj = episode_value + "_CompetitiveTierDataTable"
            if obj == data["assetObjectName"]:
                for tier in data["tiers"]:
                    rank_arr.append(tier["tierName"].capitalize())
        self.log(f"[Content] Retrieved ranks: {rank_arr}")
        return rank_arr

    def get_all_agents(self):
        rAgents = requests.get("https://valorant-api.com/v1/agents?isPlayableCharacter=true").json()
        agent_dict = {}
        for agent in rAgents["data"]:
            agent_dict.update({agent['uuid'].lower(): agent['displayName']})
        self.log(f"[Content] Retrieved agents: {agent_dict}")
        return agent_dict

    def get_all_icons(self, episode):
        rRanks = requests.get("https://valorant-api.com/v1/competitivetiers").json()
        rank_dict = {}
        for data in rRanks["data"]:
            episode_value = re.sub(r"\s+", "", episode)
            obj = episode_value + "_CompetitiveTierDataTable"
            if obj == data["assetObjectName"]:
                for tier in data["tiers"]:
                    rank_dict.update({tier["tierName"].capitalize(): tier["largeIcon"]})
        self.log(f"[Content] Retrieved ranks (icons): {rank_dict}")

        rAgents = requests.get("https://valorant-api.com/v1/agents?isPlayableCharacter=true").json()
        agent_dict = {}
        for agent in rAgents["data"]:
            agent_dict.update({agent["displayName"]: agent["displayIcon"]})
        self.log(f"[Content] Retrieved agents (icons): {agent_dict}")

        icons_dict = {}
        icons_dict.update({"Ranks": rank_dict, "Agents": agent_dict})
        self.log(f"[Content] Retrieved all icons: {icons_dict}")
        return icons_dict
