# -*- coding: utf-8 -*-
"""
Created on Thu May 16 12:06:02 2019

@author: svc_ccg
"""

"""
plot number of rewards as a function of time (days) for all mice

"""

from __future__ import division
import numpy as np
import h5py
import fileIO
from matplotlib import pyplot as plt
import pandas as pd 
from behaviorAnalysis import get_files


mice = ['460312', '460314', '457228']

        
fig, axes = plt.subplots(len(mice),1)




for im, mouse in enumerate(mice):
    numRewards = []
    files = get_files(mouse)
    print(mouse)
    for i,f in enumerate(files):
        d = h5py.File(f)
        trialResponse = d['trialResponse'].value
        trialRewardDir = d['trialRewardDir'][:-1]
        
        numRewards = 0
        
        if 'rewardFrames' in d.keys():
            rewardFrames = d['rewardFrames'].value
        elif 'responseFrames' in d.keys():
            responseTrials = np.where(trialResponse!= 0)[0]
            rewardFrames = d['responseFrames'].value[trialResponse[responseTrials]>0]
#        elif 'trialResponse' in d.keys():
#            responseTrials = np.where(trialResponse!= 0)[0]
#            rewardFrames = d['responseFrames'].value[trialResponse[responseTrials]>0]
        else:
            rewardFrames = d['trialResponseFrame'].value[trialResponse>-1]
            
        for trial, rew in zip(trialResponse, trialRewardDir):
            if trial==0 & rew==0:
                numRewards+=1
            elif rew==1:
                numRewards+=1
            else:
                pass

        d.close()
    
    axes[im].text(0, len(files), mouse)
    axes[im].set_ylim([0,800])
    axes[im].plot(numRewards, 'ko-')
    if im<len(mice)-1:
        axes[im].tick_params(labelbottom='off')
    else:
        axes[im].set_xlabel('Session number')
        axes[im].set_ylabel('Number of Rewards')