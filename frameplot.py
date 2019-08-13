# -*- coding: utf-8 -*-
"""
Created on Mon Jun 03 15:02:15 2019

@author: svc_ccg
"""

"""
plot the percent correct as a function of target length
"""

from __future__ import division
import numpy as np
import collections 
import h5py
import fileIO
from matplotlib import pyplot as plt

f = fileIO.getFile(rootDir=r'\\allen\programs\braintv\workgroups\nc-ophys\corbettb\Masking')
d = h5py.File(f)

trialRewardDirection = d['trialRewardDir'].value[:-1]
trialResponse = d['trialResponse'].value
trialLength = d['trialTargetFrames'].value[:-1]
targetLengths = d['targetFrames'].value

def create_percent(sum1, total, percent):
    for key1, val1 in sum1.items():
        for key2, val2 in total.items():
            if key1==key2:
                percent.update({key1: val1/val2})
    
#array with index values of R or L trials 
rightStim = np.where(trialRewardDirection==-1)[0]
leftStim = np.where(trialRewardDirection==1)[0]

rightStimTotal = []
leftStimTotal = []

# plot of CORRECT RESPONSES out of TOTAL
rightStimCorr = []   # rewSide = -1 (move left)
leftStimCorr = []      

# this is zipping the arrays together, separating the trials by side, and then adding the correct trials and lengths to left/rightStimCorr
for i, (resp, trial_length) in enumerate(zip(trialResponse, trialLength)): 
    if i in rightStim:
        rightStimTotal.append(trial_length)
        for j in np.unique(trial_length):
            if resp == 1:
                rightStimCorr.append(j)      
    elif i in leftStim:
        leftStimTotal.append(trial_length)
        for k in np.unique(trial_length):
            if resp == 1:
                leftStimCorr.append(k)

# this counts how many CORRECT for each length (for each side) and puts into dict, where key=length and value=count
corrRight = collections.Counter(rightStimCorr)
corrLeft = collections.Counter(leftStimCorr)

# this counts how many TOTAL trials per length on each side as dict
totalRight = collections.Counter(rightStimTotal)
totalLeft = collections.Counter(leftStimTotal)

Rpercents = {}
Lpercents = {}
create_percent(corrRight, totalRight, Rpercents)
create_percent(corrLeft, totalLeft, Lpercents)            
           
# plot percent of total correct by side
fig, ax = plt.subplots(facecolor='w')
axes = []
axes.append(plt.subplot(3,1,1))
plt.xticks(targetLengths)   
plt.suptitle(f.split('_')[-3:-1], fontsize=14)  
plt.title('Correct, all trials', fontsize=16)
plt.ylim([0,1])
plt.plot(*zip(*sorted(Rpercents.items())), color='r', marker='.') 
plt.plot(*zip(*sorted(Lpercents.items())), color='b', marker='.')


# EITHER REPSONSE
ansRight = []
ansLeft = []

for i, (trial, resp, trial_length) in enumerate(zip(trialRewardDirection, trialResponse, trialLength)):
    if i in rightStim:   
        if resp != 0:
            ansRight.append(trial_length)
        #elif resp==0:
            #noneLeft.append(trial_length)
    elif i in leftStim:
        if resp != 0:
            ansLeft.append(trial_length)
        #elif resp == 0:
           # noneLeft.append(trial_length)

ansRightDict = collections.Counter(ansRight)
ansLeftDict = collections.Counter(ansLeft)

R2percents = {}
L2percents = {}        

create_percent(corrRight, ansRightDict, R2percents)
create_percent(corrLeft, ansLeftDict, L2percents)  
            
axes.append(plt.subplot(3,1,2))
plt.xticks(targetLengths)
plt.title('Correct, Answered Trials', fontsize=16)
plt.ylabel('percent of trials', fontsize=14)
plt.ylim([0,1])
plt.plot(*zip(*sorted(R2percents.items())), color='r', marker='.') 
plt.plot(*zip(*sorted(L2percents.items())), color='b', marker='.')


#NO RESPONSE
rightNone = []  
leftNone = []      

for i, (trial, resp, trial_length) in enumerate(zip(trialRewardDirection, trialResponse, trialLength)):
    if i in rightStim:   
        if resp == 0:
            rightNone.append(trial_length)
    elif i in leftStim:
        if resp == 0:
            leftNone.append(trial_length)

noneRightDict = collections.Counter(rightNone)
noneLeftDict = collections.Counter(leftNone)

Rnopercents = {}
Lnopercents = {}

create_percent(noneRightDict, totalRight, Rnopercents)
create_percent(noneLeftDict, totalLeft, Lnopercents)
            
# plot percent of total correct by side
axes.append(plt.subplot(3,1,3))
plt.xticks(targetLengths)    
ax.set_xticklabels(targetLengths*8.3)
plt.title('No answer', fontsize=16)
plt.ylim([0,1])

plt.xlabel('Target duration (in frames)', fontsize=13)
plt.plot(*zip(*sorted(Rnopercents.items())), color='r', marker='.') 
plt.plot(*zip(*sorted(Lnopercents.items())), color='b', marker='.')

for a in axes:
    for side in ('top','right'):
        a.spines[side].set_visible(False)
    a.tick_params(direction='out',top=False,right=False)
    a.set_ylim([0,1.01])



   