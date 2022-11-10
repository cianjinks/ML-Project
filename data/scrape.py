import os
import requests
import json
from dotenv import load_dotenv
# Put your API key in a .env file as RIOT_KEY=<your api key>
from ratelimiter import RateLimiter

# Retrieve a player's `puuid` given their `region`, `gameName` and `tagLine`
def get_puuid(api_key: str, region: str, gameName: str, tagLine: str):
    url = f"https://{region}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{gameName}/{tagLine}"
    headers = {"X-Riot-Token": api_key}
    response = requests.get(url, headers=headers)
    json_data = response.json()
    if json_data["puuid"]:
        return json_data["puuid"]
    return ""

# Retrieve a list of match IDs for a given player `puuid`. The default parameters will return the most recent 20 solo/duo ranked matches.
# A list of queue types is found here: https://static.developer.riotgames.com/docs/lol/queues.json
# 420 is the id for solo/duo ranked. If we left it blank we would also get flex ranked games.
def get_match_ids(api_key: str, region: str, puuid: str, queue: int=420, match_type: str="ranked", count: str=20):
    url = f"https://{region}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids"
    params = {
        "queue": queue,
        "type": match_type,
        "count": count,
    }
    headers = {"X-Riot-Token": api_key}
    response = requests.get(url, headers=headers)
    json_data = response.json()
    if json_data:
        return json_data
    return []

# Get json data about a given match `match_id` for a given `region`
def get_match(api_key: str, region: str, match_id: str):
    url = f"https://{region}.api.riotgames.com/lol/match/v5/matches/{match_id}"
    headers = {"X-Riot-Token": api_key}
    response = requests.get(url, headers=headers)
    json_data = response.json()
    return json_data

def write_json_to_file(json_data, path: str):
    with open(path, "w+") as file:
        json.dump(json_data, file)

# Given a player `start_puuid` search through their 10 most recent ranked solo/duo matches.
# BFS search through the players in those matches most recent 10.
# Maintains a set of match IDs to avoid duplicate match traversal.
# Ensures that the 100 requests per 2 minutes limit is not exceeded.
def recurse_matches(api_key: str, region: str, start_puuid: str):
    seen_match_ids = {}
    queue = []
    rate_limiter = RateLimiter(max_calls=100, period=120)

    # Add the start players matches to the queue
    player_match_list = get_match_ids(api_key, region, start_puuid, count=10)
    for match_id in player_match_list:
        queue.append(new_match_id)

        while len(queue) > 0:
            match_id = queue.pop(0)

            # Skip matches we have seen before
            if match_id in seen_match_ids:
                continue
            seen_match_ids.add(match_id)

            # Retrieve match data and write out to file `/json/{match_id}.json`
            with rate_limiter:
                match_json_data = get_match(api_key, region, match_id)
            write_json_to_file(match_json_data, f"{os.path.dirname(os.path.realpath(__file__))}/json/{match_id}.json")

            # Add players from that match to the queue
            if match_json_data["metadata"]:
                if match_json_data["metadata"]["participants"]:
                    for player in match_json_data["metadata"]["participants"]:
                        with rate_limiter:
                            player_match_list = get_match_ids(api_key, region, player, count=10)
                        for new_match_id in player_match_list:
                            queue.append(new_match_id)

def main():
    api_key = os.environ["RIOT_KEY"]
    
    puuid = get_puuid(api_key, "europe", "HobbesOS", "0000")
    if puuid:
        match_ids = get_match_ids(api_key, "europe", puuid)
        for match_id in match_ids:
            match_data = get_match(api_key, "europe", match_id)
            write_json_to_file(match_data, f"{os.path.dirname(os.path.realpath(__file__))}/json/{match_id}.json")

if __name__ == "__main__":
    load_dotenv()
    main()