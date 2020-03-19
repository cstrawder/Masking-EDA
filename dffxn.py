# -*- coding: utf-8 -*-
"""
Created on Thu Feb 13 12:00:25 2020

Needs to assume same edits as responseTimesExp


@author: svc_ccg
"""


import fileIO, h5py
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import scipy.signal
import scipy.stats
import seaborn as sns 

from nogoData import nogo_turn

def create_df(d):
    fi = d['frameIntervals'][:]
    framerate = int(np.round(1/np.median(fi)))
    
    trialResponse = d['trialResponse'][()]
    end = len(trialResponse)
    trialRewardDirection = d['trialRewardDir'][:end]
    trialTargetFrames = d['trialTargetFrames'][:end]
    trialStimStartFrame = d['trialStimStartFrame'][:]
    trialResponseFrame = d['trialResponseFrame'][:end]    
    trialOpenLoopFrames = d['trialOpenLoopFrames'][:end]
    openLoopFrames = d['openLoopFramesFixed'][()]
    quiescentMoveFrames = d['quiescentMoveFrames'][:]
    maxQuiescentMove = d['maxQuiescentNormMoveDist'][()]
    trialEndFrame = d['trialEndFrame'][:end]
    deltaWheel = d['deltaWheelPos'][:]                      # has wheel movement for every frame of session
    trialMaskContrast = d['trialMaskContrast'][:end]
    
    maskOnset = np.round(d['maskOnset'][()] * 1000/framerate).astype(int)
    trialMaskOnset = np.round(d['trialMaskOnset'][:end] * 1000/framerate).astype(int)
    maskLength = np.round(d['maskFrames'][()] * 1000/framerate).astype(int)
    targetLength = np.round(d['targetFrames'][()] * 1000/framerate).astype(int)
    maxResp = np.round(d['maxResponseWaitFrames'][()] * 1000/framerate).astype(int) 

    
    for i, target in enumerate(trialTargetFrames):  # this is needed for older files nogos are randomly assigned a dir
        if target==0:
            trialRewardDirection[i] = 0
    
    nogos = [i for i, (rew, con) in enumerate(zip(trialRewardDirection, trialMaskContrast)) if rew==0 and con==0]

    nogoTurn, maskOnlyTurn, ind = nogo_turn(d)
     
    noMaskVal = maskOnset[-1] + round(np.mean(np.diff(maskOnset)))  # assigns noMask condition an evenly-spaced value from soas
    maskOnset = np.append(maskOnset, noMaskVal)              # makes final value the no-mask condition
        
    for i, (mask, trial) in enumerate(zip(trialMaskOnset, trialTargetFrames)):   # filters target-Only trials 
        if trial>0 and mask==0:
            trialMaskOnset[i]=noMaskVal       
    

    trialWheel = []  
    nogoWheelFromCL = [] 
    for i, (start, resp, mask) in enumerate(zip(trialStimStartFrame, trialResponseFrame, trialMaskContrast)):
        if trialRewardDirection[i]==0:
            if mask==0:  # nogo trials
                wheel = (deltaWheel[start+openLoopFrames:(start+openLoopFrames+60)])   #from start of closedLoop, len of go trial
                nogoWheelFromCL.append(wheel)
                wheel2 = (deltaWheel[start:resp])
                trialWheel.append(wheel2)
            elif mask>0:   # maskOnly
                wheel = (deltaWheel[start:resp+1])
                trialWheel.append(wheel)
        else:
            wheel = (deltaWheel[start:resp])
            trialWheel.append(wheel)
    
    nogoCumWheelFromCL = []         # this is cum wheel mvmt from goTone to wheelMvmt (past threshold) 
    for time in nogoWheelFromCL:    # for nogo trials
        time = np.cumsum(time)
        nogoCumWheelFromCL.append(time)
        
    #since deltawheel provides the difference in wheel mvmt from trial to trial
    #taking the cumulative sum gives the actual wheel mvmt and plots as a smooth curve
    cumWheel = []   
    for mvmt in trialWheel:
        time = np.cumsum(mvmt)
        cumWheel.append(time)  # not using scipy.median.filter bc flattens final frames
        
    #do not include nogo trials (==0); their wheel traces prior to gotone mess up rxn times)
    # time from stimStart to moving the wheel
    interpWheel = []
    timeToMoveWheel = []
    ignoreTrials = []
    for i, (times, resp) in enumerate(zip(cumWheel, trialResponse)):
        if i in nogos or resp==0:   # excluding nogos from rxnTime analysis
            timeToMoveWheel.append(0)
            interpWheel.append(0)    
        else:
            fp = times
            xp = np.arange(0, len(fp))*1/framerate
            x = np.arange(0, xp[-1], .001)
            interp = np.interp(x,xp,fp)
            interpWheel.append(interp)
            threshold = maxQuiescentMove*d['monSizePix'][0] 
            t = np.argmax(abs(interp)>threshold)
            if t <= 100:
                ignoreTrials.append(i)
                timeToMoveWheel.append(t)
            elif t==0:
                timeToMoveWheel.append(0)   # no resp, or moving at start of trial
            else:
                t = np.argmax(abs(interp[100::])>threshold) + 100  #100 is limit of ignore trial
                a = np.argmax(abs(np.round(np.diff(interp[100::])))>0) + 100
                if 0 < a < 200:
                    ignoreTrials.append(i)    # ask sam about ignoring trials, including nogos 
                    timeToMoveWheel.append(0)
                elif abs(t-a) < (150):
                    timeToMoveWheel.append(a)
                else:
                    b = np.argmax(abs(np.round(np.diff(interp[a::])))>0) + a
                    if abs(t-b) < (200):
                        timeToMoveWheel.append(b)
                    else:
                        c = np.argmax(abs(np.round(np.diff(interp[b::])))>1) + b
                        if c!=b:
                            timeToMoveWheel.append(c)
                        else:
                            timeToMoveWheel.append(b)
        
    
    timeToOutcome = []    # time to outcome is time from rxnTime (1st wheel mvmt) to respFrame
    for i,j in zip(cumWheel, timeToMoveWheel):    
        i = np.round(len(i)*1000/framerate)
        timeToOutcome.append(i-j)    # ends up just being the diff btwn trialLength and rxnTime
    
    velo = []           
    for i, time in enumerate(interpWheel):   #time is array of wheel mvmt
        if type(time) is int:
            velo.append(0)          # no wheel mvmt is 0, an int
        else:
            q = int(timeToMoveWheel[i])   # rxn time of the trial, in ms, used as index of interpWheel
            v = abs(time[-1] - time[q]) / timeToOutcome[i]   # dist (in pix??) moved over time/time
            velo.append(v)
            # in pix/ms?
    
    nogoRxnTimes = []               # num of frames from goTone to mvmt or reward
    for times in nogoCumWheelFromCL:
        nogoRxnTimes.append(len(times)-4)
           
    nogoTurn, maskOnly, inds = nogo_turn(d)  # 1st 2 arrays are turned direction, 3rd is indices of 1st 2                       
                                
    nogoMove = np.zeros(len(trialResponse)).astype(int)
    for i in range(len(trialResponse)):
        for (ind, turn) in zip(inds[0], nogoTurn):
            if i==ind:
                nogoMove[i] = turn
    
    data = list(zip(trialRewardDirection, trialResponse, trialStimStartFrame, trialResponseFrame))
    index = range(len(trialResponse))
    
    df = pd.DataFrame(data, index=index, columns=['rewDir', 'resp', 'stimStart', 'respFrame'])
    df['trialLength'] = [np.round(len(t)*1000/framerate) for t in trialWheel]
    df['timeToStartWheel'] = timeToMoveWheel
    df['timeToOutcome'] = timeToOutcome
    if len(maskOnset)>0:
        df['mask'] = trialMaskContrast
        df['soa'] = trialMaskOnset
    df['nogoMove'] = nogoMove  # turning direction of nogo trial
    df['interpWheel'] = interpWheel
    
    #for (ind, time) in zip(nogoTurn[2][0], nogoRxnTimes):    #adds rxnTimes to nogos; need to look at separately
    #    df.loc[ind,'reactionTime'] = time
    
    
    for i in ignoreTrials:
        df.loc[i,'ignoreTrial'] = True
    
    return df