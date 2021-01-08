# -*- coding: utf-8 -*-
"""
Created on Thu Sep 26 12:59:31 2019

@author: chelsea.strawder


Taking over the old masking plotting code to plot the "position" masking sessions
Mask appears either in center or overlapping target (normal)
Compares the performance between these two conditions so we can understand more 
about the effect of the mask presence 
"""

import numpy as np
import matplotlib
from matplotlib import pyplot as plt
from behaviorAnalysis import formatFigure
from nogoData import nogo_turn
from dataAnalysis import ignore_after
from ignoreTrials import ignore_trials

def plot_soa(data,ignoreNoRespAfter=None,showNogo=True):
    
    matplotlib.rcParams['pdf.fonttype'] = 42
    
    d=data
    
    end = ignore_after(d, ignoreNoRespAfter)[0] if ignoreNoRespAfter is not None else len(d['trialResponse'][:])
    
    ignore = ignore_trials(d)  # ignore trials with early movement
    ignoring = np.full(end, 0)
    
    for i,_ in enumerate(ignoring):
        if i in ignore:
            ignoring[i] = 1
    
    trialResponse = d['trialResponse'][:end][ignoring==0]
    trialRewardDirection = d['trialRewardDir'][:end][ignoring==0]
    trialTargetFrames = d['trialTargetFrames'][:end][ignoring==0]
    trialMaskContrast = d['trialMaskContrast'][:end][ignoring==0]
    trialMaskPosition = d['trialMaskPos'][:end][ignoring==0]
    
    trialMaskArray = np.full(len(trialMaskPosition), 0)  # used later to filter trials
    
    for i, t in enumerate(trialMaskPosition):
        if 480 in t:
            trialMaskArray[i] = 1   # mask lateral
        elif 270 in t:
            trialMaskArray[i] = 2   # mask center
        else:
            trialMaskArray[i] = 0
    
    framerate = int(np.round(1/np.median(d['frameIntervals'][:])))
    maskOnset = d['maskOnset'][()] * 1000/framerate              
    trialMaskOnset = d['trialMaskOnset'][:end][ignoring==0] * (1000/framerate)
    
    
    targetOnlyVal = maskOnset[-1] + round(np.mean(np.diff(maskOnset)))  # assigns noMask condition an evenly-spaced value from soas
    maskOnset = np.append(maskOnset, targetOnlyVal)              # makes final value the no-mask condition
        
    for i, (mask, trial) in enumerate(zip(trialMaskOnset, trialTargetFrames)):   # filters target-Only trials 
        if trial>0 and mask==0:
            trialMaskOnset[i]=targetOnlyVal
    
    
     
        
    for mask, j in zip(['mask lateral', 'mask center'], [1, 2]):

        # [turn R] , [turn L]
        hits = [[],[]]
        misses = [[], []]
        noResps = [[],[]]
        
        for i, direction in enumerate([1,-1]):
            directionResponses = [trialResponse[(trialRewardDirection==direction) & 
                                                (trialMaskArray==j) &
                                                (trialMaskOnset==soa)] for soa in np.unique(maskOnset)]
            hits[i].append([np.sum(drs==1) for drs in directionResponses])
            misses[i].append([np.sum(drs==-1) for drs in directionResponses])
            noResps[i].append([np.sum(drs==0) for drs in directionResponses])
        
        hits = np.squeeze(np.array(hits))
        misses = np.squeeze(np.array(misses))
        noResps = np.squeeze(np.array(noResps))
        totalTrials = hits+misses+noResps
        respOnly = hits+misses
        
        turns, ind = nogo_turn(d, returnArray=True)  # returns arrays with turning direction as 1/-1
        maskTurnTrial = ind[1]
        
        ## add catch?  after this loop?
        
        #maskTotal = len(trialResponse[(trialMaskContrast>0)])  sanity check
        maskOnlyTotal = len(trialResponse[(trialMaskContrast>0) & (trialTargetFrames==0)])   
        maskOnlyCorr = len(trialResponse[(trialMaskContrast>0) & (trialResponse==1) & (trialTargetFrames==0)])
        maskOnlyR = turns[1].count(1)
        maskOnlyL = turns[1].count(-1) 
        
        for title in (['Response Rate', 'Fraction Correct Given Response']): 
        
            fig, ax = plt.subplots()
            
            if mask == 'mask lateral':
                plt.suptitle('Mask Overlaps target')
            elif mask =='mask center':
                plt.suptitle('Mask Center Screen (non-overlapping)')
            
            if title=='Response Rate':
                ax.plot(maskOnset, respOnly[0]/totalTrials[0], 'ro-', lw=3, alpha=.7)  # right turning
                ax.plot(maskOnset, respOnly[1]/totalTrials[1], 'bo-', lw=3, alpha=.7)  # left turning
                 
                ax.plot(0, (maskOnlyR/maskOnlyTotal), 'ro', ms=8)   
                ax.plot(0, (maskOnlyL/maskOnlyTotal), 'bo', ms=8)
                ax.plot(0, ((maskOnlyTotal-maskOnlyCorr)/maskOnlyTotal), 'ko')
                
               ### add counts as text at top
               ### add catch trials to resp rate
               
            elif title=='Fraction Correct Given Response':
                ax.plot(maskOnset, hits[0]/respOnly[0], 'ro-', lw=3, alpha=.7)  #right turning
                ax.plot(maskOnset, hits[1]/respOnly[1], 'bo-', lw=3, alpha=.7)  # left turning
    
                 
            formatFigure(fig, ax, xLabel='Mask Onset From Target Onset (ms)', yLabel=title, 
                         title=str(d).split('_')[-3:-1])
            
            xticks = maskOnset
            xticklabels = list(np.round(xticks).astype(int))
            xticklabels[-1] = 'Target Only'
    #        if title=='Response Rate':
    #            # add catch label to plot
    #            xticks = np.concatenate((x,xticks))
    #            xticklabels = lbl+xticklabels
            ax.set_xticks(xticks)
            ax.set_xticklabels(xticklabels)
            ax.set_xlim([0,xticks[-1]+5])
            ax.set_ylim([0,1.1])
            ax.spines['right'].set_visible(False)
            ax.spines['top'].set_visible(False)
            ax.tick_params(direction='out',top=False,right=False)
            
            if title=='Response Rate':
                ax.xaxis.set_label_coords(0.5,-0.08)
      
    ## outside of plot type, plot a combined average masking frac corr
    # that includes both center and normal masks
    
    
    
    
