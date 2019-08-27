from src.constants_var import ORS_CLIENT, POI_CLIENT

def buildIsochrone(timeOrDistance, profile, longitude, latitude):
# Request of isochrones with 15 minute footwalk.
    params_iso = {'profile': profile,
                  'intervals': [timeOrDistance],  # 900/60 = 15 mins
                  # Get population count for isochrones
                  'attributes': ['total_pop'],
                  # Add apartment coords to request parameters
                  'locations': [[longitude, latitude]]
             }

    return ORS_CLIENT.isochrones(**params_iso)  # Perform isochrone request


def getPOIGroupForHouse(longitude, latitude, poi_group_id, timeOrDistance=900, profile='foot-walking'):

    # Get Isochrones
    iso = buildIsochrone(timeOrDistance, profile, longitude, latitude)

    # Common request parameters
    params_poi = {'request': 'pois', 'filter_category_group_ids': poi_group_id, 'sortby': 'distance', 'geojson': iso['features'][0]['geometry']}

    poi = {}
    treatedLocations = []

    poi = POI_CLIENT.places(**params_poi)[0]['features']  # Actual POI request

    treatedLocations = []
    res = []
    for elem in poi:
        if elem['geometry']['coordinates'] not in treatedLocations:
            treatedLocations.append(elem['geometry']['coordinates'])
            res.append(elem)

    return iso, res


def embedData(data):

    iso, foot_list_pois = getPOIGroupForHouse(data.loc[0,'longitude'], data.loc[0,'latitude'], [800, 810, 820, 830, 840], timeOrDistance=600, profile='foot-walking')  # 10 min by foot
    iso, car_list_pois = getPOIGroupForHouse(data.loc[0,'longitude'], data.loc[0,'latitude'], [800, 810, 820, 830, 840], timeOrDistance=300, profile='driving-car')  # 5 min by car

    for poi in foot_list_pois:
        for cat, info in poi['properties']['category_ids'].items():
            col_name = 'foot/' + info['category_group'] + '/' + info['category_name']
            if col_name in data.iloc[0]:
                data.loc[0,col_name] += 1
            else:
                data.loc[0,col_name] = 1

    for poi in car_list_pois:
        for cat, info in poi['properties']['category_ids'].items():
            col_name = 'car/' + info['category_group'] + '/' + info['category_name']
            if col_name in data.iloc[0]:
                data.loc[0,col_name] += 1
            else:
                data.loc[0,col_name] = 1

    filter_col = [col for col in data if col.startswith('car') or col.startswith('foot')]
    data[filter_col] = data[filter_col].fillna(value=0)
        
    return data