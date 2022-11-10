import os
import requests
import json
from dotenv import load_dotenv
# Put your API key in a .env file as RIOT_KEY=<your api key>

def get_puuid(api_key: str, region: str, gameName: str, tagLine: str):
    url = f"https://{region}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{gameName}/{tagLine}"
    headers = {"X-Riot-Token": api_key}
    response = requests.get(url, headers=headers)
    json_data = response.json()
    if json_data["puuid"]:
        return json_data["puuid"]
    return ""

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

def get_match(api_key: str, region: str, match_id: str):
    url = f"https://{region}.api.riotgames.com/lol/match/v5/matches/{match_id}"
    headers = {"X-Riot-Token": api_key}
    response = requests.get(url, headers=headers)
    json_data = response.json()
    return json_data

def write_json_to_file(json_data, path: str):
    with open(path, "w+") as file:
        json.dump(json_data, file)

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