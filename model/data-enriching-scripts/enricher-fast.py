import folium
import openrouteservice
from geojson import MultiPolygon
import csv
import pandas as pd
import numpy as np
import sys
import json

ORS_CLIENT = openrouteservice.Client(base_url='http://localhost:7070/ors')
POI_CLIENT = openrouteservice.Client(base_url='http://localhost:5000')

def buildIsochrone(timeOrDistance, profile, lonlatArray):
# Request of isochrones with 15 minute footwalk.
    params_iso = {'profile': profile,
                  'intervals': [timeOrDistance], # 900/60 = 15 mins
                  'attributes': ['total_pop'], # Get population count for isochrones
                  'locations': lonlatArray # Add apartment coords to request parameters
             }    

    return ORS_CLIENT.isochrones(**params_iso)['features'] # Perform isochrone request

def getPOIForHouse(df, categories_poi, timeOrDistance=900, profile='foot-walking'):
    # Retrieve specific house
    lonlatArray : df[['longitude','latitude']].to_numpy(dtype=None, copy=False).tolist()

    # Get Isochrones
    iso = buildIsochrone(timeOrDistance, profile, lonlatArray)

    
    # Common request parameters
    params_poi = {'request': 'pois', 'sortby': 'distance', 'geojson': iso['features'][0]['geometry'], 'filter_category_ids': category }

    poi = {}
    treatedLocations = []



    for typ, category in categories_poi.items():
        poi[typ] = dict()
        poi[typ]['geojson'] = POI_CLIENT.places(**params_poi)['features'] # Actual POI request
        
        
        treatedLocations = []
        for elem in poi[typ]['geojson']:
            if elem['geometry']['coordinates'] not in treatedLocations:
                treatedLocations.append(elem['geometry']['coordinates'])
        poi[typ]['geojson'] = treatedLocations



def getPOIGroupForHouse(df, poi_group_id, timeOrDistance=900, profile='foot-walking'):
    
     # Retrieve specific house
    lonlatArray = df[['longitude','latitude']].to_numpy(dtype=None, copy=False).tolist()

    # Get Isochrones
    iso = buildIsochrone(timeOrDistance, profile, lonlatArray)

    multi = MultiPolygon(list(map(lambda obj: obj['geometry']['coordinates'], iso)))

    with open('tmp.txt', 'w') as outfile:
        json.dump(multi, outfile)

    # Common request parameters
    params_poi = {'request': 'pois', 'filter_category_group_ids': poi_group_id, 'sortby': 'distance', 'geojson': multi}
    
    poi = POI_CLIENT.places(**params_poi ) # Actual POI request
    
    treatedLocations = []
    res = []
    for elem in poi:
        for feature in elem['features']:
            if feature['geometry']['coordinates'] not in treatedLocations:
                treatedLocations.append(feature['geometry']['coordinates'])
                res.append(feature)
        
    return iso, res

def addPOIs(data):
    index = 0
    maxIndex = len(data)
    for i in range(0, maxIndex, 10):
        iso, foot_list_pois = getPOIGroupForHouse(data.iloc[index:index+10], [800,810,820,830,840], timeOrDistance=600, profile='foot-walking') # 10 min by foot
        iso, car_list_pois = getPOIGroupForHouse(data.iloc[index:index+10], [800,810,820,830,840], timeOrDistance=300, profile='driving-car') # 5 min by car
        
        for j in range(0,10):
            tmp = {}
            for poi in foot_list_pois:
                for cat, info in poi['properties']['category_ids'].items():
                    col_name = 'foot/' + info['category_group'] + '/' + info['category_name']
                    if col_name in tmp:
                        tmp[col_name] += 1
                    else:
                        tmp[col_name] = 1
            for col_name, number in tmp.items():
                data.loc[i * 10 + j, col_name] = number  
                
            tmp = {}
            for poi in car_list_pois:
                for cat, info in poi['properties']['category_ids'].items():
                    col_name = 'car/' + info['category_group'] + '/' + info['category_name']
                    if col_name in tmp:
                        tmp[col_name] += 1
                    else:
                        tmp[col_name] = 1
                        
            for col_name, number in tmp.items():
                data.loc[i * 10 + j, col_name] = number
        
        index += 1
        sys.stdout.write('\r')
        sys.stdout.write('{}%' .format(round(((index+1) * 100)/data.shape[0],2)))
        sys.stdout.flush()
        
    filter_col = [col for col in data if col.startswith('car') or col.startswith('foot')]
    data[filter_col] = data[filter_col].fillna(value=0)
        
    return data

def main(argv):
    
    house_dataset = pd.read_csv('origin.csv')
    enriched_df = addPOIs(house_dataset[int(argv[0]):int(argv[1])])
    enriched_df.to_csv('tmp/after_enriched_' + argv[2] + '.csv', index=False)

if __name__ == "__main__":
    main(sys.argv[1:])
