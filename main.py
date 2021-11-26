import traceback
import requests
import urllib3
import os
import base64
import json
import time
from prettytable import PrettyTable
from alive_progress import alive_bar

from src.constants import *
from src.requests import Requests
from src.logs import Logging
from src.config import Config
from src.colors import Colors
from src.rank import Rank
from src.content import Content
from src.names import Names
from src.presences import Presences

from src.states.menu import Menu
from src.states.pregame import Pregame
from src.states.coregame import Coregame

from src.table import Table
from src.server import Server


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

os.system('cls')
os.system(f"title VALORANT Rank Stream Displayer v{version}")

server = ""

def program_exit(status: int):  # so we don't need to import the entire sys module
    log(f"exited program with error code {status}")
    raise SystemExit(status)

try:
    Requests = Requests(version)
    Requests.check_version()
    Requests.check_status()

    Logging = Logging()
    log = Logging.log
    cfg = Config(log)

    rank = Rank(Requests, log)
    content = Content(Requests, log)
    namesClass = Names(Requests, log)
    presences = Presences(Requests, log)

    menu = Menu(Requests, log, presences)
    pregame = Pregame(Requests, log)
    coregame = Coregame(Requests, log)

    Server = Server(Requests)
    Server.start_server()


    agent_dict = content.get_all_agents()

    colors = Colors(hide_names, agent_dict, AGENTCOLORLIST)

    tableClass = Table()

    log(f"VALORANT Rank Stream Displayer v{version}")

    gameContent = content.get_content()
    seasonID = content.get_latest_season_id(gameContent)
    lastGameState = ""

    while True:
        table = PrettyTable()
        try:
            presence = presences.get_presence()
            game_state = presences.get_game_state(presence)
        except TypeError:
            raise Exception("Game has not started yet!")
        if cfg.cooldown == 0 or game_state != lastGameState:
            log(f"getting new {game_state} scoreboard")
            lastGameState = game_state
            game_state_dict = {
                "INGAME": color('In-Game', fore=(241, 39, 39)),
                "PREGAME": color('Agent Select', fore=(103, 237, 76)),
                "MENUS": color('In-Menus', fore=(238, 241, 54)),
            }
            if game_state == "INGAME":
                coregame_stats = coregame.get_coregame_stats()
                Players = coregame_stats["Players"]
                Players = list(filter(lambda a: a["Subject"] == Requests.puuid, Players))
                server = GAMEPODS[coregame_stats["GamePodID"]]
                presences.wait_for_presence(namesClass.get_players_puuid(Players))
                names = namesClass.get_names_from_puuids(Players)
                with alive_bar(total=len(Players), title='Fetching player data', bar='classic2') as bar:
                    presence = presences.get_presence()
                    log(f"retrieved names dict: {names}")
                    Players.sort(key=lambda Players: Players["PlayerIdentity"].get("AccountLevel"), reverse=True)
                    Players.sort(key=lambda Players: Players["TeamID"], reverse=True)
                    
                    player = Players.index(0)
                    agent = str(agent_dict.get(player["CharacterID"]))
                    name = names[player["Subject"]]
                    playerRank = rank.get_rank(player["Subject"], seasonID)
                    rankStatus = playerRank[1]

                    while not rankStatus:
                        print("You have been rate limited, 😞 waiting 10 seconds!")
                        time.sleep(10)
                        playerRank = rank.get_rank(player["Subject"], seasonID)
                        rankStatus = playerRank[1]

                    # Rank
                    rankName = NUMBERTORANKS[playerRank[0]]
                    rankDisplayName = RANKS[playerRank[0]]

                    # Rank Rating
                    rr = playerRank[1]

                    # Peak Rank
                    peakRank = NUMBERTORANKS[playerRank[3]]
                    peakRankDisplay = RANKS[playerRank[3]]

                    # Leaderboard
                    leaderboard = playerRank[2]

                    # Level
                    level = player["PlayerIdentity"].get("AccountLevel")

                    tableClass.add_row_table(table, [agent,
                                                name,
                                                rankName,
                                                rr,
                                                peakRank,
                                                leaderboard,
                                                level
                                              ])
                    Content.set_values_in_file(Requests, cfg.dir, "agent", str(agent_dict.get(player["CharacterID"])))
                    Content.set_values_in_file(Requests, cfg.dir, "name", name)
                    Content.set_values_in_file(Requests, cfg.dir, "rank", rankDisplayName)
                    Content.set_values_in_file(Requests, cfg.dir, "rr", rr)
                    Content.set_values_in_file(Requests, cfg.dir, "peakRank", peakRankDisplay)
                    Content.set_values_in_file(Requests, cfg.dir, "leaderboard", leaderboard)
                    Content.set_values_in_file(Requests, cfg.dir, "level", level)
                    Content.set_values_in_file(Requests, cfg.dir, "server", server)
                    bar()   
                        
            elif game_state == "PREGAME":
                pregame_stats = pregame.get_pregame_stats()
                server = GAMEPODS[pregame_stats["GamePodID"]]
                Players = pregame_stats["AllyTeam"]["Players"]
                Players = list(filter(lambda a: a["Subject"] == Requests.puuid, Players))
                presences.wait_for_presence(namesClass.get_players_puuid(Players))
                names = namesClass.get_names_from_puuids(Players)
                with alive_bar(total=len(Players), title='Fetching Players', bar='classic2') as bar:
                    presence = presences.get_presence()
                    log(f"retrieved names dict: {names}")
                    Players.sort(key=lambda Players: Players["PlayerIdentity"].get("AccountLevel"), reverse=True)
                    for player in Players:
                        playerRank = rank.get_rank(player["Subject"], seasonID)
                        rankStatus = playerRank[1]
                        while not rankStatus:
                            print("You have been rate limited, 😞 waiting 10 seconds!")
                            time.sleep(10)
                            playerRank = rank.get_rank(player["Subject"], seasonID)
                            rankStatus = playerRank[1]
                        playerRank = playerRank[0]
                        player_level = player["PlayerIdentity"].get("AccountLevel")
                        if player["PlayerIdentity"]["Incognito"]:
                            NameColor = colors.get_color_from_team(pregame_stats['Teams'][0]['TeamID'],
                                                            names[player["Subject"]],
                                                            player["Subject"], Requests.puuid, agent=player["CharacterID"])
                        else:
                            NameColor = colors.get_color_from_team(pregame_stats['Teams'][0]['TeamID'],
                                                            names[player["Subject"]],
                                                            player["Subject"], Requests.puuid)

                        PLcolor = colors.level_to_color(player_level)
                        if player["CharacterSelectionState"] == "locked":
                            agent_color = color(str(agent_dict.get(player["CharacterID"].lower())),
                                                fore=(255, 255, 255))
                        elif player["CharacterSelectionState"] == "selected":
                            agent_color = color(str(agent_dict.get(player["CharacterID"].lower())),
                                                fore=(128, 128, 128))
                        else:
                            agent_color = color(str(agent_dict.get(player["CharacterID"].lower())), fore=(54, 53, 51))

                        # AGENT
                        agent = agent_color

                        # NAME
                        name = NameColor

                        # RANK
                        rankName = NUMBERTORANKS[playerRank[0]]
                        rankDisplayName = RANKS[playerRank[0]]

                        # RANK RATING
                        rr = playerRank[1]

                        # PEAK RANK
                        peakRank = NUMBERTORANKS[playerRank[3]]
                        peakRankDisplay = RANKS[playerRank[3]]

                        # LEADERBOARD
                        leaderboard = playerRank[2]

                        # LEVEL
                        level = PLcolor

                        tableClass.add_row_table(table, [agent,
                                                name,
                                                rankName,
                                                rr,
                                                peakRank,
                                                leaderboard,
                                                level
                                              ])
                        Content.set_values_in_file(Requests, cfg.dir, "agent", str(agent_dict.get(player["CharacterID"])))
                        Content.set_values_in_file(Requests, cfg.dir, "name", name)
                        Content.set_values_in_file(Requests, cfg.dir, "rank", rankDisplayName)
                        Content.set_values_in_file(Requests, cfg.dir, "rr", rr)
                        Content.set_values_in_file(Requests, cfg.dir, "peakRank", peakRankDisplay)
                        Content.set_values_in_file(Requests, cfg.dir, "leaderboard", leaderboard)
                        Content.set_values_in_file(Requests, cfg.dir, "level", level)
                        Content.set_values_in_file(Requests, cfg.dir, "server", server)
                        bar()
            if game_state == "MENUS":
                Players = menu.get_party_members(Requests.puuid, presence)
                names = namesClass.get_names_from_puuids(Players)
                server = ""
                with alive_bar(total=len(Players), title='Fetching Players', bar='classic2') as bar:
                    log(f"retrieved names dict: {names}")
                    Players.sort(key=lambda Players: Players["PlayerIdentity"].get("AccountLevel"), reverse=True)
                    for player in Players:
                        playerRank = rank.get_rank(player["Subject"], seasonID)
                        rankStatus = playerRank[1]
                        while not rankStatus:
                            print("You have been rate limited, 😞 waiting 10 seconds!")
                            time.sleep(10)
                            playerRank = rank.get_rank(player["Subject"], seasonID)
                            rankStatus = playerRank[1]
                        playerRank = playerRank[0]
                        player_level = player["PlayerIdentity"].get("AccountLevel")
                        PLcolor = colors.level_to_color(player_level)

                        # AGENT
                        agent = ""

                        # NAME
                        name = names[player["Subject"]]

                        # RANK
                        rankName = NUMBERTORANKS[playerRank[0]]
                        rankDisplayName = RANKS[playerRank[0]]

                        # RANK RATING
                        rr = playerRank[1]

                        # PEAK RANK
                        peakRank = NUMBERTORANKS[playerRank[3]]
                        peakRankDisplay = RANKS[playerRank[3]]

                        # LEADERBOARD
                        leaderboard = playerRank[2]

                        # LEVEL
                        level = str(player_level)

                        tableClass.add_row_table(table, [agent,
                                                name,
                                                rankName,
                                                rr,
                                                peakRank,
                                                leaderboard,
                                                level
                                              ])
                        Content.set_values_in_file(Requests, cfg.dir, "agent", agent)
                        Content.set_values_in_file(Requests, cfg.dir, "name", name)
                        Content.set_values_in_file(Requests, cfg.dir, "rank", rankDisplayName)
                        Content.set_values_in_file(Requests, cfg.dir, "rr", rr)
                        Content.set_values_in_file(Requests, cfg.dir, "peakRank", peakRankDisplay)
                        Content.set_values_in_file(Requests, cfg.dir, "leaderboard", leaderboard)
                        Content.set_values_in_file(Requests, cfg.dir, "level", level)
                        Content.set_values_in_file(Requests, cfg.dir, "server", server)
                        bar()
            if (title := game_state_dict.get(game_state)) is None:
                table.title = f"VALORANT Status: closed"
            if server != "":
                table.title = f"VALORANT Status: {title} - {server}"
            else:
                table.title = f"VALORANT Status: {title}"
            server = ""
            table.field_names = ["Agent", "Name", "Rank", "RR", "Peak Rank", "#", "Level"]
            print(table)
            print(f"VALORANT Rank Stream Displayer v{version}")
        if cfg.cooldown == 0:
            input("Press enter to fetch again...")
        else:
            time.sleep(cfg.cooldown)
except:
    print(color(
        "The program has encountered an error. If the problem persists, please reach support"
        f" with the logs found in {os.getcwd()}\logs", fore=(255, 0, 0)))
    traceback.print_exc()
    input("press enter to exit...\n")
    os._exit(1)
