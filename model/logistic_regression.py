import numpy as np
import matplotlib.pyplot as plt

from load_data import get_data
from sklearn.metrics import classification_report
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import KFold
from sklearn.metrics import f1_score
from sklearn.metrics import confusion_matrix
from sklearn.metrics import roc_curve

def print_coefficients(model):
    print("Logistic Regression Coefficients:")
    coef_meaning = ["Champion", "Tier", "Rank", "LP", "Wins", "Losses", 
        "Average Kills", "Average Deaths", "Average Assists", "Champion Mastery"]
    coef = model.coef_
    c = 0
    i = 0
    while c < len(coef[0]):
        player_coef = coef[0][c:c+10]
        print("")
        print(f"Player {i + 1}:")
        for coef_index, pc in enumerate(player_coef):
            print(f"{coef_meaning[coef_index]} Weight: {pc}")
        i += 1
        c += 10


def logistic_regression(X, y, c_target, show_plots=False,
                            c_range=[0.00001, 0.0001, 0.001, 0.01, 0.1, 1]):
    X = np.array(X)
    y = np.array(y)

    kf = KFold(n_splits=5, shuffle=True, random_state=12345)

    mean_f1 = []
    std_f1 = []
    for c in c_range:
        print(f"Considering C={c}")
        f1_s = []
        first = True
        for train_index, test_index in kf.split(X):
            X_train, X_test = X[train_index], X[test_index]
            y_train, y_test = y[train_index], y[test_index]
            model = LogisticRegression(
                penalty='l1', solver='liblinear', max_iter=100000, C=c)
            model.fit(X_train, y_train)

            ypred = model.predict(X_test)

            if show_plots and first:
                first = False  # prevent from showing plots for all 5 k-fold models
                print(
                    f"Confusion matrix:\n{confusion_matrix(y_test, ypred)}")
                fpr, tpr, _ = roc_curve(
                    y_test, model.decision_function(X_test), pos_label=200)
                plt.plot(fpr, tpr, label=f"Logistic regression classifier ROC, C={c}")
                plt.xlabel('False positive rate')
                plt.ylabel('True positive rate')
                print(classification_report(y_test, ypred))
                print_coefficients(model)

                plt.legend()

            f1_s.append(f1_score(y_test, ypred, pos_label=200))

        mean_f1.append(np.array(f1_s).mean())
        std_f1.append(np.array(f1_s).std())

    plt.show()

    plt.errorbar(c_range, mean_f1, yerr=std_f1,
                 linewidth=2, color='b', ecolor='r')

    print(f"Max occurs for c value: {c_range[np.argmax(mean_f1)]}")
    plt.xlabel('c')
    plt.ylabel('mean_f1')
    plt.legend(loc="lower left", prop={'size': 6})
    plt.show()

def main():
    features, classification = get_data("data/json/", 20840)
    logistic_regression(features, classification, 0.1, show_plots=True)

if __name__ == "__main__":
    main()