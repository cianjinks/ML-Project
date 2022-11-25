import os
import requests
import json
from dotenv import load_dotenv
from rate_limiter import RateLimiter

load_dotenv()
api_keys = [os.environ["RIOT_KEY_1"], os.environ["RIOT_KEY_2"]]

r = RateLimiter()

for api_key in api_keys:
    r.register_api_key(api_key)

def read_file(filename: str):
    f = open(filename, "r")
    return json.load(f)

def parse_player_data(filename):
    player_data = read_file(filename)

    extra_player_data = {}

    count = 0

    api_key_index = 0

    for puuid, data in player_data.items():
        encrypted_summoner_id = data["encryptedSummonerId"]
        champion_ids = data["championsPlayed"]

        api_key = api_keys[api_key_index]
        print(f"Api key used: {api_key}")

        api_key_index+=1
        api_key_index = api_key_index % len(api_keys)

        player_stats = get_player_stats(encrypted_summoner_id, api_key)

        champion_stats = {}

        for champion_id in champion_ids:
            champion_stats[champion_id] = fetch_mastery(
                encrypted_summoner_id, champion_id, api_key)

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
