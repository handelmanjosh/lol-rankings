import React from 'react';
type Player = {
    id: string;
    elo: number;
    sportsmanship_elo: number;
    objective_elo: number;
    aggression_elo: number;
    consistency_lo: number;
    wins: number;
    games_played: number;
    champion_kills: number;
    total_damage_taken_100: number;
    total_damage_dealt_100: number;
    total_damage_dealt_to_objectives_100: number;
    total_damage_dealt_to_champions_100: number;
    first_name: string;
    last_name: string;
    handle: string;
    team_id: string;
};

interface PlayerWidgetProps {
    player: Player;
}

const PlayerWidget: React.FC<PlayerWidgetProps> = ({ player }) => {
    return (
        <div className="bg-green-200 p-4 rounded-lg shadow-md">
            <h3 className="text-xl font-semibold">{player.handle} ({player.first_name} {player.last_name})</h3>
            <p>Win %: {Math.round(player.wins / player.games_played)}</p>
            <p>ELO: {player.elo.toFixed(2)}</p>
        </div>
    );
};

export default PlayerWidget;