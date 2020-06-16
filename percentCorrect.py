# -*- coding: utf-8 -*-
"""
Created on Tue Jun 25 15:01:44 2019

@author: chelsea.strawder

Returns the fraction of trials that are correct, incorrect, and no response for each side (left stim vs right stim)
Choose whether you want the repeated trials to be included in the averages.
Returns the percent correct for nogo trials and determines which direction they moved on incorrect trials.

Can be used for either task, based on turning direction 

Have to use [...] to access data in datasets (arrays)
use .dtype to check data type in datasets 

This is a copy of the orginal script, intended for Python 3 and working at my computer.
"""

import h5py as h5
import numpy as np
import fileIO

#
#f = fileIO.getFile(rootDir=r'\\allen\programs\braintv\workgroups\nc-ophys\corbettb\Masking')
#d = h5.File(f)

#this returns an integer of how many trials fulfilled the criteria (i.e correct right response, incorrect left response)
# these ints are later used to calculate the percent of the total
def session_stats(d):

    print(str(d))

    def count(resp, direction):
        return len(trialResponse[(trialResponse==resp) & (trialRewardDirection==direction) & (trialTargetFrames!=0)])
    
    trialResponse = d['trialResponse'][:]
    trialRewardDirection = d['trialRewardDir'][:len(trialResponse)]
    trialTargetFrames = d['trialTargetFrames'][:len(trialResponse)]
    targetFrames = d['targetFrames'][()]
    
    if d['incorrectTrialRepeats'][...]>0:
        ignore = 'yes' #input('Ignore repeats? (yes/no)  ')   # yes or no in console to ignore repeated trial results
    else:
        pass
    
    
    if ignore.upper()== 'YES': 
        trialResponseOG = trialResponse
        prevTrialIncorrect = np.concatenate(([False],trialResponseOG[:-1]<1))
        trialResponse = trialResponseOG[prevTrialIncorrect==False]
        trialRewardDirection = trialRewardDirection[prevTrialIncorrect==False]
        trialTargetFrames = trialTargetFrames[prevTrialIncorrect==False]
        print('Repeats: ' + (str((len(trialResponseOG) - len(trialResponse)))) + '/' + str(len(trialResponseOG)))
    elif ignore.upper() == 'NO':
        trialResponse = d['trialResponse'][:]
        print('Trials: ' + (str(len(trialResponse))))
    else:
        print('Please type yes or no')
        ignore = input('Ignore repeats?  ')
           
    
    rightTurnTotal = sum((trialRewardDirection==1) & (trialTargetFrames!=0))
    leftTurnTotal = sum((trialRewardDirection==-1) & (trialTargetFrames!=0))
    
    # count(response, reward direction) where -1 is turn left 
    rightTurnCorr, leftTurnCorr = count(1,1), count(1,-1)
    rightTurnIncorrect, leftTurnIncorrect = count(-1,1), count(-1,-1)
    rightNoResp, leftNoResp = count(0,1), count(0,-1)
    
    respTotal = (leftTurnTotal + rightTurnTotal) - (rightNoResp + leftNoResp)
    total = (leftTurnTotal + rightTurnTotal)
    
    print("Left trial total: " + str(leftTurnTotal))
    print("Right trial total: " + str(rightTurnTotal))
    
    for i, (num, denom, title) in enumerate(zip([
                                    rightTurnCorr, rightTurnIncorrect, rightNoResp, 
                                    leftTurnCorr, leftTurnIncorrect, leftNoResp, 
                                    (leftTurnCorr+rightTurnCorr), (leftTurnCorr+rightTurnCorr)], 
                                     [rightTurnTotal, rightTurnTotal, rightTurnTotal, 
                                      leftTurnTotal, leftTurnTotal, leftTurnTotal, respTotal, total],
                                 ['R % Correct:', 'R % Incorrect:', 'R % No Resp:', 
                                 'L % Correct:', 'L % Incorrect:', 'L % No Resp:', 
                                 'Total Correct, given Response:', 'Total Correct:'])):
                             
        print(str(title) + '   ' + str(round(num/denom, 2)))
        
    
    #  make this a function? 
    
    if 0 in trialTargetFrames:
        no_goTotal = len(trialTargetFrames[trialTargetFrames==0])
        no_goCorrect = len(trialResponse[(trialResponse==1) & (trialTargetFrames==0)]) 
        print('No-go Correct:  ' + str(round(no_goCorrect/no_goTotal, 2)*100) + '% of ' + str(no_goTotal))
        
        
        
    
    #returns an array of values that show the direction turned for ALL no-go trials, then returns % per direction  
        no_goTurnDir = []
    
        stimStart = d['trialStimStartFrame'][:-1] 
                                                        # this accounts for those trials where the trial started then the session ended
        if len(stimStart)==len(prevTrialIncorrect):     # otherwise the arrays are different lengths and can't be indexed
            pass
        else:
            stimStart= d['trialStimStartFrame'][:]
            trialRespFrames = d['trialResponseFrame'][:]
            trialOpenLoop = d['trialOpenLoopFrames'][:len(stimStart)] 
            deltaWheel = d['deltaWheelPos'][:]
    
        if ignore.upper()== 'YES': 
           stimStart = stimStart[prevTrialIncorrect==False]
           trialRespFrames = trialRespFrames[prevTrialIncorrect==False]
           trialOpenLoop = trialOpenLoop[prevTrialIncorrect==False]
    
        stimStart = stimStart[trialTargetFrames==0]
        trialRespFrames = trialRespFrames[trialTargetFrames==0]
        trialOpenLoop = trialOpenLoop[trialTargetFrames==0]
        deltaWheel = d['deltaWheelPos'][:]
        no_goResp = trialResponse[trialTargetFrames==0]
        
        stimStart += trialOpenLoop
        
        startWheelPos = []
        endWheelPos = []
        
        for (start, end, resp) in zip(stimStart, trialRespFrames, no_goResp):
            if resp==-1:
                endWheelPos.append(deltaWheel[end])
                startWheelPos.append(deltaWheel[start])
            
        endWheelPos = np.array(endWheelPos)
        startWheelPos = np.array(startWheelPos)   
        wheelPos = endWheelPos - startWheelPos
        
        for i in wheelPos:
            if i >0:
                no_goTurnDir.append(1)
            else:
                no_goTurnDir.append(-1)
        
        no_goTurnDir = np.array(no_goTurnDir)
        print('no-go turn R:  ' + str(sum(no_goTurnDir==1)))
        print('no-go turn L:  ' + str(sum(no_goTurnDir==-1)))
    else:
        print('*There were no nogos')
        
    trialRewards = 0    
        
    for trial, rew in zip(trialResponse, trialRewardDirection):
        if trial==0 & rew==0:
            trialRewards+=1
        elif rew==1:
            trialRewards+=1
        else:
            pass
        
    print("Rewards this session:  " + str(trialRewards))
    
    
    normReward = d['normRewardDistance'][()]
    maxResp = d['maxResponseWaitFrames'][()]
    probNogo = d['probNoGo'][()]
    probGoR = d['probGoRight'][()]
    
    fi = d['frameIntervals'][:]
    framerate = int(np.round(1/np.median(fi)))
    sessionDuration = d['trialResponseFrame'][-1]
    
    print('\n')
    print('Norm reward: ' + str(normReward))
    print('Max wait frames: ' + str(maxResp))
    print('Prob nogo: ' + str(probNogo))
    print('Prob go right: ' + str(probGoR))
    print('Session duration (mins): ' + str(np.round(sessionDuration/framerate/60, 2)))
    
    
    
