# -*- coding: utf-8 -*-
"""
Created on Tue Apr  7 14:23:34 2020

@author: chelsea.strawder

Want to find:
    time to move == from stim start to turning wheel
    time to outcome == from wheel turn to response
    velocity == wheel turning speed from timetooutcome 
    (i.e. the time they are acutally turning the wheel)

**************
Modified interpWheel

Imports dataframe
Creates new df with cols= wheel trace, trial start, stim start, resp Frame 
Slices wheelTrace in dataframe to match the length of the trial, from the stim start to the response
Returns an array of the newly sliced wheel t race

Then, using this filtered wheel trace, creates the interpolated wheel trace
and iterates through each interp wheel to find the ms where the mouse moved the wheel
using the diff between wheel movements > 1 (if no mvmt, diff==0).  
Sometimes the mouse is starting to move and then stops - impulsive turning.  
This gives us an incorrect time for when they started moving the wheel to make a choice 

To avoid this error, we can either go in reverse, from the response frame back to when the diff==0 
(though that has it's own issue of the mice stopping turning partway)

OR start with diff==1 then move to diff==2 - this indicates a bigger movement 
(but this could miss a slower turn toward choice)

could filter by tracking movement from start of closed loop - and if they are
already moving at start, THEN look at trace between stim start and response


Another thing to look at - using the trial reward direction (?), determine how many 
times they changed turning direction

******
In the end, returns the array with timeToOutcome, timeToMove, and Velocity
- or returns these as new columns appended to original df?? - to keep everything together 
ex: rxnDf = func(df), where rxnDf is the new df to analyze (or use model with) and plot from

"""

from dataAnalysis import import_data, create_df  # for now - won't need once function is complete
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import scipy.signal
import scipy.stats
import seaborn as sns 

matplotlib.rcParams['pdf.fonttype'] = 42

d = import_data()       # want to use d later to pull vals for analysis
df = create_df(d)

def wheel_trace_slice(dataframe):
    df = dataframe

    wheelDF = df[['trialStart','stimStart', 'respFrame', 'WheelTrace']]
    wheelDF['wheelLen'] = list(map(len, wheelDF['WheelTrace']))
    
    wheelDF['diff1'] = wheelDF['stimStart'] - wheelDF['trialStart']
    wheelDF['diff2'] = wheelDF['respFrame'] - wheelDF['trialStart']
    
    # unless we do the selecting for nogos and maskOnly HERE - to then look at down there
    
    
    wheel = [wheel[start:stop] for (wheel, start, stop) in zip(
            wheelDF['WheelTrace'], wheelDF['diff1'], wheelDF['diff2'])]
    
    return wheel

wheel = wheel_trace_slice(df)

'''
HOW is this actually going to work if the func takes the df as the arg?  
unless it creates the df in itself, using d as arg
like:
    d = import_data()
    rxntime = rxnTimes(d)
    
    but THEN it's obnox bc how does it do anything with rxnTime info?
    have to create the df again to add to it
    unless it's rxnTimes(d, df) - but that seems excessive
    
'''

fi = d['frameIntervals'][:]
framerate = int(np.round(1/np.median(fi)))
maxQuiescentMove = d['maxQuiescentNormMoveDist'][()]
monitorSize = d['monSizePix'][0] 
normRewardDist = d['normRewardDistance'][()]

rewThreshold = normRewardDist * monitorSize
threshold = maxQuiescentMove * monitorSize

def rxnTimes(df, wheel):
    
   # call wheel slicing func 
   # wheel = wheel_trace_slice(df)

    interpWheel = []
    timeToMoveWheel = []
    
    for i, (times, resp, nogo) in enumerate(zip(wheel, df['resp'], df['nogo'])):
        if nogo==True or resp==0:   
            timeToMoveWheel.append(0)
            interpWheel.append(0)    
        else:
            fp = times
            xp = np.arange(0, len(fp))*1/framerate
            x = np.arange(0, xp[-1], .001)
            interp = np.interp(x,xp,fp)
            interpWheel.append(interp)
            t = np.argmax(abs(interp)>threshold)
            if t <= 100:
                timeToMoveWheel.append(t)
            elif t==0:
                timeToMoveWheel.append(0)   # no resp, or moving at start of trial
            else:
                t = np.argmax(abs(interp[100::])>threshold) + 100  #100 ms is limit of ignore trial
                a = np.argmax(abs(np.round(np.diff(interp[100::])))>0) + 100
                if 0 < a < 200:
                    timeToMoveWheel.append(0)
                elif abs(t-a) < (150):
                    timeToMoveWheel.append(a)
                else:
                    b = np.argmax(abs(np.round(np.diff(interp[a::])))>0) + a
                    if abs(t-b) < (200):
                        timeToMoveWheel.append(b)
                    else:
                        c = np.argmax(abs(np.round(np.diff(interp[b::])))>1) + b
                        if c!=b:
                            timeToMoveWheel.append(c)
                        else:
                            timeToMoveWheel.append(b)
        
    return timeToMoveWheel
  
    

interpWheel = rxnTimes(df)
    



#timeToOutcome = []    # time to outcome is time from rxnTime (1st wheel mvmt) to respFrame
#for i,j in zip(cumWheel, timeToMoveWheel):    
#    i = np.round(len(i)*1000/framerate)
#    timeToOutcome.append(i-j)    # ends up just being the diff btwn trialLength and rxnTime
#
#velo = []           
#for i, time in enumerate(interpWheel):   #time is array of wheel mvmt
#    if type(time) is int:
#        velo.append(0)          # no wheel mvmt is 0, an int
#    else:
#        q = int(timeToMoveWheel[i])   # rxn time of the trial, in ms, used as index of interpWheel
#        v = abs(time[-1] - time[q]) / timeToOutcome[i]   # dist (in pix??) moved over time/time
#        velo.append(v)
#        # in pix/ms?
#






