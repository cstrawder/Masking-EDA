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

data = zip(trialResponse, trialTargetFrames, trialRewardDirection)



#create a dataframe 
#add columns measuring performance (cumulative % correct?)
#plot the dataframe

df = pd.DataFrame(data, index=trialResponseFrame, columns=['trialResp', 'trialTargetFrames', 'targetLoc'])
df['CumPercentCorrect'] = df['trialResp'].cumsum()


plt.figure()
plt.plot(df['CumPercentCorrect'])

for i, j in enumerate(df['targetLoc']):
    if j==1:
        plt.plot(trialResponseFrame[i], df.iloc['CumPercentCorrect'], 'ro')
    elif j==-1:
        plt.plot(trialResponseFrame[i], df.loc[df.iloc['CumPercentCorrect'] == i], 'bo')

plt.title(f.split('_')[-3:-1])
plt.show()
 #, trialRewardDirection, trialTargetFrames)