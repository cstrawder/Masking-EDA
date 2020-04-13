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
    
    wheelDF['diff1'] = wheelDF['stimStart'] - wheelDF['trialStart']  #prestim
    wheelDF['diff2'] = wheelDF['respFrame'] - wheelDF['trialStart']  #entire trial
    
    # unless we do the selecting for nogos and maskOnly HERE - to then look at down there
    
    
    wheel = [wheel[start:stop] for (wheel, start, stop) in zip(
            wheelDF['WheelTrace'], wheelDF['diff1'], wheelDF['wheelLen'])]
    
    return wheel

#wheel = wheel_trace_slice(df)

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

###### %%%%%  THIS NEEDS A LOT OF WORK _ HOW DOES IT ACTUALLY WORK WITH DF???  
# should it be part of dataAnalysis
# this should also take over ignoreTrials - possibly return a smaller DF that has:
#timeToMove, timeToOutcome, ignoreTrials 
# that we can then append/merge to the existing df (takes file, needs variables)
# call rxnTimes = rxnTimes(d) -- or (d, df)

def rxnTimes(dataframe):
    
    df = dataframe
    wheel = wheel_trace_slice(df)

    cumulativeWheel = [np.cumsum(mvmt) for mvmt in wheel]

    interpWheel = []
    timeToMoveWheel = []
    avgs=[]
    
    ohno=[]
    tresohno = []
    
    for i, (times, resp, rew) in enumerate(zip(cumulativeWheel, df['resp'], df['rewDir'])):
        if (rew==0 and resp==1) or (resp==0) or (df.iloc[i]['ignoreTrial']==True):   
            timeToMoveWheel.append(0)
            interpWheel.append(0)
        else:
            fp = times
            xp = np.arange(0, len(fp))*1/framerate
            x = np.arange(0, xp[-1], .001)
            interp = np.interp(x,xp,fp)
            interpWheel.append(interp)
            
            k = np.argmax(abs(np.round(np.diff(interp)))>0)
            t = np.argmax(abs(interp)>threshold)
            t2 = np.argmax(abs(interp)>(threshold*1.5))
            t3 = np.argmax(abs(interp)>rewThreshold)
            
            noise = abs(interp[k+50] - interp[k])   #check if k is noise 
            
            if noise > 35:             # if it's more than 10, it's def movement 
                timeToMoveWheel.append(k)
            else:         # if this is less than 10, mvmt at k might be noise
                if k>150:  #ms
                    if t2-k<150:
                        if t2-t<50:
                            a = k
                        else:
                            b = np.argmax(abs(np.round(np.diff(interp[t::-1])))<1)
                            a = t-b
                    elif t2-k>150:
                        val = abs(np.round(np.diff(interp[k:t])))
                        count = 0
                        for ind, (n, m) in enumerate(zip(val[:-1], val[1:])):
                            if n == m:
                                count += 1
                            elif n != m:
                                count = 0
                            if count>10:
                                break
                            start = ind + k
                        b = np.argmax(abs(np.round(np.diff(interp[start:])))>0)
                        a = start + b
                
                elif k<150: # sometimes are moving at beginning and then stop
                    if t<150: 
                        if t2>150:
                            b = np.argmax(abs(np.round(np.diff(interp[t2::-1])))<1) 
                            a = t2-b
                        elif t2<150:
                            b = np.argmax(abs(np.round(np.diff(interp[t3::-1])))<1)
                            a = t3-b
                    elif t>150:
                        if t-k>300:
                            b = np.argmax(abs(np.round(np.diff(interp[t::-1])))<1)
                            a = t-b
                        else:    
                            val = abs(np.round(np.diff(interp[k:t])))
                            count = 0
                            for ind, (n, m) in enumerate(zip(val[:-1], val[1:])):
                                if n == m:
                                    count += 1
                                elif n != m:
                                    count = 0
                                if count>20:
                                    break
                                start = ind + k
                            b = np.argmax(abs(np.round(np.diff(interp[start:])))>0)
                            if b==0:
                                a = np.argmax(abs(np.round((interp[t::-1])))==0)
                            else:
                                a = start + b
                timeToMoveWheel.append(a)
            
    return timeToMoveWheel
     
             
test = np.random.randint(0, len(interpWheel), 60)

test = [i for i, e in enumerate(interpWheel) if type(e)!=int]

for i in test[:]:
    plt.figure()
    plt.plot(interpWheel[i])
    plt.title(i)
    plt.vlines(timeToMoveWheel[i], -100, 100, ls='--')                    

  
    timeToMove = rxnTimes(df)
    
    respTime = np.round(list(map(lambda x: x * (1000/120), (df['respFrame'] - df['stimStart'])))).astype(int)
        # this needs to be converted to ms, but right now the func is local in dataAnalysis 
        # and the framerate changes -- need to be really careful
    
    timeToOutcome = [resp-move for resp, move in zip(respTime, timeToMove)]  
    
    for e, (i,j,k) in enumerate(zip(timeToMove, timeToOutcome, df['trialLength'])):
        assert i + j ==k, 'error at {}'.format(e)
    
    df['timeToMove'] = np.array(timeToMove)  # already in ms
    df['timeToOutcome'] = np.array(timeToOutcome)

    return df 

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






