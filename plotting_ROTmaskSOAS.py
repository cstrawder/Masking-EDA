# -*- coding: utf-8 -*-
"""
Created on Thu Sep 26 12:59:31 2019

@author: chelsea.strawder


This is for plotting masking sessions in the rotation mice, where there are no nogos
and we want to see their performance plotted against 'no mask' trials

"""

import fileIO
import h5py
import numpy as np
import matplotlib
from matplotlib import pyplot as plt
from behaviorAnalysis import formatFigure
from nogoTurn import nogo_turn

matplotlib.rcParams['pdf.fonttype'] = 42

f = fileIO.getFile(rootDir=r'\\allen\programs\braintv\workgroups\nc-ophys\corbettb\Masking')
d = h5py.File(f)

trialResponse = d['trialResponse'][:]
trialRewardDirection = d['trialRewardDir'][:len(trialResponse)]
maskOnset = d['maskOnset'][()]                  
trialMaskOnset = d['trialMaskOnset'][:len(trialResponse)]
trialTargetFrames = d['trialTargetFrames'][:len(trialResponse)]       
trialMaskContrast = d['trialMaskContrast'][:len(trialResponse)]     

noMaskVal = maskOnset[-1] + round(np.mean(np.diff(maskOnset)))  # assigns noMask condition an evenly-spaced value from soas
maskOnset = np.append(maskOnset, noMaskVal)              # makes final value the no-mask condition
    
for i, (mask, trial) in enumerate(zip(trialMaskOnset, trialTargetFrames)):   # filters target-Only trials 
    if trial>0 and mask==0:
        trialMaskOnset[i]=noMaskVal

# [turn R] , [turn L]
hits = [[],[]]
misses = [[], []]
noResps = [[],[]]

for i, direction in enumerate([1,-1]):
    directionResponses = [trialResponse[(trialRewardDirection==direction) & (trialMaskOnset==soa)] for soa in np.unique(maskOnset)]
    hits[i].append([np.sum(drs==1) for drs in directionResponses])
    misses[i].append([np.sum(drs==-1) for drs in directionResponses])
    noResps[i].append([np.sum(drs==0) for drs in directionResponses])

hits = np.squeeze(np.array(hits))
misses = np.squeeze(np.array(misses))
noResps = np.squeeze(np.array(noResps))
totalTrials = hits+misses+noResps
respOnly = hits+misses


maskTotal = len(trialResponse[(trialMaskContrast>0)])
maskOnlyTotal = len(trialResponse[(trialMaskContrast>0) & (trialTargetFrames==0)])   # rotation task 'mask only' trials can't be 'correct'
maskOnlyCorr = len(trialResponse[(trialMaskContrast>0) & (trialResponse==1) & (trialTargetFrames==0)])

stimStart = d['trialStimStartFrame'][:len(trialResponse)]
trialOpenLoop = d['trialOpenLoopFrames'][:len(trialResponse)]
trialRespFrames = d['trialResponseFrame'][:len(trialResponse)]
deltaWheel = d['deltaWheelPos'][:]

stimStart = stimStart[(trialTargetFrames==0)]             
trialRespFrames = trialRespFrames[(trialTargetFrames==0)]
trialMaskContrast = trialMaskContrast[(trialTargetFrames==0)]

startWheelPos = []
endWheelPos = []

# we want to see which direction they moved the wheel on mask-only trials 
for i, (start, end, mask) in enumerate(zip(stimStart, trialRespFrames, trialMaskContrast)):   
    if (mask>0):  #maskOnly
        endWheelPos.append(deltaWheel[end])
        startWheelPos.append(deltaWheel[start])

maskEnd = np.array(endWheelPos)
maskStart = np.array(startWheelPos)
maskWheelPos = maskEnd - maskStart

maskOnlyTurnDir = []

for j in maskWheelPos:
    if j>0:
        maskOnlyTurnDir.append(1)
    else:
        maskOnlyTurnDir.append(-1)
 
maskOnlyTurnDir = np.array(maskOnlyTurnDir)
maskOnlyR = sum(maskOnlyTurnDir==1)
maskOnlyL = sum(maskOnlyTurnDir==-1)   

trialMaskContrast= d['trialMaskContrast'][:len(trialResponse)]
nogoTrials = trialResponse[(trialTargetFrames==0) & (trialMaskContrast==0)]
nogoStartWheelPos = []
nogoEndWheelPos = []

# we want to see which direction they moved the wheel on an incorrect no-go
for (start, end, resp) in zip(stimStart, trialRespFrames, nogoTrials):   
    if resp==-1:
        nogoEndWheelPos.append(deltaWheel[end])
        nogoStartWheelPos.append(deltaWheel[start])
    
nogoEndWheelPos = np.array(nogoEndWheelPos)
nogoStartWheelPos = np.array(nogoStartWheelPos)   
wheelPos = nogoEndWheelPos - nogoStartWheelPos

nogoTurnDir = []

for i in wheelPos:
    if i >0:
        nogoTurnDir.append(1)
    else:
        nogoTurnDir.append(-1)

nogoTurnDir = np.array(nogoTurnDir)

nogoR = sum(nogoTurnDir[nogoTurnDir==1])
nogoL = sum(nogoTurnDir[nogoTurnDir==-1])*-1
 
nogoTotal = len(nogoTrials)
nogoCorrect = len(trialResponse[(trialResponse==1) & (trialTargetFrames==0) & (trialMaskContrast==0)])
nogoMove = len(nogoTurnDir) 
nogoTurnDir = np.array(nogoTurnDir)

for num, denom, title in zip(
        [hits, hits, respOnly],
        [totalTrials, respOnly, totalTrials],
        ['Percent Correct', 'Percent Correct Given Response', 'Total response rate']):
    
    fig, ax = plt.subplots()

    ax.plot(np.unique(maskOnset), num[0]/denom[0], 'ro-')  #here [0] is right turning trials and [1] is left turning
    ax.plot(np.unique(maskOnset), num[1]/denom[1], 'bo-')
    y=(num[0]/denom[0])
    y2=(num[1]/denom[1])
    for i, length in enumerate(np.unique(maskOnset)):
        plt.annotate(str(denom[0][i]), xy=(length,y[i]), xytext=(0, 10), textcoords='offset points')  #adds total num of trials
        plt.annotate(str(denom[1][i]), xy=(length,y2[i]), xytext=(0, -20), textcoords='offset points')
    ax.plot(np.unique(maskOnset), (num[0]+num[1])/(denom[0]+denom[1]), 'ko--', alpha=.5)  #plots the combined average  
    if 0 in trialTargetFrames:
        ax.plot(0, (maskOnlyR/maskOnlyTotal), 'r>', ms=8)   #plot the side that was turned in no-go with an arrow in that direction
        ax.plot(0, (maskOnlyL/maskOnlyTotal), 'b<', ms=8)
        ax.plot(0, (maskOnlyCorr/maskOnlyTotal), 'ko')
        ax.annotate(str(maskOnlyR), xy=(1,maskOnlyR/maskOnlyTotal), xytext=(0, 0), textcoords='offset points')
        ax.annotate(str(maskOnlyL), xy=(1,maskOnlyL/maskOnlyTotal), xytext=(0, 0), textcoords='offset points')
        
        ax.plot(-1, nogoCorrect/nogoTotal, 'go')
        ax.plot(-1, nogoR/nogoMove, 'g>')   #plot the side that was turned in no-go with an arrow in that direction
        ax.plot(-1, nogoL/nogoMove, 'g<')
    
    formatFigure(fig, ax, xLabel='SOA (frames)', yLabel='percent trials', 
                 title=title + " :  " + '-'.join(f.split('_')[-3:-1]))
    ax.set_xlim([-2, maskOnset[-1]+2])
    ax.set_ylim([0,1.1])
    ax.set_xticks(np.unique(trialMaskOnset))
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.tick_params(direction='out',top=False,right=False)
            
  
    a = ax.get_xticks().tolist()
    a = [int(i) for i in a]     
    a[-1]='no mask' 
    if maskOnlyTotal:
        a[0]='mask only'
    ax.set_xticklabels(a)
     
    plt.tight_layout()    