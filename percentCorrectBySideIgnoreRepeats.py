# -*- coding: utf-8 -*-
"""
Created on Tue Jun 25 15:01:44 2019

@author: svc_ccg

Returns the fraction of trials that are correct, incorrect, and no response for each side (left stim vs right stim)
Choose whether you want the repeated trials to be included in the averages 

Can be used for either task, based on turning direction 
"""

from __future__ import division
import h5py
import fileIO
import numpy as np

f = fileIO.getFile(rootDir=r'\\allen\programs\braintv\workgroups\nc-ophys\corbettb\Masking')
d = h5py.File(f)


print(f.split('_')[-3:-1])

#this returns an integer of how many trials fulfilled the criteria (i.e correct right response, incorrect left response)
# these ints are later used to calculate the percent of the total

def count(resp, direction):
    return len(trialResponse[(trialResponse==resp) & (trialRewardDirection==direction) & (trialTargetFrames!=0)])


trialRewardDirection = d['trialRewardDir'].value[:-1]
trialTargetFrames = d['trialTargetFrames'].value[:-1]
targetFrames = d['targetFrames'].value

ignore = raw_input('Ignore repeats? (yes/no)  ')   # yes or no in console to ignore repeated trial results

if ignore.upper()== 'YES': 
    trialResponseOG = d['trialResponse'].value
    prevTrialIncorrect = np.concatenate(([False],trialResponseOG[:-1]<1))
    trialResponse = trialResponseOG[prevTrialIncorrect==False]
    trialRewardDirection = trialRewardDirection[prevTrialIncorrect==False]
    trialTargetFrames = trialTargetFrames[prevTrialIncorrect==False]
    print('Repeats: ' + (str((len(trialResponseOG) - len(trialResponse)))) + '/' + str(len(trialResponseOG)))
elif ignore.upper() == 'NO':
    trialResponse = d['trialResponse'].value
    print('Trials: ' + (str(len(trialResponse))))
else:
    print('Please type yes or no')
    ignore = raw_input('Ignore repeats?  ')
       

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
    

#  make this a function? 

if 0 in trialTargetFrames:
    no_goTotal = len(trialTargetFrames[trialTargetFrames==0])
    no_goCorrect = len(trialResponse[(trialResponse==1) & (trialTargetFrames==0)]) 
    print('No-go Correct:  ' + str(round(no_goCorrect/no_goTotal, 2)) + ' of ' + str(no_goTotal))

#returns an array of values that show the direction turned for ALL no-go trials, then returns % per direction  
    no_goTurnDir = []

    stimStart = d['trialStimStartFrame'][:-1] 
                                                    # this accounts for those trials where the trial started then the session ended
    if len(stimStart)==len(prevTrialIncorrect):     # otherwise the arrays are different lengths and can't be indexed
        pass
    else:
        stimStart= d['trialStimStartFrame'].value
        trialRespFrames = d['trialResponseFrame'].value
        trialOpenLoop = d['trialOpenLoopFrames'][:-1] 
        deltaWheel = d['deltaWheelPos'].value

    if ignore.upper()== 'YES': 
       stimStart = stimStart[prevTrialIncorrect==False]
       trialRespFrames = trialRespFrames[prevTrialIncorrect==False]
       trialOpenLoop = trialOpenLoop[prevTrialIncorrect==False]

    stimStart = stimStart[trialTargetFrames==0]
    trialRespFrames = trialRespFrames[trialTargetFrames==0]
    trialOpenLoop = trialOpenLoop[trialTargetFrames==0]
    deltaWheel = d['deltaWheelPos'].value
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
    
    
trialRewards = 0    
    
for trial, rew in zip(trialResponse, trialRewardDirection):
    if trial==0 & rew==0:
        trialRewards+=1
    elif rew==1:
        trialRewards+=1
    else:
        pass
    
print("Rewards this session:  " + str(trialRewards))
