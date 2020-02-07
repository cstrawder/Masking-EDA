# -*- coding: utf-8 -*-
"""
Created on Mon Jul 08 12:13:37 2019

@author: svc_ccg
"""

from __future__ import division
import numpy as np
import h5py, os
from matplotlib import pyplot as plt
from behaviorAnalysis import formatFigure
import datetime

def get_files_date(mouse_id):
    directory = r'\\allen\programs\braintv\workgroups\nc-ophys\corbettb\Masking'
    dataDir = os.path.join(os.path.join(directory, mouse_id), 'training_to_analyze')   #training_ for no mask, masking_ for mask
    files = os.listdir(dataDir)
    files.sort(key=lambda f: datetime.datetime.strptime(f.split('_')[2],'%Y%m%d'))    
    return [os.path.join(dataDir,f) for f in files if '20190604' in f]


mice = ['439502', '441357', '441358']
fig = plt.figure()

avg_hits = []
avg_total = []

for im, mouse in enumerate(mice):
    
    files = get_files_date(mouse)
    for i,f in enumerate(files):
        d = h5py.File(f)
        trialRewardDirection = d['trialRewardDir'].value[:-1]
        trialResponse = d['trialResponse'].value
        targetLengths = d['targetFrames'].value
        
        trialTargetFrames = d['trialTargetFrames'][:-1]
        trialTargetFrames[np.isnan(trialTargetFrames)] = 0 

        hits = []
        misses = []
        noResps = []
        
        if mouse == '441358':
            direction = 1
        else:
            direction = -1
        directionResponse = [trialResponse[(trialRewardDirection==direction) & (trialTargetFrames == tf)] for tf in np.unique(targetLengths)]
        hits.append([np.sum(drs==1) for drs in directionResponse])
        misses.append([np.sum(drs==-1) for drs in directionResponse])
        noResps.append([np.sum(drs==0) for drs in directionResponse])
        
        hits = np.squeeze(np.array(hits))
        misses = np.squeeze(np.array(misses))
        noResps = np.squeeze(np.array(noResps))
        totalTrials = hits+misses+noResps
        
        avg_hits.append(hits)
        avg_total.append(totalTrials)
        
        for length, num, denom, title in zip([np.unique(targetLengths)], [hits], [totalTrials], ['Averaged success rate']):
            ax = plt.subplot()
            ax.plot(length, num/denom, 'k-o', alpha=.5)
            formatFigure(fig, ax, xLabel='Target Length (ms)', yLabel='percent trials', 
                         title=title + ' 6/04/2019')
            ax.set_xlim([0, targetLengths[-1]+2])
            ax.set_ylim([0,1.01])
            ax.set_xticks(np.unique(targetLengths))
            ax.set_xticklabels(np.round(targetLengths*8.3).astype(int))
            ax.spines['right'].set_visible(False)
            ax.spines['top'].set_visible(False)
            ax.tick_params(direction='out',top=False,right=False)

avg_hits = np.mean(avg_hits, axis=0)
avg_total = np.mean(avg_total, axis=0)

average = avg_hits/avg_total

plt.plot(np.unique(targetLengths), average, 'o-')
plt.errorbar(np.unique(targetLengths), average, yerr=(np.std(average)/np.sqrt(3)), c='k', linewidth=2)



                 