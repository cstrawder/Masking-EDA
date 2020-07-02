# -*- coding: utf-8 -*-
"""
Created on Tue Jun 30 16:24:15 2020

@author: chelsea.strawder
"""

from dataAnalysis import import_data, create_df
import matplotlib.pyplot as plt
import numpy as np

d = import_data()
df = create_df(d)

trialStart = d['trialStartFrame'][:]
trialEnd = d['trialEndFrame'][:]
wheelPos = d['deltaWheelPos'][:]

bigWheel = [i for i, (start, end) in enumerate(zip(trialStart, trialEnd)) if abs(np.max(wheelPos[start:end]))>.2]

for i in bigWheel[:10]:
    plt.figure()
    plt.plot(wheelPos[trialStart[i]:trialEnd[i]], label='wheel')
    plt.plot(df.loc[i, 'trialFrameIntervals'], label='fi')
    plt.title(df.mouse + ' ' + str(i))
    for j, x in enumerate(df.loc[i, 'trialFrameIntervals']):
        if x>.016:
            plt.vlines(j, -.5, .5, ls='--')   

    plt.legend()
    plt.tight_layout()
    
    
    
plt.figure()
plt.plot(wheelPos, alpha=.5, label='wheel')
plt.plot(d['frameIntervals'][:], label='fi', color='k')
plt.legend()
for e,f in enumerate(d['frameIntervals'][:]):
    if f>.018:
        plt.plot(e, .4, 'ko', alpha=.5, markersize=4)