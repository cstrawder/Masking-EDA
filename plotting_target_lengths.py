# -*- coding: utf-8 -*-
"""
Created on Mon Jul 08 18:07:23 2019

@author: svc_ccg
"""

from __future__ import division
import numpy as np
import h5py, os
from matplotlib import pyplot as plt
from behaviorAnalysis import formatFigure
import fileIO
import scipy.stats


f = fileIO.getFile(rootDir=r'\\allen\programs\braintv\workgroups\nc-ophys\corbettb\Masking')
d = h5py.File(f)

trialRewardDirection = d['trialRewardDir'].value[:-1]
trialResponse = d['trialResponse'].value
targetLengths = d['targetFrames'].value   # does not include no-gos


trialTargetFrames = d['trialTargetFrames'][:-1]

# [R stim] , [L stim]
hits = [[],[]]
misses = [[], []]
noResps = [[],[]]

for i, direction in enumerate([-1,1]):
    directionResponses = [trialResponse[(trialRewardDirection==direction) & (trialTargetFrames == tf)] for tf in targetLengths]
    hits[i].append([np.sum(drs==1) for drs in directionResponses])
    misses[i].append([np.sum(drs==-1) for drs in directionResponses])
    noResps[i].append([np.sum(drs==0) for drs in directionResponses])

hits = np.squeeze(np.array(hits))
misses = np.squeeze(np.array(misses))
noResps = np.squeeze(np.array(noResps))
totalTrials = hits+misses+noResps

# here call no_go movement function? 

if 0 in trialTargetFrames:
    no_goTotal = len(trialTargetFrames[trialTargetFrames==0])
    no_goCorrect = len(trialResponse[(trialResponse==1) & (trialTargetFrames==0)])
    no_goMove = no_goTotal - no_goCorrect
    
    no_goTurnDir = []
    
    stimStart = d['trialStimStartFrame'].value[trialTargetFrames==0]
    trialRespFrames = d['trialResponseFrame'].value[trialTargetFrames==0]
    trialOpenLoop = d['trialOpenLoopFrames'].value[trialTargetFrames==0]
    deltaWheel = d['deltaWheelPos'].value
    no_goResp = trialResponse[trialTargetFrames==0]
    
    stimStart += trialOpenLoop
    
    startWheelPos = []
    endWheelPos = []
    
    # we want to see which direction they moved the wheel on an incorrect no-go
    for (start, end, resp) in zip(stimStart, trialRespFrames, no_goResp):   
        if resp==-1:
            endWheelPos.append(deltaWheel[end])
            startWheelPos.append(deltaWheel[start])
        
    endWheelPos = np.array(endWheelPos)
    startWheelPos = np.array(startWheelPos)   
    wheelPos = endWheelPos - startWheelPos
    
    for i in wheelPos:
        if i >0:
            no_goTurnDir.append(1)
        else:
            no_goTurnDir.append(-1)
    
    no_goTurnDir = np.array(no_goTurnDir)

no_goR = sum(no_goTurnDir[no_goTurnDir==1])
no_goL = sum(no_goTurnDir[no_goTurnDir==-1])*-1

#misses = np.insert(misses, 0, [no_goR, no_goL], axis=1)  #add the no_go move trials to misses array 
  

for no_goNum, no_goDen, num, denom, title in zip([no_goCorrect, no_goCorrect,no_goMove],
                                                 [no_goTotal, no_goTotal, no_goTotal],
                                                [hits, hits, hits+misses], 
                                                [totalTrials, hits+misses, totalTrials],
                                                 ['Percent Correct', 'Percent Correct Given Response', 'Total response rate']):
    fig, ax = plt.subplots()
    ax.plot(np.unique(targetLengths), num[0]/denom[0], 'bo-')
    ax.plot(np.unique(targetLengths), num[1]/denom[1], 'ro-')
    ax.plot(0, no_goNum/no_goDen, 'ko')
    if no_goNum == no_goMove:
        ax.plot(0, no_goR/no_goMove, 'ro')
        ax.plot(0, no_goL/no_goMove, 'bo')
        
    #ax.annotate(denom, (np.unique(targetLengths), denom))
    
    '''chanceRates = [[[i/n for i in scipy.stats.binom.interval(0.95,n,0.5)] for n in h] for h in denom]
    chanceRates = np.array(chanceRates)
    for val, chanceR, chanceL in zip(np.unique(targetLengths), chanceRates[0], chanceRates[1]):
       plt.plot([val, val], chanceR, color='red', alpha=.5)     # 0 and 1 = R and L, respectively
       plt.plot([val+.2, val+.2], chanceL, color='blue', alpha=.5)'''
    formatFigure(fig, ax, xLabel='Target Length (frames)', yLabel='percent trials', 
                 title=title + " :  " + '-'.join(f.split('_')[-3:-1]))
    ax.set_xlim([-2, trialTargetFrames[0]+2])
    ax.set_ylim([0,1.01])
    ax.set_xticks(np.unique(trialTargetFrames))
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.tick_params(direction='out',top=False,right=False)


            
if 0 in trialTargetFrames:   
    a = ax.get_xticks().tolist()
    a = [int(i) for i in a]    
    a[0]='no-go' 
    ax.set_xticklabels(a)
    
    
    

