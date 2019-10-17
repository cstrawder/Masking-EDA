# -*- coding: utf-8 -*-
"""
Created on Thu Sep 26 12:59:31 2019

@author: chelsea.strawder


This is for plotting masking sessions in the rotation mice, where there are no nogos
and we want to see their performance plotted against 'no mask' trials.  
Here we want to look at the relationship between response and STA (rather than SOA).
We use the target length and mask length, along with mask onset, to calculate STA

"""

import fileIO
import h5py, os
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
targetFrames = d['targetFrames'][()]
maskFrames  = d['maskFrames'][()]       
trialMaskOnset = d['trialMaskOnset'][:len(trialResponse)]
trialTargetFrames = d['trialTargetFrames'][:len(trialResponse)]       
maskContrast = d['trialMaskContrast'][:len(trialResponse)]     

# this adjusts target length for trials where mask started before target ended
for i, (trial, soa) in enumerate(zip(trialTargetFrames, trialMaskOnset)):
    if soa>0:
        if soa<trial:
            trialTargetFrames[i]=soa


#create the STA array 
trialSTA = np.zeros(len(trialResponse))
for i, (target, mask, SOA) in enumerate(zip(trialTargetFrames, maskContrast, trialMaskOnset)):
    if target>0 and mask>0:
        term = (SOA - target) + maskFrames
        trialSTA[i] = term

maskTermination = np.unique(trialSTA)

noMaskVal = maskTermination[-1] + 4 
for i, (mask, trial) in enumerate(zip(trialSTA, trialTargetFrames)):   # filters target-Only trials 
    if trial>0 and mask==0:
        trialSTA[i]=noMaskVal

maskTermination = np.append(maskTermination, noMaskVal)  # makes final value the no-mask condition 

# [turn R] , [turn L]
hits = [[],[]]
misses = [[], []]
noResps = [[],[]]

for i, direction in enumerate([1,-1]):
    directionResponses = [trialResponse[(trialRewardDirection==direction) & (trialSTA==sta)] for sta in np.unique(trialSTA)]
    hits[i].append([np.sum(drs==1) for drs in directionResponses])
    misses[i].append([np.sum(drs==-1) for drs in directionResponses])
    noResps[i].append([np.sum(drs==0) for drs in directionResponses])

hits = np.squeeze(np.array(hits))
misses = np.squeeze(np.array(misses))
noResps = np.squeeze(np.array(noResps))
totalTrials = hits+misses+noResps
respOnly = hits+misses

maskTotal = len(trialResponse[(maskContrast>0)])

nogoTurnDir = nogo_turn(d, ignoreRepeats=False, returnArray=True)   #set false for masking
nogoMove = len(nogoTurnDir) 
maskOnlyTotal = len(trialResponse[(maskContrast>0) & (trialTargetFrames==0)])   # rotation task 'mask only' trials can't be 'correct'

stimStart = d['trialStimStartFrame'][:len(trialResponse)]
trialOpenLoop = d['trialOpenLoopFrames'][:len(trialResponse)]
trialRespFrames = d['trialResponseFrame'][:]
deltaWheel = d['deltaWheelPos'][:]

stimStart = stimStart[(trialTargetFrames==0)]             
trialRespFrames = trialRespFrames[(trialTargetFrames==0)]

startWheelPos = []
endWheelPos = []

# we want to see which direction they moved the wheel on mask-only trials 
for i, (start, end, mask) in enumerate(zip(stimStart, trialRespFrames, maskContrast)):   
    if (mask==1):  #maskOnly
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

nogoTurnDir = np.array(nogoTurnDir)
maskOnlyTurnDir = np.array(maskOnlyTurnDir)

nogoR = sum(nogoTurnDir==1)
nogoL = sum(nogoTurnDir==-1)
maskOnlyR = sum(maskOnlyTurnDir==1)
maskOnlyL = sum(maskOnlyTurnDir==-1)


for num, denom, title in zip(
        [hits, hits, respOnly],
        [totalTrials, respOnly, totalTrials],
        ['Percent Correct', 'Percent Correct Given Response', 'Total response rate']):
    
    fig, ax = plt.subplots()

    ax.plot(np.unique(trialSTA), num[0]/denom[0], 'ro-')  #here [0] is right turning trials and [1] is left turning
    ax.plot(np.unique(trialSTA), num[1]/denom[1], 'bo-')
    y=(num[0]/denom[0])
    y2=(num[1]/denom[1])
    for i, length in enumerate(np.unique(trialSTA)):
        plt.annotate(str(denom[0][i]), xy=(length,y[i]), xytext=(0, 10), textcoords='offset points')  #adds total num of trials
        plt.annotate(str(denom[1][i]), xy=(length,y2[i]), xytext=(0, -20), textcoords='offset points')
    ax.plot(np.unique(trialSTA), (num[0]+num[1])/(denom[0]+denom[1]), 'ko--', alpha=.5)  #plots the combined average  
    if 0 in trialTargetFrames:
        ax.plot(0, (maskOnlyR/maskOnlyTotal), 'r>', ms=8)   #plot the side that was turned in no-go with an arrow in that direction
        ax.plot(0, (maskOnlyL/maskOnlyTotal), 'b<', ms=8)
        ax.annotate(str(maskOnlyR), xy=(1,maskOnlyR/maskOnlyTotal), xytext=(0, 0), textcoords='offset points')
        ax.annotate(str(maskOnlyL), xy=(1,maskOnlyL/maskOnlyTotal), xytext=(0, 0), textcoords='offset points')
    
    formatFigure(fig, ax, xLabel='STA (frames)', yLabel='percent trials', 
                 title=title + " :  " + '-'.join(f.split('_')[-3:-1]))
    ax.set_xlim([-2, maskTermination[-1]+2])
    ax.set_ylim([0,1.1])
    ax.set_xticks(np.unique(maskTermination))
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