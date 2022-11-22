import json
from os import listdir
from os.path import isfile, join

def get_files(mypath: str):
    return [f for f in listdir(mypath) if isfile(join(mypath, f))]

def read_file(filename: str):
    f = open(filename, "r")
    return json.load(f)

def post_process():
    files = get_files("json")

    # stored by match_id
    # version of the game
    # each participant puuid
    # for each participant team, position, champion id
    # who won
    match_data = {}

    # stored by puuid
    # encrypted id
    # average kills 
    # average deaths
    # average assists
    # champions played
    # average total minions killed
    player_data = {}

    looking_at = 0

    for filename in files:
        looking_at += 1
        if filename == ".gitignore":
            continue

        print(f"Looking at: {filename}, {looking_at}/{len(files)}")
        json_rep = read_file("json/" + filename)
        match_id = json_rep["metadata"]["matchId"]

        if match_id not in match_data:         
            game_version = json_rep["info"]["gameVersion"]
            participant_puuids = json_rep["metadata"]["participants"]
            
            winning_team = -1

            draft = []
            for participant in json_rep["info"]["participants"]:
                
                if participant["win"]:
                    winning_team = participant["teamId"]

                puuid = participant["puuid"]
                champion_id = participant["championId"]
                position = participant["teamPosition"]
                team_id = participant["teamId"]
                encrypted_summoner_id = participant["summonerId"]
                kills = participant["kills"]
                deaths = participant["deaths"]
                assits = participant["assists"]

                draft.append(
                {
                    "puuid": puuid,
                    "championId": champion_id,
                    "position": position, 
                    "teamId": team_id
                })

                if puuid in player_data:
                    match_count = player_data[puuid]["matchCount"]
                    averageKills = player_data[puuid]["averageKills"]
                    averageDeaths = player_data[puuid]["averageDeaths"]
                    averageAssists = player_data[puuid]["averageAssists"]

                    player_data[puuid]["averageKills"] = (
                        match_count * averageKills + kills) / (match_count + 1)
                    player_data[puuid]["averageDeaths"] = (
                        match_count * averageDeaths + kills) / (match_count + 1)
                    player_data[puuid]["averageAssists"] = (
                        match_count * averageAssists + kills) / (match_count + 1)
                    player_data[puuid]["matchCount"] += 1

                else:
                    player_data[puuid] = {
                        "encryptedSummonerId": encrypted_summoner_id,
                        "averageKills": kills,
                        "averageDeaths": deaths,
                        "averageAssists": assits,
                        "championsPlayed": [champion_id],
                        "matchCount": 1,
                    }


            match_data[match_id] = {
                "gameVersion": game_version,
                "puuids": participant_puuids,
                "draft": draft,
                "winningTeam": winning_team
            }
    
    with open("match_data.json", "w+") as outfile:
        json.dump(match_data, outfile)
    
    with open("player_data.json", "w+") as outfile:
        json.dump(player_data, outfile)


if __name__ == "__main__":
    post_proces()

