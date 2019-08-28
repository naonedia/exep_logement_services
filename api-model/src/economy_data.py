from datetime import date
import pandas as pd
import numpy as np

from src.constants_var import AVAILABLE_TRIMESTER, ECONOMY_DATA

def monthToTrimester(month):
    if month <= 3:
        return 'T1'
    elif month <= 6:
        return 'T2'
    elif month <= 9:
        return 'T3'
    elif month <= 12:
        return 'T4'

def getLastNYears(year, month, n ):
    index = AVAILABLE_TRIMESTER.index(str(year) + '-'+ monthToTrimester(month))
    
    return AVAILABLE_TRIMESTER[index-20: index]

def encode(data, col, max_val):
    data[col + '_sin'] = np.sin(2 * np.pi * data[col]/max_val)
    data[col + '_cos'] = np.cos(2 * np.pi * data[col]/max_val)
    return data

def addEco(data):
    data['annee'] = 2018
    data = encode(data, 'mois', 12)

    YEAR_LOOKBACK = 5
    toRetrieve = getLastNYears(data.loc[0,'annee'], data.loc[0,'mois'],YEAR_LOOKBACK)
    k = YEAR_LOOKBACK - 1
    j = 0
    for val in toRetrieve:
        if j >= 4:
            j %= 4
            k -= 1
        j += 1
        res = ECONOMY_DATA[ECONOMY_DATA['periode']==val].drop(['annee','trimestre','periode'], axis=1)
        for col_name in list(res):
            data.loc[0,str(k) + '-' + str(j) + '-' + col_name] = float(res[col_name].item())

    return data