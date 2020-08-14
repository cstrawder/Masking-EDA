# -*- coding: utf-8 -*-
"""
Created on Mon Aug 12 12:42:51 2019

@author: chelsea.strawder 
"""
"""
replica of percentCorrectBySideIgnoreRepeats, just turned into a function (maily for use in plotting)
"""

import h5py
import fileIO
import numpy as np
import matplotlib.pyplot as plt
from behaviorAnalysis import get_files, formatFigure
import statsmodels.api as sm


def performance_data(mouse, ignoreRepeats=True):
    
    def count(resp, direction):
        return len(trialResponse[(trialResponse==resp) & (trialRewardDirection==direction) & (trialTargetFrames!=0)])
        
    rightCorr = []
    leftCorr = []
    rightNoResp = []
    leftNoResp = []
    totalTrials = []

    no_goCorr = []
    no_goMoveL = []
    no_goMoveR = []

    files = get_files(mouse, 'training_')
    for i,f in enumerate(files):
        d = h5py.File(f)
 
        trialResponse = d['trialResponse'][:]
        trialRewardDirection = d['trialRewardDir'][:len(trialResponse)]
        trialTargetFrames = d['trialTargetFrames'][:len(trialResponse)]      
        
        if ignoreRepeats== True and d['incorrectTrialRepeats'][()] > 0:
            trialResponseOG = trialResponse        
            if 'trialRepeat' in d.keys():
                prevTrialIncorrect = d['trialRepeat'][:len(trialResponse)]
            else:   
                prevTrialIncorrect = np.concatenate(([False],trialResponseOG[:-1]<1))
            trialResponse = trialResponseOG[prevTrialIncorrect==False]
            trialRewardDirection = trialRewardDirection[prevTrialIncorrect==False]
            trialTargetFrames = trialTargetFrames[prevTrialIncorrect==False]
            print('Repeats: ' + (str((len(trialResponseOG) - len(trialResponse)))) + '/' + str(len(trialResponseOG)))
    
        elif ignoreRepeats == False or d['incorrectTrialRepeats'][()]==0:
            pass
     
        
        rightTurnTotal = sum((trialRewardDirection==1) & (trialTargetFrames!=0))
        leftTurnTotal = sum((trialRewardDirection==-1) & (trialTargetFrames!=0))
        
        # count(response, reward direction) where -1 is turn left 
        rightTurnCorr, leftTurnCorr = count(1,1), count(1,-1)
        rightTurnIncorrect, leftTurnIncorrect = count(-1,1), count(-1,-1)
        rightNoResp, leftNoResp = count(0,1), count(0,-1)
        
        respTotal = (leftTurnTotal + rightTurnTotal) - (rightNoResp + leftNoResp)
        total = (leftTurnTotal + rightTurnTotal)


        leftCorr.append(leftTurnCorr/leftTurnTotal)
        rightCorr.append(rightTurnCorr/rightTurnTotal)
        totalTrials.append(total)
            
                                 
         
    #  make this a function? 
#        if 0 not in trialTargetFrames:
#            pass
#        elif 0 in trialTargetFrames:     
#            no_goTotal = len(trialTargetFrames[trialTargetFrames==0])
#            no_goCorrect = len(trialResponse[(trialTargetFrames==0) & (trialResponse==1)]) 
#            print('No-go Correct:  ' + str(round(no_goCorrect/no_goTotal, 2)) + ' of ' + str(no_goTotal))
#        
#        #returns an array of values that show the direction turned for ALL no-go trials, then returns % per direction  
#            no_goTurnDir = []
#      
#            stimStart= d['trialStimStartFrame'][:len(trialResponse)]
#            trialRespFrames = d['trialResponseFrame'][:len(trialResponse)]
#            trialOpenLoop = d['trialOpenLoopFrames'][:len(trialResponse)] 
#            deltaWheel = d['deltaWheelPos'].value
#            
#            
#            if ignoreRepeats== True: 
#               stimStart = stimStart[prevTrialIncorrect==False]
#               trialRespFrames = trialRespFrames[prevTrialIncorrect==False]
#               trialOpenLoop = trialOpenLoop[prevTrialIncorrect==False]
#        
#            stimStart = stimStart[trialTargetFrames==0]
#            trialRespFrames = trialRespFrames[trialTargetFrames==0]
#            trialOpenLoop = trialOpenLoop[trialTargetFrames==0]
#            deltaWheel = d['deltaWheelPos'].value
#            no_goResp = trialResponse[trialTargetFrames==0]
#            
#            stimStart += trialOpenLoop
#            
#            startWheelPos = []
#            endWheelPos = []
#            
#            for (start, end, resp) in zip(stimStart, trialRespFrames, no_goResp):
#                if resp==-1:
#                    endWheelPos.append(deltaWheel[end])
#                    startWheelPos.append(deltaWheel[start])
#                
#            endWheelPos = np.array(endWheelPos)
#            startWheelPos = np.array(startWheelPos)   
#            wheelPos = endWheelPos - startWheelPos
#            
#            for i in wheelPos:
#                if i >0:
#                    no_goTurnDir.append(1)
#                else:
#                    no_goTurnDir.append(-1)
#            
#            no_goTurnDir = np.array(no_goTurnDir)
#            print('no-go turn R:  ' + str(sum(no_goTurnDir==1)))
#            print('no-go turn L:  ' + str(sum(no_goTurnDir==-1)))
#        

        d.close()

    fig, ax = plt.subplots()
    xaxis = range(len(files))
    ax.plot(xaxis, rightCorr, 'ro-')
    ax.plot(xaxis, leftCorr, 'bo-')
   # ax.plot(xaxis, np.mean(rightCorr+leftCorr), 'k--')
    formatFigure(fig, ax, xLabel='Session number', yLabel='Percent Correct', title='Performance over time,  ' + mouse, xTickLabels=range(len(files)))  
    
    