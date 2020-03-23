# -*- coding: utf-8 -*-
"""
Created on Wed Mar 11 13:02:06 2020

@author: chelsea.strawder

My hope is to combine and condense all of the data analysis functions into a single file
that we can then use to analyze the session data in a simpler script 
"""

import fileIO, h5py
import numpy as np
import pandas as pd
from nogoData import nogo_turn
from ignoreTrials import ignore_trials


def import_data():
    f = fileIO.getFile(rootDir=r'\\allen\programs\braintv\workgroups\nc-ophys\corbettb\Masking')
    d = h5py.File(f)
    return d

def extract_vars(data):
    return {key: data[str(key)][()] for key in data.keys()}
    

def create_vars(dn):
    for key,val in dn.items():
        return exec (key + '=val')



def create_df(d):   #contrast, target, mask    
    
    fi = d['frameIntervals'][:]
    framerate = int(np.round(1/np.median(fi)))
    
    #pull all of the relevant data to create a dataframe object 
    trialResponse = d['trialResponse'][:]
    end = len(trialResponse)
    trialRewardDirection = d['trialRewardDir'][:end]
    trialTargetFrames = d['trialTargetFrames'][:end]
    trialStartFrame = d['trialStartFrame'][:]    
    preStimFrames = d['preStimFramesFixed'][()]
    preStimVar = d['preStimFramesVariableMean'][()]              
    openLoopFrames = d['openLoopFramesFixed'][()]
    openLoopVar = d['openLoopFramesVariableMean'][()]
    openLoopMax = d['openLoopFramesMax'][()]
    trialOpenLoopFrames = d['trialOpenLoopFrames'][:end]
    maxQuiescentMove = d['maxQuiescentNormMoveDist'][()]
    quiescentMoveFrames = d['quiescentMoveFrames'][:]    #would be nice to count these per trial
    trialStimStartFrame = d['trialStimStartFrame'][:]
    trialResponseFrame = d['trialResponseFrame'][:end] 
    trialEndFrame = d['trialEndFrame'][:end]
    deltaWheel = d['deltaWheelPos'][:]                      
    trialMaskContrast = d['trialMaskContrast'][:end]
    trialTargetContrast = d['trialTargetContrast'][:end]
    nogoWait = d['nogoWaitFrames'][()]
    
    def convert_to_ms(value):
        return np.round(value * 1000/framerate).astype(int)
    
    # converted to ms
    maskOnset = convert_to_ms(d['maskOnset'][()])
    trialMaskOnset = convert_to_ms(d['trialMaskOnset'][:end])
    
    for i, target in enumerate(trialTargetFrames):  # this is needed for older files nogos are randomly assigned a dir
        if target==0:
            trialRewardDirection[i] = 0
    
    nogos = [i for i, (rew, con) in enumerate(zip(trialRewardDirection, trialMaskContrast)) if rew==0 and con==0]
   
    if np.any(trialMaskOnset>0):
        noMaskVal = maskOnset[-1] + round(np.mean(np.diff(maskOnset)))  # assigns noMask condition an evenly-spaced value from soas
        maskOnset = np.append(maskOnset, noMaskVal)              # makes final value the no-mask condition
            
        for i, (mask, trial) in enumerate(zip(trialMaskOnset, trialTargetFrames)):   # filters target-Only trials 
            if trial>0 and mask==0:
                trialMaskOnset[i]=noMaskVal       
    
    trialWheel = []   
    for i, (stimStart, resp) in enumerate(zip(trialStimStartFrame, trialResponseFrame)):
        trialWheel.append(deltaWheel[stimStart:resp])
    
    cumWheel = [np.cumsum(mvmt) for mvmt in trialWheel]
    
    ignoreTrials = ignore_trials(d)

    nogoTurn, maskOnly, inds = nogo_turn(d)  # 1st 2 arrays are turned direction, 3rd is indices of 1st 2                       

    nogoMove = np.zeros(len(trialResponse)).astype(int)
    for i in range(len(trialResponse)):
        for (ind, turn) in zip(inds[0], nogoTurn):
            if i==ind:
                nogoMove[i] = turn
    
    data = list(zip(trialRewardDirection, trialResponse, trialStartFrame, trialStimStartFrame, trialResponseFrame))
    index = range(len(trialResponse))

    df = pd.DataFrame(data, index=index, columns=[
            'rewDir', 'resp', 'trialStart', 'stimStart', 'respFrame'])
    
    df['trialLength'] = [convert_to_ms(len(t)) for t in trialWheel]
    df['mask'] = trialMaskContrast
    df['soa'] = trialMaskOnset
   # df['maskLength'] = convert_to_ms(d['trialMaskFrames'][:end])
    df['maskContrast'] = trialMaskContrast

    df['targetLength'] = convert_to_ms(d['trialTargetFrames'][:end])
    df['targetContrast'] = trialTargetContrast
    df['ignoreTrial'] = False   
    for i in ignoreTrials:
        df.loc[i, 'ignoreTrial'] = True
    df['nogoMove'] = nogoMove
    df['cumWheel'] = cumWheel
    
  
    return df





