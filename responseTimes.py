# -*- coding: utf-8 -*-
"""
Created on Thu Aug 22 12:56:20 2019

@author: chelsea.strawder

Creats dataframe of response times per trial, by side, and plots distributions - 
including quiescent period violations 
(how quickly they turn after stim onset and/or goTone)

Use this to determine which trials to not include in analysis (move before 180 ms)

"""

import fileIO, h5py
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import scipy.signal
import seaborn as sns 
from freedmanDiaconis import freedman_diaconis



f = fileIO.getFile(rootDir=r'\\allen\programs\braintv\workgroups\nc-ophys\corbettb\Masking')
d = h5py.File(f)

trialResponse = d['trialResponse'][()]
end = len(trialResponse)
trialRewardDirection = d['trialRewardDir'][:end]
trialTargetFrames = d['trialTargetFrames'][:end]
trialStimStartFrame = d['trialStimStartFrame'][:]
trialResponseFrame = d['trialResponseFrame'][:end]    #if they don't respond, then nothing is recorded here - this limits df to length of this variable
trialOpenLoopFrames = d['trialOpenLoopFrames'][:end]
quiescentMoveFrames = d['quiescentMoveFrames'][:]
trialEndFrame = d['trialEndFrame'][:end]
deltaWheel = d['deltaWheelPos'][:]   # has wheel movement for every frame of session

for i, trial in enumerate(trialTargetFrames):
    if trial==0:
        trialRewardDirection[i] = 0

data = list(zip(trialRewardDirection, trialResponse, trialStimStartFrame, trialResponseFrame))
index = range(len(trialResponse))

df = pd.DataFrame(data, index=index, columns=['rewDir', 'resp', 'stimStart', 'respFrame'])

responseTime = []

for i, (start, resp) in enumerate(zip(trialStimStartFrame, trialResponseFrame)):
        respTime = (deltaWheel[start:resp])
        responseTime.append(respTime)

cumRespTime = []
for i, time in enumerate(responseTime):
    time = np.cumsum(time)
    cumRespTime.append(time)
    
rxnTimes=[]         
for resp, time in zip(trialResponse, cumRespTime):
    rxntime = []
    if resp==1:
        for x in time:
            if abs(x)<abs(2):
                rxntime.append(x)
    rxnTimes.append(rxntime)
   
df['reactionTime'] = [len(n) for n in rxnTimes]

df[(df['rewDir']!=0) & (df['resp']==1)]

plt.hist(df['reactionTime'])
        

for i, (time, resp) in enumerate(zip(cumRespTime, df['resp'])):
    if i<50:
        if resp==1:
            fig, ax = plt.subplots()
            plt.plot(time)
            plt.plot(0, len(time))
            plt.axvline(x=24, ymin=0, ymax=1, c='k', ls='--', alpha=.5)
            plt.title('-'.join(f.split('_')[-3:-1] + [str(i)]))
        
    
    
    response = np.where(respTime<respTime[0]-1)
    respTime+=len(respTime[respTime>1])

df['responseTime'] = responseTime

df['trialLength'] = (trialResponseFrame-trialStimStartFrame)

df['respTime'] = [len(i) for i in responseTime[i>1] if len(i)>0]

newTimes=[] 
rxnTimes=[]         
for resp, time in zip(trialResponse, responseTime):
    newtime = []
    rxntime = []
    if resp==1:
        for x in time:
            if abs(x)>abs(3):
                newtime.append(x)
            else:
                rxntime.append(x)
                
    newTimes.append(newtime)
    rxnTimes.append(rxntime)
    
df['newTimes'] = [len(m) for m in newTimes]
df['reactionTime'] = [len(n) for n in rxnTimes]
            
#encoderAngle = d['rotaryEncoderRadians'][:]
#reactionThresh = 0.1
#reactionTime = np.full(trialResponse.size,np.nan)

#for trial,(start,end) in enumerate(zip(trialStimStartFrame,trialEndFrame)):
#    r = np.where(np.absolute(deltaWheel[start:end])>reactionThresh)[0]
#    if any(r):
#        reactionTime[trial] = r[0]/120


rightTrials = df[df['rewDir']==1]
rightCorrect = rightTrials[rightTrials['resp']==1]

leftTrials = df[df['rewDir']==-1]
leftCorrect = leftTrials[leftTrials['resp']==1]    #need to take delta wheel into account, to know when they started moving the wheel 

rightArray = np.array(rightCorrect['responseTime'])
leftArray = np.array(leftCorrect['responseTime'])

rBins = freedman_diaconis(rightArray, returnas='bins')
lBins = freedman_diaconis(leftArray, returnas='bins')

totalTrials = df[df['resp']==1]
totalTrials = totalTrials[totalTrials['rewDir']!=0]
totalArray = np.array(totalTrials['responseTime'])
# does wheel pos reset for each trial start?? ask Sam


#need to take delta wheel into account, to know when they started moving the wheel 
 
 
rightArray = np.array(rightCorrect['newTimes'])
leftArray = np.array(leftCorrect['newTimes'])

rBins = freedman_diaconis(rightArray, returnas='bins')
lBins = freedman_diaconis(leftArray, returnas='bins')

totalTrials = df[df['resp']==1]
totalTrials = totalTrials[totalTrials['rewDir']!=0]
totalArray = np.array(totalTrials['newTimes'])


#fig, ax = plt.subplots()
#plt.hist(rightCorrect['responseTime'], bins=rBins, rwidth=4.1, color='r', alpha=.5)   # choose bin-width based on freedman-diaconis
#plt.hist(leftCorrect['responseTime'], bins=lBins, color='b', alpha=.5)
#plt.axvline(np.median(leftCorrect['responseTime']), c='b', ls='--')
#plt.axvline(np.mean(rightCorrect['responseTime']), c='r', ls='--')    # mean or median?

plt.figure()
sns.distplot(rightArray)
sns.distplot(leftArray)
plt.title('Distribution of response times by side:  ' + '-'.join(f.split('_')[-3:-1]))
plt.figure()
sns.distplot(totalArray, color='r')

# use gaussian KDE

 

'''want:
rew Dir so we know what trial type it was (L or R)
trial target frames so we know which trials were nogos
trialResponse so we know if they answered correctly 
stimstart so we know when the stim came on screen
trialResponseFrames so we know when they responded
deltaWheel bc we want to know WHEN they started moving the wheel and how quickly they moved it to center - tis is the response time
stimStart and Resp create a window within which deltawheal matters 

want to plot a distribution of both trial types and estimate parameters for each side 
for response time, it would be great to know time from moving wheel to hitting normRew

qperiod:
trialstartframes, openloop, quiescentframes (scalar), quiescent moveframes 
(frames in which movement ended/restarted q period) ** think about this one more
why do we want this plot?

nogos:
distance and direction turned for nogo, as well as responsetime'''

