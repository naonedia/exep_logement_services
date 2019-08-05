from flask import Flask, request
from flask_restful import Resource, Api, reqparse
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from geojson_utils import retrieveNameAndPostalCode
from embed_data import embedData
from io_utils import appendNewData


def checkJSONEstimate(data):
    if 'type_housing' not in data:
        return False, "Missing type_housing in given data"
    if 'ground_surface' not in data:
        return False, "Missing ground_surface in given data"
    if 'ground_surface_carrez' not in data:
        return False, "Missing ground_surface_carrez in given data"
    if 'ground_surface_total' not in data:
        return False, "Missing ground_surface_total in given data"
    if 'room_number' not in data:
        return False, "Missing room_number in given data"
    if 'longitude' not in data:
        return False, "No longitude in given data"
    if 'latitude' not in data:
        return False, "No latitude in given data"
    
    return True, ""


def checkJSONParticipate(data):
    res, error = checkJSONEstimate(data)

    if(res):
        if 'price' not in data:
            return False, "Missing price in given data"
        if 'year' not in data:
            return False, "Missing year in given data"
        return True, ""    
    else:    
        return False, error

def create_app():
    app = Flask(__name__)
    api = Api(app)

    class Estimate(Resource):
        def post(self):
            json_data = request.get_json(force=True)

            if checkJSONEstimate(json_data):
                enriched_data = embedData(json_data)
                town_name, postal_code = retrieveNameAndPostalCode
                if town_name and postal_code:
                    enriched_data['nom_commune'] = town_name
                    enriched_data['code_postal'] = postal_code
                    
                    # Call Tensorflow serving
                    
                    # Return estimation
                    return enriched_data
                else:

                    # Error whilst retrieving town name and postal code
                    return 'Internal Server Error', 500
            
            # Missing params in post request
            return 'Unsupported Media Type', 415

    class Participate(Resource):
        def post(self):
            json_data = request.get_json(force=True)
            
            if checkJSONParticipate(json_data):

                enriched_data = embedData(json_data)
                town_name, postal_code = retrieveNameAndPostalCode
                if town_name and postal_code:
                    enriched_data['nom_commune'] = town_name
                    enriched_data['code_postal'] = postal_code
                    
                    appendNewData(enriched_data)
                    
                    # No return
                    return '', 200
                    
                else:
                    # Error whilst retrieving town name and postal code
                    return 'Internal Server Error', 500
            
            # Missing params in post request
            return 'Unsupported Media Type', 415




    api.add_resource(Estimate, '/api/estimate')
    api.add_resource(Participate, '/api/participate')

    return app


if __name__ == '__main__':

    app = create_app()

    limiter = Limiter(
        app,
        key_func=get_remote_address,
        default_limits=["200 per day", "50 per hour"]
    )

    app.run(debug=True,use_reloader=False,host='0.0.0.0',port=6000)