# -*- coding: utf-8 -*-
"""
Created on Fri Aug 14 12:03:51 2020

@author: svc_ccg
"""

import numpy as np
import matplotlib
from matplotlib import pyplot as plt
from behaviorAnalysis import formatFigure
from ignoreTrials import ignore_trials
from dataAnalysis import get_dates, ignore_after, create_df


matplotlib.rcParams['pdf.fonttype'] = 42
    
# create dataframe of session
df = create_df(d)

# separate out the target only, mask only, catch only, and masking trials
# (we are using the averages of these, not left/right)
# remove the ignore trials  
maskOnly = df[(df['trialType']=='maskOnly') & (df['ignoreTrial']==False)]
targetOnly = df[(df['trialType']=='targetOnly') & (df['ignoreTrial']==False)]
masking = df[(df['trialType']=='mask') & (df['ignoreTrial']==False)]
catch = df[(df['trialType']=='maskOnly') & (df['ignoreTrial']==False)]

# separate out by onset and count correct by onset
optoOnset = d['optoOnset'][:]

hits = [[] for i in range(4)]  # list for each df above
noResps = [[] for i in range(4)]


for i, frame in enumerate([maskOnly, targetOnly, masking, catch]):
    for on in optoOnset:
        hit = np.sum(frame['resp']==1))
        noResps[i].append(np.sum())
    



# plot the percent correct against the opto onset on the xaxis

# format the plots 