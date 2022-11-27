# This script creates a baseline predictor model and logistc regression model for the 100 dataset.
# A few baseline predictor ideas:
    # Most frequent
    # Team total ELO
    # Team total champion mastery

import json
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression

MATCH_DATA_FILE = "small_dataset/match_data_100.json"
PLAYER_DATA_FILE = "small_dataset/player_data_100.json"
EXTRA_PLAYER_DATA_FILE = "small_dataset/extra_player_data_100.json"
FEATURES_PER_PLAYER = 10

# THESE SHOULD BE DICTIONARIES

# Convert lane position to offset into features array
def get_position_feature_offset(position: str):
    if position == "TOP":
        return 0 * FEATURES_PER_PLAYER
    elif position == "JUNGLE":
        return 1 * FEATURES_PER_PLAYER
    elif position == "MIDDLE":
        return 2 * FEATURES_PER_PLAYER
    elif position == "BOTTOM":
        return 3 * FEATURES_PER_PLAYER
    elif position == "UTILITY":
        return 4 * FEATURES_PER_PLAYER
    print(f"[ERROR] Player has invalid lane position: {position}")
    return 0

def convert_tier(tier: str):
    if tier == "IRON":
        return 0
    elif tier == "BRONZE":
        return 1
    elif tier == "SILVER":
        return 2
    elif tier == "GOLD":
        return 3
    elif tier == "PLATINUM":
        return 4
    elif tier == "DIAMOND":
        return 5
    elif tier == "MASTER":
        return 6
    elif tier == "GRANDMASTER":
        return 7
    elif tier == "CHALLENGER":
        return 8

    print(f"[ERROR] Player has invalid tier: {tier}")
    return 0

def convert_rank(rank: str):
    if rank == "I":
        return 1
    elif rank == "II":
        return 2
    elif rank == "III":
        return 3
    elif rank == "IV":
        return 4
    
    print(f"[ERROR] Player has invalid rank: {rank}")
    return 0

def get_json_data(filename: str):
    json_data = {}
    with open(filename) as f:
        json_data = json.load(f)
        f.close()
    return json_data

def get_data():
    match_data = get_json_data(MATCH_DATA_FILE)
    player_data = get_json_data(PLAYER_DATA_FILE)
    extra_player_data = get_json_data(EXTRA_PLAYER_DATA_FILE)

    features = []
    classification = []

    for match_id, match in match_data.items():
        # Order of players: B Top, Jungle, Mid, ADC, Supp, R Top, Jungle, Mid, ADC, Supp
        # Order of features per player: Champion, Tier, Rank, LP, Winrate, Average Kills, Average Deaths, Champion Mastery
        match_features = [None] * 10 * FEATURES_PER_PLAYER # 10 features per player

        # preprocess the draft so I can access by puuid
        draft = {}
        for d in match["draft"]:
            draft[d["puuid"]] = d

        # TODO: This will be incorrect if players swapped roles!!!!!
        for index, player in enumerate(match["puuids"]):

            player_draft = draft[player]
            player_info = player_data[player]
            extra_player_info = extra_player_data[player]
            
            # position = player_draft["position"]

            match_features[(FEATURES_PER_PLAYER * index) + 0] = player_draft["championId"]
            match_features[(FEATURES_PER_PLAYER * index) + 1] = convert_tier(extra_player_info["stats"]["tier"])
            match_features[(FEATURES_PER_PLAYER * index) + 2] = convert_rank(extra_player_info["stats"]["rank"])
            match_features[(FEATURES_PER_PLAYER * index) + 3] = extra_player_info["stats"]["leaguePoints"]
            match_features[(FEATURES_PER_PLAYER * index) + 4] = extra_player_info["stats"]["wins"]
            match_features[(FEATURES_PER_PLAYER * index) + 5] = extra_player_info["stats"]["losses"]
            match_features[(FEATURES_PER_PLAYER * index) + 6] = player_info["averageKills"]
            match_features[(FEATURES_PER_PLAYER * index) + 7] = player_info["averageDeaths"]
            match_features[(FEATURES_PER_PLAYER * index) + 8] = player_info["averageAssists"]
            match_features[(FEATURES_PER_PLAYER * index) + 9] = extra_player_info["championMastery"][str(player_draft["championId"])]["championPoints"]
        
        features.append(match_features)
        classification.append(match["winningTeam"])

    return features, classification

def champion_mastery_classifier(Xtest):
    preds = []
    for match in Xtest:
        blue_team_mastery = 0
        red_team_mastery = 0

        player = 0
        while player < 5:
            blue_team_mastery += match[(FEATURES_PER_PLAYER * player) + 9]
            player += 1
        
        while player < 10:
            red_team_mastery += match[(FEATURES_PER_PLAYER * player) + 9]
            player += 1

        if blue_team_mastery > red_team_mastery:
            preds.append(100)
        else:
            preds.append(200)
    
    return preds


def baseline(X, Y):
    print("Running most frequent classifier...")
    dummy = DummyClassifier(strategy="most_frequent")
    dummy.fit(X, Y)
    preds = dummy.predict(X)
    print(classification_report(Y, preds))

    print("Running total champion mastery classifier...")
    preds2 = champion_mastery_classifier(X)
    print(classification_report(Y, preds2))

def logistic_regiression(X, Y):
    # Split the data into training and test sets with 80/20 ratio
    Xtrain, Xtest, ytrain, ytest = train_test_split(X, Y, test_size=0.2)
    
    print("Running logistic regression classifier...")
    model = LogisticRegression(solver="liblinear", penalty="l1", C=0.1, max_iter=10000)
    model.fit(Xtrain, ytrain)
    preds = model.predict(Xtest)
    print(classification_report(ytest, preds))

def main():
    X, Y = get_data()
    baseline(X, Y)
    logistic_regiression(X, Y)

if __name__ == "__main__":
    main()