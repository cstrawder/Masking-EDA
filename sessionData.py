# -*- coding: utf-8 -*-
"""
Created on Tue Jun 25 15:01:44 2019

@author: svc_ccg

Returns the fraction of trials that are correct, incorrect, and no response for each side (left stim vs right stim)
Choose whether you want the repeated trials to be included in the averages 

Can be used for either task, based on turning direction 
"""

import numpy as np
import matplotlib.pyplot as plt 
from nogoTurn import nogo_turn

def session(data, ignoreRepeats=True, printValues=True):
    
    d = data
    
    def count(resp, direction):
        return len(trialResponse[(trialResponse==resp) & (trialRewardDirection==direction) & (trialTargetFrames!=0)])
    

    trialResponse = d['trialResponse'][()]
    trialRewardDirection = d['trialRewardDir'][:len(trialResponse)]
    trialTargetFrames = d['trialTargetFrames'][:len(trialResponse)]

    trialRewards = 0    
    
    for trial in trialResponse:
        if trial==1:
            trialRewards+=1
        
    if ignoreRepeats == True:

        trialResponseOG = trialResponse
        trialResponseOG = d['trialResponse'][:]

        #nogo_turn(d, ignoreRepeats=True, returnArray=False)
        if 'trialRepeat' in d.keys():
            prevTrialIncorrect = d['trialRepeat'][:len(trialResponse)]
        else:
            prevTrialIncorrect = np.concatenate(([False],trialResponseOG[:-1]<1))
        trialResponse = trialResponseOG[prevTrialIncorrect==False]
        trialRewardDirection = trialRewardDirection[prevTrialIncorrect==False]
        trialTargetFrames = trialTargetFrames[prevTrialIncorrect==False]
        print('Repeats: ' + (str((len(trialResponseOG) - len(trialResponse)))) + '/' + str(len(trialResponseOG)))
        print((round(len(trialResponseOG)-len(trialResponse))/len(trialResponseOG)))
        
    elif ignoreRepeats == False:

        trialResponse = d['trialResponse'][:]

        #nogo_turn(d, ignoreRepeats=False, returnArray=False)
        print('Trials: ' + (str(len(trialResponse))))
    else:
        pass
    
       
    rightTurnTotal = sum((trialRewardDirection==1) & (trialTargetFrames!=0))   #left stim
    leftTurnTotal = sum((trialRewardDirection==-1) & (trialTargetFrames!=0))   #right stim
    nogoTotal = sum(trialTargetFrames==0)
    
    # count(response, reward direction) where -1 is turn left 
    rightTurnCorr, leftTurnCorr = count(1,1), count(1,-1)
    rightTurnIncorrect, leftTurnIncorrect = count(-1,1), count(-1,-1)
    rightNoResp, leftNoResp = count(0,1), count(0,-1)
    
    nogoCorr = sum((trialResponse==1) & (trialTargetFrames==0))
    nogoMove = len(trialResponse[(trialTargetFrames==0) & (trialResponse==-1)])
    respTotal = len(trialResponse[trialResponse!=0])
    totalCorrect = len(trialResponse[trialResponse==1])
    total = len(trialResponse)
    
    trialRewards2 = 0    
    
    for trial in trialResponse:
        if trial==1:
            trialRewards2+=1
    print('Counted rewards: ' + str(trialRewards2))
    print("Rewards this session:  " + str(trialRewards))
      
    
    for i, (num, denom, title) in enumerate(zip([rightTurnCorr, rightTurnIncorrect, rightNoResp, leftTurnCorr, leftTurnIncorrect, leftNoResp, nogoCorr, (leftTurnCorr+rightTurnCorr), totalCorrect], 
                                     [rightTurnTotal, rightTurnTotal, rightTurnTotal, 
                                      leftTurnTotal, leftTurnTotal, leftTurnTotal, nogoTotal, respTotal, total],
                                 ['Turn R % Correct:', 'Turn R % Incorre:', 'Turn R % No Resp:', 
                                 'L % Correct:', 'L % Incorre:', 'L % No Resp:', 'NoGo Corr:',
                                 'Total Correct, given Response:', 'Total Correct (incl nogos):'])):
        cell_text[i].append(num[i]/denom[i])
        
        
        if printValues==True:         
            print(str(title) + '   ' + str(round(num/denom, 2)))
        else:
            pass




