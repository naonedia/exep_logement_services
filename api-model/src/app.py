from flask import Flask, request
from flask_restful import Resource, Api, reqparse
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_cors import CORS

import sys
import logging
import pandas as pd
import numpy as np
import tensorflow as tf
import keras as k

from src.geojson_utils import retrieveNameAndPostalCode, encodeCommune, encodePostalCode, encodeType
from src.embed_data import embedData
from src.io_utils import appendNewData, backup
from src.economy_data import addEco
from src.constants_var import COLUMNS_ORDER, MODEL_FILENAME

global KERAS_MODEL
global graph
global session

def normalize(data):
    mu = COLUMNS_ORDER.loc[0].to_numpy()
    std = COLUMNS_ORDER.loc[1].to_numpy()
    return (data - mu) / std


def translate_features_name(data):
    data['surface_reelle_bati'] = data['groundSurface']
    data['surface_carrez'] = data['groundSurfaceCarrez']
    data['nombre_pieces_principales'] = data['roomNumber']
    data['surface_terrain'] = data['groundSurfaceTotal']
    data.pop('groundSurface', None)
    data.pop('groundSurfaceCarrez', None)
    data.pop('roomNumber', None)
    data.pop('groundSurfaceTotal', None)

    return data


def checkJSONEstimate(data):
    if 'type' not in data:
        return False, "Missing type in given data"
    if 'groundSurface' not in data:
        return False, "Missing groundSurface in given data"
    if 'groundSurfaceCarrez' not in data:
        return False, "Missing groundSurfaceCarrez in given data"
    if 'groundSurfaceTotal' not in data:
        return False, "Missing groundSurfaceTotal in given data"
    if 'roomNumber' not in data:
        return False, "Missing roomNumber in given data"
    if 'longitude' not in data:
        return False, "No longitude in given data"
    if 'latitude' not in data:
        return False, "No latitude in given data"
    if data['groundSurface'] <= 0:
        return False, "Ground surface can't be less than 1 square meter"
    if data['groundSurfaceCarrez'] <= 0:
        return False, "Ground surface can't be less than 1 square meter"
    if data['groundSurfaceTotal'] <= 0:
        return False, "Ground surface can't be less than 1 square meter"
    if data['roomNumber'] <= 0:
        return False, "Room number can't be 0"
    if data['type'] != 'house' and data['type'] != 'flat':
        return False, "Type must be 'house' or 'flat'"

    return True, ""

def checkJSONParticipate(data):
    res, error = checkJSONEstimate(data)

    if(res):
        if 'price' not in data:
            return False, "Missing price in given data"
        if 'month' not in data:
            return False, "Missing month in given data"
        if 'year' not in data:
            return False, "Missing year in given data"
        if int(data['year']) >= 2005 and int(data['year']) < 2019:
            return False, "Year must be between 2005 and 2018 included"
        if int(data['month']) >= 1 and int(data['month']) <= 12:
            return False, "Month must be between 1 and 12 included"
        
        return True, ""
    else:
        return False, error

def create_app():

    app = Flask(__name__)
    api = Api(app)

    class Estimate(Resource):
        def post(self):

            json_data = request.get_json(force=True)

            json_check, err = checkJSONEstimate(json_data)
            if json_check:
                data = translate_features_name(json_data)
                data = pd.io.json.json_normalize(json_data)
                data = embedData(data)
                data = addEco(data)

                town_name, postal_code = retrieveNameAndPostalCode(data.loc[0,'longitude'],data.loc[0,'latitude'])
                if town_name and postal_code:
                    data.loc[0,'nom_commune'] = town_name
                    data.loc[0,'code_postal'] = postal_code

                    encodeCommune(data)
                    encodePostalCode(data)
                    encodeType(data)


                    missingColumns = set(COLUMNS_ORDER).difference(set(data))
                    for val in missingColumns:
                        data.loc[0,val] = 0

                    # Re-ordering columns according to the trained model
                    data = data[COLUMNS_ORDER.columns]


                    # Normalize data
                    data = normalize(data.to_numpy())

                    # Return estimation
                    with session.graph.as_default():
                        k.backend.set_session(session)
                        res = KERAS_MODEL.predict(np.array(data)[0:1])

                    print('response returned ' + str(res))
                    app.logger.info('response returned ' + str(res))

                    return {"type": "estimate","price": str(res[0][0])}
                else:

                    # Error whilst retrieving town name and postal code
                    return 'Longitude and/or latitude are out of range', 500

            # Missing params in post request
            return err, 415

    class Participate(Resource):
        def post(self):

            json_data = request.get_json(force=True)

            json_check, err = checkJSONParticipate(json_data)
            if json_check:
                data = translate_features_name(json_data)
                data = pd.io.json.json_normalize(json_data)
                data = embedData(data)
                data = addEco(data)

                town_name, postal_code = retrieveNameAndPostalCode(data['longitude'],data['latitude'])
                if town_name and postal_code:
                    data.loc[0,'nom_commune'] = town_name
                    data.loc[0,'code_postal'] = postal_code

                    encodeCommune(data)
                    encodePostalCode(data)
                    encodeType(data)

                    missingColumns = set(COLUMNS_ORDER).difference(set(data))
                    for val in missingColumns:
                        data.loc[0,val] = 0

                    # Re-ordering columns according to the trained model
                    data = data[COLUMNS_ORDER.columns]

                    appendNewData(data)

                    # Normalize data
                    data = normalize(data.to_numpy())

                    # Return estimation
                    with session.graph.as_default():
                        k.backend.set_session(session)
                        res = KERAS_MODEL.predict(np.array(data)[0:1])

                    return {"type": "participate","price": str(res[0][0])}
                else:
                    # Error whilst retrieving town name and postal code
                    return 'Longitude and/or latitude are out of range', 500

            # Missing params in post request
            return err, 415

    class Healthcheck(Resource):
        def get(self):
            return 'OK', 200



    api.add_resource(Estimate, '/api/estimate')
    api.add_resource(Participate, '/api/participate')
    api.add_resource(Healthcheck, '/api/healthcheck')

    session = tf.Session(graph=tf.Graph())
    with session.graph.as_default():
        k.backend.set_session(session)
        KERAS_MODEL = k.models.load_model(MODEL_FILENAME)

    cors = CORS(app, resources={r"*": {"origins": "*"}})

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

    backup()

    return app

app = create_app()

if __name__ == '__main__':

    app.run(debug=True,use_reloader=False,host='0.0.0.0',port=6000)
    