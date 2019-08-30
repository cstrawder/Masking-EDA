# -*- coding: utf-8 -*-
"""
Created on Tue Aug 20 15:47:02 2019

@author: chelsea.strawder
"""

from __future__ import division
import h5py
import fileIO
import numpy as np


def nogo_turn(data, ignoreRepeats=True, returnArray=True):

    d = data
    trialResponse = d['trialResponse'].value
    trialTargetFrames = d['trialTargetFrames'][:len(trialResponse)]
    trialRespFrames = d['trialResponseFrame'].value
    trialOpenLoop = d['trialOpenLoopFrames'][:len(trialResponse)] 
    stimStart = d['trialStimStartFrame'].value
    deltaWheel = d['deltaWheelPos'].value
    
    no_goTurnDir = []   #returns an array of values that show the direction turned for ALL no-go trials,


    if 0 in trialTargetFrames:
        no_goTotal = len(trialTargetFrames[trialTargetFrames==0])
        no_goCorrect = len(trialResponse[(trialResponse==1) & (trialTargetFrames==0)])  
    else:
        print('There were no no-go trials')


    if ignoreRepeats == True: 
        trialResponseOG = d['trialResponse'].value
        if 'trialRepeat' in d.keys():
            prevTrialIncorrect = d['trialRepeat'][:len(trialResponseOG)]
        else:
            prevTrialIncorrect = np.concatenate(([False],trialResponseOG[:-1]<1))
        no_goTotal = len(trialTargetFrames[(prevTrialIncorrect==False) & (trialTargetFrames==0)])
        no_goCorrect = len(trialTargetFrames[(prevTrialIncorrect==False) & (trialResponse==1) & (trialTargetFrames==0)])
        stimStart = stimStart[prevTrialIncorrect==False]
        trialResponse = trialResponseOG[prevTrialIncorrect==False]
        trialTargetFrames = trialTargetFrames[prevTrialIncorrect==False]
        trialRespFrames = trialRespFrames[prevTrialIncorrect==False]
        trialOpenLoop = trialOpenLoop[prevTrialIncorrect==False]
    elif ignoreRepeats==False:
        trialResponse = d['trialResponse'].value
   
    
    stimStart = stimStart[trialTargetFrames==0]
    no_goResp = trialResponse[trialTargetFrames==0]     #trial response
    trialRespFrames = trialRespFrames[trialTargetFrames==0]
    trialOpenLoop = trialOpenLoop[trialTargetFrames==0]
    deltaWheel = d['deltaWheelPos'].value
    
    
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
    
    
    
    if returnArray==True:    
        return no_goTurnDir
    else:
        print('No-go Correct:  ' + str(round(no_goCorrect/no_goTotal, 2)) + ' of ' + str(no_goTotal))
        print('no-go turn R:  ' + str(sum(no_goTurnDir==1)))
        print('no-go turn L:  ' + str(sum(no_goTurnDir==-1)))        
        