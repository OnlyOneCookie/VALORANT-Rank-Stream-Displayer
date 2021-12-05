import json
from io import TextIOWrapper
from json import JSONDecodeError

from src.logs import Logging

class Config:
    def __init__(self, log):
        self.log = log
        try:
            with open("config.json", "r") as file:
                self.log("[Config] Opened")
                config = json.load(file)
                if config.get("cooldown") is None or config.get("dir") is None:
                    self.log("[Config] Some config values are None, getting new config")
                    config = self.config_dialog(file)
        except (FileNotFoundError, JSONDecodeError):
            self.log("[Config] File not found or invalid")
            with open("config.json", "w") as file:
                config = self.config_dialog(file)
        finally:
            self.cooldown = config["cooldown"]
            self.dir = config["dir"]
            self.log(f"[Config] Cooldown with value '{self.cooldown}'")
            self.log(f"[Config] Directory with value '{self.dir}'")

    def config_dialog(self, fileToWrite: TextIOWrapper):
        self.log("[Config] Prompt called")
        jsonToWrite = {"cooldown": 1, "dir": "C:/VRSD/"}
        json.dump(jsonToWrite, fileToWrite)
        return jsonToWrite