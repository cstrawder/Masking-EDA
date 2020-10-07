# -*- coding: utf-8 -*-
"""
Created on Wed Oct  7 14:35:50 2020

@author: svc_ccg
"""

from dataAnalysis import import_data, get_dates, ignore_after
from behaviorAnalysis import formatFigure
import numpy as np
import matplotlib.pyplot as plt
import matplotlib


def plot_opto_uin(data, ignoreAfter):

    matplotlib.rcParams['pdf.fonttype'] = 42

    
    d = data
    end = ignore_after(d, ignoreAfter)[0]
    

    trialType = d['trialType'][:end]
    targetContrast = d['trialTargetContrast'][:end]
    optoChan = d['trialOptoChan'][:end]
    optoOnset = d['trialOptoOnset'][:end]
    rewardDir = d['trialRewardDir'][:end]
    response = d['trialResponse'][:end]
    responseDir = d['trialResponseDir'][:end]
    
    d.close()
    
    goLeft = rewardDir==-1
    goRight = rewardDir==1
    catch = np.isnan(rewardDir)
    noOpto = np.isnan(optoOnset)
    optoLeft = optoChan[:,0] & ~optoChan[:,1]
    optoRight = ~optoChan[:,0] & optoChan[:,1]
    optoBoth = optoChan[:,0] & optoChan[:,1]
    
    fig = plt.figure(figsize=(10,6))
    gs = matplotlib.gridspec.GridSpec(2,2)
    x = np.arange(4)
    for j,contrast in enumerate([c for c in np.unique(targetContrast) if c>0]):
        for i,ylbl in enumerate(('Response Rate','Fraction Correct')):
            ax = fig.add_subplot(gs[i,j])
            for trials,trialLabel,clr,ty in zip((catch,goLeft,goRight),('catch','stim right (go left)','stim left (go right)'),'kbr',(1.05,1.1,1.15)):
                n = []
                y = []
                for opto in (noOpto,optoLeft,optoRight,optoBoth):
                    ind = trials & opto
                    if trialLabel != 'catch':
                        ind = trials & opto & (targetContrast==contrast)
                    r = ~np.isnan(responseDir[ind])
                    if ylbl=='Response Rate':
                        n.append(np.sum(ind))
                        y.append(r.sum()/n[-1])
                    else:
                        n.append(r.sum())
                        if trialLabel=='catch':
                            y.append(np.nan)
                        else:
                            y.append(np.sum(r & (response[ind]==1))/n[-1])
                ax.plot(x,y,clr,marker='o',mec=clr,mfc='none',label=trialLabel)
                for tx,tn in zip(x,n):
                    fig.text(tx,ty,str(tn),color=clr,transform=ax.transData,va='bottom',ha='center',fontsize=8)
            for side in ('right','top'):
                ax.spines[side].set_visible(False)
            ax.tick_params(direction='out',top=False,right=False)
            ax.set_xticks(x)
            xticklabels = ('no\nopto','opto\nleft','opto\nright','opto\nboth') if i==1 else []
            ax.set_xticklabels(xticklabels)
            ax.set_xlim([-0.5,3.5])
            ax.set_ylim([0,1.05])
            if j==0:
                ax.set_ylabel(ylbl)
            if i==1 and j==0:
                ax.legend(fontsize='small', loc='best')
        tx = 0.3 if j==0 else 0.7
        fig.text(tx,0.99,'contrast '+str(contrast),va='top',ha='center')
    
    
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)
    for side,lbl,clr in zip((np.nan,-1,1),('no response','move left','move right'),'kbr'):
        n = []
        y = []
        for opto in (noOpto,optoLeft,optoRight,optoBoth):
            ind = catch & opto
            n.append(ind.sum())
            if np.isnan(side):
                y.append(np.sum(np.isnan(responseDir[ind]))/n[-1])
            else:
                y.append(np.sum(responseDir[ind]==side)/n[-1])
        ax.plot(x,y,clr,marker='o',mec=clr,mfc='none',label=lbl)
    for tx,tn in zip(x,n):
        fig.text(tx,1.05,str(tn),color='k',transform=ax.transData,va='bottom',ha='center',fontsize=8)
    for side in ('right','top'):
        ax.spines[side].set_visible(False)
    ax.tick_params(direction='out',top=False,right=False)
    ax.set_xticks(x)
    ax.set_xticklabels(('no\nopto','opto\nleft','opto\nright','opto\nboth'))
    ax.set_xlim([-0.5,3.5])
    ax.set_ylim([0,1.05])
    ax.set_ylabel('Fraction of catch trials')
    ax.legend()
    fig.text(0.525,0.99,'Catch trial movements',va='top',ha='center')
    
    
    fig = plt.figure()
    gs = matplotlib.gridspec.GridSpec(8,1)
    x = np.arange(4)
    for j,contrast in enumerate([c for c in np.unique(targetContrast) if c>0]):
        for i,(trials,trialLabel) in enumerate(zip((goLeft,goRight,catch),('Right Stimulus','Left Stimulus','No Stimulus'))):
            if i<2 or j==0:
                ax = fig.add_subplot(gs[i*3:i*3+2,j])
                for resp,respLabel,clr,ty in zip((-1,1),('move left','move right'),'br',(1.05,1.1)):
                    n = []
                    y = []
                    for opto in (noOpto,optoLeft,optoRight,optoBoth):
                        ind = trials & opto
                        if trialLabel != 'No Stimulus':
                            ind = trials & opto & (targetContrast==contrast)
                        n.append(ind.sum())
                        y.append(np.sum(responseDir[ind]==resp)/n[-1])
                    ax.plot(x,y,clr,marker='o',mec=clr,mfc='none',label=respLabel)
                for tx,tn in zip(x,n):
                    fig.text(tx,ty,str(tn),color='k',transform=ax.transData,va='bottom',ha='center',fontsize=8)
                title = trialLabel if trialLabel=='No Stimulus' else trialLabel+', Contrast '+str(contrast)
                fig.text(1.5,1.25,title,transform=ax.transData,va='bottom',ha='center',fontsize=10)
                for side in ('right','top'):
                    ax.spines[side].set_visible(False)
                ax.tick_params(direction='out',top=False,right=False)
                ax.set_xticks(x)
                xticklabels = ('no\nopto','opto\nleft','opto\nright','opto\nboth')# if i==2 else []
                ax.set_xticklabels(xticklabels)
                ax.set_xlim([-0.5,3.5])
                ax.set_ylim([0,1.05])
                if j==0:
                    ax.set_ylabel('Fraction of trials')
                if i==0 and j==0:
                    ax.legend(fontsize='small', loc=(0.71,0.71))
                    
                    
    
    
    
    
