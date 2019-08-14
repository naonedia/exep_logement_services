import folium
import openrouteservice

import csv
import pandas as pd
import numpy as np
import sys


ORS_CLIENT = openrouteservice.Client(base_url='http://localhost:7070/ors')
POI_CLIENT = openrouteservice.Client(base_url='http://localhost:5000')

def buildIsochrone(timeOrDistance, profile, longitude, latitude):
# Request of isochrones with 15 minute footwalk.
    params_iso = {'profile': profile,
                  'intervals': [timeOrDistance], # 900/60 = 15 mins
                  'attributes': ['total_pop'], # Get population count for isochrones
                  'locations': [[longitude,latitude]] # Add apartment coords to request parameters
             }    

    return ORS_CLIENT.isochrones(**params_iso) # Perform isochrone request

def getPOIForHouse(df, categories_poi, map1, index, timeOrDistance=900, profile='foot-walking'):
    # Retrieve specific house
    row = df.iloc[[index]]

    # Get Isochrones
    iso = buildIsochrone(timeOrDistance, profile,row['longitude'].item(), row['latitude'].item())
    
    # Draw isochrone on map
    folium.features.GeoJson(iso).add_to(map1)
    
    # Center map on house
    map1.location = [row['latitude'].item(),row['longitude'].item()]
    
    # Draw house marker on map
    folium.map.Marker(
        [row['latitude'].item(),row['longitude'].item()],
        icon=folium.Icon(color='lightgray', icon_color='#cc0000', icon='home', prefix='fa'),
        popup="%i m2,  %i pièces\n%i €" % (row['surface_reelle_bati'].item(), row['nombre_pieces_principales'].item(),row['valeur_fonciere'].item())
    ).add_to(map1)
    
    # Common request parameters
    params_poi = {'request': 'pois', 'sortby': 'distance', 'geojson': iso['features'][0]['geometry'] }

    poi = {}
    treatedLocations = []

    for typ, category in categories_poi.items():
        params_poi['filter_category_ids'] = category
        poi[typ] = dict()
        poi[typ]['geojson'] = POI_CLIENT.places(**params_poi)[0]['features'] # Actual POI request
        
        
        treatedLocations = []
        for elem in poi[typ]['geojson']:
            if elem['geometry']['coordinates'] not in treatedLocations:
                treatedLocations.append(elem['geometry']['coordinates'])
            
                folium.map.Marker(list(reversed(elem['geometry']['coordinates'])), # reverse coords due to weird folium lat/lon syntax
                          icon=folium.Icon(color='blue',
                                            icon_color='#cc0000',
                                            icon='pushpin',
                                            prefix='fa',
                                           ),
                     ).add_to(map1) # Add apartment locations to map
        poi[typ]['geojson'] = treatedLocations

    return map1

def getPOIGroupForHouse(row, poi_group_id, timeOrDistance=900, profile='foot-walking'):
    iso = {}
    # Get Isochrones
    if pd.Series == type(row) :
        iso = buildIsochrone(timeOrDistance, profile, row['longitude'], row['latitude'])
    else:
        iso = buildIsochrone(timeOrDistance, profile, row['longitude'].item(), row['latitude'].item())

    # Common request parameters
    params_poi = {'request': 'pois', 'filter_category_group_ids': poi_group_id, 'sortby': 'distance', 'geojson': iso['features'][0]['geometry']}
    
    poi = {}
    treatedLocations = []
    
    poi = POI_CLIENT.places(**params_poi)[0]['features'] # Actual POI request
    
    treatedLocations = []
    res = []
    for elem in poi:
        if elem['geometry']['coordinates'] not in treatedLocations:
            treatedLocations.append(elem['geometry']['coordinates'])
            res.append(elem)
        
    return iso, res

def addPOIs(data):
    index = 0
    for i, row in data.iterrows():
        iso, foot_list_pois = getPOIGroupForHouse(row, [800,810,820,830,840], timeOrDistance=600, profile='foot-walking') # 10 min by foot
        iso, car_list_pois = getPOIGroupForHouse(row, [800,810,820,830,840], timeOrDistance=300, profile='driving-car') # 5 min by car
        
        tmp = {}
        for poi in foot_list_pois:
            for cat, info in poi['properties']['category_ids'].items():
                col_name = 'foot/' + info['category_group'] + '/' + info['category_name']
                if col_name in tmp:
                    tmp[col_name] += 1
                else:
                    tmp[col_name] = 1
        for col_name, number in tmp.items():
            data.loc[i,col_name] = number  
            
        tmp = {}
        for poi in car_list_pois:
            for cat, info in poi['properties']['category_ids'].items():
                col_name = 'car/' + info['category_group'] + '/' + info['category_name']
                if col_name in tmp:
                    tmp[col_name] += 1
                else:
                    tmp[col_name] = 1
                    
        for col_name, number in tmp.items():
            data.loc[i,col_name] = number
        
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
