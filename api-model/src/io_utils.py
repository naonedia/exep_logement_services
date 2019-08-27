import csv
import os
from os import path
from datetime import date

from src.constants_var import NEW_DATA, NEW_DATA_FILENAME, COLUMNS_ORDER_FILENAME, BACKUP_NEW_DATA_FILENAME_BEGIN, BACKUP_NEW_DATA_FILENAME_END

def appendNewData(data):
    NEW_DATA = NEW_DATA.append(data)
    NEW_DATA.to_csv(NEW_DATA_FILENAME, index=False)    

def backup():
    if path.exists(NEW_DATA_FILENAME):
        os.rename(NEW_DATA_FILENAME, BACKUP_NEW_DATA_FILENAME_BEGIN + date.today().strftime("%d-%m-%Y")+ '-' + BACKUP_NEW_DATA_FILENAME_END)

    with open(COLUMNS_ORDER_FILENAME, 'r') as f:
            with open(NEW_DATA_FILENAME, 'w') as g:
                g.write(f.readline())