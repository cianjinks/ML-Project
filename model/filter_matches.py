FEEDER_DEATH_THRESHOLD = 20
GAME_VERSION = "12.22.479.5277"

def filter_match_data(match_json):
    match_players = match_json["info"]["participants"]

    if match_json["info"]["gameVersion"] != GAME_VERSION:
        return False

    if len(match_players) < 10:
        return False

    for player in match_players:
        if player["deaths"] >= FEEDER_DEATH_THRESHOLD:
            return False

        if player["gameEndedInEarlySurrender"]:
            return False

        if player["teamPosition"] not in ["MIDDLE", "TOP", "JUNGLE", "BOTTOM", "UTILITY"]:
            return False

    return True



