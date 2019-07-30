from constants_var import NEW_DATA_FILE

import csv


def appendNewData(data):
    with open(NEW_DATA_FILE, 'a') as f:
        writer = csv.writer(f)
        writer.writerow([
            data['valeur_fonciere'],

            data['surface_carrez'],
            data['surface_reelle_bati'],
            data['surface_terrain'],

            data['code_postal'],
            data['nom_commune'],
            
            data['nombre_pieces_principales'],
            data['type_local'],

            data['longitude'],
            data['latitude'],

            data['foot/distractions/arts_centre'],
            data['foot/distractions/bar'],
            data['foot/distractions/gallery'],
            data['foot/distractions/library'],
            data['foot/distractions/museum'],
            data['foot/distractions/place_of_worship'],
            data['foot/distractions/restaurant'],
            data['foot/distractions/zoo'],
            data['foot/jardin/park'],
            data['foot/jardin/playground'],
            data['foot/medical/clinic'],
            data['foot/medical/doctors'],
            data['foot/medical/hospital'],
            data['foot/tan/bus_stop'],
            data['foot/tan/station'],
            data['foot/tan/tram_stop'],
            data['foot/vie_courante/convenience'],
            data['foot/vie_courante/pharmacy'],
            data['foot/vie_courante/social_facility'],
            data['foot/vie_courante/supermarket'],
            data['foot/vie_courante/townhall'],

            data['car/distractions/arts_centre'],
            data['car/distractions/bar'],
            data['car/distractions/gallery'],
            data['car/distractions/library'],
            data['car/distractions/museum'],
            data['car/distractions/place_of_worship'],
            data['car/distractions/restaurant'],
            data['car/distractions/zoo'],
            data['car/jardin/park'],
            data['car/jardin/playground'],
            data['car/medical/clinic'],
            data['car/medical/doctors'],
            data['car/medical/hospital'],
            data['car/tan/bus_stop'],
            data['car/tan/station'],
            data['car/tan/tram_stop'],
            data['car/vie_courante/convenience'],
            data['car/vie_courante/pharmacy'],
            data['car/vie_courante/social_facility'],
            data['car/vie_courante/supermarket'],
            data['car/vie_courante/townhall'],
        ])