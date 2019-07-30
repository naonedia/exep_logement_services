import json
from shapely.geometry import shape, Point

# load GeoJSON file containing sectors
with open('../data/communes-nantes-metropole.geojson') as f:
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