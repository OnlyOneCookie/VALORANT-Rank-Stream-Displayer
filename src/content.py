import requests

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
                self.log(f"[Content] Retrieved season id: {season['ID']}")
                return season["ID"]

    def get_current_season(self, content): 
        return self.get_current_act(content) + " - " + self.get_current_episode(content)

    def get_current_act(self, content):
        for season in content["Seasons"]:
            if season["IsActive"] and season["Type"] == "act":
                return season["Name"].capitalize()

    def get_current_episode(self, content):
        for season in content["Seasons"]:
            if season["IsActive"] and season["Type"] == "episode":
                return season["Name"].capitalize()

    def get_all_maps(self):
        rMaps = requests.get("https://valorant-api.com/v1/maps").json()
        map_dict = {}
        for map in rMaps["data"]:
            map_dict.update({map["mapUrl"]: map["displayName"]})
        self.log(f"[Content] Retrieved maps: {map_dict}")
        return map_dict

    def get_all_modes(self):
        rModes = requests.get("https://valorant-api.com/v1/gamemodes").json()

    def get_all_agents(self):
        rAgents = requests.get("https://valorant-api.com/v1/agents?isPlayableCharacter=true").json()
        agent_dict = {}
        for agent in rAgents["data"]:
            agent_dict.update({agent['uuid'].lower(): agent['displayName']})
        self.log(f"[Content] Retrieved agents: {agent_dict}")
        return agent_dict

    def get_all_ranks_icon(self, episode):
        rRanks = requests.get("https://valorant-api.com/v1/competitivetiers").json()
        rank_dict = {}
        for data in rRanks["data"]:
            obj = episode.replace(" ", "") + "_CompetitiveTierDataTable"
            if obj == data["assetObjectName"]:
                for tier in data["tiers"]:
                    rank_dict.update({tier["tierName"].capitalize(): tier["largeIcon"]})
        self.log(f"[Content] Retrieved ranks (icons): {rank_dict}")
        return rank_dict

    def get_all_agents_icon(self):
        rAgents = requests.get("https://valorant-api.com/v1/agents?isPlayableCharacter=true").json()
        agent_dict = {}
        for agent in rAgents["data"]:
            agent_dict.update({agent["displayName"]: agent["displayIcon"]})
        self.log(f"[Content] Retrieved agents (icons): {agent_dict}")
        return agent_dict