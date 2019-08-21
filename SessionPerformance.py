# -*- coding: utf-8 -*-
"""
Created on Tue Aug 13 11:20:20 2019

@author: svc_ccg
"""

from __future__ import division
import h5py
import fileIO
import numpy as np
import pandas as pd 
from matplotlib import pyplot as plt
from nogo_turn import nogo_turn

"""
plots the choices (in temporal order) over the length of a session

"""

f = fileIO.getFile(rootDir=r'\\allen\programs\braintv\workgroups\nc-ophys\corbettb\Masking')
d = h5py.File(f)

#pull necessary variable arrays from hdf5 file

trialResponse = d['trialResponse'].value
trialResponseFrame = d['trialResponseFrame'][:len(trialResponse)]
trialTargetFrames= d['trialTargetFrames'][:len(trialResponse)]   # to identify nogos 
trialRewardDirection = d['trialRewardDir'][:len(trialResponse)]

for i, trial in enumerate(trialTargetFrames):
    if trial==0:
        trialRewardDirection[i] = 0 

data = zip(trialRewardDirection, trialResponse)

df = pd.DataFrame(data, index=trialResponseFrame, columns=['rewardDir', 'trialResp'])
df['CumPercentCorrect'] = df['trialResp'].cumsum()

index = df.index
values = df.values

#function? 
rightCorr = df[(df['trialResp']==1) & (df['rewardDir']==1)]
leftCorr = df[(df['trialResp']==1) & (df['rewardDir']==-1)]
nogoCorr = df[(df['trialResp']==1) & (df['rewardDir']==0)]

rightMiss = df[(df['trialResp']==-1) & (df['rewardDir']==1)]
leftMiss = df[(df['trialResp']==-1) & (df['rewardDir']==-1)]
nogoMiss = df[(df['trialResp']==-1) & (df['rewardDir']==0)]

rightNoResp = df[(df['trialResp']==0) & (df['rewardDir']==1)]
leftNoResp = df[(df['trialResp']==0) & (df['rewardDir']==-1)]

# for i in nogoMiss:
# add in code that determines which direction was turned
# and plot by half-filling marker that color
    
no_gos = nogo_turn(d, ignoreRepeats=False)
nogoMiss = pd.DataFrame(nogoMiss['CumPercentCorrect'])

plt.figure()
plt.plot(df['CumPercentCorrect'])
plt.plot(rightCorr['CumPercentCorrect'], 'r^', ms=10)
plt.plot(leftCorr['CumPercentCorrect'], 'b^', ms=10)
plt.plot(nogoCorr['CumPercentCorrect'], 'g^', ms=10)

plt.plot(rightMiss['CumPercentCorrect'], 'rv', ms=10)
plt.plot(leftMiss['CumPercentCorrect'], 'bv', ms=10)
for nogo, x, direction in zip(no_gos, nogoMiss.index, nogoMiss['CumPercentCorrect']):
    if nogo > 0:
        plt.plot(x, direction, 'gv', ms=10, markerfacecoloralt='red', fillstyle='left')  # set marker face fill style to reflect direction turned (e.g. half red)
    elif nogo < 0:
        plt.plot(x, direction, 'gv', ms=10, markerfacecoloralt='blue', fillstyle='right')
plt.plot(rightNoResp['CumPercentCorrect'], 'o', mec='r', mfc='none',  ms=10)
plt.plot(leftNoResp['CumPercentCorrect'], 'o', mec='b', mfc='none', ms=10)


plt.title(f.split('_')[-3:-1])
plt.show()


