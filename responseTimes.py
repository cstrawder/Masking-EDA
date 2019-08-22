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


f = fileIO.getFile(rootDir=r'\\allen\programs\braintv\workgroups\nc-ophys\corbettb\Masking')
d = h5py.File(f)

trialResponse = d['trialResponse'].value
end = len(trialResponse)
trialRewardDirection = d['trialRewardDir'][:end]
trialTargetFrames = d['trialTargetFrames'][:end]
trialStimStartFrame = d['trialStimStartFrame'][:end]
trialResponseFrame = d['trialResponseFrame'][:end]
trialOpenLoopFrames = d['trialOpenLoopFrames'][:end]
deltaWheel = d['deltaWheelPos'].value

data = zip(trialTargetFrames, trialRewardDirection, trialResponse, trialStimStartFrame, trialResponseFrame, trialOpenLoopFrames)

df = pd.DataFrame(data, index=range(len(trialResponse)), columns=['targetFrames', 'rewDir', 'resp', 'stimStart', 'respFrame', 'trialOpenLoopFrames'])

print(trialResponseFrame-trialStimStartFrame-trialOpenLoopFrames) * 8.3

'''want:
rew Dir so we know what trial type it was (L or R)
trial target frames so we know which trials were nogos
trialResponse so we know if they answered correctly 
stimstart so we know when the stim came on screen
trialResponseFrames so we know time to response

want to plot a distribution of both trial types and estimate parameters for each side 


qperiod:
trialstartframes, openloop, quiescentframes (scalar), quiescent moveframes (frames in which movement ended/restarted q period) ** think about this one more


nogos:
distance and direction turned for nogo, as well as responsetime