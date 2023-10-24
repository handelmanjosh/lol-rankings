import teams from '../data/teams.json';
import players from '../data/players.json';
export function calculateTeamStats(team_id: string) {
    const team = teams.find(team => team.id === team_id);
    if (!team) return undefined;

    const teamPlayers = players.filter(player => player.team_id === team_id);

    const average_kill_elo = teamPlayers.reduce((acc, player) => acc + player.elo, 0) / teamPlayers.length;
    const average_sportsmanship_elo = teamPlayers.reduce((acc, player) => acc + player.sportsmanship_elo, 0) / teamPlayers.length;
    const average_objective_elo = teamPlayers.reduce((acc, player) => acc + player.objective_elo, 0) / teamPlayers.length;
    const average_consistency_elo = teamPlayers.reduce((acc, player) => acc + player.consistency_elo, 0) / teamPlayers.length;
    const average_aggression_elo = teamPlayers.reduce((acc, player) => acc + player.aggression_elo, 0) / teamPlayers.length;
    const elo_average = [average_kill_elo, average_sportsmanship_elo, average_objective_elo, average_consistency_elo, average_aggression_elo].reduce((acc, elo) => acc + elo, 0) / 5;
    const elo_variance = [average_kill_elo, average_sportsmanship_elo, average_objective_elo, average_consistency_elo, average_aggression_elo].reduce((acc, elo) => acc + Math.pow(elo - elo_average, 2), 0) / 5;

    const combined_skill_elo = (team.elo * 3 + average_kill_elo * 2 + average_sportsmanship_elo + average_objective_elo + average_consistency_elo + average_aggression_elo) / 9;
    let elo_average_distance = 0;
    let times = 0;
    for (const player1 of players) {
        for (const player2 of players) {
            if (player2.id === player1.id) continue;
            elo_average_distance += distance(toList(player1), toList(player2));
            times++;
        }
    }
    elo_average_distance /= times;

    return {
        average_kill_elo,
        average_sportsmanship_elo,
        average_objective_elo,
        average_consistency_elo,
        average_aggression_elo,
        elo_average,
        elo_variance,
        elo_average_distance,
        combined_skill_elo
    };
}
function toList(player: any) {
    return [player.elo, player.sportsmanship_elo, player.objective_elo, player.consistency_elo, player.aggression_elo];
}
function distance(a: number[], b: number[]) {
    if (a.length !== b.length) new Error("No");
    return Math.sqrt(a.reduce((acc, val, index) => acc + Math.pow(val - b[index], 2), 0));
}