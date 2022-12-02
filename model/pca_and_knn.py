import numpy as np
import math
import matplotlib.pyplot as plt
from load_data import get_data
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import classification_report
from sklearn.metrics import f1_score
from sklearn.model_selection import KFold
from sklearn.metrics import confusion_matrix
from sklearn.metrics import roc_curve


def pca_and_knn(X, y, k_target):    
    X = np.array(X)
    y = np.array(y)
    n_neighbors = int(math.sqrt(20840)) + 1

    # perform pca dimensionality reduction
    scaler = StandardScaler()
    scaler.fit(X)
    X = scaler.transform(X)

    pca = PCA(0.95)
    pca.fit(X)

    plt.plot(range(1, len(pca.explained_variance_ratio_) + 1),
             pca.explained_variance_ratio_, label="Explained variance ratio")
    plt.xlabel('Number of principal components')
    plt.ylabel('Explained variance')
    plt.show()

    pca = PCA(6)
    pca.fit(X)

    X = pca.transform(X)


    k_range = range(1, n_neighbors)
    kf = KFold(n_splits=5, shuffle=True, random_state=12345)

    mean_f1 = []
    std_f1 = []

    for n in k_range:
        f1_scores = []
        first = True
        print(f"Considering {n} out of {n_neighbors}")
        for train_index, test_index in kf.split(X):
            Xtrain, Xtest = X[train_index], X[test_index]
            ytrain, ytest = y[train_index], y[test_index]

            model = KNeighborsClassifier(n, weights="uniform").fit(Xtrain, ytrain)
            ypred = model.predict(Xtest)
            f1_scores.append(f1_score(ytest, ypred, pos_label=200))

            if k_target == n and first:
                print(f"The number of components in PCA: {len(pca.components_)}")
                print(classification_report(ytest, ypred))
                print(
                    f"Confusion matrix:\n{confusion_matrix(ytest, ypred)}")
                
                fpr, tpr, _ = roc_curve(
                    ytest, model.predict_proba(Xtest)[:, 1], pos_label=200)
                plt.plot(fpr, tpr, label="kNN classifier ROC")
                plt.xlabel('False positive rate')
                plt.ylabel('True positive rate')
                plt.legend()
                plt.show()

                first = False

        mean_f1.append(np.array(f1_scores).mean())
        std_f1.append(np.array(f1_scores).std())

    print(f"Max occurs for k value: {k_range[np.argmax(mean_f1)]}")

    plt.errorbar(k_range, mean_f1, yerr=std_f1,
                 linewidth=2, color='b', ecolor='r')

    plt.xlabel('k (number of neighbours)')
    plt.ylabel('mean_f1')
    plt.legend(loc="lower left", prop={'size': 6})
    plt.show()

def main():
    features, classification = get_data("data/json/", 20840)
    pca_and_knn(features, classification, 53)

if __name__ == "__main__":
    main()