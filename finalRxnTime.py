# -*- coding: utf-8 -*-
"""
Created on Mon Apr 20 14:15:32 2020

@author: chelsea.strawder

combining my modifiedInterpWheel, Sam's code, and formating it for use with df

call rxnTimes --> returns array; append array to df

can either call this for ignore trials or the old code; old code calls this function

"""

from dataAnalysis import import_data, create_df  # for now - won't need once function is complete
from modifiedInterpWheel import wheel_trace_slice
import numpy as np
import pandas as pd


d = import_data()       # want to use d later to pull vals for analysis


def rxnTimes(data, output='initiation'):
    '''
    outcome == 'initiation', 'ignoreTrials', 'outcomeTime', 'choice'
    'choice' refers to the wheel movement that leads to a choice; useful for looking
    at wheel direction changes/calculating velocity (sam's code, goes backwards from rewardThresh)
    '''
    
    d = data
    df = create_df(d)
    
    fi = d['frameIntervals'][:]
    framerate = int(np.round(1/np.median(fi)))
    
    monitorSize = d['monSizePix'][0] 
    
    normRewardDist = d['normRewardDistance'][()]
    wheelSpeedGain = d['wheelSpeedGain'][()]
    
    rewThreshold = normRewardDist * monitorSize
    initiationThreshDeg = 0.5  #how did he decide this?
    initiationThreshPix = initiationThreshDeg*np.pi/180*wheelSpeedGain
    
    wheelTrace = wheel_trace_slice(df)
    cumulativeWheel = [np.cumsum(mvmt) for mvmt in wheelTrace]

    interpWheel = []
    initiateMovement = []
    ignoreTrials = []
    outcomeTimes = []
    
    for i, (wheel, resp, rew, soa) in enumerate(zip(
            cumulativeWheel, df['resp'], df['rewDir'], df['soa'])):
        if (rew==0 and resp==1) or (resp==0):   
            
            initiateMovement.append(0)
            interpWheel.append(0)
            outcomeTimes.append(0)
        else:
            fp = wheel
            xp = np.arange(0, len(fp))*1/framerate
            x = np.arange(0, xp[-1], .001)
            interp = np.interp(x,xp,fp)
            interpWheel.append(interp)

            init = np.argmax(abs(interp)>initiationThreshPix)
            initiateMovement.append(init)
            if init<100:
                ignoreTrials.append(i)
                
            outcome = np.argmax(abs(interp)>= rewThreshold)
            if outcome>0:
                outcomeTimes.append(outcome)
            else:
                outcomeTimes.append(0)

    if output=='ignoreTrials':
        return ignoreTrials
    elif output=='outcomeTime':
        return outcomeTimes
    else:
        return initiateMovement
         
                
                
                
                
