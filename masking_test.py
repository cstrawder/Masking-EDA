# -*- coding: utf-8 -*-
"""
Created on Thu Sep 26 12:59:31 2019

@author: chelsea.strawder


Taking over the old masking plotting code to plot the "position" masking sessions
Mask appears either in center or overlapping target (normal)
Compares the performance between these two conditions so we can understand more 
about the effect of the mask presence 
for most of the indexing, [0]=Left and [1]=Right turning
"""

import numpy as np
import matplotlib
from matplotlib import pyplot as plt
from behaviorAnalysis import formatFigure
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
    
    # bring in and clean relevant variables
    trialResponse = d['trialResponse'][:end][ignoring==0]
    trialRewardDirection = d['trialRewardDir'][:end][ignoring==0]
    trialTargetFrames = d['trialTargetFrames'][:end][ignoring==0]
    trialMaskContrast = d['trialMaskContrast'][:end][ignoring==0]
    trialMaskPosition = d['trialMaskPos'][:end][ignoring==0]
    trialType = d['trialType'][:end][ignoring==0]
    trialStimStart = d['trialStimStartFrame'][:end][ignoring==0]
    trialRespFrame = d['trialResponseFrame'][:end][ignoring==0]
    deltaWheel = d['deltaWheelPos'][:]
    
    framerate = int(np.round(1/np.median(d['frameIntervals'][:])))
    maskOnset = d['maskOnset'][()] * 1000/framerate              
    trialMaskOnset = d['trialMaskOnset'][:end][ignoring==0] * (1000/framerate)
    
    
# create new, simpler array for mask position
    trialMaskArray = np.full(len(trialMaskPosition), 0)  # used later to filter trials
    
    for i, t in enumerate(trialMaskPosition):
        if 480 in t:
            trialMaskArray[i] = 1   # mask lateral (overlapping target)
        elif 270 in t:
            trialMaskArray[i] = 2   # mask center
        else:
            trialMaskArray[i] = 0
    
    
# filter and count target only trials (no mask)
# these are independent from mask postition and thus outside of loop below
    
    targetOnlyVal = maskOnset[-1] + round(np.mean(np.diff(maskOnset)))  # assigns evenly-spaced value from soas
        
    for i, (mask, trial) in enumerate(zip(trialMaskOnset, trialTargetFrames)):   # filters target-Only trials 
        if trial>0 and mask==0:
            trialMaskOnset[i]=targetOnlyVal
    
    targetOnlyHit = [[],[]]   # [left turning], [right turning]
    targetOnlyResp = [[],[]]
    targetOnlyTotals = [[],[]]
    
    for i, side in enumerate([-1, 1]):    # [L turning], [R turning]
        for (typ, rew, resp) in zip(trialType, trialRewardDirection, trialResponse):
            if typ == 'targetOnly':
                if rew==side:
                    targetOnlyTotals[i].append(1)
                    if resp==1:
                        targetOnlyHit[i].append(1)
                    if resp!=0:
                        targetOnlyResp[i].append(1)
    
    def total(var):
        return list(map(sum, var))
                    
    targetOnlyHit = total(targetOnlyHit)
    targetOnlyResp = total(targetOnlyResp)
    targetOnlyTotals = total(targetOnlyTotals)
    
### PLOTTING    
        
    for mask, j in zip(['mask lateral', 'mask center'], [1, 2]):

        # depending on mask position, filter and count trial resps
        # [turn L] , [turn R]
        hits = [[],[]]
        misses = [[], []]
        noResps = [[],[]]
        
        for i, direction in enumerate([-1,1]):
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
        
        # mask only -- mask only center and side
        maskOnlyTurns = [[],[]]  # 1st is indices, 2nd is turning dir
        
        for i, (t, pos, start, end) in enumerate(zip(trialType, trialMaskArray, trialStimStart, trialRespFrame)):
            if t == 'maskOnly' and pos == j:
                wheel = (np.cumsum(deltaWheel[start:end])[-1])
                maskOnlyTurns[0].append(i)
                maskOnlyTurns[1].append((wheel/abs(wheel)).astype(int))
        
        ## add catch?  after this loop?
        
        maskOnlyTotal = len(trialResponse[(trialMaskContrast>0) & (trialTargetFrames==0)])   
        maskOnlyR = maskOnlyTurns[1].count(1)
        maskOnlyL = maskOnlyTurns[1].count(-1) 
        maskOnlyMove = len(maskOnlyTurns)
        
        for title in (['Response Rate', 'Fraction Correct Given Response']): 
        
            fig, ax = plt.subplots()
            
            if mask == 'mask lateral':
                plt.suptitle('Mask Overlaps target')
            elif mask =='mask center':
                plt.suptitle('Mask Center Screen (non-overlapping)')
            
            if title=='Response Rate':
                ax.plot(maskOnset, respOnly[0]/totalTrials[0], 'bo-', lw=3, alpha=.7)  # left turning
                ax.plot(maskOnset, respOnly[1]/totalTrials[1], 'ro-', lw=3, alpha=.7)  # right turning
                
                #plot mask only for given mask position
                ax.plot(5, (maskOnlyR/maskOnlyTotal), 'ro')   
                ax.plot(5, (maskOnlyL/maskOnlyTotal), 'bo')
                ax.plot(5, ((maskOnlyTotal-maskOnlyCorr)/maskOnlyTotal), 'ko')
                
                ax.plot(targetOnlyVal, targetOnlyResp[0]/targetOnlyTotals[0], 'bo')
                ax.plot(targetOnlyVal, targetOnlyResp[1]/targetOnlyTotals[1], 'ro')
               
               ### add catch trials to resp rate??
               ### add catch counts as text at top
               
                denom = totalTrials
               
               
            elif title=='Fraction Correct Given Response':
                ax.plot(maskOnset, hits[0]/respOnly[0], 'bo-', lw=3, alpha=.7)  # left turning
                ax.plot(maskOnset, hits[1]/respOnly[1], 'ro-', lw=3, alpha=.7)  # right turning
    
                ax.plot(targetOnlyVal, targetOnlyHit[0]/targetOnlyResp[0], 'bo')
                ax.plot(targetOnlyVal, targetOnlyHit[1]/targetOnlyResp[1], 'ro')
                
                denom = respOnly
            
            for x,Ltrials,Rtrials in zip(maskOnset, denom[0], denom[1]):   #denom[0]==L, denom[1]==R
                    for y,n,clr in zip((1.03,1.08),[Rtrials, Ltrials],'rb'):
                        fig.text(x,y,str(n),transform=ax.transData,color=clr,fontsize=10,ha='center',va='bottom')
            
            
            formatFigure(fig, ax, xLabel='Mask Onset From Target Onset (ms)', yLabel=title) 
                         
            ax.set_title(str(d).split('_')[-3:-1], fontdict={'fontsize':10}, pad=10)
            
            xticks = np.append(maskOnset, targetOnlyVal)
            xticks = np.insert(xticks, 0, 5)
            xticklabels = list(np.round(xticks).astype(int))
            xticklabels[0] = 'Mask Only'
            xticklabels[-1] = 'Target Only'
    #        if title=='Response Rate':
    #            # add catch label to plot
    #               x = 0
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
    
    
    
    
