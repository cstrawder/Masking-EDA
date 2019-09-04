# -*- coding: utf-8 -*-
"""
Created on Tue Jun 25 15:01:44 2019

@author: svc_ccg

Returns the fraction of trials that are correct, incorrect, and no response for each side (left stim vs right stim)
Choose whether you want the repeated trials to be included in the averages 

Can be used for either task, based on turning direction 
"""

from __future__ import division
import numpy as np
from nogoTurn import nogo_turn

def session(data, ignoreRepeats=True):
    
    d = data
    
    def count(resp, direction):
        return len(trialResponse[(trialResponse==resp) & (trialRewardDirection==direction) & (trialTargetFrames!=0)])
    
    trialResponse = d['trialResponse'].value
    trialRewardDirection = d['trialRewardDir'].value[:len(trialResponse)]
    trialTargetFrames = d['trialTargetFrames'].value[:len(trialResponse)]
    targetFrames = d['targetFrames'].value
    
    trialRewards = 0    
    
    for trial in trialResponse:
        if trial==1:
            trialRewards+=1
        
    print("Rewards this session:  " + str(trialRewards))
    
    
    if ignoreRepeats == True:
        trialResponseOG = d['trialResponse'].value
        #nogo_turn(d, ignoreRepeats=True, returnArray=False)
        if 'trialRepeat' in d.keys():
            prevTrialIncorrect = d['trialRepeat'][:len(trialResponse)]
        else:
            prevTrialIncorrect = np.concatenate(([False],trialResponseOG[:-1]<1))
        trialResponse = trialResponseOG[prevTrialIncorrect==False]
        trialRewardDirection = trialRewardDirection[prevTrialIncorrect==False]
        trialTargetFrames = trialTargetFrames[prevTrialIncorrect==False]
        print('Repeats: ' + (str((len(trialResponseOG) - len(trialResponse)))) + '/' + str(len(trialResponseOG)))
        
    elif ignoreRepeats == False:
        trialResponse = d['trialResponse'].value
        #nogo_turn(d, ignoreRepeats=False, returnArray=False)
        print('Trials: ' + (str(len(trialResponse))))
    else:
        pass
           
    
    rightTurnTotal = sum((trialRewardDirection==1) & (trialTargetFrames!=0))
    leftTurnTotal = sum((trialRewardDirection==-1) & (trialTargetFrames!=0))
    
    # count(response, reward direction) where -1 is turn left 
    rightTurnCorr, leftTurnCorr = count(1,1), count(1,-1)
    rightTurnIncorrect, leftTurnIncorrect = count(-1,1), count(-1,-1)
    rightNoResp, leftNoResp = count(0,1), count(0,-1)
    
    respTotal = (leftTurnTotal + rightTurnTotal) - (rightNoResp + leftNoResp)
    total = (leftTurnTotal + rightTurnTotal)
    
    for i, (num, denom, title) in enumerate(zip([
                                    rightTurnCorr, rightTurnIncorrect, rightNoResp, 
                                    leftTurnCorr, leftTurnIncorrect, leftNoResp, 
                                    (leftTurnCorr+rightTurnCorr), (leftTurnCorr+rightTurnCorr)], 
                                     [rightTurnTotal, rightTurnTotal, rightTurnTotal, 
                                      leftTurnTotal, leftTurnTotal, leftTurnTotal, respTotal, total],
                                 ['Turn R % Correct:', 'Turn R % Incorre:', 'Turn R % No Resp:', 
                                 'L % Correct:', 'L % Incorre:', 'L % No Resp:', 
                                 'Total Correct, given Response:', 'Total Correct:'])):
                             
        print(str(title) + '   ' + str(round(num/denom, 2)))
    
    
