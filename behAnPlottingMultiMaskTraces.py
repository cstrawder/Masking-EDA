
# -*- coding: utf-8 -*-
"""
Created on Fri May 03 18:44:40 2019

@author: svc_ccg

This is supposed to be a copy of behaviorAnalysis that separates out trials by 
mask onset, and plots those wheel traces together - or plots them all on one plot by color 


"""

import numpy as np
import h5py, os
from matplotlib import pyplot as plt
import pandas as pd 
import datetime
import matplotlib.style
import matplotlib as mpl
import scipy.signal 
from ignoreTrials import ignore_trials

mpl.rcParams['pdf.fonttype']=42

mpl.style.use('classic')

'''
    Makes plot of trial by trial wheel trajectory color coded by reward direction (turning direction)  
    INPUTS:
    data: path to h5 file created at end of behavioral session
    returnData: whether to return the trial wheel data for go right and go left trials. Default is to not return data.
    responseFilter: list of trial responses to include. For example [-1, 1] to analyze only active response trials.
                    [1] to analyze only hits etc. Defaults to include all trials
    ignoreRepeats:  choose to omit the repeated trials after an incorrect trials, if repeatIncorrectTrials is set
    
    OUTPUTS:
    rightTrials, turnLeftTrials: numpy arrays of all go right and go left trial wheel trajectories. Trials are padded
                            with nans to correct for variable length. 
'''
    
def makeWheelPlot(data, returnData=False, responseFilter=[-1,0,1], ignoreRepeats=True, 
                  framesToShowBeforeStart=60, mask=False, maskOnly=False):


    #Clean up inputs if needed    
    #if response filter is an int, make it a list
    if type(responseFilter) is int:
        responseFilter = [responseFilter]
    
    d = data
    frameRate = d['frameRate'][()]
    trialEndFrames = d['trialEndFrame'][:]
    trialStartFrames = d['trialStartFrame'][:trialEndFrames.size]
    trialRewardDirection = d['trialRewardDir'][:trialEndFrames.size]
    trialResponse = d['trialResponse'][:trialEndFrames.size]
    deltaWheel = d['deltaWheelPos'][:]
    
    preStimFrames = d['trialStimStartFrame'][:trialEndFrames.size]-trialStartFrames if 'trialStimStartFrame' in d else np.array([d['preStimFrames'][:]]*trialStartFrames.size)
    
    trialStartFrames += preStimFrames    
    
    if 'trialOpenLoopFrames' in d.keys():
        openLoopFrames = d['trialOpenLoopFrames'][:]
    elif 'openLoopFrames' in d.keys():
        openLoopFrames = d['openLoopFrames'][:]
    else:
        raise ValueError 
    
    
    if 'rewardFrames' in d.keys():
        rewardFrames = d['rewardFrames'][:]
    elif 'responseFrames' in d.keys():
        responseTrials = np.where(trialResponse!= 0)[0]
        rewardFrames = d['responseFrames'][:][trialResponse[responseTrials]>0]
    else:
        rewardFrames = d['trialResponseFrame'][:len(trialResponse)]
        rewardFrames = rewardFrames[trialResponse>0]  
        
    nogo = d['trialTargetFrames'][:-1]==0
    
        
    # alters the necessary variables to exclude any trials that are an incorrect repeat 
    #(i.e, a repeated trial after an incorrect choice).  If there are no repeats, it passes
    if ignoreRepeats == True:
        if 'trialRepeat' in d.keys():
            prevTrialIncorrect = d['trialRepeat'][:len(trialResponse)]
            subtitle = ['repeats ignored']
        elif 'incorrectTrialRepeats' in d and d['incorrectTrialRepeats'][()] > 0:
            prevTrialIncorrect = np.concatenate(([False],trialResponse[:-1]<1))
            trialResponse = trialResponse[prevTrialIncorrect==False]
            trialStartFrames = trialStartFrames[prevTrialIncorrect==False]
            trialEndFrames = trialEndFrames[prevTrialIncorrect==False]
            trialRewardDirection = trialRewardDirection[prevTrialIncorrect==False]
            nogo = nogo[prevTrialIncorrect==False]
            subtitle = ['repeats ignored']
        elif 'incorrectTrialRepeats' in d and d['incorrectTrialRepeats'][()] == 0:
            subtitle= ['no repeated trials']
    else:
        subtitle = ['repeats incl']

    
    ignoreTrials = ignore_trials(d)
    
    postTrialFrames = 0 if d['postRewardTargetFrames'][()]>0 else 1 #make sure we have at least one frame after the reward

    fig, ax = plt.subplots()
    
    # turnRightTrials == stim presented on L, turn right - viceversa for turnLeftTrials - or for orientation, turn right
    nogoTrials = []
    turnRightTrials = []
    turnLeftTrials = []
    maxTrialFrames = max(trialEndFrames-trialStartFrames+framesToShowBeforeStart+postTrialFrames)  #??? why  
    trialTime = (np.arange(maxTrialFrames)-framesToShowBeforeStart)/frameRate  # evenly-spaced array of times for x-axis
    for i, (trialStart, trialEnd, rewardDirection, resp) in enumerate(zip(
            trialStartFrames, trialEndFrames, trialRewardDirection, trialResponse)):
        if i>0 and i<len(trialStartFrames):
            if i in ignoreTrials:
                pass
            else:
                if resp in responseFilter:
                    #get wheel position trace for this trial!
                    trialWheel = np.cumsum(deltaWheel[
                            trialStart-framesToShowBeforeStart:trialStart-framesToShowBeforeStart + maxTrialFrames
                            ])
                    trialWheel -= trialWheel[0]
                    trialreward = np.where((rewardFrames>trialStart)&(rewardFrames<=trialEnd))[0]
                    rewardFrame = rewardFrames[trialreward[0]]-trialStart+framesToShowBeforeStart if len(trialreward)>0 else None
                    if nogo[i]:
                        ax.plot(trialTime[:trialWheel.size], trialWheel, 'g', alpha=0.2)   # plotting no-go trials
                        if rewardFrame is not None:
                            ax.plot(trialTime[rewardFrame], trialWheel[rewardFrame], 'go')
                        nogoTrials.append(trialWheel)
                    elif rewardDirection>0:
                        ax.plot(trialTime[:trialWheel.size], trialWheel, 'r', alpha=0.2)  #plotting right turning 
                        if rewardFrame is not None:
                            ax.plot(trialTime[rewardFrame], trialWheel[rewardFrame], 'ro')
                        turnRightTrials.append(trialWheel)
                    elif rewardDirection<0:
                        ax.plot(trialTime[:trialWheel.size], trialWheel, 'b', alpha=0.2)   # plotting left turning 
                        if rewardFrame is not None:
                            ax.plot(trialTime[rewardFrame], trialWheel[rewardFrame], 'bo')
                        turnLeftTrials.append(trialWheel)
    
    turnRightTrials = pd.DataFrame(turnRightTrials).fillna(np.nan).values
    turnLeftTrials = pd.DataFrame(turnLeftTrials).fillna(np.nan).values
    nogoTrials = pd.DataFrame(nogoTrials).fillna(np.nan).values
    ax.plot(trialTime[:turnRightTrials.shape[1]], np.nanmean(turnRightTrials,0), 'r', linewidth=3)
    ax.plot(trialTime[:turnLeftTrials.shape[1]], np.nanmean(turnLeftTrials, 0), 'b', linewidth=3)
    ax.plot(trialTime[:nogoTrials.shape[1]], np.nanmean(nogoTrials,0), 'k', linewidth=3)
    ax.plot([trialTime[framesToShowBeforeStart+openLoopFrames]]*2, ax.get_ylim(), 'k--')
    
    name_date = str(data).split('_')    

    
    formatFigure(fig, ax, xLabel='Time from stimulus onset (s)', 
                 yLabel='Wheel Position (pix)', title=name_date[-3:-1] + subtitle)
    plt.tight_layout()
 
    
'''
Here is code to plot the masking trials separately from the other trials (target only, nogo)
mask=True means plot the masking trials 
maskOnly=True means only plot the masking trials, and separate by color 

'''
   
    
    if mask:
        trialMaskContrast = d['trialMaskContrast'][:len(trialResponse)]  
        trialMaskOnset = d['trialMaskOnset'][:len(trialResponse)]
        trialStimStartFrames = d['trialStimStartFrame'][:len(trialResponse)]
        maxTrialFrames = d['maxResponseWaitFrames'][()]
# better to use interp here?
        trialTime = (np.arange(maxTrialFrames+framesToShowBeforeStart))/frameRate  

        onset = np.unique(trialMaskOnset)   #soa==0 includes target only, nogo, and mask only - need to split
        
        fig, ax = plt.subplots()
        nogoMask = []
        rightMask = []
        leftMask = []
        for i, (trialStart, trialEnd, rewardDirection, mask, soa, resp) in enumerate(zip(
                trialStimStartFrames, trialEndFrames, trialRewardDirection, 
                trialMaskContrast, trialMaskOnset, trialResponse)):
            if i>0 and i<len(trialStartFrames):
                if resp in responseFilter:
                    trialWheel = np.cumsum(
                            deltaWheel[trialStart-framesToShowBeforeStart:
                                trialStart + maxTrialFrames])
                    trialWheel -= trialWheel[0]
                    trialreward = np.where((rewardFrames>trialStart)&(rewardFrames<=trialEnd))[0]
                    rewardFrame = rewardFrames[trialreward[0]]-trialStart+framesToShowBeforeStart if len(trialreward)>0 else None

#       plotting nogo trials - Necessary??
#                    if nogo[i] and mask==0:
#                        ax.plot(trialTime[:trialWheel.size], trialWheel, 'g', alpha=0.3)   # plotting no-go trials
#                        
#                        if rewardFrame is not None:
#                            ax.plot(trialTime[rewardFrame], trialWheel[rewardFrame], 'go')
#                        nogoMask.append(trialWheel)
                    
                    if maskOnly==True:
                        if rewardDirection!=0:
                            print(soa)
                            onsetDict = defaultdict(list)
                            onsetDict[soa].append(trialWheel)
                            
                            
                        
        from matplotlib.cm import get_cmap
        cmap = get_cmap('Dark2')     # type: matplotlib.colors.ListedColormap
        colors = cmap.colors
        cols = int(len(onset)/2)
        fig, axes = plt.subplots(nrows=2, ncols=cols)
        for a, o, c in zip(axes.flatten(), onsetDict, colors[:len(onset)]):
            a.plot(o, trialWheel, color=c, alpha=.3, label=str(soa)) 
           
'''
above approach not working - try to create a dict that saves all the wheel traces for each soa,
then plots all the traces on a new subplot for each soa - 6 separate plots, or maybe 6 in one plot?
'''
                    
                    
                    
                    
                    
                    
                    
                    
                    else:
                        if rewardDirection!=0:
#                            ax.plot(trialTime[:trialWheel.size], trialWheel, 'r', alpha=0.2)  #plotting right turning 
#                            if rewardFrame is not None:
#                                ax.plot(trialTime[rewardFrame], trialWheel[rewardFrame], 'ro')
#                            rightMask.append(trialWheel)
                            if soa==3:
                                ax.plot(trialTime[:trialWheel.size], trialWheel,  color='m', alpha=.3) 
                                rightMask.append(trialWheel)
#                            elif soa==4:
#                                ax.plot(trialTime[:trialWheel.size], trialWheel, color='c', alpha=.3) 
#                                rightMask.append(trialWheel)
                            elif soa==6:
                                ax.plot(trialTime[:trialWheel.size], trialWheel, color='g', alpha=.3)
#                            elif soa==12:
#                                ax.plot(trialTime[:trialWheel.size], trialWheel, color='k', alpha=.3) 

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
        
    else:
        pass
    
    if returnData:
        return turnRightTrials, turnLeftTrials


def get_files(mouse_id, task):
    directory = r'\\allen\programs\braintv\workgroups\nc-ophys\corbettb\Masking'
    dataDir = os.path.join(os.path.join(directory, mouse_id), task)   #training_ for no mask, masking_ for mask
    files = os.listdir(dataDir)
    files.sort(key=lambda f: datetime.datetime.strptime(f.split('_')[2],'%Y%m%d'))
    return [os.path.join(dataDir,f) for f in files]  
    
              
def trials(data):
    trialResponse = data['trialResponse'].value
    trials = np.count_nonzero(trialResponse)
    correct = (trialResponse==1).sum()
    percentCorrect = (correct/float(trials)) * 100
    return percentCorrect

def formatFigure(fig, ax, title=None, xLabel=None, yLabel=None, xTickLabels=None, yTickLabels=None, blackBackground=False, saveName=None):
    fig.set_facecolor('w')
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.tick_params(direction='out',top=False,right=False)
    
    if title is not None:
        ax.set_title(title)
    if xLabel is not None:
        ax.set_xlabel(xLabel)
    if yLabel is not None:
        ax.set_ylabel(yLabel)
        
    if blackBackground:
        ax.set_axis_bgcolor('k')
        ax.tick_params(labelcolor='w', color='w')
        ax.xaxis.label.set_color('w')
        ax.yaxis.label.set_color('w')
        for side in ('left','bottom'):
            ax.spines[side].set_color('w')

        fig.set_facecolor('k')
        fig.patch.set_facecolor('k')
    if saveName is not None:
        fig.savefig(saveName, facecolor=fig.get_facecolor())
 

       
def performanceByParam(data, paramName, units=''):
    
    if not paramName in data.keys():
        print('No parameter named ' + paramName + ' in hdf5 file')
        return
    
    d =  data
    
    trialResponse = d['trialResponse'].value    
    numTrials = len(trialResponse)
    
    trialRewardDirection = d['trialRewardDir'].value[:numTrials]
    trialParam = d[paramName][:numTrials] 
    
    if any(np.isnan(trialParam)):    
        trialParam[np.isnan(trialParam)] = -1

    paramValues = np.unique(trialParam)
    
    hits = [[],[]]
    misses = [[], []]
    noResps = [[],[]]
    for i, direction in enumerate([-1,1]):
        directionResponses = [trialResponse[(trialRewardDirection==direction) & (trialParam == p)] for p in paramValues]
        hits[i].append([np.sum(drs==1) for drs in directionResponses])
        misses[i].append([np.sum(drs==-1) for drs in directionResponses])
        noResps[i].append([np.sum(drs==0) for drs in directionResponses])
    
    hits = np.squeeze(np.array(hits))
    misses = np.squeeze(np.array(misses))
    noResps = np.squeeze(np.array(noResps))
    totalTrials = hits+misses+noResps
    
    for num, denom, title in zip([hits, hits, noResps], [totalTrials, hits+misses, totalTrials], ['total hit rate', 'response hit rate', 'no response rate']):
        fig, ax = plt.subplots()
        ax.plot(paramValues, num[0]/denom[0], 'bo-')
        ax.plot(paramValues, num[1]/denom[1], 'ro-')
        ax.set_ylim([0,1.01])
        ax.set_xlim([0, paramValues[-1]*1.1])
        ax.set_xticks(paramValues)
        formatFigure(fig, ax, xLabel=paramName + '('+units+')', yLabel='percent trials', title=title)
    
        
