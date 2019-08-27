import openrouteservice
import pandas as pd
import os

pd.options.mode.chained_assignment = None

POI_CLIENT= openrouteservice.Client(base_url='http://localhost:22222')
ORS_CLIENT = openrouteservice.Client(base_url='http://localhost:9999/ors')

if os.environ['ENV_TYPE'] == 'prod':
    print("Starting API as in PRODUCTION ENVIRONMENT")
    POI_CLIENT= openrouteservice.Client(base_url='http://gunicorn_flask:5000')
    ORS_CLIENT = openrouteservice.Client(base_url='http://ors-app:8080/ors')

ECONOMY_DATA = pd.read_csv('/app/data/finance.csv')
ECONOMY_DATA['annee'] = ECONOMY_DATA['annee'].astype(str)
ECONOMY_DATA['periode'] = ECONOMY_DATA[['annee', 'trimestre']].apply(lambda x: '-'.join(x), axis=1)
ECONOMY_DATA['annee'] = ECONOMY_DATA['annee'].astype('int64')

AVAILABLE_TRIMESTER = [str(j) + '-' + i for j in range(2000,2019,1) for i in ['T1', 'T2', 'T3', 'T4']]

COMMUNES_NANTES_METROPOLE = ['NANTES','REZE','ST-HERBLAIN','VERTOU','ST-SEBASTIEN','COUERON','ORVAULT',
'CARQUEFOU','LA-CHAPELLE-SUR-ERDRE','BOUGUENAIS','SAINTE-LUCE-SUR-LOIRE','THOUARE-SUR-LOIRE','BOUAYE',
'SAUTRON','LES-SORINIERES','LA-MONTAGNE','BASSE-GOULAINE','INDRE','LE-PELLERIN','SAINT-JEAN-DE-BOISEAU',
'SAINT-AIGNAN-GRANDLIEU','MAUVES-SUR-LOIRE','SAINT-LEGER-LES-VIGNES','BRAINS' ]

POSTAL_CODE = [44000,44300,44100,44400,44800,44470,44120,44230,44200,44220,44700,44240,44340,44980,
44830,44640,44880,44840,44115,44620,44610,44860,44710]

COLUMNS_ORDER = pd.read_csv('/app/data/models/model.COLUMNS_ORDER.csv', header=0)
MODEL_FILE = '/app/data/models/model.h5'

NEW_DATA_FILENAME = '/app/data/newdata/data.csv'

NEW_DATA_FILE = pd.read_csv(NEW_DATA_FILENAME, header=0)