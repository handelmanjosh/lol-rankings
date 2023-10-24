import React from 'react';
import { calculateTeamStats } from './utils';
type Team = {
    id: string;
    elo: number;
    wins: number;
    games_played: number;
    name: string;
};

interface TeamWidgetProps {
    team: Team;
}

const TeamWidget: React.FC<TeamWidgetProps> = ({ team }) => {
    const stats = calculateTeamStats(team.id);
    if (stats) {
        return (
            <div className="bg-blue-200 p-4 rounded-lg shadow-md">
                <h3 className="text-xl font-semibold">{team.name}</h3>
                <p>ELO: {stats.combined_skill_elo.toFixed(2)}</p>
            </div>
        );
    } else {
        return (
            <div className="bg-blue-200 p-4 rounded-lg shadow-md">
                <h3 className="text-xl font-semibold">{team.name}</h3>
                <p>ELO: {team.elo.toFixed(2)}</p>
            </div>
        );
    }
};

export default TeamWidget;