# -*- coding: utf-8 -*-
"""
Created on Wed Sep 04 17:07:09 2019

@author: svc_ccg
"""

import numpy as np
import h5py, os
from matplotlib import pyplot as plt
from behaviorAnalysis import formatFigure
import fileIO


f = fileIO.getFile(rootDir=r'\\allen\programs\braintv\workgroups\nc-ophys\corbettb\Masking')
d = h5py.File(f)

trialResponse = d['trialResponse'][()]
trialRewardDirection = d['trialRewardDir'][:len(trialResponse)]    # leave off last trial, ended session before answer 

maskOnset = d['maskOnset'][()]                  # list of ind lengths, does not include no-gos (0)
trialMaskOnset = d['trialMaskOnset'][:len(trialResponse)]
trialTargetFrames = d['trialTargetFrames'][:len(trialResponse)]         # also leaves off last trial


# [R stim/left-turning] , [L stim/rightturning]
trialRewardDirection = d['trialRewardDir'][:-1]    # leave off last trial, ended session before answer 
trialResponse = d['trialResponse'][:]
maskOnset = d['maskOnset'][:]                  # list of ind lengths, does not include no-gos (0)
trialMaskOnset = d['trialMaskOnset'][:-1] 
trialTargetFrames = d['trialTargetFrames'][:len(trialResponse)] 
maskContrast = d['trialMaskContrast'][:len(trialResponse)]      # also leaves off last trial


# [L stim/right turning] , [R stim/left turning]
hits = [[],[]]
misses = [[], []]
noResps = [[],[]]

for i, direction in enumerate([1,-1]):
    directionResponses = [trialResponse[(trialRewardDirection==direction) & (trialMaskOnset == soa)] for soa in maskOnset]
    hits[i].append([np.sum(drs==1) for drs in directionResponses])
    misses[i].append([np.sum(drs==-1) for drs in directionResponses])
    noResps[i].append([np.sum(drs==0) for drs in directionResponses])

hits = np.squeeze(np.array(hits))
misses = np.squeeze(np.array(misses))
noResps = np.squeeze(np.array(noResps))
totalTrials = hits+misses+noResps


maskOnly = len(trialResponse[(maskContrast>0) & (trialTargetFrames==0)])
maskOnlyCorr = len(trialResponse[(maskContrast>0) & (trialTargetFrames==0) & (trialResponse==1)])
maskMove = maskOnly - maskOnlyCorr

nogoTurnDir = []
  
stimStart = d['trialStimStartFrame'][:]
trialOpenLoop = d['trialOpenLoopFrames'][:len(trialResponse)]
trialRespFrames = d['trialResponseFrame'][:]
deltaWheel = d['deltaWheelPos'][:]

stimStart = stimStart[(trialTargetFrames==0) & (maskContrast>0)]
trialRespFrames = trialRespFrames[(trialTargetFrames==0) & (maskContrast>0)]
trialOpenLoop = trialOpenLoop[(trialTargetFrames==0) & (maskContrast>0)]
trialResp = trialResponse[(trialTargetFrames==0) & (maskContrast>0)]

stimStart += trialOpenLoop

startWheelPos = []
endWheelPos = []

# we want to see which direction they moved the wheel on mask-only trials (nogo with mask)
for i, (start, end, resp) in enumerate(zip(stimStart, trialRespFrames, trialResp)):   
    if (resp==-1):
        endWheelPos.append(deltaWheel[end])
        startWheelPos.append(deltaWheel[start])

endWheelPos = np.array(endWheelPos)
startWheelPos = np.array(startWheelPos)   
wheelPos = endWheelPos - startWheelPos

for i in wheelPos:
    if i>0:
        nogoTurnDir.append(1)
    else:
        nogoTurnDir.append(-1)

nogoTurnDir = np.array(nogoTurnDir)

nogoR = sum(nogoTurnDir[nogoTurnDir==1])
nogoL = sum(nogoTurnDir[nogoTurnDir==-1])*-1



for nogoNum, nogoDenom, num, denom, title in zip(
        [maskOnlyCorr, maskOnlyCorr,maskMove],                              
        [maskOnly, maskOnly, maskOnly],
        [hits, hits, hits+misses],
        [totalTrials, hits+misses, totalTrials],
        ['Percent Correct', 'Percent Correct Given Response', 'Total response rate']
        ):
    fig, ax = plt.subplots()

    ax.plot(np.unique(maskOnset), num[0]/denom[0], 'bo-')  #here [0] is right stim/left turning trials and [1] is left stim/r turning
    ax.plot(np.unique(maskOnset), num[1]/denom[1], 'ro-')

    ax.plot(np.unique(maskOnset), num[0]/denom[0], 'ro-')  #here [0] is right trials and [1] is left
    ax.plot(np.unique(maskOnset), num[1]/denom[1], 'bo-')
    ax.plot(np.unique(maskOnset), (num[0]+num[1])/(denom[0]+denom[1]), 'ko--', alpha=.5)  #plots the combined average 
    #ax.text(np.unique(maskOnset), num[0]/denom[0], texts) 
    #ax.plot(0, nogoNum/nogoDenom, 'go')
#    if nogoNum == maskMove:
#        ax.plot(0, nogoR/maskOnly, 'r>', ms=8)   #plot the side that was turned in no-go with an arrow in that direction
#        ax.plot(0, nogoL/maskOnly, 'b<', ms=8)

    formatFigure(fig, ax, xLabel='SOA (frames)', yLabel='percent trials', 
                 title=title + " :  " + '-'.join(f.split('_')[-3:-1]))
    ax.set_xlim([-2, maskOnset[-1]+2])
    ax.set_ylim([0,1.01])
    ax.set_xticks(np.unique(trialMaskOnset))
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.tick_params(direction='out',top=False,right=False)

    #ax.text(np.unique(maskOnset), (num[0]/denom[0]), str(denom))
            
    if 0 in trialTargetFrames:   
        a = ax.get_xticks().tolist()
        a = [int(i) for i in a]    
        a[0]='mask only' 
        ax.set_xticklabels(a)