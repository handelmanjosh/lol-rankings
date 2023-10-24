import json


players = json.load(open('players.json', 'r'))
teams = json.load(open('teams.json', 'r'))

player_data = json.load(open('esports-data/players.json', 'r'))
team_data = json.load(open('esports-data/teams.json', 'r'))
def find(id, data, key):
    for point in data:
        if point[key] == id:
            return point
    return None
for player in players:
    data = find(player["id"], player_data, "player_id")
    if data != None:
        player["first_name"] = data["first_name"]
        player["last_name"] = data["last_name"]
        player["handle"] = data["handle"]
        player["team_id"] = data["home_team_id"]
    else:
        player["first_name"] = ""
        player["last_name"] = ""
        player["handle"] = ""
        player["team_id"] = ""
        
for team in teams:
    data = find(team["id"], team_data, "team_id")
    if data != None:
        team["name"] = data["name"]
    else:
        team["name"] = ""
        

def findMany(id: str, data, key: str) -> list:
    result = []
    for point in data:
        if point[key] == id:
            result.append(point)
    return result

for team in teams:
    team_players = findMany(team["id"], players, "team_id")
    for player in team_players:
        pass
json.dump(players, open('players.json', 'w'))
json.dump(teams, open('teams.json', 'w'))