import sys

import tensorflow as tf
import pandas as pd
import numpy as np

from keras.layers.core import Activation, Dense
from keras.models import Sequential
from keras.optimizers import Adam

from sklearn.model_selection import train_test_split

def normalize(x_train, x_test):
    mu = np.mean(x_train, axis=0)
    std = np.std(x_train, axis=0)
    x_train_normalized = (x_train - mu) / std
    x_test_normalized = (x_test - mu) / std
    return x_train_normalized, x_test_normalized


def load_data(path):
    dataset = pd.read_csv(path)

    train_data, test_data = train_test_split(dataset, test_size=0.25, random_state=42)

    X_train = train_data.drop(['valeur_fonciere'], axis=1).to_numpy()
    y_train = train_data['valeur_fonciere'].to_numpy()
    X_test = test_data.drop(['valeur_fonciere'], axis=1).to_numpy()
    y_test = test_data['valeur_fonciere'].to_numpy()

    X_train_normal, X_test_normal = normalize(X_train, X_test)

    return X_train_normal, y_train, X_test_normal, y_test


def create_model(dataset):

    # define our MLP network
    model = Sequential()
        
    # Input Layer :
    model.add(Dense(128, kernel_initializer='normal',input_dim = dataset.shape[1], activation='relu'))
        
    # Hidden Layers :
    model.add(Dense(256, kernel_initializer='normal',activation='relu'))
    model.add(Dense(512, kernel_initializer='normal',activation='relu'))
    model.add(Dense(512, kernel_initializer='normal',activation='relu'))
    model.add(Dense(256, kernel_initializer='normal',activation='relu'))
    # Output Layer :
    model.add(Dense(1, kernel_initializer='normal',activation='linear'))

    opt = Adam(lr=1e-2, decay=1e-3 / 10)
    model.compile(loss='mae', optimizer=opt, metrics=["mse", "mae"])

    return model 


def convertKerasToTensor(model, output):
    # The export path contains the name and the version of the model
    tf.keras.backend.set_learning_phase(0)  # Ignore dropout at inference

    # Fetch the Keras session and save the model
    # The signature definition is defined by the input and output tensors
    # And stored with the default serving key
    with tf.keras.backend.get_session() as sess:
        tf.saved_model.simple_save(
            sess,
            output,
            inputs={'input_data': model.input},
            outputs={t.name: t for t in model.outputs})


def main(argv):
    X_train, y_train, X_test, y_test = load_data(argv[0])

    model = keras.load_model(argv[2])
    
    # Train the model
    print("[INFO] training model...")
    history = model.fit(X_train, y_train, validation_data=(X_test, y_test), epochs=1000, batch_size=40000, verbose=2)

    convertKerasToTensor(model, argv[1])

if __name__ == '__main__':
    
    main(sys.argv[1:])
    

