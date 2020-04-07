# -*- coding: utf-8 -*-
"""
Created on Fri Apr  3 11:32:49 2020

@author: chelsea.strawder
"""
import h5py
import numpy as np
import pandas as pd
from collections import defaultdict
from dataAnalysis import create_df
from behaviorAnalysis import get_files, formatFigure
from responsePlotByParam import plot_by_param


## change this to a function, where args are mouseID, list of dates
# then change below logic to select files by date, rather than manual slicing

# files = [file if date is in files] - use regex??


files = get_files('486634','masking_to_analyze') 

def combine_files(files, *dates, output='df'):
    dn = {}
    filtered_files = [file for file in files for date in dates if date in file]
    for i, f in enumerate(filtered_files):  
        d = h5py.File(f) 
        if output=='df':
            dn['df_{}'.format(i)] = create_df(d)
        else:
            dn['df_{}'.format(i)] = d
    return dn


def combine_dfs(dict1):
    dictget = lambda x, k: [x[i] for i in k]
    return pd.concat(dictget(dict1, list(map(str, dict1.keys()))), ignore_index=True)

    
    