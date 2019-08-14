import json
from shapely.geometry import shape, Point
from constants_var import COMMUNES_NANTES_METROPOLE, POSTAL_CODE

# load GeoJSON file containing sectors
with open('./data/communes-nantes-metropole.geojson') as f:
    nantes_metropolis_geojson = json.load(f)


def retrieveNameAndPostalCode(longitude, latitude):
    # construct point based on lon/lat returned by geocoder
    point = Point(longitude, latitude)

    # check each polygon to see if it contains the point
    for feature in nantes_metropolis_geojson['features']:
        polygon = shape(feature['geometry'])
        if polygon.contains(point):
            return (feature['properties']['nom'], feature['properties']['code_postal'])
    
    return (None, None)

def encodeCommune(data):
    for val in COMMUNES_NANTES_METROPOLE:
        if data.loc[0,'nom_commune'] == val:
            data.loc[0,val] = 1
        else:
            data.loc[0,val] = 0
    data.drop('nom_commune', axis=1, inplace=True)
    return data

def encodePostalCode(data):
    for val in POSTAL_CODE:
        if data.loc[0,'code_postal'] == val:
            data.loc[0,str(val)] = 1
        else:
            data.loc[0,str(val)] = 0
    data.drop('code_postal', axis=1, inplace=True)
    return data

def encodeType(data):
    if data.loc[0,'type'] == 'house':
        data.loc[0,'Appartement'] = 0
        data.loc[0,'Maison'] = 1
    else:
        data.loc[0,'Appartement'] = 0
        data.loc[0,'Maison'] = 1
    data.drop('type', axis=1, inplace=True)
    return data