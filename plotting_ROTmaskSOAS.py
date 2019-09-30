# -*- coding: utf-8 -*-
"""
Created on Thu Sep 26 12:59:31 2019

@author: chelsea.strawder


This is for plotting masking sessions in the rotation mice, where there are no nogos
and we want to see their performance plotted against no mask trials

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

trialRewardDirection = d['trialRewardDir'][:-1]    # leave off last trial, ended session before answer 
trialResponse = d['trialResponse'][:]
maskOnset = d['maskOnset'][:]                  # list of ind lengths, does not include no-gos (0)
trialMaskOnset = d['trialMaskOnset'][:-1] 
trialTargetFrames = d['trialTargetFrames'][:len(trialResponse)] 
maskContrast = d['trialMaskContrast'][:len(trialResponse)]      # also leaves off last trial

maskOnset = np.append(maskOnset, 30)  # makes final value the no-mask condition

for i, val in enumerate(trialMaskOnset):
    if val==0:
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

for num, denom, title in zip(
        [hits, hits, hits+misses],
        [totalTrials, hits+misses, totalTrials],
        ['Percent Correct', 'Percent Correct Given Response', 'Total response rate']
        ):
    fig, ax = plt.subplots()

    ax.plot(np.unique(maskOnset), num[0]/denom[0], 'ro-')  #here [0] is right stim/left turning trials and [1] is left stim/r turning
    ax.plot(np.unique(maskOnset), num[1]/denom[1], 'bo-')
    y=(num[0]/denom[0])
    y2=(num[1]/denom[1])
    for i, length in enumerate(np.unique(maskOnset)):
        plt.annotate(str(denom[0][i]), xy=(length,y[i]), xytext=(0, 10), textcoords='offset points')  #adds total num of trials
        plt.annotate(str(denom[1][i]), xy=(length,y2[i]), xytext=(0, -20), textcoords='offset points')
    ax.plot(np.unique(maskOnset), (num[0]+num[1])/(denom[0]+denom[1]), 'ko--', alpha=.5)  #plots the combined average 
    formatFigure(fig, ax, xLabel='SOA (frames)', yLabel='percent trials', 
                 title=title + " :  " + '-'.join(f.split('_')[-3:-1]))
    ax.set_xlim([-2, maskOnset[-1]+2])
    ax.set_ylim([0,1.01])
    ax.set_xticks(np.unique(trialMaskOnset))
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.tick_params(direction='out',top=False,right=False)
            
    if 30 in trialMaskOnset:   
        a = ax.get_xticks().tolist()
        a = [int(i) for i in a]    
        a[-1]='no mask' 
        ax.set_xticklabels(a)