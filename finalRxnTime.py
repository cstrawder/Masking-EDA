# -*- coding: utf-8 -*-
"""
Created on Mon Apr 20 14:15:32 2020

@author: chelsea.strawder

combining my modifiedInterpWheel, Sam's code, and formating it for use with df

call rxnTimes --> returns array with 3 arrays; append arrays to df

can either call this for ignore trials or the old code; old code calls this function

"""

from dataAnalysis import create_df  
from dataAnalysis import wheel_trace_slice
import numpy as np


def rxnTimes(data, dataframe):
    
    d = data
    df = dataframe
    
    fi = d['frameIntervals'][:]
    framerate = int(np.round(1/np.median(fi)))
    
    monitorSize = d['monSizePix'][0] 
    
    normRewardDist = d['normRewardDistance'][()]
    maxQuiescentMove = d['maxQuiescentNormMoveDist'][()]
    wheelSpeedGain = d['wheelSpeedGain'][()]
    
    initiationThreshDeg = 0.5  #how did he decide this?
    initiationThreshPix = initiationThreshDeg*np.pi/180*wheelSpeedGain
    sigThreshold = maxQuiescentMove * monitorSize
    rewThreshold = normRewardDist * monitorSize

    wheelTrace = wheel_trace_slice(df)
    cumulativeWheel = [np.cumsum(mvmt) for mvmt in wheelTrace]

    interpWheel = []
    initiateMovement = []
    significantMovement = []
    ignoreTrials = []  # old ignore_trials func actually calls this func, returns this list
    outcomeTimes = []
    
    ## use below code to determine wheel direction changes during trial 
    # during just trial time (ie in nogos before trial ends) or over entire potential time? 
    
    for i, (wheel, resp, rew, soa) in enumerate(zip(
            cumulativeWheel, df['resp'], df['rewDir'], df['soa'])):

        fp = wheel
        xp = np.arange(0, len(fp))*1/framerate
        x = np.arange(0, xp[-1], .001)
        interp = np.interp(x,xp,fp)
        interpWheel.append(interp)
        
        if (rew==0) and (resp==1):
            init = 0 
        elif (rew==0) and (resp==-1):
            init = np.argmax(abs(interp[100:])>initiationThreshPix) + 100
# sam wants to allow mvmt before 100 ms for nogos; doesnt matter what they do before 200 ms gotone
        else:
            init = np.argmax(abs(interp)>initiationThreshPix)
        initiateMovement.append(init)
        
        sigMove = np.argmax(abs(interp)>=sigThreshold)
        significantMovement.append(sigMove)
        
        if (0<init<100) and (0<sigMove<100):
            ignoreTrials.append(i)
            
        outcome = np.argmax(abs(interp)>= rewThreshold)
        if outcome>0:
            outcomeTimes.append(outcome)
        else:
            outcomeTimes.append(0)

    return np.array([initiateMovement, outcomeTimes, ignoreTrials])
         

                
                
                
