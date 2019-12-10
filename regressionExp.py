# -*- coding: utf-8 -*-
"""
Created on Mon Nov 18 11:15:05 2019

@author: chelsea.strawder

This gives you a nice dataframe of the session data for an individual mouse

Describe model, fit model, and summarize model

Look at prevResp, prevIncorrect, trial number (better at start/learning over time)


"""
import fileIO, h5py
import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
import scipy 
from patsy import dmatrices
import statsmodels.api as sm

from rxnTimesFunc import ignore_trials
from sessionData import session

matplotlib.rcParams['pdf.fonttype'] = 42

f = fileIO.getFile(rootDir=r'\\allen\programs\braintv\workgroups\nc-ophys\corbettb\Masking')
d = h5py.File(f)

trialResponse = d['trialResponse'][()]
end = len(trialResponse)

trialRewardDirection = d['trialRewardDir'][:end]
trialTargetFrames = d['trialTargetFrames'][:end]
trialStimStartFrame = d['trialStimStartFrame'][:]
trialResponseFrame = d['trialResponseFrame'][:end]    #if they don't respond, then nothing is recorded here - this limits df to length of this variable
trialOpenLoopFrames = d['trialOpenLoopFrames'][:end]
trialMaskOnset = d['trialMaskOnset'][:end]
openLoop = d['openLoopFramesFixed'][()]
quiescentMoveFrames = d['quiescentMoveFrames'][:]
trialEndFrame = d['trialEndFrame'][:end]
deltaWheel = d['deltaWheelPos'][:]                      # has wheel movement for every frame of session
maxResp = d['maxResponseWaitFrames'][()]   
maskContrast = d['trialMaskContrast'][:end]==1
maskOnset = d['maskOnset'][()]
prevTrialIncorrect = d['trialRepeat'][:end]  # this will be most useful for guessing 

for i, trial in enumerate(trialTargetFrames):  # this is needed for older files nogos are randomly assigned a dir
    if trial==0:
        trialRewardDirection[i] = 0


# length of time from start of stim to response (or no response) for each trial
trialTimes = []   
for i, (start, resp) in enumerate(zip(trialStimStartFrame, trialResponseFrame)):
        respTime = (deltaWheel[start:resp])
        trialTimes.append(respTime)

#since deltawheel provides the difference in wheel mvmt from trial to trial
#taking the cumulative sum gives the actual wheel mvmt and plots as a smooth curve
#which we can then analyze to find when they made a response 
cumRespTimes = []
for i, time in enumerate(trialTimes):
    time = np.cumsum(time)
    smoothed = scipy.signal.medfilt(time, kernel_size=5)
    cumRespTimes.append(smoothed)

trialResponseTimes = []
for i in cumRespTimes:
    trialResponseTimes.append(len(i))

rxnTimes = []
for i, times in enumerate(cumRespTimes):
   # time2 = time2[::-1]
    mask = (abs(times[:])>10)
    val = np.argmax(mask)
   # t = len(time2) - val
    rxnTimes.append(val)
       
#    np.argmax(abs(time2)>50)   #this is in pixels, calculated from Monitor norm and quiescent move threshold (.025)


data = list(zip(trialRewardDirection, trialResponse, trialStimStartFrame, trialResponseFrame))
index = range(len(trialResponse))

#create the dataframe
df = pd.DataFrame(data, index=index, columns=['rewDir', 'resp', 'stimStart', 'respFrame'])
df['trialLength'] = [len(t) for t in trialTimes]
df['reactionTime'] = rxnTimes
if len(maskOnset)>0:
    df['mask'] = maskContrast
    df['soa'] = trialMaskOnset
    
df['prevTrial'] = prevTrialIncorrect


y, X = dmatrices('resp ~ rewDir + prevTrial + mask', data=df, return_type='dataframe')

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
    
    