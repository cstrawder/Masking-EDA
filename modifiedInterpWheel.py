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

    wheelDF = df[['trialStart','stimStart', 'respFrame', 'deltaWheel']].copy()
    wheelDF['wheelLen'] = list(map(len, wheelDF.loc[:,'deltaWheel']))
    
    wheelDF['diff1'] = wheelDF['stimStart'] - wheelDF['trialStart']  #prestim
    wheelDF['diff2'] = wheelDF['respFrame'] - wheelDF['trialStart']  #entire trial
    
    # unless we do the selecting for nogos and maskOnly HERE - to then look at down there
    
    
    wheel = [wheel[start:stop] for (wheel, start, stop) in zip(
            wheelDF['deltaWheel'], wheelDF['diff1'], wheelDF['wheelLen'])]
    
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
    
    -- could create a new dataframe off the existing one, return that, 
    and then you merge that with the existing (after calling )
    
'''

fi = d['frameIntervals'][:]
framerate = int(np.round(1/np.median(fi)))
maxQuiescentMove = d['maxQuiescentNormMoveDist'][()]
monitorSize = d['monSizePix'][0] 
normRewardDist = d['normRewardDistance'][()]
wheelSpeedGain = d['wheelSpeedGain'][()]

rewThreshold = normRewardDist * monitorSize
threshold = maxQuiescentMove * monitorSize
initiationThreshDeg = 0.5  #how did he decide this?
initiationThreshPix = initiationThreshDeg*np.pi/180*wheelSpeedGain

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
    otherTime = []
    ignoreTrials = []
    
    for i, (wheel, resp, rew, soa) in enumerate(zip(cumulativeWheel, df['resp'], df['rewDir'], df['soa'])):
        if (rew==0 and resp==1) or (resp==0) or (df.iloc[i]['ignoreTrial']==True):   
            
            timeToMoveWheel.append(0)
            interpWheel.append(0)
            otherTime.append(0)
        else:
            fp = wheel
            xp = np.arange(0, len(fp))*1/framerate
            x = np.arange(0, xp[-1], .001)
            interp = np.interp(x,xp,fp)
            interpWheel.append(interp)
            
           
            init = np.argmax(abs(interp)>initiationThreshPix)
            otherTime.append(init)
            if init<100:
                ignoreTrials.append(i)
                
            
 ######################################################################
            
            k = np.argmax(abs(np.round(np.diff(interp)))>0)
            t = np.argmax(abs(interp)>threshold)
            t2 = np.argmax(abs(interp)>(threshold*1.5))
            t3 = np.argmax(abs(interp)>rewThreshold)
            
            noise = abs(interp[k+50] - interp[k])   #check if k is noise 
            
            if noise > 35:  
                a = np.argmax(abs(interp)>5)
                if a<k:
                    timeToMoveWheel.append(a)
                else:
                    timeToMoveWheel.append(k)
            # if this is less than 10, mvmt at k might be noise       
            else:         
                if k>150:  #ms
                    
                    if t-k<100:
                        
                        if t2-t<50:
                            b = np.argmax(abs(np.round(np.diff(interp[t::-1])))<1)
                            a = t-b
                            
                    elif t-k>100:
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
                        if a>k:
                            a=k
                
                elif k<150: # sometimes are moving at beginning and then stop
                    if t<150: 
                        if t2>150:
                            b = np.argmax(abs(np.round(np.diff(interp[t2::-1])))<1) 
                            a = t2-b
                        elif t2<150:
                            b = np.argmax(abs(np.round(np.diff(interp[t3::-1])))<1)
                            a = t3-b
                    elif t>150:
                        if t-k>200:
#                            if t2-t<100:
#                                b = np.argmax(abs(np.round(interp[t::-1]))<10)
#                                a = t-b
#                            elif t2-t>100:
                            b = np.argmax(abs(np.round(np.diff(interp[100:t])))>0)
                            a = b + 100
                        elif t-k<200:
                            b = np.argmax(abs(np.round(np.diff(interp[100:t])))>0)
                            c = np.argmax(abs(np.round(interp))>10)
                            a = b + 100
                            if a==k:
                                a=c
#                            pt = np.argmax(abs(interp)>10)
#                            b = np.argmax(abs(np.round(np.diff(interp[pt::-1])))<1)
#                            a = pt-b
#                            if (t-pt) < (t-k)/2:
#                                val = abs(np.round(np.diff(interp[pt:t])))
#                                count = 0
#                                for ind, (n, m) in enumerate(zip(val[:-1], val[1:])):
#                                    if n == m:
#                                        count += 1
#                                    elif n != m:
#                                        count = 0
#                                    if count>20:
#                                        break
#                                    start = ind + (k-5)
#                                b = np.argmax(abs(np.round(np.diff(interp[start:])))>0)
#                                if b==0:
#                                    a = np.argmax(abs(np.round((interp[t::-1])))==0)
#                                else:
#                                    a = start + b
                timeToMoveWheel.append(a)
            
    return timeToMoveWheel
  
    




for i, trace in enumerate(masterList):
    plt.figure()
    plt.plot(interpWheel[trace[0]])
    plt.vlines(trace[1], -400, 400, ls='--', color='m')
    plt.vlines(times[i], -400, 400, ls='-', color='g')
    plt.title(trace[0])
             
test = np.random.randint(0, len(interpWheel), 60)

test = [i for i, e in enumerate(interpWheel) if type(e)!=int]

for i in range(30):
    plt.figure()
    plt.plot(interpWheel[i], lw=2)
    plt.title(i)
    plt.vlines(initiateMovement[i], -400, 400, ls='--')
    plt.vlines(outcomeTimes[i], -400, 400, ls='--')
    
    plt.vlines(timeToMoveWheel[i], -200, 200, ls='--', color='k')
    plt.vlines(initiationTime[i], -200, 200, ls='-', color='g')
    plt.vlines(otherTime[i], -200, 200, ls='--', color='m')

maskTest = []
for i, time in enumerate(timeToMoveWheel):
    if type(time) is not int:
        maskTest.append(i)
        
for i in maskTest[:50]:
    plt.figure()
    plt.plot(interpWheel[i], lw=2)
    plt.title([i, timeToMoveWheel[i][1]])
    plt.vlines(timeToMoveWheel[i][0], -200, 200, ls='--', color='k', lw=2)
    if timeToMoveWheel[i][1]!=max(np.unique(df['soa'])):
        plt.vlines(timeToMoveWheel[i][1], -100, 100, ls='-', color='m')   
        plt.vlines(timeToMoveWheel[i][1]+200, -100, 100, ls='-', color='m')                 

  
    timeToMove = rxnTimes(df)
    
    respTime = np.round(list(map(lambda x: x * (1000/120), (df['respFrame'] - df['stimStart'])))).astype(int)
        # this needs to be converted to ms, but right now the func is local in dataAnalysis 
        # and the framerate changes -- need to be really careful
    
    timeToOutcome = [resp-move for resp, move in zip(respTime, timeToMove)]  
    
#    for e, (i,j,k) in enumerate(zip(timeToMove, timeToOutcome, df['trialLength'])):
#        assert i + j ==k, 'error at {}'.format(e)
    
    df['timeToMove'] = np.array(timeToMoveWheel)  # already in ms
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






