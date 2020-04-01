# -*- coding: utf-8 -*-
"""
Created on Fri Mar 27 11:31:25 2020

@author: chelsea.strawder
"""
import numpy as np
import pandas as pd
import matplotlib 
import matplotlib.pyplot as plt
from dataAnalysis import import_data, create_df, extract_vars


d = import_data()
df = create_df(d)
dn = extract_vars(d)

for key,val in dn.items():   
    exec (key + '=val')



### issue now is that the df is importing the wheel trace for the entire trial
### and techncially we want from the start of the stim to when they start moving 
### at least here;  in another place it might be nice to look at movement after a resp 
### like a nogo, or movement (velocity, direction) BEFORE a stim starts 
### so this should be a felxible function that can accomodate all these conditions 
### rather than writing the whole loop over and over 
### maybe you need to slice the wheelTrace BEFORE using in the func
    
def wheel_trace_slice(dataframe):
    df = dataframe
    # process wheel trace using stim start and resp frames
    # assign to variable 'wheel'
    wheelDF = df[['trialStart','stimStart', 'respFrame', 'WheelTrace']]
  # want to create a col that has the len of each WheelTrace
    wheelDF['wheelLen'] = list(map(len, wheelDF['WheelTrace']))
    assert np.all(wheelDF['wheelLen'] == (wheelDF['respFrame'] - wheelDF['trialStart'])), 'Wheel error'
    wheelDF['diff1'] = wheelDF['stimStart'] - wheelDF['trialStart']
    wheelDF['diff2'] = wheelDF['respFrame'] - wheelDF['trialStart']
    wheel = [wheel[start:stop] for (wheel, start, stop) in zip(
            wheelDF['WheelTrace'], wheelDF['diff1'], wheelDF['diff2'])]
    
    return wheel
    
 # use wheel_trace_slice as arg in interpWheel() 

interpWheel = []
timeToMoveWheel = [] 

maxDir = []
same = []

firstDiffList = []
qMoveList = []      
twiceQList = []
halfwayList = []
rewMoveList = []
maxDistList = [] 

def interpWheel(dataframe, wheel):   #where wheel is already processed from the same df
    df = dataframe
    interpWheel = []
    for i, (times, resp, direction) in enumerate(zip
           (wheel, df['resp'], df['rewDir'])):
        fp = times    
        xp = np.arange(0, len(fp))*1/(np.round(frameRate))
        x = np.arange(0, xp[-1], .001)    #wheel mvmt each ms 
        interp = np.interp(x,xp,fp)
        interpWheel.append(interp)
    return interpWheel
        
        
        qThreshold = maxQuiescentNormMoveDist * monSizePix[0]   
        rewThreshold = normRewardDistance * monSizePix[0]

        
    firstDiff = np.argmax(abs(np.round(np.diff(interp)))>0)
    qMove = np.argmax(abs(interp)>qThreshold)        # first time they move past quiescent thresh
    twiceQ = np.argmax(abs(interp)>(qThreshold*2))
    halfway = np.argmax(abs(interp)>(rewThreshold/2))
    rewMove = np.argmax(abs(interp)>rewThreshold)    # first move past reward dist (i.e make a choice)
    maxDist = np.argmax(abs(interp))                 # farthest they move wheel either direction
    
    idx2 = np.where(np.sign(np.diff(interp[:-1])) != np.sign(np.diff(interp[1:])))[0] + 1
    notable = [i for (i,e) in zip(idx2, np.diff(idx2)) if e>25]
    reward = np.argmax(np.cumsum(interp)>250)
    
    firstDiffList.append(firstDiff)
    qMoveList.append(qMove)      
    twiceQList.append(twiceQ)
    halfwayList.append(halfway)
    rewMoveList.append(rewMove)
    maxDistList.append(maxDist)
    
   # print((firstDiff, qMove, twiceQ, halfway, rewMove, maxDist, len(interp)))
    

    
    if interp[maxDist]/abs(interp[maxDist]) == direction:
        same.append(True)
    else:
        same.append(False)
    maxDir.append(interp[maxDist])
        
    if i in nogos and resp==1:
        timeToMoveWheel.append(0)    # correct nogo; no mvmt
    else:
        if 0<rewMove<150:               #if they move the wheel past the reward threshold before 150ms (pre-gotone)
            ignoreTrials.append(i)     # ignore this trial's wheel movement (more analysis can be done on ignoreTrials)
            timeToMoveWheel.append(0)
            print('first ignore ' + str(i))
        else:
            
            if 0 < qMove <= 50:           # if they move past qthreshold before 50ms, ignore this trial
                ignoreTrials.append(i)
                print('second ignore ' + str(i))
                timeToMoveWheel.append(0)   # no resp, or moving before 50 ms
            else:
                t = np.argmax(abs(interp[50::])>qThreshold) + 50  #100 ms is limit of ignore trial
                a = np.argmax(abs(np.round(np.diff(interp[50::])))>0) + 50
                if 0 < a < 50:
                    ignoreTrials.append(i)    
                    print('third ignore ' + str(i))
                    print(a)
                    timeToMoveWheel.append(0)
                else:
                    timeToMoveWheel.append(a)
               
                
#                else:
#                    ### since a usu ends up being when some mvmt was made, b ends up being 0
#                    # this seems like a good point to go from the end and narrow in
#                    
#                    b = rew - np.argmax(abs(np.round(np.diff(interp[rew::-1])))<=0) 
                    
#                    if abs(t-b) < (200):
#                        timeToMoveWheel.append(b)
#                    else:
#                        c = np.argmax(abs(np.round(np.diff(interp[b::])))>1) + b
#                        if c!=b:
#                            timeToMoveWheel.append(c)
#                        else:
#                            timeToMoveWheel.append(b)

 
mvmtdf = pd.DataFrame(data=list(zip(firstDiffList, qMoveList, twiceQList, halfwayList, rewMoveList, maxDistList)), 
                      columns=('first', 'quiescent', 'twiceQ', 'halfRew', 'rew', 'max'))

# add column to df with TimeToMove values (ms)
# for trialLength in df.trialLength, subtract TimeToMove from trialLength, 
# use in ang velocity calculation (look at resptimeExp) w pixels/radians wheel moved


