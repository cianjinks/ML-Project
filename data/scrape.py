import os
import requests
import json
import time
from dotenv import load_dotenv
# Put your API key in a .env file as RIOT_KEY=<your api key>

# Retrieve a player's `puuid` given their `region`, `gameName` and `tagLine`

request_window_limit_1 = []
request_window_limit_120 = []

MAX_QUEUE_SIZE = 180

def update_time_windows():
    global request_window_limit_1
    global request_window_limit_120

    current_time = time.time()
    last_1 = current_time -  1
    last_120 = current_time - 120

    new_request_window_limit_1 = []
    new_request_window_limit_120 = []

    for t in request_window_limit_1:
        if t >= last_1:
            new_request_window_limit_1.append(t)

    for t in request_window_limit_120:
        if t >=last_120:
            new_request_window_limit_120.append(t)

    request_window_limit_1 = new_request_window_limit_1
    request_window_limit_120 = new_request_window_limit_120


def block_execution():
    global request_window_limit_1
    global request_window_limit_120
    return len(request_window_limit_120) >= 95 or len(request_window_limit_1) >= 18

def append_moment():
    global request_window_limit_1
    global request_window_limit_120
    current = time.time()
    request_window_limit_1.append(current)
    request_window_limit_120.append(current)
    print(f"Sent a request: {current}")

def rate_limit():
    first = True
    while block_execution():
        update_time_windows()
        if first:
            print("Waiting...")
            first = False

def get_puuid(api_key: str, summonerName: str):
   
    url = f"https://euw1.api.riotgames.com/lol/summoner/v4/summoners/by-name/{summonerName}"
    headers = {"X-Riot-Token": api_key}

    rate_limit()
    response = requests.get(url, headers=headers)

    append_moment()
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

    rate_limit()
    response = requests.get(url, headers=headers, params=params)
    append_moment()
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

    rate_limit()
    response = requests.get(url, headers=headers)
    append_moment()
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
            print(f"Start match: {start_match_id}, match_id: {current}, "
                    f"progress: {matches_fetched}/{matches_to_be_fetched}, queue: {len(queue)}")

            if len(queue) < max_queue_size:
                if "participants" in match_json_data["metadata"] and match_json_data["metadata"]["participants"]:
                    for player in match_json_data["metadata"]["participants"]:
                        player_match_list = []
                        while not player_match_list:
                            player_match_list = get_match_ids(api_key, region, player, count=2)
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
    api_key = os.environ["RIOT_KEY"]

    # players in increasing order of their skill
    players = [
        ("Sauromat", "Iron 4"),
        ("Hungardt", "Bronze 3"),
        ("Ebbo", "Silver 2"),
        ("TheBardussy", "Gold 4"),
        ("123trebor", "Platinum 4"),
        ("Seojunny", "Diamond 1"),
        ("Lοtuss", "Master 500"),
        ("twitchtvELOSANTA", "Grandmaster 700"),
        ("Agurin", "Challenger 1700"),
    ]

    for player_name, _ in players:
        print(player_name)
        puuid = get_puuid(api_key, player_name)

        if puuid:
            match_ids = get_match_ids(api_key, "europe", puuid, count=1)     
            if match_ids:
                start_match_id = match_ids[0]
                recurse_matches_v2(api_key, "europe", start_match_id, 20)

if __name__ == "__main__":
    load_dotenv()
    main()
