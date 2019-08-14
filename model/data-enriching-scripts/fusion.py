import glob
import pandas as pd

frames = [ pd.read_csv(file) for file in glob.glob("tmp/*.csv")]

pd.concat(frames,ignore_index=True, sort=False).to_csv('origin_enriched.csv',index=False)
