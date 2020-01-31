# -*- coding: utf-8 -*-
"""
Created on Wed Aug 14 13:46:52 2019

@author: chelsea.strawder
"""

import h5py
import fileIO
import numpy as np
import psignifit as ps
import psigniplot
import ignoreTrials

'''
First, we need to pull the data from the file (session) we want to analyze
Then we need the data in the format (x | nCorrect | total)
'''


f = fileIO.getFile(rootDir=r'\\allen\programs\braintv\workgroups\nc-ophys\corbettb\Masking')
d = h5py.File(f)

#this returns an integer of how many trials fulfilled the criteria (i.e correct right response, incorrect left response)
# these ints are later used to calculate the percent of the total

def count(resp, direction):
    return len(trialResponse[(trialResponse==resp) & (trialRewardDirection==direction) & (trialTargetFrames!=0)])


trialRewardDirection = d['trialRewardDir'].value[:-1]
trialTargetFrames = d['trialTargetFrames'].value[:-1]
targetFrames = d['targetFrames'].value

if d['incorrectTrialRepeats'][...]>0:
    ignore = input('Ignore repeats? (yes/no)  ')   # yes or no in console to ignore repeated trial results
else:
    pass


if ignore.upper()== 'YES': 
    trialResponseOG = d['trialResponse'].value[()]
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
       
# ADD IN THE IGNORE TRIALS FUNCTION to elimiate guesses
    ## can also use those trials to train MLA??


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



data = np.array([[-1, rightTurnIncorrect, rightTurnTotal],
                 [0, rightNoResp, rightTurnTotal],
                 [1, rightTurnCorr, rightTurnTotal]])

options = dict()

res = ps.psignifit(data, options)

psigniplot.plotPsych(res)

'''
How can we also characterize the bias that is most likely for an animal model?
'''