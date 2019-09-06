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

trialRewardDirection = d['trialRewardDir'].value[:-1]    # leave off last trial, ended session before answer 
trialResponse = d['trialResponse'].value
maskOnset = d['maskOnset'].value                  # list of ind lengths, does not include no-gos (0)
trialMaskOnset = d['trialMaskOnset'][:-1] 
trialTargetFrames = d['trialTargetFrames'][:len(trialResponse)]         # also leaves off last trial


# [R stim] , [L stim]
hits = [[],[]]
misses = [[], []]
noResps = [[],[]]

for i, direction in enumerate([-1,1]):
    directionResponses = [trialResponse[(trialRewardDirection==direction) & (trialMaskOnset == soa)] for soa in maskOnset]
    hits[i].append([np.sum(drs==1) for drs in directionResponses])
    misses[i].append([np.sum(drs==-1) for drs in directionResponses])
    noResps[i].append([np.sum(drs==0) for drs in directionResponses])

hits = np.squeeze(np.array(hits))
misses = np.squeeze(np.array(misses))
noResps = np.squeeze(np.array(noResps))
totalTrials = hits+misses+noResps

# here call no_go movement function? 

if 0 in trialTargetFrames:        # this already excludes repeats 

    no_goTotal = len(trialTargetFrames[trialTargetFrames==0])
    no_goCorrect = len(trialResponse[(trialResponse==1) & (trialTargetFrames==0)])
    no_goMove = no_goTotal - no_goCorrect
    
    no_goTurnDir = []
  
    stimStart = d['trialStimStartFrame'].value
    trialOpenLoop = d['trialOpenLoopFrames'][:len(trialResponse)]
    trialRespFrames = d['trialResponseFrame'].value  #gives the frame number of a response
    deltaWheel = d['deltaWheelPos'].value
    
    stimStart = stimStart[(trialTargetFrames==0)]
    trialRespFrames = trialRespFrames[(trialTargetFrames==0)]
    trialOpenLoop = trialOpenLoop[(trialTargetFrames==0)]
    no_goResp = trialResponse[(trialTargetFrames==0)]
    
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
  
#texts = [str(j) for i in hits for j in i] #to add n as text for each point

for no_goNum, no_goDenom, num, denom, title in zip([no_goCorrect, no_goCorrect,no_goMove],
                                                 [no_goTotal, no_goTotal, no_goTotal],
                                                [hits, hits, hits+misses], 
                                                [totalTrials, hits+misses, totalTrials],
                                                 ['Percent Correct', 'Percent Correct Given Response', 'Total response rate']):
    fig, ax = plt.subplots()
    ax.plot(np.unique(maskOnset), num[0]/denom[0], 'bo-')  #here [0] is right trials and [1] is left
    ax.plot(np.unique(maskOnset), num[1]/denom[1], 'ro-')
    ax.plot(np.unique(maskOnset), (num[0]+num[1])/(denom[0]+denom[1]), 'ko-')  #plots the combined average 
    #ax.text(np.unique(maskOnset), num[0]/denom[0], totalTrials) 
    ax.plot(0, no_goNum/no_goDenom, 'go')
    if no_goNum == no_goMove:
        ax.plot(0, no_goR/no_goMove, 'g>')   #plot the side that was turned in no-go with an arrow in that direction
        ax.plot(0, no_goL/no_goMove, 'g<')
       
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
        a[0]='no-go' 
        ax.set_xticklabels(a)