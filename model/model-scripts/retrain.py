import sys
import json

import pandas as pd
import numpy as np

from keras import regularizers
from keras.layers.core import Activation, Dense
from keras.models import Sequential, load_model
from keras.optimizers import Adam

from sklearn.model_selection import train_test_split

from tensorflow import set_random_seed

np.random.seed(42)
PYTHONHASHSEED=42
set_random_seed(42)

def normalize(x_train, x_test, columns):
    mu = np.mean(x_train, axis=0)
    std = np.std(x_train, axis=0)
    x_train_normalized = (x_train - mu) / std
    x_test_normalized = (x_test - mu) / std
    
    return x_train_normalized, x_test_normalized


def load_data(path):
    train_data = pd.read_csv(path + '.train.csv')
    test_data = pd.read_csv(path + '.test.csv')
    
    X_train = train_data.drop(['valeur_fonciere'], axis=1).to_numpy()
    y_train = train_data['valeur_fonciere'].to_numpy()
    X_test = test_data.drop(['valeur_fonciere'], axis=1).to_numpy()
    y_test = test_data['valeur_fonciere'].to_numpy()

    X_train_normal, X_test_normal = normalize(X_train, X_test, train_data.drop(['valeur_fonciere'], axis=1).columns)

    return X_train_normal, y_train, X_test_normal, y_test

def main(argv):
    X_train, y_train, X_test, y_test = load_data(argv[0])

    # Load model
    model = load_model(argv[0] + '.h5')

    # Load old history
    with open(argv[0] + '.history.json', 'r') as f:
        historyOld = json.load(f)
    
    # Re-train the model
    print("[INFO] training model...")
    history = model.fit(X_train, y_train, validation_data=(X_test, y_test), epochs=1000, batch_size=40000, verbose=2)

    # Save model
    model.save(argv[1] + '.h5')

    # Concat old and new history
    historyConcat = {}
    for key in historyOld.keys():
        historyConcat[key] = historyOld[key] + history.history[key]
    
    # Save concatenated history
    with open(argv[1] + '.history.json', 'w') as f:
        json.dump(historyConcat, f)

if __name__ == '__main__':
        main(sys.argv[1:])