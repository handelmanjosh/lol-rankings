
import math

class ELO():
    eq = lambda x : math.e ** (x / 50 if x / 50 < 250 else 250)
    """ELO class for ELO rating. Only used when matchups are made"""
    def __init__(self):
        self.value: int = 1500
    def __add__(self, others: list["ELO"]):
        """self is the one killed, others are the ones who killed them. First player in others is killer, rest are assists"""
        # calculate scaled average difference, scaling the difference of the killer by 2
        scaled_avg_diff = ((self.value - others[0].value) * 2 + sum([self.value - i.value for i in others[1:]])) / (len(others[1:]) + 2)
        diff = ELO.eq(scaled_avg_diff)
        self.value -= diff
        for other in others:
            other.value += diff
    def __str__(self):
        return str(self.value)
    @staticmethod
    def create_elo(value: int):
        elo = ELO()
        elo.value = value
        return elo
        
class Increment():
    def __init__(self):
        self.value: float = 0
    def inc(self, amount: float):
        self.value += amount  
class Curve():
    def __init__(self):
        self.points: list[float] = []
    def __len__(self):
        return len(self.points)
    def add(self, point: float):
        self.points.append(point)
    def max(self):
        return max(self.points)
    def last(self):
        return self.points[-1]
    def deriv(self):
        return [self.points[i] - self.points[i - 1] for i in range(1, len(self.points))]
    def percentage_deriv(self):
        result = []
        for i in range(1, len(self.points)):
            if self.points[i] == 0:
                result.append(0)
            elif self.points[i - 1] == 0:
                result.append(1000)
            else:
                result.append(self.points[i] / self.points[i - 1])
        return result
    def percentage_second_deriv(self):
        deriv = self.deriv()
        result = []
        for i in range(1, len(deriv)):
            if deriv[i] == 0:
                result.append(0)
            elif deriv[i - 1] != 0:
                result.append(deriv[i] / deriv[i - 1])
            else:
                result.append(1000)
        return result
    def avg_percentage_deriv(self):
        percentage_deriv = self.percentage_deriv()
        return sum(percentage_deriv) / len(percentage_deriv)
    def avg_percentage_second_deriv(self):
        percentage_second_deriv = self.percentage_second_deriv()
        return sum(percentage_second_deriv) / len(percentage_second_deriv)
    def avg(self):
        return sum(self.points) / len(self.points)
    def var(self):
        avg = self.avg()
        return sum([(i - avg) ** 2 for i in self.points]) / len(self.points)
    def var_deriv(self):
        avg = self.avg_deriv()
        return sum([(i - avg) ** 2 for i in self.deriv()]) / len(self.deriv())
    def var_second_deriv(self):
        avg = self.avg_second_deriv()
        return sum([(i - avg) ** 2 for i in self.second_deriv()]) / len(self.second_deriv())
    def avg_deriv(self):
        deriv = self.deriv()
        return sum(deriv) / len(deriv)
    def avg_second_deriv(self):
        deriv = self.deriv()
        return sum([deriv[i] - deriv[i - 1] for i in range(1, len(deriv))]) / (len(deriv) - 1)
    def second_deriv(self):
        deriv = self.deriv()
        return [deriv[i] - deriv[i - 1] for i in range(1, len(deriv))]

class Player():
    def __init__(self, id: int):
        self.id: int = id
        self.account_id: str = None
        self.perk_ids: list[int] = []
        self.perk_style: int = None
        self.perk_sub_style: int = None
        self.champion_name: str = None
        self.team_id: int = None
        
        self.elo: ELO = ELO()
        self.sportsmanship_elo: ELO = None
        self.objective_elo: ELO = None
        self.aggression_elo: ELO = None
        self.consistency_elo: ELO = None
        
        self.increments: dict[str, Increment] = {}
        self.curves: dict[str, Curve] = {}
        
        self.champion_kills: int = 0
        self.wins: int = 0
        self.games_played: int = 0
        self.total_damage_taken_100: float = 0
        self.total_damage_dealt_100: float = 0
        self.total_damage_dealt_to_objectives_100: float = 0
        self.total_damage_dealt_to_champions_100: float = 0
        
    def __str__(self):
        return f"""
        Player: {self.id}
        Account ID: {self.account_id}
        Perk IDs: {self.perk_ids}
        Perk Style: {self.perk_style}
        Perk Sub Style: {self.perk_sub_style}
        Champion Name: {self.champion_name}
        Team ID: {self.team_id}
        ELO: {self.elo.value}
        Aggression ELO: {self.aggression_elo.value}
        Consistency ELO: {self.consistency_elo.value}
        Objective ELO: {self.objective_elo.value}
        Sportsmanship ELO: {self.sportsmanship_elo.value}
        """
    def die_to(self, others: list["Player"]):
        self.elo + [i.elo for i in others]
    def combine(self, other: "Player"):
        self.elo.value = (self.elo.value + other.elo.value) / 2
        self.sportsmanship_elo.value = (self.sportsmanship_elo.value + other.sportsmanship_elo.value) / 2
        self.objective_elo.value = (self.objective_elo.value + other.objective_elo.value) / 2
        self.aggression_elo.value = (self.aggression_elo.value + other.aggression_elo.value) / 2
        self.consistency_elo.value = (self.consistency_elo.value + other.consistency_elo.value) / 2
        self.wins += other.wins
        self.games_played += other.games_played
        self.champion_kills += other.champion_kills
        self.total_damage_taken_100 += other.total_damage_taken_100
        self.total_damage_dealt_100 += other.total_damage_dealt_100
        self.total_damage_dealt_to_objectives_100 += other.total_damage_dealt_to_objectives_100
        self.total_damage_dealt_to_champions_100 += other.total_damage_dealt_to_champions_100
    def serialize(self):
        return {
            "id": self.id,
            "elo": self.elo.value,
            "sportsmanship_elo": self.sportsmanship_elo.value,
            "objective_elo": self.objective_elo.value,
            "aggression_elo": self.aggression_elo.value,
            "consistency_elo": self.consistency_elo.value,
            "wins": self.wins,
            "games_played": self.games_played,
            "champion_kills": self.champion_kills,
            "total_damage_taken_100": self.total_damage_taken_100,
            "total_damage_dealt_100": self.total_damage_dealt_100,
            "total_damage_dealt_to_objectives_100": self.total_damage_dealt_to_objectives_100,
            "total_damage_dealt_to_champions_100": self.total_damage_dealt_to_champions_100
        }
class Team():
    def __init__(self, id: int):
        self.id: int = id
        self.won = False
        self.elo: ELO = ELO()
        
        self.wins: int = 0
        self.games_played: int = 0
    def __str__(self):
        return f"Team: {self.id}, won: {self.won}"
    def lose_to(self, other: "Team"):
        self.elo + [other.elo]
    def combine(self, other: "Team"):
        self.wins += other.wins
        self.games_played += other.games_played
    def serialize(self):
        return {
            "id": self.id,
            "elo": self.elo.value,
            "wins": self.wins,
            "games_played": self.games_played
        }
        
class Game():
    def __init__(self):
        self.teams: list[Team] = []
        self.players: list[Player] = [] 
        self.platform_game_id: str = ""
    def __str__(self):
        teamstring = [str(team) for team in self.teams]
        playerstring = [str(player) for player in self.players]
        return f"""
        Game: {self.platform_game_id}
        Teams: {teamstring}
        Players: {playerstring}
    """
