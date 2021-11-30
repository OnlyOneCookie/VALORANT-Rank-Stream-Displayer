import requests
import shutil
import os

from src.constants import ICONS

class Data():
    def __init__(self, Requests, directory, log):
        self.Requests = Requests
        self.directory = directory
        self.log = log

    def set_data(self, agent, name, rank, rr, peakRank, leaderboard, level, server, map, mode, currentSeason):
        self.__save("agent", agent)
        self.__save("name", name)
        self.__save("rank", rank)
        self.__save("rr", rr)
        self.__save("peakRank", peakRank)
        self.__save("leaderboard", leaderboard)
        self.__save("level", level)
        self.__save("server", server)
        self.__save("map", map)
        self.__save("mode", mode)
        self.__save("season", currentSeason)

    def __save(self, type, value):
        if not self.directory.endswith('/'):
            self.directory += '/'
        if not os.path.exists(self.directory):
                os.makedirs(self.directory)

        if type == "rank" or type == "peakRank" or type == "agent":
            url = ""
            if type == "rank" or type == "peakRank":
                url = ICONS.get("Ranks").get(value, ICONS.get("Ranks").get("None"))
            if type == "agent":
                url = ICONS.get("Agents").get(value, ICONS.get("Agents").get("None"))
            r = requests.get(url, stream=True)

            if r.status_code == 200:
                r.raw.decode_content = True

                with open(f"{self.directory}{type}.png", 'wb+') as f:
                    shutil.copyfileobj(r.raw, f)
                    f.close()
            else:
                self.log("[Data] Image couldn\'t be retrieved")
        
        file = f"{self.directory}{type}.txt"

        with open(file, 'w+', encoding='utf-8') as f:
            f.write(f"{value}")
            f.close()