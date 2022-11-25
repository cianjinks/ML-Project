import os
import sys
import requests
import json
import time
from dotenv import load_dotenv
from rate_limiter import RateLimiter

# Put your API key in a .env file as RIOT_KEY=<your api key>
# Retrieve a player's `puuid` given their `region`, `gameName` and `tagLine`

start_time = time.time()

SECONDS_IN_20_HOURS = 72000

r = RateLimiter()

MAX_QUEUE_SIZE = 180
total_matches_fetched = 0
total_matches_to_be_fetched = -1

# get mastery for a player given the champion
def fetch_mastery(encrypted_summoner_id, champion_id, api_key):
    url = (f"https://euw1.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-summoner/"
           f"{encrypted_summoner_id}/by-champion/{champion_id}")
    headers = {"X-Riot-Token": api_key}

    r.rate_limit(api_key)
    response = requests.get(url, headers=headers)
    r.append_moment(api_key)

    stats = {"championLevel": -1, "championPoints": -1, "lastPlayTime": -1}

    if response.ok:
        json_data = response.json()
        stats["championLevel"] = json_data["championLevel"]
        stats["championPoints"] = json_data["championPoints"]
        stats["lastPlayTime"] = json_data["lastPlayTime"]

    else:
        print(response.text)

    return stats

# get player's rank, lp, wins, losses
def get_player_stats(encrypted_summoner_id, api_key):
    url = f"https://euw1.api.riotgames.com/lol/league/v4/entries/by-summoner/{encrypted_summoner_id}"
    headers = {"X-Riot-Token": api_key}

    r.rate_limit(api_key)
    response = requests.get(url, headers=headers)
    r.append_moment(api_key)
    stats = {"tier": "Unknown", "rank": -1,
             "leaguePoints": -1, "wins": -1, "losses": -1}

    if response.ok:
        json_data = response.json()
        for queue_info in json_data:
            if queue_info["queueType"] == "RANKED_SOLO_5x5":
                stats["tier"] = queue_info["tier"]
                stats["rank"] = queue_info["rank"]
                stats["leaguePoints"] = queue_info["leaguePoints"]
                stats["wins"] = queue_info["wins"]
                stats["losses"] = queue_info["losses"]
    else:
        print(response.text)

    return stats

def get_puuid(api_key: str, summonerName: str):
   
    url = f"https://euw1.api.riotgames.com/lol/summoner/v4/summoners/by-name/{summonerName}"
    headers = {"X-Riot-Token": api_key}

    r.rate_limit(api_key)
    response = requests.get(url, headers=headers)
    r.append_moment(api_key)

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

    r.rate_limit(api_key)
    response = requests.get(url, headers=headers, params=params)
    r.append_moment(api_key)
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

    r.rate_limit(api_key)
    response = requests.get(url, headers=headers)
    r.append_moment(api_key)
    json_data = response.json()

    participants_data = {}
    
    for participant in json_data["info"]["participants"]:
        puuid = participant["puuid"]
        champion_id = participant["championId"]
        encrypted_summoner_id = participant["summonerId"]

        stats = get_player_stats(encrypted_summoner_id, api_key)
        mastery = fetch_mastery(
            encrypted_summoner_id, champion_id, api_key)

        participants_data[puuid] = {
            "stats": stats,
            "mastery": mastery,
            "championId": champion_id,
            "encryptedSummonerId": encrypted_summoner_id
        }

    json_data["customParticipantData"] = participants_data

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
    global start_time

    visited = set()
    queue = [start_match_id]
    matches_fetched = 0

    max_queue_size = min(matches_to_be_fetched, MAX_QUEUE_SIZE)

    while len(queue) > 0 and matches_fetched < matches_to_be_fetched:
        current_time = time.time()

        if current_time - start_time > SECONDS_IN_20_HOURS:
            break

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
    r.register_api_key(api_key)

    # players in increasing order of their skill
    players = [
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
    with open('logs.txt', 'w+') as sys.stdout:
        main()
