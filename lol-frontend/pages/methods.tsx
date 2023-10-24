import { useState } from "react";
import teams from "@/data/teams.json";
import tournaments from "@/esports-data/tournaments.json";
import BasicButton from "@/components/BasicButton";
import TeamWidget from "@/components/TeamWidget";
import { calculateTeamStats } from "@/components/utils";


export default function API() {
    const [tournamentId, setTournamentId] = useState<string>("");
    const [stage, setStage] = useState<string>("");
    const [numberOfTeams, setNumberOfTeams] = useState<number>(0);
    const [teamIds, setTeamIds] = useState<string>("");
    const [shownTeams, setShownTeams] = useState<any[]>([]);
    const getTournamentRankings = () => {
        if (!tournamentId) return;
        // @ts-ignore
        const tournament = tournaments.find((t: any) => t.id === tournamentId);
        const result: any[] = [];
        if (tournament) {
            if (stage) {
                const selectedStage = tournament.stages.find((s: any) => s.name === stage);
                if (selectedStage) {
                    for (const section of selectedStage.sections) {
                        for (const match of section.matches) {
                            const team1 = teams.find((t) => t.id === match.teams[0].id);
                            const team2 = teams.find((t) => t.id === match.teams[1].id);
                            team1 && result.push(team1);
                            team2 && result.push(team2);
                        }
                    }
                }
            } else {
                for (const stage of tournament.stages) {
                    for (const section of stage.sections) {
                        for (const match of section.matches) {
                            const team1 = teams.find((t) => t.id === match.teams[0].id);
                            const team2 = teams.find((t) => t.id === match.teams[1].id);
                            team1 && !result.includes(team1) && result.push(team1);
                            team2 && !result.includes(team2) && result.push(team2);
                        }
                    }
                }
            }
        }
        console.log(result);
        setShownTeams(result.filter((t) => t.games_played > 0 && t.elo > 1500).sort((a, b) => {
            let astats = calculateTeamStats(a.id);
            let bstats = calculateTeamStats(b.id);
            if (astats && bstats) {
                return bstats.combined_skill_elo - astats.combined_skill_elo;
            } else {
                return b.elo - a.elo;
            }
        }));
    };
    function getGlobalRankings() {
        if (numberOfTeams < 1) return;
        const teamstats = teams.map((t) => {
            const stats = calculateTeamStats(t.id);
            if (stats) {
                return {
                    ...stats,
                    id: t.id
                };
            } else {
                return {
                    id: t.id,
                    combined_skill_elo: t.elo
                };
            }
        });
        const sorted = teamstats.sort((a, b) => b.combined_skill_elo - a.combined_skill_elo).map((t) => {
            return teams.find((team) => team.id === t.id)!;
        });
        setShownTeams(sorted.splice(0, numberOfTeams));
    }
    function getTeamRankings() {
        const team_ids: string[] = teamIds.split(",").map((t: string) => t.trim());
        console.log(team_ids);
        if (team_ids.length < 1) return;
        const result = teams.filter((t) => team_ids.includes(t.id));
        console.log(result);
        setShownTeams(result.sort((a, b) => {
            let astats = calculateTeamStats(a.id);
            let bstats = calculateTeamStats(b.id);
            if (astats && bstats) {
                return bstats.combined_skill_elo - astats.combined_skill_elo;
            } else {
                return b.elo - a.elo;
            }
        }));
    }
    return (
        <div className="flex flex-col gap-2 justify-center items-center w-screen p-4">
            <div className="flex flex-row justify-center items-center gap-4">
                <p>GET /tournament_rankings/:tournament_id</p>
                <input
                    value={tournamentId}
                    placeholder={"Tournament ID"}
                    onChange={(event: any) => setTournamentId(event.target.value)}
                    className="appearance-none bg-gray-200 outline-none p-2 focus:border-black focus:border rounded-md"
                />
                <input
                    value={stage}
                    placeholder={"Stage"}
                    onChange={(event: any) => setStage(event.target.value)}
                    className="appearance-none bg-gray-200 outline-none p-2 focus:border-black focus:border rounded-md"
                />
                <BasicButton onClick={getTournamentRankings} text="Get Tournament Rankings" />
            </div>
            <div className="flex flex-row justify-center items-center gap-4">
                <p>GET /global_rankings </p>
                <input
                    value={numberOfTeams}
                    placeholder="Number of Teams"
                    onChange={(event: any) => setNumberOfTeams(event.target.value)}
                    className="appearance-none bg-gray-200 outline-none p-2 focus:border-black focus:border rounded-md"
                />
                <BasicButton onClick={getGlobalRankings} text="Get Global Rankings" />
            </div>
            <div className="flex flex-row justify-center items-center gap-4">
                <p>GET /team_rankings/</p>
                <input
                    value={teamIds}
                    placeholder="Team IDs (comma separated)"
                    onChange={(event: any) => setTeamIds(event.target.value)}
                    className="appearance-none bg-gray-200 outline-none p-2 focus:border-black focus:border rounded-md"
                />
                <BasicButton onClick={getTeamRankings} text="Get Team Rankings" />
            </div>
            <div className="grid grid-cols-8 justify-center items-center mt-4 gap-2">
                {shownTeams.map((team, i) => (
                    <TeamWidget key={i} team={team} />
                ))}
            </div>
            <p className="text-red-600 font-bold">Warning! A limited amount of data has been processed. {"(About 1/6 of 2023)"}</p>
        </div>
    );
}


