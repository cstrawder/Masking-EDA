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


trialRewardDirection = d['trialRewardDir'][:-1]
trialResponse = d['trialResponse'][()]

optoOnset = d['optoOnset'][:]
trialoptoOnset = d['trialOptoOnset'][:len(trialRewardDirection)]
trialContrast = c['trialTargetContrast'][:len(trialRewardDirection)]
contrast = np.unique(trialContrast)    #(pilfered from 521266 yesterday)


contrast_num = len(np.unique(contrast))

# lists for each SOA 
hitsR = [[] for i in range(contrast_num)]
missesR = [[] for i in range(contrast_num)]
noRespsR = [[] for i in range(contrast_num)]
 
for i, con in enumerate(np.unique(contrast)):
    maskResponses = [trialResponse[(trialContrast==con) & (trialRewardDirection==-1) & 
                                   (trialoptoOnset == op)] for op in np.unique(optoOnset)]
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
    maskResponsesL = [trialResponse[(trialContrast==con) & (trialRewardDirection==1) & 
                                    (trialoptoOnset == op)] for op in np.unique(optoOnset)]
    hitsL[i].append([np.sum(drs==1) for drs in maskResponsesL])
    missesL[i].append([np.sum(drs==-1) for drs in maskResponsesL])
    noRespsL[i].append([np.sum(drs==0) for drs in maskResponsesL])
        
hitsL = np.squeeze(np.array(hitsL))
missesL = np.squeeze(np.array(missesL))
noRespsL = np.squeeze(np.array(noRespsL))
totalTrialsL = hitsL+missesL+noRespsL

for i, con in enumerate(contrast):
    for Rnum, Lnum, Rdenom, Ldenom, title in zip([hitsR, hitsR, hitsR+missesR], 
                                                 [hitsL, hitsL, hitsL+missesL],
                                                 [totalTrialsR, hitsR+missesR, totalTrialsR],
                                                 [totalTrialsL, hitsR+missesL, totalTrialsL],
                                                 ['Fraction Correct', 'Fraction Correct Given Response', 'Response Rate']):
                fig, ax = plt.subplots()
                ax.plot(optoOnset, Rnum[i]/Rdenom[i], 'bo-', lw=3, alpha=.7, label='Right turning')  #here [0] is right trials and [1] is left
                ax.plot(optoOnset, Lnum[i]/Ldenom[i], 'ro-', lw=3, alpha=.7, label='Left turning')
                ax.plot(optoOnset, (Rnum[i]+Lnum[i])/(Rdenom[i]+Ldenom[i]), 'ko--', alpha=.5, label='Combined average')  #plots the combined average 
               
                xticks = optoOnset
                xticklabels = list(optoOnset)
    
                showTrialN=True           
                if showTrialN==True:
                    for x,Rtrials,Ltrials in zip(sessionParams,denom[0], denom[1]):
                        for y,n,clr in zip((1.05,1.1),[Rtrials, Ltrials],'rb'):
                            fig.text(x,y,str(n),transform=ax.transData,color=clr,fontsize=10,ha='center',va='bottom')
            
                xlab = 'Opto onset from target onset'
                formatFigure(fig, ax, xLabel=xlab, yLabel=title)
                fig.suptitle(('(' + mouse + '    ' + date + ')    Target Contrast = ' + str(con)), fontsize=13)
                ax.set_xticks(xticks)
                ax.set_xticklabels(xticklabels)

                    
                ax.set_ylim([0,1.05])
                ax.spines['right'].set_visible(False)
                ax.spines['top'].set_visible(False)
                ax.tick_params(direction='out',top=False,right=False)
                plt.subplots_adjust(top=0.86, bottom=0.105, left=0.095, right=0.92, hspace=0.2, wspace=0.2)
                plt.legend(loc='best', fontsize='small', numpoints=1) 
                
                
            
            