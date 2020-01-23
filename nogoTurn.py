# -*- coding: utf-8 -*-
"""
Created on Tue Aug 20 15:47:02 2019

@author: chelsea.strawder


I want this to also return the index of the nogos/maskOnly

"""

import h5py
import fileIO
import numpy as np
from ignoreTrials import ignore_trials


def nogo_turn(data, ignoreRepeats=True, returnArray=True):

    d = data
    trialResponse = d['trialResponse'][:]
    trialTargetFrames = d['trialTargetFrames'][:len(trialResponse)]
    trialMaskContrast = d['trialMaskContrast'][:len(trialResponse)]

    if 0 not in trialTargetFrames:
        print('There were no nogo trials')
    else:

        trialRespFrames = d['trialResponseFrame'][:]
        trialOpenLoop = d['trialOpenLoopFrames'][:len(trialResponse)] 
        stimStart = d['trialStimStartFrame'][:len(trialResponse)]
        deltaWheel = d['deltaWheelPos'][:]
        
        nogoTurnDir = []   #returns an array of values that show the direction turned for ALL no-go trials,
    
        noTargetTrials = trialTargetFrames[trialTargetFrames==0]
        noTarget = trialTargetFrames==0
        nogoTotal = len(trialTargetFrames[(trialTargetFrames==0) & (trialMaskContrast==0)])
        nogoCorrect = len(trialResponse[(trialTargetFrames==0) & (trialMaskContrast==0) & (trialResponse==1)])  
   
        if ignoreRepeats == True: 
            trialResponseOG = d['trialResponse'][:]
            if 'trialRepeat' in d.keys():
                prevTrialIncorrect = d['trialRepeat'][:len(trialResponseOG)]
            else:
                prevTrialIncorrect = np.concatenate(([False],trialResponseOG[:-1]<1))
            nogoTotal = len(trialTargetFrames[(prevTrialIncorrect==False) & (trialTargetFrames==0) & (trialMaskContrast==0)])
            nogoCorrect = len(trialTargetFrames[(prevTrialIncorrect==False) & (trialResponse==1) & (trialTargetFrames==0) & (trialMaskContrast==0)])
            trialStimStart = stimStart[(prevTrialIncorrect==False)]
            trialResponse = trialResponseOG[prevTrialIncorrect==False]
            trialTargetFrames = trialTargetFrames[prevTrialIncorrect==False]
            trialRespFrames = trialRespFrames[prevTrialIncorrect==False]
            trialOpenLoop = trialOpenLoop[prevTrialIncorrect==False]
            trialMaskContrast = trialMaskContrast[prevTrialIncorrect==False]
        elif ignoreRepeats==False:
            trialResponse = d['trialResponse'][:]
        
        deltaWheel = d['deltaWheelPos'][:]    
        
        startWheelPos = [[],[]]  # first is nogo, 2nd maskOnly
        endWheelPos = [[],[]]
        ind = [[],[]]

        for i, (start, end, resp, target, mask) in enumerate(
                zip(trialStimStart, trialRespFrames, trialResponse, trialTargetFrames, trialMaskContrast)):
            if mask==0:
                if target==0 and resp==-1:
                      endWheelPos[0].append(deltaWheel[end])
                      startWheelPos[0].append(deltaWheel[start])
                      ind[0].append(i)
            elif mask>0 and target==0 and resp==-1:
                endWheelPos[1].append(deltaWheel[end])
                startWheelPos[1].append(deltaWheel[start])
                ind[1].append(i)
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        nogoStimStart = stimStart[(trialTargetFrames==0) & (trialMaskContrast==0)]
        nogoResp = trialResponse[(trialTargetFrames==0) & (trialMaskContrast==0)]
        nogoTrialRespFrames = trialRespFrames[(trialTargetFrames==0) & (trialMaskContrast==0)]
        trialOpenLoop = trialOpenLoop[(trialTargetFrames==0) & (trialMaskContrast==0)]
   
        
        startWheelPos = []
        endWheelPos = []
        
        for (start, end, resp) in zip(nogoStimStart, nogoTrialRespFrames, nogoResp):
            if resp==-1:
                endWheelPos.append(deltaWheel[end])
                startWheelPos.append(deltaWheel[start])
            
        endWheelPos = np.array(endWheelPos)
        startWheelPos = np.array(startWheelPos)   
        wheelPos = endWheelPos - startWheelPos
        
        for i in wheelPos:
            if i >0:
                nogoTurnDir.append(1)
            else:
                nogoTurnDir.append(-1)
        
        nogoTurnDir = np.array(nogoTurnDir)
        
        
    print('No-go Correct:  ' + str(round(nogoCorrect/nogoTotal, 2)) + ' of ' + str(nogoTotal))
    print('no-go turn R:  ' + str(sum(nogoTurnDir==1)))
    print('no-go turn L:  ' + str(sum(nogoTurnDir==-1)))    
        
    if 1 in trialMaskContrast:
        maskTotal = len(trialResponse[(trialMaskContrast>0)])
        maskOnlyTotal = len(trialResponse[(trialMaskContrast>0) & (trialTargetFrames==0)])   # rotation task 'mask only' trials can't be 'correct'
        #maskOnlyCorr = len(trialResponse[(trialMaskContrast>0) & (trialResponse==1) & (trialTargetFrames==0)])
          
        maskStimStart = stimStart[(trialTargetFrames==0) & (trialMaskContrast>0)]             
        maskTrialRespFrames = trialRespFrames[(trialTargetFrames==0) & (trialMaskContrast>0)]
        
        startWheelPos = []
        endWheelPos = []
        
        # we want to see which direction they moved the wheel on mask-only trials 
        for i, (start, end) in enumerate(zip(maskStimStart, maskTrialRespFrames)):    #maskOnly
            endWheelPos.append(deltaWheel[end])
            startWheelPos.append(deltaWheel[start])
        
        maskEnd = np.array(endWheelPos)
        maskStart = np.array(startWheelPos)
        maskWheelPos = maskEnd - maskStart
        
        maskOnlyTurnDir = []
        
        for j in maskWheelPos:
            if j>0:
                maskOnlyTurnDir.append(1)
            else:
                maskOnlyTurnDir.append(-1)
         
        maskOnlyTurnDir = np.array(maskOnlyTurnDir)
        maskOnlyR = sum(maskOnlyTurnDir==1)
        maskOnlyL = sum(maskOnlyTurnDir==-1)   

    print('Mask Only Trials: ' + str(maskOnlyTotal))
    print('Mask only turn R: ' + str(maskOnlyR))
    print('Mask only turn L: ' + str(maskOnlyL))
    

    if returnArray==True:    
        return [nogoTurnDir, maskOnlyTurnDir]

         
     
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        


        