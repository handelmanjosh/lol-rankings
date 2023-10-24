from player import Player, Team, Increment, Curve, ELO, Game
import json
import os

import traceback

    

level_up_scale = lambda level: level ** 2

def process_game(filename: str) -> Game:
    
    game_json = json.load(open(filename, "r"))
    
    game: Game = Game()
    teams: list[Team] = [Team(100), Team(200)]
    players: list[Player] = [Player(i) for i in range(1, 11)]
    game.teams = teams
    game.players = players
    
    for event in game_json:
        try:
            type = event["eventType"]
            if type == "building_destroyed":
                indexes = [i - 1 for i in event["assistants"]]
                indexes.append(event["lastHitter"] - 1)
                inc = 1 / len(indexes)
                for index in indexes:
                    if "building_destroyed" not in players[index].increments:
                        players[index].increments["building_destroyed"] = Increment()
                        players[index].increments["building_destroyed"].inc(inc)
                    else:
                        players[index].increments["building_destroyed"].inc(inc)
            elif type == "champion_kill":
            # fires when a champion is killed
                killer_index: int = event["killer"] - 1
                players[killer_index].champion_kills += 1
                killee_index: int = event["victim"] - 1
                killers = [killer_index]
                for i in event["assistants"]:
                    killers.append(i - 1)
                players[killee_index].die_to([players[i] for i in killers])
            elif type == "champion_kill_special":
                index = event["killer"] - 1
                if "champion_kill_special" not in players[index].increments:
                    players[index].increments["champion_kill_special"] = Increment()
                    players[index].increments["champion_kill_special"].inc(1)
                else:
                    players[index].increments["champion_kill_special"].inc(1)
            elif type == "champion_level_up":
                index = event["participant"] - 1
                inc = level_up_scale(event["level"])
                if "champion_level_up" not in players[index].increments:
                    players[index].increments["champion_level_up"] = Increment()
                    players[index].increments["champion_level_up"].inc(inc)
                else:
                    players[index].increments["champion_level_up"].inc(inc)
            elif type == "epic_monster_kill":
                indexes = [event["killer"] - 1]
                for i in event["assistants"]:
                    indexes.append(i - 1)
                mult = event["killerGold"] + (10 if event["inEnemyJungle"] else 0)
                inc = 1 / (len(indexes) + 1) * mult
                for i, index in enumerate(indexes):
                    if "epic_monster_kill" not in players[index].increments:
                        players[index].increments["epic_monster_kill"] = Increment()
                        players[index].increments["epic_monster_kill"].inc(inc * (2 if i == 0 else 1))
                    else:
                        players[index].increments["epic_monster_kill"].inc(inc * (2 if i == 0 else 1))
            elif type == "game_info":
            # sets up game info
                game.platform_game_id = str(event["platformGameId"])
                for participant in event["participants"]:
                    index: int = participant["participantID"] - 1 # need to subtract 1 to adjust
                    players[index].account_id = str(participant["accountID"])
                    players[index].champion_name = participant["championName"]
                    players[index].perk_ids = participant["perks"][0]["perkIds"]
                    players[index].perk_style = participant["perks"][0]["perkStyle"]
                    players[index].perk_sub_style = participant["perks"][0]["perkSubStyle"]
                    players[index].team_id = participant["teamID"]            
            elif type == "game_end":
                index = (event["winningTeam"] // 100) - 1
                teams[index].won = True
                teams[index].wins += 1
                for player in players:
                    if player.team_id == teams[index].id:
                        player.wins += 1
                    player.games_played += 1
                teams[0].games_played += 1
                teams[1].games_played += 1
            elif type == "item_destroyed":
                index = event["participantID"] - 1
                if "item_destroyed" not in players[index].increments:
                    players[index].increments["item_destroyed"] = Increment()
                    players[index].increments["item_destroyed"].inc(1)
                else:
                    players[index].increments["item_destroyed"].inc(1)
            elif type == "item_purchased":
                index = event["participantID"] - 1  
                if "item_purchased" not in players[index].increments:
                    players[index].increments["item_purchased"] = Increment()
                    players[index].increments["item_purchased"].inc(1)
                else:
                    players[index].increments["item_purchased"].inc(1)
            elif type == "item_sold":
                index = event["participantID"] - 1
                if "item_sold" not in players[index].increments:
                    players[index].increments["item_sold"] = Increment()
                    players[index].increments["item_sold"].inc(1)
                else:
                    players[index].increments["item_sold"].inc(1)
            elif type == "skill_level_up":
                index = event["participant"] - 1
                if "skill_level_up" not in players[index].increments:
                    players[index].increments["skill_level_up"] = Increment()
                    players[index].increments["skill_level_up"].inc(1)
                else:
                    players[index].increments["skill_level_up"].inc(1)
            elif type == "stats_update":
                targeted_stats = ["currentGold", "level", "health", "XP"]
                targeted_stats_2 = ["MINIONS_KILLED", "CHAMPIONS_KILLED", "NUM_DEATHS", "ASSISTS", "WARD_PLACED", "WARD_KILLED",
                                "TOTAL_DAMAGE_DEALT", "TOTAL_DAMAGE_DEALT_TO_CHAMPIONS", "TOTAL_DAMAGE_DONE_TO_BUILDINGS",
                                "TOTAL_DAMAGE_DEALT_TO_OBJECTIVES", "TOTAL_HEAL_ON_TEAMMATES", "TOTAL_DAMAGE_TAKEN"]
                for i, participant in enumerate(event["participants"]):
                    index = participant["participantID"] - 1
                    for stat in targeted_stats:
                        if stat not in players[index].curves:
                            players[index].curves[stat] = Curve()
                        players[index].curves[stat].add(participant[stat])
                    for stat in participant["stats"]:
                        if stat["name"] in targeted_stats_2:
                            if stat["name"] not in players[index].curves:
                                players[index].curves[stat["name"]] = Curve()
                            players[index].curves[stat["name"]].add(stat["value"])
            elif type == "summoner_spell_used":
                index = event["participantID"] - 1
                if "summoner_spell_used" not in players[index].increments:
                    players[index].increments["summoner_spell_used"] = Increment()
                players[index].increments["summoner_spell_used"].inc(1)
            elif type == "turret_plate_destroyed":
                indexes = [i - 1 for i in event["assistants"]]
                indexes.append(event["lastHitter"] - 1)
                inc = 1 / len(indexes)
                for index in indexes:
                    if "turret_plate_destroyed" not in players[index].increments:
                        players[index].increments["turret_plate_destroyed"] = Increment()
                    players[index].increments["turret_plate_destroyed"].inc(inc)
            elif type == "turret_plate_gold_earned":
                index = event["participantID"] - 1
                if "turret_plate_gold_earned" not in players[index].increments:
                    players[index].increments["turret_plate_gold_earned"] = Increment()
                players[index].increments["turret_plate_gold_earned"].inc(event["bounty"])
            elif type == "ward_killed":
                index = event["killer"] - 1
                if "ward_killed" not in players[index].increments:
                    players[index].increments["ward_killed"] = Increment()
                players[index].increments["ward_killed"].inc(1)
            elif type == "ward_placed":
                index = event["placer"] - 1
                if "ward_placed" not in players[index].increments:
                    players[index].increments["ward_placed"] = Increment()
                players[index].increments["ward_placed"].inc(1)
        except Exception as e:
            #print(f"Error processing {event}")
            #print(f"Event: {type} ")
            #traceback.print_exc()
            continue
    
    summed = {}
    basic_parameters = [
        "building_destroyed",
        "champion_kill_special",
        "champion_level_up",
        "epic_monster_kill",
        "item_destroyed",
        "item_purchased",
        "item_sold",
        "skill_level_up",
        "summoner_spell_used",
        "turret_plate_destroyed",
        "turret_plate_gold_earned",
        "ward_killed",
        "ward_placed"
    ]
    for player in players:
        player.total_damage_taken_100 = player.curves["TOTAL_DAMAGE_TAKEN"].last() / 100
        player.total_damage_dealt_100 = player.curves["TOTAL_DAMAGE_DEALT"].last() / 100
        player.total_damage_dealt_to_champions_100 = player.curves["TOTAL_DAMAGE_DEALT_TO_CHAMPIONS"].last() / 100
        player.total_damage_dealt_to_objectives_100 = player.curves["TOTAL_DAMAGE_DEALT_TO_OBJECTIVES"].last() / 100
        
    for parameter in basic_parameters:
        for player in players:
            if parameter not in player.increments:
                player.increments[parameter] = Increment()
        
        summed[parameter] = sum([player.increments[parameter].value for player in players])
    curve_parameters = [
        "currentGold",
        "level",
        "health",
        "XP",
        "MINIONS_KILLED",
        "CHAMPIONS_KILLED",
        "NUM_DEATHS",
        "ASSISTS",
        "WARD_PLACED",
        "WARD_KILLED",
        "TOTAL_DAMAGE_DEALT",
        "TOTAL_DAMAGE_DEALT_TO_CHAMPIONS",
        "TOTAL_DAMAGE_DONE_TO_BUILDINGS",
        "TOTAL_DAMAGE_DEALT_TO_OBJECTIVES",
        "TOTAL_HEAL_ON_TEAMMATES",
        "TOTAL_DAMAGE_TAKEN"
    ]
    maxes = {}
    for parameter in curve_parameters:
        last = [player.curves[parameter].last() if parameter in player.curves else 0 for player in players]
        summed[parameter] = sum(last) / len(last) 
        maxed = [player.curves[parameter].max() if parameter in player.curves else 0 for player in players]
        maxes[parameter] = sum(maxed) / len(maxed)
        
    
    for player in players:
        sportsmanship_elo = calculate_sportsmanship_elo(player, summed, maxes)
        consistency_elo = calculate_consistency_elo(player, summed, maxes)
        aggression_elo = calculate_aggression_elo(player, summed, maxes)
        objective_elo = calculate_objective_elo(player, summed, maxes)
        player.sportsmanship_elo = ELO.create_elo(sportsmanship_elo)
        player.consistency_elo = ELO.create_elo(consistency_elo)
        player.aggression_elo = ELO.create_elo(aggression_elo)
        player.objective_elo = ELO.create_elo(objective_elo)

    ranked_elos = [200 * (i + 2) for i in range(len(players))]
    
    players.sort(key=lambda x: x.sportsmanship_elo.value, reverse=True)
    for i, player in enumerate(players):
        player.sportsmanship_elo.value = ranked_elos[i]
    players.sort(key=lambda x: x.consistency_elo.value, reverse=True)
    for i, player in enumerate(players):
        player.consistency_elo.value = ranked_elos[i]
    players.sort(key=lambda x: x.aggression_elo.value, reverse=True)
    for i, player in enumerate(players):
        player.aggression_elo.value = ranked_elos[i]
    players.sort(key=lambda x: x.objective_elo.value, reverse=True)
    for i, player in enumerate(players):
        player.objective_elo.value = ranked_elos[i]
    #print(game)
    return game
    
def calculate_sportsmanship_elo(player: "Player", summed: dict[str, float], maxes: dict[str, float]) -> float:
    sportsmanship_elo_basic: dict[str, tuple[bool, float]] = {
        "item_purchased": (True, 1),
        "item_sold": (True, 1),
        "WARD_PLACED": (False, 1),
        "WARD_KILLED": (False, 1),
        "TOTAL_HEAL_ON_TEAMMATES": (False, 1),
        "ASSISTS": (False, 1),
    }
    sportsmanship_elo_complex: list[tuple[str, float, function]] = [
        ("TOTAL_HEAL_DONE_ON_TEAMMATES", 6, lambda x: x.avg_percentage_deriv()), # need to be close to 1
        ("TOTAL_HEAL_DONE_ON_TEAMMATES", 4, lambda x: x.avg_percentage_second_deriv()),
    ]
    
    m: dict[float, float] = {}
    for key, (status, value) in sportsmanship_elo_basic.items():
        new_key = ((player.increments[key].value / summed[key]) if status else player.curves[key].last() / summed[key]) if key in player.curves else 0
        m[new_key] = value
    for (name, value, f) in sportsmanship_elo_complex:
        new_key = f(player.curves[name]) if name in player.curves else 0
        m[new_key] = value
        
    max_weighted_sum = sum([value for _, value in m.items()])
    weighted_sum = sum([key * value for key, value in m.items()])
    return weighted_sum / max_weighted_sum * 1000
    
def calculate_objective_elo(player: "Player", summed: dict[str, float], maxes: dict[str, float]) -> float:
    objective_elo_basic: dict[str, tuple[bool, float]] = {
        "building_destroyed": (True, 1),
        "epic_monster_kill": (True, 1),
        "turret_plate_destroyed": (True, 1),
        "turret_plate_gold_earned": (True, 1),
        "champion_level_up": (True, 1),
        "item_destroyed": (True, 1),
        "TOTAL_DAMAGE_DEALT_TO_OBJECTIVES": (False, 8),
        "TOTAL_DAMAGE_DONE_TO_BUILDINGS": (False, 8),
        "TOTAL_DAMAGE_DEALT": (False, 2),
        "TOTAL_DAMAGE_DEALT_TO_CHAMPIONS": (False, 2),
    }
    objective_elo_complex: list[tuple[str, float, function]] = [
        ("TOTAL_DAMAGE_DEALT_TO_OBJECTIVES", 8, lambda x: x.avg_percentage_deriv()),
        ("TOTAL_DAMAGE_DEALT_TO_OBJECTIVES", 4, lambda x: x.avg_percentage_second_deriv()),
        ("TOTAL_DAMAGE_DONE_TO_BUILDINGS", 4, lambda x: x.avg_percentage_deriv()),
        ("TOTAL_DAMAGE_DEALT", 2, lambda x: x.avg_percentage_deriv()),
        ("TOTAL_DAMAGE_DEALT_TO_CHAMPIONS", 2, lambda x: x.avg_percentage_deriv()),
    ]
    m: dict[float, float] = {}
    for key, (status, value) in objective_elo_basic.items():
        new_key = ((player.increments[key].value / summed[key]) if status else player.curves[key].last() / summed[key]) if key in player.curves else 0
        m[new_key] = value
    for (name, value, f) in objective_elo_complex:
        new_key = f(player.curves[name]) if name in player.curves else 0
        m[new_key] = value
    max_weighted_sum = sum([value for _, value in m.items()])
    weighted_sum = sum([key * value for key, value in m.items()])
    return weighted_sum / max_weighted_sum * 1000

def calculate_aggression_elo(player: "Player", summed: dict[str, float], maxes: dict[str, float]) -> float:
    aggression_elo_basic: dict[str, tuple[bool, float]] = {
        "champion_kill_special": (True, 1),
        "champion_level_up": (True, 3),
        "epic_monster_kill": (True, 1),
        "skill_level_up": (True, 1),
        "summoner_spell_used": (True, 1),
        "item_purchased": (True, 1),
        "item_sold": (True, 1),
        "item_destroyed": (True, 1),
        "MINIONS_KILLED": (False, 1),
        "CHAMPIONS_KILLED": (False, 8),
        "NUM_DEATHS": (False, 4),
        "ASSISTS": (False, 4),
        "WARD_PLACED": (False, 1),
        "WARD_KILLED": (False, 1),
        "TOTAL_DAMAGE_DEALT": (False, 5),
        "TOTAL_DAMAGE_DEALT_TO_CHAMPIONS": (False, 10),
        "TOTAL_DAMAGE_DONE_TO_BUILDINGS": (False, 1),
        "TOTAL_DAMAGE_DEALT_TO_OBJECTIVES": (False, 8),
    }
    aggression_elo_complex: list[tuple[str, float, function]] = [
        
    ]
    m: dict[float, float] = {}
    for key, (status, value) in aggression_elo_basic.items():
        new_key = ((player.increments[key].value / summed[key]) if status else player.curves[key].last() / summed[key]) if key in player.curves else 0
        m[new_key] = value
    for (name, value, f) in aggression_elo_complex:
        new_key = f(player.curves[name]) if name in player.curves else 0
        m[new_key] = value
    max_weighted_sum = sum([value for _, value in m.items()])
    weighted_sum = sum([key * value for key, value in m.items()])
    return weighted_sum / max_weighted_sum * 1000

def calculate_consistency_elo(player: "Player", summed: dict[str, float], maxes: dict[str, float]) -> float:
    consistency_elo_basic: dict[str, tuple[bool, float]] = {
        
    }
    consistency_elo_complex: list[tuple[str, float, function]] = [
        ("TOTAL_DAMAGE_DONE_TO_CHAMPIONS", 4, lambda x : 1 / x.var()),
        ("TOTAL_DAMAGE_DONE_TO_CHAMPIONS", 2, lambda x : 1 / x.var_deriv()),
        ("TOTAL_DAMAGE_DONE_TO_CHAMPIONS", 1, lambda x : 1 / x.var_second_deriv()),
        ("TOTAL_DAMAGE_DONE_TO_BUILDINGS", 4, lambda x : 1 / x.var()),
        ("TOTAL_DAMAGE_DONE_TO_BUILDINGS", 2, lambda x : 1 / x.var_deriv()),
        ("TOTAL_DAMAGE_DONE_TO_BUILDINGS", 1, lambda x : 1 / x.var_second_deriv()),
    ]
    m: dict[float, float] = {}
    for key, (status, value) in consistency_elo_basic.items():
        new_key = ((player.increments[key].value / summed[key]) if status else player.curves[key].last() / summed[key]) if key in player.curves else 0
        m[new_key] = value
    for (name, value, f) in consistency_elo_complex:
        new_key = f(player.curves[name]) if name in player.curves else 0
        m[new_key] = value
    max_weighted_sum = sum([value for _, value in m.items()])
    weighted_sum = sum([key * value for key, value in m.items()])
    return weighted_sum / max_weighted_sum * 1000

