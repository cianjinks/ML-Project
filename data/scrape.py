import os
import requests
import json
import time
from dotenv import load_dotenv
from rate_limiter import RateLimiter

# Put your API key in a .env file as RIOT_KEY=<your api key>
# Retrieve a player's `puuid` given their `region`, `gameName` and `tagLine`

r = RateLimiter()

MAX_QUEUE_SIZE = 180
total_matches_fetched = 0
total_matches_to_be_fetched = -1

def get_puuid(api_key: str, summonerName: str):
   
    url = f"https://euw1.api.riotgames.com/lol/summoner/v4/summoners/by-name/{summonerName}"
    headers = {"X-Riot-Token": api_key}

    r.rate_limit()
    response = requests.get(url, headers=headers)
    r.append_moment()

    if response.ok:
        json_data = response.json()
        if json_data["puuid"]:
            return json_data["puuid"]
    else:
        print(response.text)
        return ""

# Retrieve a list of match IDs for a given player `puuid`.
# The default parameters will return the most recent 20 solo/duo ranked matches.
# A list of queue types is found here: https://static.developer.riotgames.com/docs/lol/queues.json
# 420 is the id for solo/duo ranked. If we left it blank we would also get flex ranked games.


def get_match_ids(api_key: str, region: str, puuid: str, queue: int = 420,
                  match_type: str = "ranked", count: int = 20):
    url = f"https://{region}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids"
    params = {
        "queue": queue,
        "type": match_type,
        "count": count
    }
    headers = {"X-Riot-Token": api_key}

    r.rate_limit()
    response = requests.get(url, headers=headers, params=params)
    r.append_moment()
    if response.ok:
        json_data = response.json()
        if json_data:
            return json_data
    else:
        return []

# Get json data about a given match `match_id` for a given `region`


def get_match(api_key: str, region: str, match_id: str):
    url = f"https://{region}.api.riotgames.com/lol/match/v5/matches/{match_id}"
    headers = {"X-Riot-Token": api_key}

    r.rate_limit()
    response = requests.get(url, headers=headers)
    r.append_moment()
    json_data = response.json()
    return json_data


def write_json_to_file(json_data, path: str):
    with open(path, "w+") as file:
        json.dump(json_data, file)

# Given a player `start_puuid` search through their 10 most recent ranked solo/duo matches.
# BFS search through the players in those matches most recent 10.
# Maintains a set of match IDs to avoid duplicate match traversal.
# Ensures that the 100 requests per 2 minutes limit is not exceeded.

def recurse_matches_v2(api_key: str, region: str, start_match_id: str, matches_to_be_fetched: int = 20):
    global total_matches_fetched
    global total_matches_to_be_fetched
    visited = set()
    queue = [start_match_id]
    matches_fetched = 0

    max_queue_size = min(matches_to_be_fetched, MAX_QUEUE_SIZE)

    while len(queue) > 0 and matches_fetched < matches_to_be_fetched:
        current = queue.pop(0)

        if current in visited:
            print(f"Already visited: {current}, skipping!")
            continue
        
        visited.add(current)
        match_json_data = get_match(api_key, region, current)
        
        if "metadata" in match_json_data:
            write_json_to_file(
                match_json_data, f"{os.path.dirname(os.path.realpath(__file__))}/json/{current}.json")
            matches_fetched += 1
            total_matches_fetched+=1
            print(f"Start match: {start_match_id}, match_id: {current}, "
                    f"progress: {total_matches_fetched}/{total_matches_to_be_fetched}, queue: {len(queue)}, matches fetched "
                        f"for the player: {matches_fetched}")

            if len(queue) < max_queue_size:
                if "participants" in match_json_data["metadata"] and match_json_data["metadata"]["participants"]:
                    for player in match_json_data["metadata"]["participants"]:
                        player_match_list = []
                        while not player_match_list:
                            player_match_list = get_match_ids(api_key, region, player, count=10)
                            if len(player_match_list) == 1:
                                print(f"Player only played 1 game in Ranked!")
                                break

                            if player_match_list:
                                for new_match_id in player_match_list:
                                    queue.append(new_match_id)
                            else:
                                print(f"Player match list is empty: {player}!")
                else:
                    print("No participants in response!")
        else:
            print("No metadata in response, trying again!")
            queue.append(current)


def main():
    global total_matches_to_be_fetched

    api_key = os.environ["RIOT_KEY"]

    # players in increasing order of their skill
    players = [
        ("Sköll y Hati", "P1"),
        ("lorenz goes pro", "M 55"),
        ("me no win sorry", "G3"),
        ("F0R" , "S3"),
        ("Obsess", "GM 870"),
        ("ERROR 423", "B2"),
        ("TeLoÉxplico", "I3"),
        ("DonMartin", "D3"),
        ("Nightmares", "chal 1008")
    ]

    match_count = 5000
    total_matches_to_be_fetched = match_count * len(players)

    for player_name, _ in players:
        print(player_name)
        puuid = get_puuid(api_key, player_name)

        if puuid:
            match_ids = get_match_ids(api_key, "europe", puuid, count=1)     
            if match_ids:
                start_match_id = match_ids[0]
                recurse_matches_v2(api_key, "europe",
                                   start_match_id, match_count)

if __name__ == "__main__":
    load_dotenv()
    main()
