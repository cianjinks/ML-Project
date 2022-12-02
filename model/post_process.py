import json
from os import listdir
from os.path import isfile, join
from filter_matches import filter_match_data

def get_files(mypath: str):
    return [f for f in listdir(mypath) if isfile(join(mypath, f))]

def read_file(filename: str):
    f = open(filename, "r")
    return json.load(f)

def post_process(path):
    files = get_files(path)
    player_data = {}

    looking_at = 0

    for filename in files:
        looking_at += 1
        if filename == ".gitignore":
            continue

        print(f"Looking at: {filename}, {looking_at}/{len(files)}")
        json_rep = read_file(path + filename)

        if not filter_match_data(json_rep):
            continue
        
        if len(json_rep["info"]["participants"]) < 10:
            pass
        
        for participant in json_rep["info"]["participants"]:

            puuid = participant["puuid"]
            kills = participant["kills"]
            deaths = participant["deaths"]
            assits = participant["assists"]

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
                    "averageKills": kills,
                    "averageDeaths": deaths,
                    "averageAssists": assits,
                    "matchCount": 1,
                }

    with open("data/processed_data/player_data.json", "w+") as outfile:
        json.dump(player_data, outfile)


if __name__ == "__main__":
    post_process("data/json/")