import requests
import json
import gzip
import shutil
import time
import os
from io import BytesIO
import traceback
from player import Player, Team, ELO
from system import process_game

S3_BUCKET_URL = "https://power-rankings-dataset-gprhack.s3.us-west-2.amazonaws.com"


def download_gzip_and_write_to_json(file_name):
   local_file_name = file_name.replace(":", "_")
   # If file already exists locally do not re-download game
   if os.path.isfile(f"{local_file_name}.json"):
       return

   response = requests.get(f"{S3_BUCKET_URL}/{file_name}.json.gz")
   if response.status_code == 200:
       try:
           gzip_bytes = BytesIO(response.content)
           with gzip.GzipFile(fileobj=gzip_bytes, mode="rb") as gzipped_file:
               with open(f"{local_file_name}.json", 'wb') as output_file:
                   shutil.copyfileobj(gzipped_file, output_file)
               print(f"{file_name}.json written")
       except Exception as e:
           print("Error:", e)
   else:
       print(f"Failed to download {file_name}")
   return local_file_name


def download_esports_files():
   directory = "esports-data"
   if not os.path.exists(directory):
       os.makedirs(directory)
   else:
       return
   esports_data_files = ["leagues", "tournaments", "players", "teams", "mapping_data"]
   #esports_data_files = ["mapping_data"]
   for file_name in esports_data_files:
       download_gzip_and_write_to_json(f"{directory}/{file_name}")

def loadTeams():
    teams = {}
    if os.path.exists("teams.json"):
        with open("teams.json", "r") as json_file:
            teams_data = json.load(json_file)
        for team in teams_data:
            new_team = Team(team["id"])
            new_team.elo.value = team["elo"]
            new_team.games_played = team["games_played"]
            new_team.wins = team["wins"]
            teams[team["id"]] = Team(team["id"])
    return teams
def loadPlayers():
    players = {}
    if os.path.exists("players.json"):
        with open("players.json", "r") as json_file:
            players_data = json.load(json_file)
        for player in players_data:
            new_player = Player(player["id"])
            new_player.elo.value = player["elo"]
            new_player.sportsmanship_elo = ELO.create_elo(player["sportsmanship_elo"])
            new_player.objective_elo = ELO.create_elo(player["objective_elo"])
            new_player.aggression_elo = ELO.create_elo(player["aggression_elo"])
            new_player.consistency_elo = ELO.create_elo(player["consistency_elo"])
            new_player.wins = player["wins"]
            new_player.games_played = player["games_played"]
            new_player.champion_kills = player["champion_kills"]
            new_player.total_damage_taken_100 = player["total_damage_taken_100"]
            new_player.total_damage_dealt_100 = player["total_damage_dealt_100"]
            new_player.total_damage_dealt_to_objectives_100 = player["total_damage_dealt_to_objectives_100"]
            new_player.total_damage_dealt_to_champions_100 = player["total_damage_dealt_to_champions_100"]
            players[player["id"]] = new_player
    return players
# add functionality to load existing...
teams = loadTeams()
players = loadPlayers()

target = "ESPORTSTMNT01:3391622"
found = False
def download_games(year):
    start_time = time.time()
    with open("esports-data/tournaments.json", "r") as json_file:
        tournaments_data = json.load(json_file)
    with open("esports-data/mapping_data.json", "r") as json_file:
        mappings_data = json.load(json_file)

    directory = "games"
    if not os.path.exists(directory):
        os.makedirs(directory)

    mappings = {
        esports_game["esportsGameId"]: esports_game for esports_game in mappings_data
    }

    game_counter = 0
    global found
    for tournament in tournaments_data:
        start_date = tournament.get("startDate", "")
        if start_date.startswith(str(year)):
            print(f"Processing {tournament['slug']}")
            for stage in tournament["stages"]:
                for section in stage["sections"]:
                    for match in section["matches"]:
                        for game in match["games"]:
                            if game["state"] == "completed":
                                try:
                                    local_file_name = None
                                    platform_game_id = mappings[game["id"]]["platformGameId"]
                                    if platform_game_id == target:
                                        found = True
                                    if not found:
                                        print("Looking for last game...")
                                    else:
                                        local_file_name = download_gzip_and_write_to_json(f"{directory}/{platform_game_id}")
                                        try:
                                            if local_file_name != None:
                                                processed_game = process_game(f"{local_file_name}.json")
                                                for player in processed_game.players:
                                                    player_id = mappings[game["id"]]["participantMapping"][str(player.id)]
                                                    if player_id not in players:
                                                        players[player_id] = player
                                                        players[player_id].id = player_id
                                                    else:
                                                        players[player_id].combine(player)
                                                team_1_id = mappings[game["id"]]["teamMapping"][str(processed_game.teams[0].id)]
                                                team_2_id = mappings[game["id"]]["teamMapping"][str(processed_game.teams[1].id)]
                                                
                                                if team_1_id not in teams:
                                                    teams[team_1_id] = processed_game.teams[0]
                                                    teams[team_1_id].id = team_1_id
                                                else:
                                                    teams[team_1_id].combine(processed_game.teams[0])
                                                    
                                                if team_2_id not in teams:
                                                    teams[team_2_id] = processed_game.teams[1]
                                                    teams[team_2_id].id = team_2_id
                                                else:
                                                    teams[team_2_id].combine(processed_game.teams[1])
                                                    
                                                if processed_game.teams[0].won:
                                                    teams[team_1_id].lose_to(teams[team_2_id])
                                                else:
                                                    teams[team_2_id].lose_to(teams[team_1_id])  
                                                    
                                            os.remove(f"{local_file_name}.json")
                                        except Exception as e:
                                            print(f"Error processing {platform_game_id}: {type(e).__name__} - {e}")
                                        #print("Mapping: ", mappings[game["id"]])
                                            traceback.print_exc()
                                            if os.path.exists(f"{local_file_name}.json"):
                                                os.remove(f"{local_file_name}.json")
                                            continue
                                except KeyError:
                                    print(f"{platform_game_id} {game['id']} not found in the mapping table")
                                    if local_file_name != None:
                                        if os.path.exists(f"{local_file_name}.json"):
                                            os.remove(f"{local_file_name}.json")
                                    continue
                                game_counter += 1

                            if game_counter % 10 == 0:
                                print(
                                   f"----- Processed {game_counter} games, current run time: \
                                   {round((time.time() - start_time)/60, 2)} minutes"
                                )
    
    teams_json = [team.serialize() for _, team in teams.items()]
    players_json = [player.serialize() for _, player in players.items()]
    
    with open('teams.json', "w") as f:
        json.dump(teams_json, f)
    with open('players.json', "w") as f:
        json.dump(players_json, f)
    


if __name__ == "__main__":
   #download_esports_files()
    start_time = time.time()
    try:
        download_games(2023)
    except KeyboardInterrupt:
        print("Keyboard Interrupt!")
        teams_json = [team.serialize() for _, team in teams.items()]
        players_json = [player.serialize() for _, player in players.items()]
    
        with open('teams.json', "w") as f:
            json.dump(teams_json, f)
        with open('players.json', "w") as f:
            json.dump(players_json, f)
    except Exception as e:
        print(f"An error occurred: {type(e).__name__} - {e}")
        traceback.print_exc()
        teams_json = [team.serialize() for _, team in teams.items()]
        players_json = [player.serialize() for _, player in players.items()]
    
        with open('teams.json', "w") as f:
            json.dump(teams_json, f)
        with open('players.json', "w") as f:
            json.dump(players_json, f)
    finally:
        print(f"----- Processed {len(teams)} teams and {len(players)} players, total run time: \
            {round((time.time() - start_time)/60, 2)} minutes")
   