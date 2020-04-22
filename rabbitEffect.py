# -*- coding: utf-8 -*-
"""
Created on Tue Apr 21 16:08:34 2020

@author: chelsea.strawder

looking for Rabbit effect
will the response time be longer for a correct trial that follows an incorrect trial?

incorrect == turned the wrong way (not no resp)


"""

from dataAnalysis import import_data, create_df  # for now - won't need once function is complete
from dataAnalysis import wheel_trace_slice
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


d = import_data()
df = create_df()

trials = []
oppRabbit = []

for e, (prev, current) in enumerate(zip(df['resp'][:-1], df['resp'][1:])):
    if prev==-1 and current==1:
        if (df.loc[e, 'rewDir'] !=0) and (df.loc[e+1, 'rewDir'] !=0):
            trials.append((e, e+1))
    elif prev==1 and current==-1:
         if (df.loc[e, 'rewDir'] !=0) and (df.loc[e+1, 'rewDir'] !=0):
            oppRabbit.append((e, e+1))
        
        
prevIncorrect = [df.loc[time[0], 'outcomeTime'] for time in trials]
currentCorrect = [df.loc[time[1], 'outcomeTime'] for time in trials]

prevCorrect = [df.loc[time[0], 'outcomeTime'] for time in oppRabbit]
currIncorrect = [df.loc[time[1], 'outcomeTime'] for time in oppRabbit]
    
rabbitDf = pd.DataFrame()
rabbitDf['error'] = prevIncorrect
rabbitDf['correct'] = currentCorrect

plt.figure()
sns.barplot(data=rabbitDf)
plt.ylabel('Response Time')
plt.title('Response Time in Consecutive Trials')
plt.xlabel('Previous Trial | Next Trial')




oppDf = pd.DataFrame()
oppDf['correct'] = prevCorrect
oppDf['error'] = currIncorrect

plt.figure()
sns.barplot(data=oppDf)
plt.ylabel('Response Time')
plt.title('Response Times in Consecutive Trials')
plt.xlabel('Previous Trial | Next Trial')




prevCorr = []
prevIncorrect = []

for e, (prev, current) in enumerate(zip(df['resp'][:-1], df['resp'][1:])):
    if prev!=0 and current!=0:
        if prev==-1:
            if (df.loc[e, 'rewDir'] !=0) and (df.loc[e+1, 'rewDir'] !=0):
                prevIncorrect.append(df.loc[e+1, 'outcomeTime'])
        elif prev==1:
             if (df.loc[e, 'rewDir'] !=0) and (df.loc[e+1, 'rewDir'] !=0):
                prevCorr.append(df.loc[e+1, 'outcomeTime'])
            
        
rabbitt = pd.DataFrame()
rabbitt['prevIncorrect'] = prevIncorrect
rabbitt['prevCorrect'] = prevCorr




































