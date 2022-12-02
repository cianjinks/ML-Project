import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt

from tensorflow.keras import layers
from tensorflow.keras import regularizers
from tensorflow.keras import initializers
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from load_data import get_data
from sklearn.preprocessing import StandardScaler
import pathlib

from keras.models import Model
from keras.layers import Dense, Input, Concatenate, Lambda

def create_custom_model():
    inputTensor = Input((100,))

    group1 = Lambda(lambda x: x[:, :10], output_shape=((10,)))(inputTensor)
    group2 = Lambda(lambda x: x[:, 10:20], output_shape=((10,)))(inputTensor)
    group3 = Lambda(lambda x: x[:, 20:30], output_shape=((10,)))(inputTensor)
    group4 = Lambda(lambda x: x[:, 30:40], output_shape=((10,)))(inputTensor)
    group5 = Lambda(lambda x: x[:, 40:50], output_shape=((10,)))(inputTensor)
    group6 = Lambda(lambda x: x[:, 50:60], output_shape=((10,)))(inputTensor)
    group7 = Lambda(lambda x: x[:, 60:70], output_shape=((10,)))(inputTensor)
    group8 = Lambda(lambda x: x[:, 70:80], output_shape=((10,)))(inputTensor)
    group9 = Lambda(lambda x: x[:, 80:90], output_shape=((10,)))(inputTensor)
    group10 = Lambda(lambda x: x[:, 90:], output_shape=((10,)))(inputTensor)
    
    group1 = Dense(5, activation="relu")(group1)
    group2 = Dense(5, activation="relu")(group2)
    group3 = Dense(5, activation="relu")(group3)
    group4 = Dense(5, activation="relu")(group4)
    group5 = Dense(5, activation="relu")(group5)
    group6 = Dense(5, activation="relu")(group6)
    group7 = Dense(5, activation="relu")(group7)
    group8 = Dense(5, activation="relu")(group8)
    group9 = Dense(5, activation="relu")(group9)
    group10 = Dense(5, activation="relu")(group10)

    outputTensor = Concatenate()([group1, group2, group3, group4, group5, group6, group7, group8, group9, group10])

    group1 = Lambda(lambda x: x[:, :25], output_shape=((25,)))(outputTensor)
    group2 = Lambda(lambda x: x[:, 25:], output_shape=((25,)))(outputTensor)


    group1 = Dense(10, activation="relu")(group1)
    group2 = Dense(10, activation="relu")(group2)

    outputTensor = Concatenate()([group1, group2])
    outputTensor = Dense(1, activation="sigmoid", kernel_regularizer=regularizers.l2(0.001))(outputTensor)

    model = Model(inputTensor, outputTensor)

    return model


def train_model(X, y):

    X = np.array(X)
    y = np.array(y)

    scaler = StandardScaler()
    scaler.fit(X)
    Xtrain = scaler.transform(X)

    for i in range(len(y)):
        if y[i] == 200:
            y[i] = 1
        else:
            y[i] = 0

    print(X[:5])
    print(y[:5])

    Xtrain, Xtest, ytrain, ytest = train_test_split(X, y, test_size=0.2)

    print(len(Xtrain))
    print(len(ytrain))

    print(ytrain[:25])
    print(ytest[:25])

    model = create_custom_model()

    model.summary()

    model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=0.00001),
                  loss="binary_crossentropy",
                  metrics=['accuracy'])

    epochs = 1000
    batch_size = 128

    history = model.fit(Xtrain, ytrain,
                        epochs=epochs, validation_split=0.1, batch_size=batch_size)

    model.save("league_classification.model")

    plt.subplot(211)


    plt.plot(history.history['accuracy'])
    plt.plot(history.history['val_accuracy'])
    plt.title('model accuracy')
    plt.ylabel('accuracy')
    plt.xlabel('epoch')
    plt.legend(['train', 'val'], loc='upper left')
    plt.subplot(212)
    plt.plot(history.history['loss'])
    plt.plot(history.history['val_loss'])
    plt.title('model loss')
    plt.ylabel('loss')
    plt.xlabel('epoch')
    plt.legend(['train', 'val'], loc='upper left')
    plt.show()

    preds = model.predict(Xtest)
    print(" ".join([str(x) for x in preds]))

    y_pred = [None] * len(preds)

    for i in range(len(preds)):
        if preds[i] > 0.5:
            y_pred[i] = 1
        else:
            y_pred[i] = 0

    unique_values = set()

    for x in y_pred:
        unique_values.add(x)

    print(" ".join([str(x) for x in y_pred]))

    print(f"Unique values: {len(unique_values)}")

    y_pred = np.array(y_pred)

    print(classification_report(ytest, y_pred))

if __name__ == "__main__":
    features, classification = get_data("data/json/", 20840)
    train_model(features, classification)
    # create_custom_model()
