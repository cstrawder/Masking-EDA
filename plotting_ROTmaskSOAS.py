# -*- coding: utf-8 -*-
"""
Created on Thu Sep 26 12:59:31 2019

@author: chelsea.strawder


This is for plotting masking sessions in the rotation mice, where there are no nogos
and we want to see their performance plotted against 'no mask' trials

"""

import fileIO
import h5py, os
import numpy as np
from matplotlib import pyplot as plt
from behaviorAnalysis import formatFigure


f = fileIO.getFile(rootDir=r'\\allen\programs\braintv\workgroups\nc-ophys\corbettb\Masking')
d = h5py.File(f)

trialResponse = d['trialResponse'][:]
trialRewardDirection = d['trialRewardDir'][:len(trialResponse)]
maskOnset = d['maskOnset'][()]                  
trialMaskOnset = d['trialMaskOnset'][:len(trialResponse)]
trialTargetFrames = d['trialTargetFrames'][:len(trialResponse)]       
maskContrast = d['trialMaskContrast'][:len(trialResponse)]     

maskOnset = np.append(maskOnset, 30)  # makes final value the no-mask condition
np.insert(maskOnset, 0, 0)
     
for i, (mask, trial) in enumerate(zip(trialMaskOnset, trialTargetFrames)):
    if trial>0 and mask==0:
        trialMaskOnset[i]=30

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
respOnly = hits+misses

maskOnly = len(trialResponse[(maskContrast>0) & (trialTargetFrames==0)])  # rotation task 'mask only' trials can't be 'correct'

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

# we want to see which direction they moved the wheel on mask-only trials 
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


for num, denom, title in zip(
        [hits, hits, respOnly],
        [totalTrials, respOnly, totalTrials],
        ['Percent Correct', 'Percent Correct Given Response', 'Total response rate']):
    
    fig, ax = plt.subplots()

    ax.plot(np.unique(maskOnset), num[0]/denom[0], 'ro-')  #here [0] is right stim/left turning trials and [1] is left stim/r turning
    ax.plot(np.unique(maskOnset), num[1]/denom[1], 'bo-')
    y=(num[0]/denom[0])
    y2=(num[1]/denom[1])
    for i, length in enumerate(np.unique(maskOnset)):
        plt.annotate(str(denom[0][i]), xy=(length,y[i]), xytext=(0, 10), textcoords='offset points')  #adds total num of trials
        plt.annotate(str(denom[1][i]), xy=(length,y2[i]), xytext=(0, -20), textcoords='offset points')
    ax.plot(np.unique(maskOnset), (num[0]+num[1])/(denom[0]+denom[1]), 'ko--', alpha=.5)  #plots the combined average  
    ax.plot(0, (nogoR/maskOnly), 'r>', ms=8)   #plot the side that was turned in no-go with an arrow in that direction
    ax.plot(0, (nogoL/maskOnly), 'b<', ms=8)
    ax.annotate(str(nogoR), xy=(1,nogoR/maskOnly), xytext=(0, 0), textcoords='offset points')
    ax.annotate(str(nogoL), xy=(1,nogoL/maskOnly), xytext=(0, 0), textcoords='offset points')
    
    formatFigure(fig, ax, xLabel='SOA (frames)', yLabel='percent trials', 
                 title=title + " :  " + '-'.join(f.split('_')[-3:-1]))
    ax.set_xlim([-2, maskOnset[-1]+2])
    ax.set_ylim([0,1.1])
    ax.set_xticks(np.unique(trialMaskOnset))
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.tick_params(direction='out',top=False,right=False)
            
    if 30 in trialMaskOnset:   
        a = ax.get_xticks().tolist()
        a = [int(i) for i in a]    
        a[-1]='no mask' 
        a[0]='mask only'
        ax.set_xticklabels(a)
        