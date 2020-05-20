# -*- coding: utf-8 -*-
"""
Created on Mon Nov 18 11:15:05 2019

@author: chelsea.strawder

This gives you a nice dataframe of the session data for an individual mouse

Describe model, fit model, and summarize model

Look at prevResp, prevIncorrect, trial number (better at start/learning over time)


"""
from dataAnalysis import import_data, create_df
import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
import scipy 
from patsy import dmatrices
import statsmodels.api as sm

from sessionData import session

matplotlib.rcParams['pdf.fonttype'] = 42

d = import_data()
df = create_df(d)

maxResp = d['maxResponseWaitFrames'][()]   

    
y, X = dmatrices('resp ~ rewDir + mask', data=df, return_type='dataframe')

mod = sm.OLS(y,X)

res = mod.fit()

res.summary()
    
#onehotencode the categorical variables (resp, dir))
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
 
#List of (name, transformer, column(s)) tuples
ct = ColumnTransformer(
        [('encode1', OneHotEncoder(df), 'rewDir'), ('encode2', OneHotEncoder(df), 'resp')], remainder='passthrough')


df_scaled = pd.DataFrame(ct.fit_transform(df), columns=[0,1])
    
    