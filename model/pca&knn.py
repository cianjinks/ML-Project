import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import classification_report


def pca(X, Y):
    # Split the data into training and test sets with 80/20 ratio
    Xtrain, Xtest, ytrain, ytest = train_test_split(X, Y, test_size=0.2)
    
    scaler = StandardScaler()
    scaler.fit(Xtrain)
    Xtrain = scaler.transform(Xtrain)
    Xtest = scaler.transform(Xtest)

    pca = PCA(.95)
    pca.fit(Xtrain)
    Xtrain = pca.transform(Xtrain)
    Xtest = pca.transform(Xtest)

    model = KNeighborsClassifier(n_neighbors=7,weights="uniform").fit(Xtrain, ytrain)
    ypred = model.predict(Xtest)
    print(classification_report(ytest, ypred))
