import openrouteservice

NEW_DATA_FILE = '/data/newdata.csv'

ORS_CLIENT = openrouteservice.Client(base_url='http://ors-app:9090/ors')
POI_CLIENT = openrouteservice.Client(base_url='http://openpoiservice_gunicorn_flask_1:5000')

TENSORFLOW_API = 'http://tensorflow_serving_1'