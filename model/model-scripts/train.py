import sys
import json

import pandas as pd
import numpy as np

from keras.layers.core import Activation, Dense
from keras.models import Sequential
from keras.optimizers import Adam

from sklearn.model_selection import train_test_split

def normalize(x_train, x_test, output, columns):
    mu = np.mean(x_train, axis=0)
    std = np.std(x_train, axis=0)
    x_train_normalized = (x_train - mu) / std
    x_test_normalized = (x_test - mu) / std
    
    print(pd.Series(mu, index=columns))

    df = pd.DataFrame(columns=columns)
    df = df.append(pd.Series(mu, index=columns), ignore_index=True)
    df = df.append(pd.Series(std, index=columns), ignore_index=True)
    
    df.to_csv(output + '.COLUMNS_ORDER.csv', index=False)
    
    return x_train_normalized, x_test_normalized


def load_data(path, output):
    dataset = pd.read_csv(path)

    train_data, test_data = train_test_split(dataset, test_size=0.25, random_state=42)

    X_train = train_data.drop(['valeur_fonciere'], axis=1).to_numpy()
    y_train = train_data['valeur_fonciere'].to_numpy()
    X_test = test_data.drop(['valeur_fonciere'], axis=1).to_numpy()
    y_test = test_data['valeur_fonciere'].to_numpy()

    X_train_normal, X_test_normal = normalize(X_train, X_test, output, train_data.drop(['valeur_fonciere'], axis=1).columns)

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

    

def main(argv):
    X_train, y_train, X_test, y_test = load_data(argv[0], argv[1])

    model = create_model(X_train)
    
    # Train the model
    print("[INFO] training model...")
    history = model.fit(X_train, y_train, validation_data=(X_test, y_test), epochs=2000, batch_size=40000, verbose=2)

    model.save(argv[1] + '.h5')
    
    with open(argv[1] + '.history.json', 'w') as f:
        json.dump(history.history, f)

if __name__ == '__main__':
        main(sys.argv[1:])