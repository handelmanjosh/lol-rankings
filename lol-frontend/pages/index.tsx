import BasicButton from '@/components/BasicButton';
import ELO from '@/components/ELO';
import PieChart, { PieChartProps } from '@/components/PieChart';
import Search from '@/components/Search';
import { calculateTeamStats } from '@/components/utils';
import players from '@/data/players.json';
import teams from '@/data/teams.json';
import { useState } from 'react';

export default function Home() {
  const [error, setError] = useState<string | null>(null);
  const [primaryElos, setPrimaryElos] = useState<[string, number][]>([]);
  const [secondaryElos, setSecondaryElos] = useState<[string, number][]>([]);
  const [eloPies, setEloPies] = useState<PieChartProps[]>([]);
  const [winPercentage, setWinPercentage] = useState<number | null>(null);
  const searchPlayer = (s: string) => {
    const player = players.find(p => p.id === s);
    if (!player) {
      setError('Player not found');
      return;
    } else {
      setError(null);
    }

    setPrimaryElos(
      [
        ["Kill ELO", player.elo], ["Sportsmanship ELO", player.sportsmanship_elo],
        ["Objective ELO", player.objective_elo], ["Aggression ELO", player.aggression_elo], ["Consistency ELO", player.consistency_elo]
      ]
    );
    const eloPieArray = [{
      data: {
        labels: ["Kill ELO", "Sportsmanship ELO", "Objective ELO", "Aggression ELO", "Consistency ELO"],
        datasets: [
          {
            data: [player.elo, player.sportsmanship_elo, player.objective_elo, player.aggression_elo, player.consistency_elo],
            backgroundColor: [
              '#FF6384',
              '#36A2EB',
              '#FFCE56',
              '#9900cc',
              '#33cc33'
            ],
          }
        ]
      },
      options: {
        plugins: {
          datalabels: {
            color: "black",
            formatter: function (value: any, context: any) {
              return context.chart.data.labels[context.dataIndex];
            }
          }
        }
      },
      title: "Player ELO Breakdown"
    }];
    const team = teams.find(t => t.id == player.team_id);
    console.log(team);
    if (team) {
      const teamPlayers = players.filter(p => p.team_id === team.id);
      const teamKillElo = teamPlayers.reduce((a, b) => a + b.elo, 0);
      eloPieArray.push({
        data: {
          labels: ["Player", "Rest of Team"],
          datasets: [
            {
              data: [player.elo, teamKillElo - player.elo],
              backgroundColor: [
                "#0080FF",
                "#FF3333"
              ],
            }
          ]
        },
        options: {
          plugins: {
            datalabels: {
              color: "black",
              formatter: function (value: any, context: any) {
                return context.chart.data.labels[context.dataIndex];
              }
            }
          }
        },
        title: "Player VS Team ELO"
      });
    }
    setEloPies(eloPieArray);
    setWinPercentage(player.wins / player.games_played * 100);
    setSecondaryElos([]);
  };
  const searchTeam = (s: string) => {
    const team = teams.find(t => t.id === s);
    if (!team) {
      setError('Team not found');
      return;
    } else {
      setError(null);
    }
    const teamPlayers = players.filter(p => p.team_id === team.id);
    const teamKillElo = teamPlayers.reduce((a, b) => a + b.elo, 0) / teamPlayers.length;
    const teamSportsmanshipElo = teamPlayers.reduce((a, b) => a + b.sportsmanship_elo, 0) / teamPlayers.length;
    const teamObjectiveElo = teamPlayers.reduce((a, b) => a + b.objective_elo, 0) / teamPlayers.length;
    const teamAggressionElo = teamPlayers.reduce((a, b) => a + b.aggression_elo, 0) / teamPlayers.length;
    const teamConsistencyElo = teamPlayers.reduce((a, b) => a + b.consistency_elo, 0) / teamPlayers.length;

    setPrimaryElos([["Team ELO", team.elo]]);
    setEloPies([{
      data: {
        labels: ["Team ELO", "Kill ELO", "Sportsmanship ELO", "Objective ELO", "Aggression ELO", "Consistency ELO"],
        datasets: [
          {
            data: [team.elo, teamKillElo, teamSportsmanshipElo, teamObjectiveElo, teamAggressionElo, teamConsistencyElo],
            backgroundColor: [
              '#FF6384',
              '#36A2EB',
              '#FFCE56',
              '#9900cc',
              '#33cc33',
              '#ff9900'
            ],
          }
        ]
      },
      options: {
        plugins: {
          datalabels: {
            color: "black",
            formatter: function (value, context) {
              return context.chart.data.labels[context.dataIndex];
            }
          }
        }
      },
      title: "Team ELO Breakdown"
    }]);
    setWinPercentage(team.wins / team.games_played * 100);
    const stats = calculateTeamStats(s);
    if (stats) {
      const transformedData: [string, number][] = Object.entries(stats).map(([key, value]): [string, number] => {
        // Convert the key to the desired label
        const label = key
          .split('_')  // Split on underscore
          .map(word => word.charAt(0).toUpperCase() + word.slice(1))
          .join(" ");
        return [label, value];
      });
      setSecondaryElos(transformedData);
    }
  };
  return (
    <div className="w-screen flex flex-col justify-center items-center p-4">
      <div className="flex flex-row justify-start gap-6 items-center w-full">
        <p className="text-xl font-bold">LOL Stats Online</p>
        <BasicButton onClick={() => window.location.href = "/methods"} text="API" />
        <div className="flex flex-row justify-center items-center gap-2 flex-grow">
          <Search onSearch={searchPlayer} data={players} placeholder="Search for Players (id)" />
          <Search onSearch={searchTeam} data={teams} placeholder="Search for Teams (id)" />
        </div>
      </div>
      {error ?
        <p className="text-red-500 font-bold text-2xl">{error}</p>
        :
        <div className="flex flex-col justify-center items-center w-full">
          <div className="flex flex-row justify-center items-center gap-4">
            {primaryElos.map(([name, value]: [string, number], i: number) => (
              <ELO key={i} name={name} value={value} />
            ))}
          </div>
          <div className="flex flex-row justify-center items-center gap-2">
            {eloPies && eloPies.length > 0 && eloPies.map((eloPie, i) => (<PieChart key={i} {...eloPie} />))}
          </div>
          {winPercentage !== null && !Number.isNaN(winPercentage) && <p className="text-lg font-bold">{`Win percentage: ${Math.round(winPercentage)}%`}</p>}
          <div className="flex flex-row justify-center items-center">
            {secondaryElos.map(([name, value]: [string, number], i: number) => (
              <ELO key={i} name={name} value={value} />
            ))}
          </div>
        </div>
      }
    </div>
  );
}
