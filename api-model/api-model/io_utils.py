from constants_var import NEW_DATA_FILE, NEW_DATA_FILENAME

import csv

index = 0

def appendNewData(data):

    global index

    NEW_DATA_FILE = NEW_DATA_FILE.append(data)
    index += 1

    if(index == 10):
        NEW_DATA_FILE.to_csv(NEW_DATA_FILENAME, index=False)
        index = 0
