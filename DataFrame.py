# -*- coding: utf-8 -*-
"""
Created on Thu Jan 16 17:00:41 2020

@author: svc_ccg

creating a DF that we easily holds all the information
Need to be careful about frame rates!! 
"""

import h5py 
import fileIO
import pandas as pd
import numpy as np
import seaborn as sns
import scipy.signal
import scipy.stats
from behaviorAnalysis import formatFigure
from ignoreTrials import ignore_trials
import matplotlib.pyplot as plt

f = fileIO.getFile(rootDir=r'\\allen\programs\braintv\workgroups\nc-ophys\corbettb\Masking')
d = h5py.File(f)

frameRate = d['frameRate'][()]
trialResponse = d['trialResponse'][()]
end = len(trialResponse)

trialRewardDirection = d['trialRewardDir'][:end]
trialTargetFrames = d['trialTargetFrames'][:end]
trialStartFrames = d['trialStartFrame'][:end]
trialEndFrames = d['trialEndFrame'][:end]
trialStimStartFrame = d['trialStimStartFrame'][:]
trialResponseFrame = d['trialResponseFrame'][:end]    #if they don't respond, then nothing is recorded here - this limits df to length of this variable
trialOpenLoopFrames = d['trialOpenLoopFrames'][:end]
trialMaskOnset = d['trialMaskOnset'][:end]
openLoop = d['openLoopFramesFixed'][()]
quiescentMoveFrames = d['quiescentMoveFrames'][:]
trialEndFrame = d['trialEndFrame'][:end]
deltaWheel = d['deltaWheelPos'][:]            
maxResp = d['maxResponseWaitFrames'][()]   
maskFrames = d['maskFrames'][()]
maskContrast = d['trialMaskContrast'][:end]>0
maskOnset = d['maskOnset'][()]
timeout = d['incorrectTimeoutFrames'][()]
nogoWait = d['nogoWaitFrames'][()]


preStimFramesFixed = d['preStimFramesFixed'][()]

preStimFrames = d['trialStimStartFrame'][:trialEndFrames.size]-trialStartFrames if 'trialStimStartFrame' in d else np.array([d['preStimFrames'][:]]*trialStartFrames.size)
trialStartFrames += preStimFrames    
nogo = d['trialTargetFrames'][:-1]==0

postTrialFrames = 0 if d['postRewardTargetFrames'][()]>0 else 1

def transfer(d):
    files = []
    for file in d.keys():
        if 'trial' in file:
            files.append(file)
    for i in files:
        return (str(file) = d[i][:])      
    
            
#trialWheel = np.cumsum(deltaWheel[trialStart-framesToShowBeforeStart:trialStart-framesToShowBeforeStart + maxTrialFrames])