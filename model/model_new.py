import json
from os import listdir
from os.path import isfile, join

def get_files(mypath: str):
    return [f for f in listdir(mypath) if isfile(join(mypath, f))]

def read_file(filename: str):
    f = open(filename, "r")
    return json.load(f)

# Convert's a player's rank (tier) to a number
# Many players have tier UNKNOWN because they haven't gotten a rank yet, so this is 0
TIER_MAP = {
    "IRON": 1,
    "BRONZE": 2,
    "SILVER": 3,
    "GOLD": 4,
    "PLATINUM": 5,
    "DIAMOND": 6,
    "MASTER": 7,
    "GRANDMASTER": 8,
    "CHALLENGER": 9,
    "Unknown": 0
}
def convert_tier(tier: str):
    if tier in TIER_MAP:
        return TIER_MAP[tier]

    print(f"[ERROR] Player has invalid tier: {tier}")
    return 0

# Convert a player's subrank (ex: Diamond 2) to a number
RANK_MAP = {
    "I": 1,
    "II": 2,
    "III":  3,
    "IV": 4,
    -1: 0
}
def convert_rank(rank):
    if rank in RANK_MAP:
        return RANK_MAP[rank]

    print(f"[ERROR] Player has invalid rank: {rank}")
    return 0

# Get player offset in the features array based on their team and position
def get_player_offset(team_id: int, team_position: str):
    offset = 0
    if team_id == 200: # Red
        offset += 50
    elif team_id != 100:
        print(f"[ERROR] Player has unknown team id: {team_id}")

    if team_position == "TOP":
        offset += 0 * FEATURES_PER_PLAYER
    elif team_position == "JUNGLE":
        offset +=  1 * FEATURES_PER_PLAYER
    elif team_position == "MIDDLE":
        offset +=  2 * FEATURES_PER_PLAYER
    elif team_position == "BOTTOM":
        offset +=  3 * FEATURES_PER_PLAYER
    elif team_position == "UTILITY":
        offset +=  4 * FEATURES_PER_PLAYER
    else:
        print(f"[ERROR] Player has invalid lane position: {team_position}")

    return offset


FEATURES_PER_PLAYER = 10
def get_data():
    features = []
    classification = []

    matches = get_files("../data/json")
    for match in matches:
        match_json = read_file("../data/json/" + match)

        # Order of players: B Top, Jungle, Mid, ADC, Supp, R Top, Jungle, Mid, ADC, Supp
        # Order of features per player: Champion, Tier, Rank, LP, Winrate, Average Kills, Average Deaths, Champion Mastery
        match_features = [None] * 10 * FEATURES_PER_PLAYER # 10 players * 10 features

        winning_team = 100
        match_players = match_json["info"]["participants"]
        match_extra_player_data = match_json["customParticipantData"]
        for player in match_players:
            player_team_id = player["teamId"]
            player_team_position = player["teamPosition"]
            player_offset = get_player_offset(player_team_id, player_team_position)
            player_puuid = player["puuid"]
            player_stats = match_extra_player_data[player_puuid]["stats"]
            player_mastery = match_extra_player_data[player_puuid]["mastery"]

            player_champion = player["championId"]
            player_tier = convert_tier(player_stats["tier"])
            player_rank = convert_rank(player_stats["rank"])
            player_lp = player_stats["leaguePoints"]
            player_wins = player_stats["wins"]
            player_losses = player_stats["losses"]
            player_average_kills = 0
            player_average_deaths = 0
            player_average_assists = 0
            player_champion_mastery = player_mastery["championPoints"]
            player_win = player["win"]

            match_features[player_offset + 0] = player_champion
            match_features[player_offset + 1] = player_tier
            match_features[player_offset + 2] = player_rank
            match_features[player_offset + 3] = player_lp
            match_features[player_offset + 4] = player_wins
            match_features[player_offset + 5] = player_losses
            match_features[player_offset + 6] = player_average_kills
            match_features[player_offset + 7] = player_average_deaths
            match_features[player_offset + 8] = player_average_assists
            match_features[player_offset + 9] = player_champion_mastery

            if player_win:
                winning_team = player_team_id

        features.append(match_features)
        classification.append(winning_team)

    return features, classification

def main():
    X, Y = get_data()

if __name__ == "__main__":
    main()