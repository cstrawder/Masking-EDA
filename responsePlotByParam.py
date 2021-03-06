# -*- coding: utf-8 -*-
"""
Created on Fri Mar 20 12:45:29 2020

@author: chelsea.strawder
"""


import fileIO, h5py
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from nogoData import nogo_turn
from dataAnalysis import import_data, create_df

matplotlib.rcParams['pdf.fonttype'] = 42

#def plot_by_param(param):    #turn into callable function - IN dataAnalysis?
df = create_df(import_data())
param='targetLength'

nonzeroRxns = df[(df['trialLength']!=df['trialLength'].max()) & (df['ignoreTrial']!=True) & (df['resp']!=0)]
corrNonzero = nonzeroRxns[(nonzeroRxns['resp']==1) & (nonzeroRxns['rewDir']!=0)]
missNonzero = nonzeroRxns[(nonzeroRxns['resp']==-1) & (nonzeroRxns['rewDir']!=0)]

miss = missNonzero.pivot_table(values='trialLength', index='{}'.format(param), columns='rewDir', 
                        margins=True, dropna=True)
hit = corrNonzero.pivot_table(values='trialLength', index='{}'.format(param), columns='rewDir', 
                        margins=True, dropna=True)

hit.plot(title='hits')
miss.plot(title='misses')


hits = [[],[]]  #R, L
misses = [[],[]]

for val in np.unique(df['{}'.format(param)]):
    hitVal = [[],[]]
    missVal = [[],[]]
    for j, (time, p, resp, direc) in enumerate(zip(
            nonzeroRxns['trialLength'], nonzeroRxns['{}'.format(param)], nonzeroRxns['resp'], 
            nonzeroRxns['rewDir'])):
        if p==val:  
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
        
Rmed = list(map(np.median, hits[0]))  #one way
Lmed = [np.median(x) for x in hits[1]]
RmissMed = [np.median(x) for x in misses[0]]
LmissMed = [np.median(x) for x in misses[1]]

Rmean = [np.mean(x) for x in hits[0]]
Lmean = [np.mean(x) for x in hits[1]]
RmissMean = [np.mean(x) for x in misses[0]]
LmissMean = [np.mean(x) for x in misses[1]]

#max = np.max(np.mean(Rmed+Lmed))
fig, ax = plt.subplots()
ax.plot(np.unique(df['{}'.format(param)]), Rmed, 'ro-', label='R hit',  alpha=.6, lw=3)
ax.plot(np.unique(df['{}'.format(param)]), RmissMed, 'ro-', label='R miss', ls='--', alpha=.3, lw=2)
ax.plot(np.unique(df['{}'.format(param)]), Lmed, 'bo-', label='L hit', alpha=.6, lw=3)
ax.plot(np.unique(df['{}'.format(param)]), LmissMed, 'bo-', label='L miss', ls='--', alpha=.3, lw=2)
#ax.plot(0, np.median(maskOnly), marker='o', c='k')
ax.set(title='Median Response Time From StimStart, by {}'.format(param), 
       xlabel='{}'.format(param), ylabel='Reaction Time (ms)')
ax.set_xticks(np.unique(df['{}'.format(param)]))
a = ax.get_xticks().tolist()
#a = [int(i) for i in a]     
if param=='soa':
    a[0] = ''
    a[-1] = 'TargetOnly'
ax.set_xticklabels(a)
matplotlib.rcParams["legend.loc"] = 'best'
ax.legend()

fig, ax = plt.subplots()
ax.plot(np.unique(df['{}'.format(param)]), Rmean, 'ro-', label='R hit',  alpha=.6, lw=3)
ax.plot(np.unique(df['{}'.format(param)]), RmissMean, 'ro-', label='R miss', ls='--', alpha=.3, lw=2)
ax.plot(np.unique(df['{}'.format(param)]), Lmean, 'bo-', label='L hit', alpha=.6, lw=3)
ax.plot(np.unique(df['{}'.format(param)]), LmissMean, 'bo-', label='L miss', ls='--', alpha=.3, lw=2)
#ax.plot(0, np.median(maskOnly), marker='o', c='k')
ax.set(title='Mean Response Time From StimStart, by {}'.format(param), 
       xlabel='{}'.format(param), ylabel='Reaction Time (ms)')
ax.set_xticks(np.unique(df['{}'.format(param)]))
a = ax.get_xticks().tolist()
#a = [int(i) for i in a]     
if param=='soa':
    a[0] = 'MaskOnly'
    a[-1] = 'Target Only'
ax.set_xticklabels(a)
matplotlib.rcParams["legend.loc"] = 'best'
ax.legend()