from sklearn.metrics import classification_report
from sklearn.dummy import DummyClassifier
from load_data import get_data

FEATURES_PER_PLAYER = 10

def champion_mastery_classifier(Xtest):
    preds = []
    for match_index, match in enumerate(Xtest):
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


if __name__ == "__main__":
    features, classification = get_data("data/json/", 20840)

    baseline(features, classification)

    

