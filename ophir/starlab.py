"""
This module is to deal with output from Starlab's output files.
"""
import re
import pandas as pd

def load_starlab_file(filename):
    
    with open(filename, 'r') as f:
        lines = f.read().splitlines()
    
    for i, ln in enumerate(lines):
        splits = [s.strip() for s in re.split("[\t]", ln.strip())]
        if splits[0]=="Timestamp":
            startline = i
            break

    data = pd.read_csv(filename, skiprows=startline, sep="\t")
    data.drop(data.columns[-1], axis=1, inplace=True)
    data.columns = splits
    
    return data