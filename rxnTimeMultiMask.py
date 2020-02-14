# -*- coding: utf-8 -*-
"""
Created on Thu Feb 13 11:56:13 2020

pulls recent masking session files and creates dataframes for each day
then combines the data frames (usu 3)
analyzes the combined data frames and plots avg performance



@author: svc_ccg
"""

import h5py 
import fileIO
import pandas as pd
import numpy as np
from dffxn import create_df
import matplotlib.pyplot as plt
from behaviorAnalysis import get_files, formatFigure
from collections import defaultdict
import seaborn as sns


mouse='495786'

files = get_files(mouse,'masking_to_analyze')

dn = {}

for i, f in enumerate(files[-3:]):
    d = h5py.File(f)
    dn['df_%01d' % i] = create_df(d)

dictget = lambda x, *k: [x[i] for i in k]
df1, df2, df3 = dictget(dn, 'df_0', 'df_1', 'df_2')
#var1, var2, var3 = (lambda df_0, df_1, df_2: (df_0, df_1, df_2))(**dn)
dfall = df1.append(df2.append(df3))

nonzeroRxns = dfall[(dfall['reactionTime']!=0) & (dfall['ignoreTrial']!=True) & (dfall['resp']!=0)]
corrNonzero = nonzeroRxns[nonzeroRxns['resp']==1]

np.mean(nonzeroRxns['reactionTime'])

plt.figure()
sns.violinplot(x=nonzeroRxns['soa'], y=nonzeroRxns['reactionTime'])
plt.title('Dist of reaction times by SOA:  ' + str(f.split('_')[-3:-1]))

trialMaskOnset = np.round(d['trialMaskOnset'][:] * 1000/120).astype(int)
hits = [[],[]]  #R, L
misses = [[],[]]

for onset in np.unique(trialMaskOnset):
    hitVal = [[],[]]
    missVal = [[],[]]
    for j, (time, soa, resp, mask, direc) in enumerate(zip(
            nonzeroRxns['reactionTime'], nonzeroRxns['soa'], nonzeroRxns['resp'], 
            nonzeroRxns['mask'], nonzeroRxns['rewDir'])):
        if soa==onset:  
            if direc==1:       # soa=0 is targetOnly, R turning
                if resp==1:
                    hitVal[0].append(time)  
                else:
                    missVal[0].append(time)  
            elif direc==-1:   # soa=0 is targetOnly, L turning
                if resp==1:
                    hitVal[1].append(time)  
                else:
                    missVal[1].append(time)
       
    for i in (0,1):         
        hits[i].append(hitVal[i])
        misses[i].append(missVal[i])
        
Rmed = [np.median(x) for x in hits[0]]
Lmed = [np.median(x) for x in hits[1]]
RmissMed = [np.median(x) for x in misses[0]]
LmissMed = [np.median(x) for x in misses[1]]

Rmean = [np.mean(x) for x in hits[0]]
Lmean = [np.mean(x) for x in hits[1]]
RmissMean = [np.mean(x) for x in misses[0]]
LmissMean = [np.mean(x) for x in misses[1]]

#max = np.max(np.mean(Rmed+Lmed))
fig, ax = plt.subplots()
ax.plot(np.unique(trialMaskOnset[:-2]), Rmed, 'ro-', label='Rhit',  alpha=.6, lw=3)
ax.plot(np.unique(trialMaskOnset[:-2]), RmissMed, 'ro-', label='R miss', ls='--', alpha=.3, lw=2)
ax.plot(np.unique(trialMaskOnset[:-2]), Lmed, 'bo-', label='L hit', alpha=.6, lw=3)
ax.plot(np.unique(trialMaskOnset[:-2]), LmissMed, 'bo-', label='L miss', ls='--', alpha=.3, lw=2)
#ax.plot(0, np.median(maskOnly), marker='o', c='k')
ax.set(title='Median Reaction Time From StimStart, by SOA', xlabel='SOA', ylabel='Reaction Time (ms)')
plt.suptitle(str(f.split('_')[-3:-1]))
#ax.set_ylim([np.max()])
ax.set_xticks(np.unique(trialMaskOnset))
a = ax.get_xticks().tolist()
a = [int(i) for i in a]     
a[0] = 'MaskOnly'
ax.set_xticklabels(a)
ax.legend()