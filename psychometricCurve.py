# -*- coding: utf-8 -*-
"""
Created on Fri Jan 10 16:01:03 2020

@author: svc_ccg
"""

'''
for psychometric curve, need:
    multiple contrast conditions (to start)
    dir
    resp
    repeats
    
'''

import fileIO
import h5py
import numpy as np
import matplotlib
from matplotlib import pyplot as plt
from behaviorAnalysis import formatFigure

matplotlib.rcParams['pdf.fonttype'] = 42

f = fileIO.getFile(rootDir=r'\\allen\programs\braintv\workgroups\nc-ophys\corbettb\Masking')
d = h5py.File(f)

trialResponse = d['trialResponse'][:]
trialRewardDirection = d['trialRewardDir'][:len(trialResponse)]              
trialTargetFrames = d['trialTargetFrames'][:len(trialResponse)]       
trialTargetContrast = d['trialTargetContrast'][:len(trialResponse)]
targetContrast= d['targetContrast'][:len(trialResponse)]
trialRepeats = d['trialRepeat'][:len(trialResponse)]

if 'trialRepeat' in d.keys():
    prevTrialIncorrect = d['trialRepeat'][:len(trialResponse)]  #recommended, since keeps track of how many repeats occurred 
else:
    prevTrialIncorrect = np.concatenate(([False],trialResponse[:-1]<1))     # array of boolean values, if trial before was incorr
trialResponse2 = trialResponse[prevTrialIncorrect==False]                   # false = not a repeat, true = repeat
trialRewardDirection = trialRewardDirection[prevTrialIncorrect==False]      # use this to filter out repeated trials 
trialTargetContrast = trialTargetContrast[prevTrialIncorrect==False]
trialTargetFrames = trialTargetFrames[prevTrialIncorrect==False]

for i, rew in enumerate(trialRewardDirection):
    if rew==-1:  # left turning
        trialTargetContrast[i] = trialTargetContrast[i]*-1
'''
all we really need are R turns given right turning, and right turns given left turning trial - 
not hits, misses, etc - just first 3 misses, and last 3 hits
and right turning given it was a nogo
'''     
hits = []
misses = []
noResps = []

directionResponses = [trialResponse2[(trialTargetContrast == tc)] for tc in np.unique(trialTargetContrast)]
hits.append([np.sum(drs==1) for drs in directionResponses])
misses.append([np.sum(drs==-1) for drs in directionResponses])
noResps.append([np.sum(drs==0) for drs in directionResponses])

hits = np.squeeze(np.array(hits))
misses = np.squeeze(np.array(misses))
noResps = np.squeeze(np.array(noResps))
totalTrials = hits+misses+noResps
'''
plot
x-axis is contrast
where -val is incorrect (R stim, L turning) and + val is L stim (R turning)
0 is nogo trial - can see bias 
y-axis is %correct GIVEN right turning

given it was a left turning trial, did they turn left?  if so, 0% rightward
'''
ax, fig = plt.subplots()

