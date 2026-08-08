import pandas as pd 
import glob

files = sorted(glob.glob("./csv/*.csv"))
dfs = [pd.read_csv(file) for file in files]

final = pd.concat(dfs, ignore_index=True)
final.to_csv("size_impact.csv", index=False)