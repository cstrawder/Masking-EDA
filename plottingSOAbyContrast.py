# -*- coding: utf-8 -*-
"""
Created on Fri Jun 14 12:05:13 2019

@author: svc_ccg
"""

from __future__ import division
import numpy as np
import h5py
from matplotlib import pyplot as plt
from behaviorAnalysis import formatFigure
import fileIO


"""  
analyzing data from the days we tested variable mask contrasts in the masking task - june 12-13


"""

f = fileIO.getFile(rootDir=r'\\allen\programs\braintv\workgroups\nc-ophys\corbettb\Masking')
d = h5py.File(f)

trialRewardDirection = d['trialRewardDir'].value[:-1]
trialResponse = d['trialResponse'].value
maskOnset = d['maskOnset'][:]
#maskLengths[0]=30      #no mask condition 

trialMaskOnset= d['trialMaskOnset'][:-1]
contrast = d['maskContrast'].value
trialContrast = d['trialMaskContrast'].value[:-1]
contrast_num = len(np.unique(contrast))

# lists for each SOA 
hitsR = [[] for i in range(contrast_num)]
missesR = [[] for i in range(contrast_num)]
noRespsR = [[] for i in range(contrast_num)]
 
for i, con in enumerate(np.unique(contrast)):
    maskResponses = [trialResponse[(trialContrast==con) & (trialRewardDirection==-1) & (trialMaskOnset == SOA)] for SOA in np.unique(maskOnset)]
    hitsR[i].append([np.sum(drs==1) for drs in maskResponses])
    missesR[i].append([np.sum(drs==-1) for drs in maskResponses])
    noRespsR[i].append([np.sum(drs==0) for drs in maskResponses])

hitsR = np.squeeze(np.array(hitsR))
missesR = np.squeeze(np.array(missesR))
noRespsR = np.squeeze(np.array(noRespsR))
totalTrialsR = hitsR+missesR+noRespsR


hitsL = [[] for i in range(contrast_num)]
missesL = [[] for i in range(contrast_num)]
noRespsL = [[] for i in range(contrast_num)]


for i, con in enumerate(np.unique(contrast)):     
    maskResponsesL = [trialResponse[(trialContrast==con) & (trialRewardDirection==1) & (trialMaskOnset == SOA)] for SOA in np.unique(maskOnset)]
    hitsL[i].append([np.sum(drs==1) for drs in maskResponsesL])
    missesL[i].append([np.sum(drs==-1) for drs in maskResponsesL])
    noRespsL[i].append([np.sum(drs==0) for drs in maskResponsesL])
        
hitsL = np.squeeze(np.array(hitsL))
missesL = np.squeeze(np.array(missesL))
noRespsL = np.squeeze(np.array(noRespsL))
totalTrialsL = hitsL+missesL+noRespsL

#plot for R side 
fig= plt.figure(facecolor='w', figsize=(10,10), tight_layout=True) #title='-'.join(f.split('_')[-3:-1]))

for i, (num, denom, title) in enumerate(zip([hitsR, hitsR, hitsR+missesR], 
                             [totalTrialsR, hitsR+missesR, totalTrialsR],
                             ['Right Side, Total hit rate', 'Right Side, Response hit rate', 'Right Side, Total response rate'])):
    ax = fig.add_subplot(2,3, i+1)
    for i, ct in enumerate(contrast):   
        ax.plot(np.unique(maskOnset), num[i]/denom[i], marker='o', label=ct)
    ax.set_xticks(np.unique(maskOnset))
    formatFigure(fig, ax, xLabel='Mask SOA', yLabel='percent trials', title=title + " :  " + '-'.join(f.split('_')[-3:-1]))
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.tick_params(direction='out',top=False,right=False)
    ax.set_ylim([0,1.01])  
    ax.set_xlim([-1,max(maskOnset)+5])
    
for i, (num, denom, title) in enumerate(zip([hitsL, hitsL, hitsL+missesL], 
                             [totalTrialsL, hitsL+missesL, totalTrialsL], 
                             ['Left Side, Total hit rate', 'Left Side, Response hit rate', 'Left Side, Total response rate'])):
    ax = fig.add_subplot(2,3, i+4)                            
    for i, ct in enumerate(contrast):    
        ax.plot(np.unique(maskOnset), num[i]/denom[i], marker='o', label=ct)
    ax.set_xticks(np.unique(maskOnset))
    formatFigure(fig, ax, xLabel='Mask Contrast', yLabel='percent trials', title=title)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.tick_params(direction='out',top=False,right=False)
    ax.set_ylim([0,1.01])    
    ax.set_xlim([-1,max(maskOnset)+5])
    L=plt.legend(loc='lower right')
    for i, m in enumerate(contrast):
        L.get_texts()[i].set_text(m)