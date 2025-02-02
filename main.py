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
from src.data import Data
from src.requests import Requests
from src.logs import Logging
from src.config import Config
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
    Logging = Logging()
    log = Logging.log
    cfg = Config(log)

    Requests = Requests(version, log)
    Requests.check_version()
    Requests.check_status()

    rankClass = Rank(Requests, log)
    content = Content(Requests, log)
    data = Data(Requests, cfg.dir, log)
    namesClass = Names(Requests, log)
    presences = Presences(Requests, log)

    menu = Menu(Requests, log, presences)
    pregame = Pregame(Requests, log)
    coregame = Coregame(Requests, log)

    Server = Server(Requests)
    Server.start_server()

    log(f"[App] VALORANT Rank Stream Displayer v{version}")

    tableClass = Table()
    gameContent = content.get_content()
    episode = content.get_current_episode()
    act = content.get_current_act()
    currentSeason = content.get_current_season()

    ranks_arr = content.get_all_ranks(episode)
    agent_dict = content.get_all_agents()
    map_dict = content.get_all_maps()
    mode_dict = content.get_all_modes()

    icons_dict = content.get_all_icons(episode)
    data.set_icons(icons_dict)

    seasonID = content.get_latest_season_id()
    lastGameState = ""

    while True:
        table = PrettyTable()
        try:
            presence = presences.get_presence()
            game_state = presences.get_game_state(presence)
        except TypeError:
            raise Exception(color("VALORANT has not started yet or the Riot Client has been closed!", fore=(255, 0, 0)))

        if cfg.cooldown == 0 or game_state != lastGameState:
            log(f"[Game State] Getting new statistics from the {game_state}")
            lastGameState = game_state

            game_state_dict = {
                "INGAME": color('In-Game', fore=(241, 39, 39)),
                "PREGAME": color('Agent Select', fore=(103, 237, 76)),
                "MENUS": color('In-Menus', fore=(238, 241, 54)),
                None: color("")
            }

            if game_state == "INGAME":
                coregame_stats = coregame.get_coregame_stats()
                log(f"core game {coregame_stats}")
                server = GAMEPODS[coregame_stats["GamePodID"]]
                map = map_dict[coregame_stats["MapID"]]
                mode = mode_dict[coregame_stats["ModeID"].split(".", 1)[0]]

                Players = coregame_stats["Players"]
                Players = list(filter(lambda a: a["Subject"] == Requests.puuid, Players))
                
                presences.wait_for_presence(namesClass.get_players_puuid(Players))
                names = namesClass.get_names_from_puuids(Players)

                with alive_bar(total=len(Players), title='Fetching player data', bar='classic2') as bar:
                    presence = presences.get_presence()
                    log(f"[Player] Details: {names}")
                    
                    # Player
                    player = Players[0]

                    # Agent
                    agent = str(agent_dict.get(player["CharacterID"]))

                    # Name
                    name = names[player["Subject"]]

                    playerRank = rankClass.get_rank(player["Subject"], seasonID)
                    rankStatus = playerRank[1]

                    while not rankStatus:
                        print("You have been rate limited, 😞 waiting 10 seconds!")
                        time.sleep(10)
                        playerRank = rankClass.get_rank(player["Subject"], seasonID)
                        rankStatus = playerRank[1]

                    playerRank = playerRank[0]

                    # Rank
                    rank = ranks_arr[playerRank[0]]

                    # Rank Rating
                    rr = playerRank[1]

                    # Peak Rank
                    peakRank = ranks_arr[playerRank[3]]

                    # Leaderboard
                    leaderboard = playerRank[2]

                    # Level
                    level = player["PlayerIdentity"].get("AccountLevel")

                    tableClass.add_row_table(table, [agent,
                                                name,
                                                rank,
                                                rr,
                                                peakRank,
                                                leaderboard,
                                                level
                                            ])
                    data.set_data(agent, name, rank, rr, peakRank, leaderboard, level, server, map, mode, currentSeason)
                    bar()
                        
            elif game_state == "PREGAME":
                pregame_stats = pregame.get_pregame_stats()
                server = GAMEPODS[pregame_stats["GamePodID"]]
                map = map_dict[pregame_stats["MapID"]]
                mode = mode_dict[pregame_stats["Mode"].split(".", 1)[0]]

                Players = pregame_stats["AllyTeam"]["Players"]
                Players = list(filter(lambda a: a["Subject"] == Requests.puuid, Players))
                presences.wait_for_presence(namesClass.get_players_puuid(Players))
                names = namesClass.get_names_from_puuids(Players)

                with alive_bar(total=len(Players), title='Fetching player data', bar='classic2') as bar:
                    presence = presences.get_presence()
                    log(f"[Player] Details: {names}")

                    # Player
                    player = Players[0]

                    playerRank = rankClass.get_rank(player["Subject"], seasonID)
                    rankStatus = playerRank[1]

                    while not rankStatus:
                        print("You have been rate limited, 😞 waiting 10 seconds!")
                        time.sleep(10)
                        playerRank = rankClass.get_rank(player["Subject"], seasonID)
                        rankStatus = playerRank[1]

                    playerRank = playerRank[0]

                    # Agent
                    if player["CharacterSelectionState"] == "locked":
                        agent = str(agent_dict.get(player["CharacterID"]))
                    elif player["CharacterSelectionState"] == "selected":
                        agent = str(agent_dict.get(player["CharacterID"]))
                    else:
                        agent = str(agent_dict.get(player["CharacterID"]))

                    # Name
                    name = names[player["Subject"]]

                    # Rank
                    rank = ranks_arr[playerRank[0]]

                    # Rank Rating
                    rr = playerRank[1]

                    # Peak Rank
                    peakRank = ranks_arr[playerRank[3]]

                    # Leaderboard
                    leaderboard = playerRank[2]

                    # Level
                    level = player["PlayerIdentity"].get("AccountLevel")

                    tableClass.add_row_table(table, [agent,
                                                name,
                                                rank,
                                                rr,
                                                peakRank,
                                                leaderboard,
                                                level
                                            ])
                    data.set_data(agent, name, rank, rr, peakRank, leaderboard, level, server, map, mode, currentSeason)
                    bar()
            elif game_state == "MENUS":
                server = ""
                map = ""
                mode = ""

                Players = menu.get_party_members(Requests.puuid, presence)
                names = namesClass.get_names_from_puuids(Players)
                
                with alive_bar(total=len(Players), title='Fetching player data', bar='classic2') as bar:
                    log(f"[Player] Details: {names}")

                    player = Players[0]

                    playerRank = rankClass.get_rank(player["Subject"], seasonID)
                    rankStatus = playerRank[1]

                    while not rankStatus:
                        print("You have been rate limited, 😞 waiting 10 seconds!")
                        time.sleep(10)
                        playerRank = rankClass.get_rank(player["Subject"], seasonID)
                        rankStatus = playerRank[1]

                    playerRank = playerRank[0]

                    # Agent
                    agent = ""

                    # Name
                    name = names[player["Subject"]]

                    # Rank
                    rank = ranks_arr[playerRank[0]]

                    # Rank Rating
                    rr = playerRank[1]

                    # Peak Rank
                    peakRank = ranks_arr[playerRank[3]]

                    # Leaderboard
                    leaderboard = playerRank[2]

                    # Level
                    level = player["PlayerIdentity"].get("AccountLevel")

                    tableClass.add_row_table(table, [agent,
                                                name,
                                                rank,
                                                rr,
                                                peakRank,
                                                leaderboard,
                                                level
                                            ])
                    data.set_data(agent, name, rank, rr, peakRank, leaderboard, level, server, map, mode, currentSeason)
                    bar()
            elif game_state == None:
                server = ""
                map = ""
                mode = ""

                with alive_bar(total=1, title='Loading', bar='classic2') as bar:
                    # Agent
                    agent = ""

                    # Name
                    name = ""

                    # Rank
                    rank = ""

                    # Rank Rating
                    rr = ""

                    # Peak Rank
                    peakRank = ""

                    # Leaderboard
                    leaderboard = ""

                    # Level
                    level = ""

                    tableClass.add_row_table(table, [agent,
                                                name,
                                                rank,
                                                rr,
                                                peakRank,
                                                leaderboard,
                                                level
                                            ])
                    data.set_data(agent, name, rank, rr, peakRank, leaderboard, level, server, map, mode, currentSeason)
                    bar()

            title = game_state_dict.get(game_state)

            if game_state is None:
                table.title = f"VALORANT Status: closed"
            else:
                if server != "":
                    table.title = f"VALORANT Status: {title} - {currentSeason} - {map} - {mode} - {server}"
                else:
                    table.title = f"VALORANT Status: {title} - {currentSeason}"

            table.field_names = ["Agent", "Name", "Rank", "RR", "Peak Rank", "#", "Level"]
            print(table)
            print(f"Files can be found here: {cfg.dir}")
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
