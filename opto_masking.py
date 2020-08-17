# -*- coding: utf-8 -*-
"""
Created on Fri Aug 14 12:03:51 2020

@author: svc_ccg
"""

import numpy as np
import matplotlib
from matplotlib import pyplot as plt
from behaviorAnalysis import formatFigure
from dataAnalysis import get_dates, ignore_after, create_df



def plot_opto_masking(d):
    matplotlib.rcParams['pdf.fonttype'] = 42
        
# create dataframe of session
    df = create_df(d)
    mouse = df.mouse
    framerate = df.framerate
    date = get_dates(df.date)
    df['respDir'] = d['trialResponseDir'][:len(df)]
    
# separate out the target only, mask only, catch only, and masking trials
# (we are using the averages of these, not left/right)
# remove the ignore trials  
    
# no opto trials 
    
    maskOnly = df[(df['trialType']=='maskOnly') & (df['ignoreTrial']==False)]
    targetOnly = df[(df['trialType']=='targetOnly') & (df['ignoreTrial']==False)]
    masking = df[(df['trialType']=='mask') & (df['ignoreTrial']==False)]
    catch = df[(df['trialType']=='catch') & (df['ignoreTrial']==False)]

    hitsNoOpto = [[] for i in range(4)]  # list for each df above
    respsNoOpto = [[] for i in range(4)]
    totalsNoOpto = [[] for i in range(4)]
    
    for i, frame in enumerate([maskOnly, targetOnly, masking, catch]):
    
        hitsNoOpto[i].append(np.sum((frame['resp']==1)))
        respsNoOpto[i].append(np.sum((np.isfinite(frame['respDir']))))
        totalsNoOpto[i].append(len(frame))
    
    totalTrialsNoOpto = np.array([len(frame) for frame in [maskOnly, targetOnly, masking, catch]])
    
    hitsNoOpto = np.squeeze(np.array(hitsNoOpto))
    respsNoOpto = np.squeeze(np.array(respsNoOpto))
    totalsNoOpto = np.squeeze(np.array(totalsNoOpto))

# opto trials 

    maskOnlyOpto = df[(df['trialType']=='maskOnlyOpto') & (df['ignoreTrial']==False)]
    targetOnlyOpto = df[(df['trialType']=='targetOnlyOpto') & (df['ignoreTrial']==False)]
    maskingOpto = df[(df['trialType']=='maskOpto') & (df['ignoreTrial']==False)]
    catchOpto = df[(df['trialType']=='catchOpto') & (df['ignoreTrial']==False)]

# separate out by onset and count correct by onset
    optoOnset = d['optoOnset'][:]
    
    hits = [[] for i in range(4)]  # list for each df above
    resps = [[] for i in range(4)]
    totals = [[] for i in range(4)]
    
    for i, frame in enumerate([maskOnlyOpto, targetOnlyOpto, maskingOpto, catchOpto]):
        for on in optoOnset:
            
            hits[i].append(np.sum((frame['optoOnset']==on) & (frame['resp']==1)))
            resps[i].append(np.sum((frame['optoOnset']==on) & (np.isfinite(frame['respDir']))))
            totals[i].append(np.sum(frame['optoOnset']==on))
    
    totalTrialsOpto = np.array([len(frame) for frame in [maskOnlyOpto, targetOnlyOpto, maskingOpto, catchOpto]])
    
    hits = np.squeeze(np.array(hits))
    resps = np.squeeze(np.array(resps))
    totals = np.squeeze(np.array(totals))

   
# plot the percent correct against the opto onset on the xaxis
    
    xNoOpto = max(optoOnset)+1
    
    for num, denom, title in zip([resps, hits], 
                                 [totals, resps],
                                 ['Response Rate', 'Fraction Correct Given Response']):
            
            
        fig, ax = plt.subplots()
        for i, (al, c, lbl, pt) in enumerate(zip([.3,.5, .8, 1], ['k', 'c', 'k', 'm'],
               ['Mask only', 'Target only', 'Masked trials', 'Catch'],
               list(respsNoOpto/totalsNoOpto))):   # this needs to be resps over totals for no opto


        #for fraction correct there should only be target and masked plotted 
       # or the plot needs to be different, like the ones sam made 


                ax.plot(optoOnset, num[i]/denom[i], 'o-', color = c, lw=3, alpha=al, label=lbl)
                ax.plot(xNoOpto, pt, 'o', color=c, alpha=al)

                    
#        for x, trials in zip(optoOnset, np.transpose(totals)):  
#            for y, n in zip([1.05,1.1,1.15,1.2], trials):
#                fig.text(x,y,str(trials),transform=ax.transData,color='c', alpha=al, fontsize=10,ha='center',va='bottom')

## format the plots 
            
           
        formatFigure(fig, ax, xLabel='Opto onset (ms)', yLabel=title)
            
        fig.suptitle(('(' + mouse + '    ' + date + ')'), fontsize=13)
        
        xticks = list(optoOnset)
       
        xticklabels = [int(np.round((tick/framerate)*1000)) for tick in optoOnset]
        x,lbl = ([xNoOpto],['no\nopto'])
        xticks = np.concatenate((xticks,x))
        xticklabels = xticklabels+lbl
        
         
        ax.set_xticks(xticks)
        ax.set_xticklabels(xticklabels)
          
        ax.set_xlim([min(optoOnset)-1, max(xticks)+1])
        
        ax.set_ylim([0,1.05])
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        ax.tick_params(direction='out',top=False,right=False)
        plt.subplots_adjust(top=0.815, bottom=0.135, left=0.1, right=0.92, hspace=0.2, wspace=0.2)
        plt.legend(loc='best', fontsize='small', numpoints=1) 
                
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            