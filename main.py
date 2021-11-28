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

    rankClass = Rank(Requests, log)
    content = Content(Requests, log)
    namesClass = Names(Requests, log)
    presences = Presences(Requests, log)

    menu = Menu(Requests, log, presences)
    pregame = Pregame(Requests, log)
    coregame = Coregame(Requests, log)

    Server = Server(Requests)
    Server.start_server()

    agent_dict = content.get_all_agents()

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
            raise Exception(color("VALORANT has not started yet or the Riot Client has been closed!", fore=(255, 0, 0)))

        if cfg.cooldown == 0 or game_state != lastGameState:
            log(f"getting new {game_state} scoreboard")
            lastGameState = game_state

            game_state_dict = {
                "INGAME": color('In-Game', fore=(241, 39, 39)),
                "PREGAME": color('Agent Select', fore=(103, 237, 76)),
                "MENUS": color('In-Menus', fore=(238, 241, 54)),
                None: color("")
            }

            if game_state == "INGAME":
                coregame_stats = coregame.get_coregame_stats()
                server = GAMEPODS[coregame_stats["GamePodID"]]

                Players = coregame_stats["Players"]
                Players = list(filter(lambda a: a["Subject"] == Requests.puuid, Players))
                
                presences.wait_for_presence(namesClass.get_players_puuid(Players))
                names = namesClass.get_names_from_puuids(Players)

                with alive_bar(total=len(Players), title='Fetching player data', bar='classic2') as bar:
                    presence = presences.get_presence()
                    log(f"retrieved names dict: {names}")
                    
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
                    rank = RANKS[playerRank[0]]

                    # Rank Rating
                    rr = playerRank[1]

                    # Peak Rank
                    peakRank = RANKS[playerRank[3]]

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
                    Content.set_values_in_file(Requests, cfg.dir, "agent", agent)
                    Content.set_values_in_file(Requests, cfg.dir, "name", name)
                    Content.set_values_in_file(Requests, cfg.dir, "rank", rank)
                    Content.set_values_in_file(Requests, cfg.dir, "rr", rr)
                    Content.set_values_in_file(Requests, cfg.dir, "peakRank", peakRank)
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

                with alive_bar(total=len(Players), title='Fetching player data', bar='classic2') as bar:
                    presence = presences.get_presence()
                    log(f"retrieved names dict: {names}")

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
                    rank = RANKS[playerRank[0]]

                    # Rank Rating
                    rr = playerRank[1]

                    # Peak Rank
                    peakRank = RANKS[playerRank[3]]

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
                    Content.set_values_in_file(Requests, cfg.dir, "agent", agent)
                    Content.set_values_in_file(Requests, cfg.dir, "name", name)
                    Content.set_values_in_file(Requests, cfg.dir, "rank", rank)
                    Content.set_values_in_file(Requests, cfg.dir, "rr", rr)
                    Content.set_values_in_file(Requests, cfg.dir, "peakRank", peakRank)
                    Content.set_values_in_file(Requests, cfg.dir, "leaderboard", leaderboard)
                    Content.set_values_in_file(Requests, cfg.dir, "level", level)
                    Content.set_values_in_file(Requests, cfg.dir, "server", server)
                    bar()
            elif game_state == "MENUS":
                server = ""

                Players = menu.get_party_members(Requests.puuid, presence)
                names = namesClass.get_names_from_puuids(Players)
                
                with alive_bar(total=len(Players), title='Fetching player data', bar='classic2') as bar:
                    log(f"retrieved names dict: {names}")

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
                    rank = RANKS[playerRank[0]]

                    # Rank Rating
                    rr = playerRank[1]

                    # Peak Rank
                    peakRank = RANKS[playerRank[3]]

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
                    Content.set_values_in_file(Requests, cfg.dir, "agent", agent)
                    Content.set_values_in_file(Requests, cfg.dir, "name", name)
                    Content.set_values_in_file(Requests, cfg.dir, "rank", rank)
                    Content.set_values_in_file(Requests, cfg.dir, "rr", rr)
                    Content.set_values_in_file(Requests, cfg.dir, "peakRank", peakRank)
                    Content.set_values_in_file(Requests, cfg.dir, "leaderboard", leaderboard)
                    Content.set_values_in_file(Requests, cfg.dir, "level", level)
                    Content.set_values_in_file(Requests, cfg.dir, "server", server)
                    bar()
            elif game_state == None:
                server = ""
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
                    Content.set_values_in_file(Requests, cfg.dir, "agent", agent)
                    Content.set_values_in_file(Requests, cfg.dir, "name", name)
                    Content.set_values_in_file(Requests, cfg.dir, "rank", rank)
                    Content.set_values_in_file(Requests, cfg.dir, "rr", rr)
                    Content.set_values_in_file(Requests, cfg.dir, "peakRank", peakRank)
                    Content.set_values_in_file(Requests, cfg.dir, "leaderboard", leaderboard)
                    Content.set_values_in_file(Requests, cfg.dir, "level", level)
                    Content.set_values_in_file(Requests, cfg.dir, "server", server)
                    bar()


            title = game_state_dict.get(game_state)

            if game_state is None:
                table.title = f"VALORANT Status: closed"
            else:
                if server != "":
                    table.title = f"VALORANT Status: {title} - {server}"
                else:
                    table.title = f"VALORANT Status: {title}"

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
