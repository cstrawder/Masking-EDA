# -*- coding: utf-8 -*-
"""
Created on Thu Jan 16 14:36:15 2020

@author: svc_ccg

Plotting wheel traces as a function of SOA, independent target spatial locations
this combines masking trials for a single mouse (consc masking days)
"""

import numpy as np
import h5py, os
from matplotlib import pyplot as plt
import pandas as pd 
import datetime
import matplotlib.style
import matplotlib as mpl
import scipy.signal 
from behaviorAnalysis import formatFigure
from ignoreTrials import ignore_trials

mpl.rcParams['pdf.fonttype']=42

mpl.style.use('classic')


f = fileIO.getFile(rootDir=r'\\allen\programs\braintv\workgroups\nc-ophys\corbettb\Masking')
d = h5py.File(f)
   
frameRate = d['frameRate'][()]
trialEndFrames = d['trialEndFrame'][:]
trialStartFrames = d['trialStartFrame'][:trialEndFrames.size]
trialStimStartFrames = d['trialStimStartFrame'][:trialEndFrames.size]
trialRewardDirection = d['trialRewardDir'][:trialEndFrames.size]
trialResponse = d['trialResponse'][:trialEndFrames.size]
deltaWheel = d['deltaWheelPos'][:]
trialOpenLoopFrames = d['trialOpenLoopFrames'][:]
trialResponseFrames = d['trialResponseFrame'][:]
trialMaskOnset = d['trialMaskOnset'][:]
maskContrast = d['trialMaskContrast'][:]

preStimFrames = trialStimStartFrames-trialStartFrames if 'trialStimStartFrame' in d else np.array([d['preStimFrames'][:]]*trialStartFrames.size)

trialStartFrames += preStimFrames    
    
nogo = d['trialTargetFrames'][:-1]==0

ignoreTrials = ignore_trials(d)

postTrialFrames = 0 if d['postRewardTargetFrames'][()]>0 else 1 #make sure we have at least one frame after the reward

data = list(zip(trialRewardDirection, trialResponse, trialStartFrames, 
                trialStimStartFrame, trialResponseFrame, trialEndFrames,
                trialMaskOnset, maskContrast))
index = range(len(trialResponse))

df = pd.DataFrame(data, index=index, columns=['rewDir', 'resp', 'trialStart', 'stimStart', 'respFrame', 'endFrame', 'soa', 'mask'])


fig, ax = plt.subplots()

# turnRightTrials == stim presented on L, turn right - viceversa for turnLeftTrials - or for orientation, turn right
nogoTrials = []
turnRightTrials = []
turnLeftTrials = []
maskedTrials=[]

framesToShowBeforeStart = 30
maxTrialFrames = max(trialEndFrames-trialStartFrames+framesToShowBeforeStart+postTrialFrames)
trialTime = (np.arange(maxTrialFrames)-framesToShowBeforeStart)/frameRate  # evenly-spaced array of times for x-axis
#for i, (trialStart, trialEnd, rewardDirection, resp) in enumerate(zip(
#        trialStartFrames, trialEndFrames, trialRewardDirection, trialResponse)):
#    if i>0 and i<len(trialStartFrames):
#        if i in ignoreTrials:
#            pass
#        else:
#            trialWheel = np.cumsum(deltaWheel[
#                    trialStart-framesToShowBeforeStart:
#                        trialStart-framesToShowBeforeStart + maxTrialFrames])
#            trialWheel -= trialWheel[0]
#            trialreward = np.where((trialResponseFrames>trialStart)&(trialResponseFrames<=trialEnd))[0]
#            rewardFrame = trialResponseFrames[trialreward[0]]-trialStart+framesToShowBeforeStart if len(trialreward)>0 else None
#            if nogo[i]:
#                ax.plot(trialTime[:trialWheel.size], trialWheel, 'g', alpha=0.2)   # plotting no-go trials
#                if rewardFrame is not None:
#                    ax.plot(trialTime[rewardFrame], trialWheel[rewardFrame], 'go')
#                nogoTrials.append(trialWheel)
#            elif rewardDirection>0:
#                ax.plot(trialTime[:trialWheel.size], trialWheel, 'r', alpha=0.2)  #plotting right turning 
#                if rewardFrame is not None:
#                    ax.plot(trialTime[rewardFrame], trialWheel[rewardFrame], 'ro')
#                turnRightTrials.append(trialWheel)
#            elif rewardDirection<0:
#                ax.plot(trialTime[:trialWheel.size], trialWheel, 'b', alpha=0.2)   # plotting left turning 
#                if rewardFrame is not None:
#                    ax.plot(trialTime[rewardFrame], trialWheel[rewardFrame], 'bo')
#                turnLeftTrials.append(trialWheel)
#
#turnRightTrials = pd.DataFrame(turnRightTrials).fillna(np.nan).values
#turnLeftTrials = pd.DataFrame(turnLeftTrials).fillna(np.nan).values
#nogoTrials = pd.DataFrame(nogoTrials).fillna(np.nan).values
#ax.plot(trialTime[:turnRightTrials.shape[1]], np.nanmean(turnRightTrials,0), 'r', linewidth=3)
#ax.plot(trialTime[:turnLeftTrials.shape[1]], np.nanmean(turnLeftTrials, 0), 'b', linewidth=3)
#ax.plot(trialTime[:nogoTrials.shape[1]], np.nanmean(nogoTrials,0), 'k', linewidth=3)
#ax.plot([trialTime[framesToShowBeforeStart+openLoopFrames]]*2, ax.get_ylim(), 'k--')

#name_date = str(data).split('_')    
#
#
#formatFigure(fig, ax, xLabel='Time from stimulus onset (s)', 
#             yLabel='Wheel Position (pix)', title=name_date[-3:-1] + subtitle)
#plt.tight_layout()

maskContrast = d['trialMaskContrast'][:len(trialResponse)]  #plot mask only trials 
maskOnset = d['trialMaskOnset'][:len(trialResponse)]
fig, ax = plt.subplots()
nogoMask = []
rightMask = [[],[],[],[]]
leftMask = []
for i, (trialStart, trialEnd, rewardDirection, mask, soa, resp) in enumerate(zip(
        trialStartFrames, trialEndFrames, trialRewardDirection, maskContrast, maskOnset, trialResponse)):
    if i>0 and i<len(trialStartFrames):
        trialWheel = np.cumsum(
                deltaWheel[trialStart-framesToShowBeforeStart:trialStart-framesToShowBeforeStart + maxTrialFrames
                           ])
        trialWheel -= trialWheel[0]
        trialreward = np.where((trialResponseFrames>trialStart)&(trialResponseFrames<=trialEnd))[0]
        rewardFrame = trialResponseFrames[trialreward[0]]-trialStart+framesToShowBeforeStart if len(trialreward)>0 else None
#        if nogo[i] and mask==0:
#            ax.plot(trialTime[:trialWheel.size], trialWheel, 'g', alpha=0.3)   # plotting no-go trials
#            if rewardFrame is not None:
#                ax.plot(trialTime[rewardFrame], trialWheel[rewardFrame], 'go')
#            nogoMask.append(trialWheel)
##        elif nogo[i] and mask>0:
#            ax.plot(trialTime[:trialWheel.size], trialWheel, 'm', alpha=.3)  #plotting mask only trials 
#        else:
        if rewardDirection>0 and mask>0:
            if soa==2: 
                ax.plot(trialTime[:trialWheel.size], trialWheel, 'b', alpha=0.2)  #plotting right turning 
                if rewardFrame is not None:
                    ax.plot(trialTime[rewardFrame], trialWheel[rewardFrame], 'bo')
                rightMask[0].append(trialWheel)
            elif soa==6:
                ax.plot(trialTime[:trialWheel.size], trialWheel, 'g', alpha=0.2)  #plotting right turning 
                if rewardFrame is not None:
                    ax.plot(trialTime[rewardFrame], trialWheel[rewardFrame], 'go')
            
        elif rewardDirection<0 and mask>0:
            ax.plot(trialTime[:trialWheel.size], trialWheel, 'b', alpha=0.2)   # plotting left turning 
            if rewardFrame is not None:
                ax.plot(trialTime[rewardFrame], trialWheel[rewardFrame], 'bo')
            leftMask.append(trialWheel)
rightMask = pd.DataFrame(rightMask).fillna(np.nan).values
leftMask = pd.DataFrame(leftMask).fillna(np.nan).values
nogoMask = pd.DataFrame(nogoMask).fillna(np.nan).values
ax.plot(trialTime[:rightMask.shape[1]], np.nanmean(rightMask,0), 'r', linewidth=3)
ax.plot(trialTime[:leftMask.shape[1]], np.nanmean(leftMask, 0), 'b', linewidth=3)
ax.plot(trialTime[:nogoMask.shape[1]], np.nanmean(nogoMask,0), 'k', linewidth=3)
ax.plot([trialTime[framesToShowBeforeStart+openLoopFrames]]*2, ax.get_ylim(), 'k--')

    
    formatFigure(fig, ax, xLabel='Time from stimulus onset (s)', 
                 yLabel='Wheel Position (pix)', title=name_date[-3:-1] + [ 'Mask Trials'])
    plt.tight_layout()

