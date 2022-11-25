import os
import requests
import json
from dotenv import load_dotenv
from rate_limiter import RateLimiter

load_dotenv()
api_key = os.environ["RIOT_KEY"]

r = RateLimiter()


# get mastery for a player given the champion
def fetch_mastery(encrypted_summoner_id, champion_id):
    url = (f"https://euw1.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-summoner/"
            f"{encrypted_summoner_id}/by-champion/{champion_id}")
    headers = {"X-Riot-Token": api_key}

    r.rate_limit()
    response = requests.get(url, headers=headers)
    r.append_moment()

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
def get_player_stats(encrypted_summoner_id):
    url = f"https://euw1.api.riotgames.com/lol/league/v4/entries/by-summoner/{encrypted_summoner_id}"
    headers = {"X-Riot-Token": api_key}

    r.rate_limit()
    response = requests.get(url, headers=headers)
    r.append_moment()
    stats = {"tier": "Unknown", "rank": -1, "leaguePoints": -1, "wins": -1, "losses": -1}

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


def read_file(filename: str):
    f = open(filename, "r")
    return json.load(f)

def parse_player_data(filename):
    player_data = read_file(filename)

    extra_player_data = {}

    count = 0

    for puuid, data in player_data.items():
        encrypted_summoner_id = data["encryptedSummonerId"]
        champion_ids = data["championsPlayed"]

        player_stats = get_player_stats(encrypted_summoner_id)

        champion_stats = {}

        for champion_id in champion_ids:
            champion_stats[champion_id] = fetch_mastery(encrypted_summoner_id, champion_id)

        extra_player_data[puuid] = {
            "stats": player_stats,
            "championMastery": champion_stats
        }
        count+=1

        print(f"Processed: {count}/{len(player_data)} players")

    with open("extra_player_data.json", "w+") as outfile:
        json.dump(extra_player_data, outfile)
        

def test():
    champion_id = 34
    encrypted_summoner_id = "XT6zAd8EriCUWwvsTr6v27-XiHk4djIX6YTVaxMqyAEvN7Y"
    print(get_player_stats(encrypted_summoner_id))
    print(fetch_mastery(encrypted_summoner_id, champion_id))

if __name__ == "__main__":
    parse_player_data("player_data.json")
