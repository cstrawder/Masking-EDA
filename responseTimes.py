# -*- coding: utf-8 -*-
"""
Created on Thu Aug 22 12:56:20 2019

@author: chelsea.strawder

Creats dataframe of response times per trial, by side, and plots distributions - 
including quiescent period violations 
(how quickly they turn after stim onset and/or goTone)

"""

from __future__ import division
import fileIO, h5py
import numpy as np
import pandas as pd
import seaborn as sns 
from behaviorAnalysis import formatFigure
from freedmanDiaconis import freedman_diaconis


f = fileIO.getFile(rootDir=r'\\allen\programs\braintv\workgroups\nc-ophys\corbettb\Masking')
d = h5py.File(f)

trialResponse = d['trialResponse'].value
end = len(trialResponse)
trialRewardDirection = d['trialRewardDir'][:end]
trialTargetFrames = d['trialTargetFrames'][:end]
trialStimStartFrame = d['trialStimStartFrame'].value
trialResponseFrame = d['trialResponseFrame'][:end]    #if they don't respond, then nothing is recorded here - this limits df to length of this variable
trialOpenLoopFrames = d['trialOpenLoopFrames'][:end]
quiescentMoveFrames = d['quiescentMoveFrames'].value
trialEndFrame = d['trialEndFrame'][:end]
deltaWheel = d['deltaWheelPos'].value   # has wheel movement for every frame of session

for i, trial in enumerate(trialTargetFrames):
    if trial==0:
        trialRewardDirection[i] = 0

data = zip(trialRewardDirection, trialResponse, trialStimStartFrame, trialResponseFrame)

df = pd.DataFrame(data, index=range(len(trialResponse)), columns=['rewDir', 'resp', 'stimStart', 'respFrame'])

df['responseTime'] = (trialResponseFrame-trialStimStartFrame-trialOpenLoopFrames)*8.33

rightTrials = df[df['rewDir']==1]
rightCorrect = rightTrials[rightTrials['resp']==1]

leftTrials = df[df['rewDir']==-1]
leftCorrect = leftTrials[leftTrials['resp']==1]    #need to take delta wheel into account, to know when they started moving the wheel 

rightArray = np.array(rightCorrect['responseTime'])
leftArray = np.array(leftCorrect['responseTime'])






# does wheel pos reset for each trial start?? ask Sam



fig, ax = plt.subplots()
plt.hist(rightCorrect['responseTime'], bins=50, color='r', alpha=.5)   # choose bin-width based on freedman-diaconis
plt.hist(leftCorrect['responseTime'], bins=50, color='b', alpha=.5)
plt.axvline(np.median(leftCorrect['responseTime']), c='b', ls='--')
plt.axvline(np.mean(rightCorrect['responseTime']), c='r', ls='--')    # mean or median?


# use gaussian KDE



formatFigure(fig, ax, title='Response time for trial direction', xLabel='Response Time (ms)')


'''want:
rew Dir so we know what trial type it was (L or R)
trial target frames so we know which trials were nogos
trialResponse so we know if they answered correctly 
stimstart so we know when the stim came on screen
trialResponseFrames so we know time to response
deltaWheel bc we want to know when they started moving the wheel and how quickly they moved it to center

want to plot a distribution of both trial types and estimate parameters for each side 
for response time, it would be great to know time from moving wheel to hitting normRew

qperiod:
trialstartframes, openloop, quiescentframes (scalar), quiescent moveframes (frames in which movement ended/restarted q period) ** think about this one more


nogos:
distance and direction turned for nogo, as well as responsetime