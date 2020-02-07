# -*- coding: utf-8 -*-
"""
Created on Thu Aug 22 12:56:20 2019

@author: chelsea.strawder

Creats dataframe of response times per trial, by side, and plots distributions - 

(how quickly they turn after stim onset and/or goTone)


*add a plot of rxn times from the start of mask (not stimStart) to see if there is
dependence on mask presence

"""

import fileIO, h5py
import math
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import scipy.signal
import scipy.stats
import seaborn as sns 

from nogoData import nogo_turn

matplotlib.rcParams['pdf.fonttype'] = 42

f = fileIO.getFile(rootDir=r'\\allen\programs\braintv\workgroups\nc-ophys\corbettb\Masking')
d = h5py.File(f)

fi = d['frameIntervals'][:]
framerate = int(np.round(1/np.median(fi)))

trialResponse = d['trialResponse'][()]
end = len(trialResponse)
trialRewardDirection = d['trialRewardDir'][:end]
trialTargetFrames = d['trialTargetFrames'][:end]
trialStimStartFrame = d['trialStimStartFrame'][:]
trialResponseFrame = d['trialResponseFrame'][:end]    #if they don't respond, then nothing is recorded here - this limits df to length of this variable
trialOpenLoopFrames = d['trialOpenLoopFrames'][:end]
openLoopFrames = d['openLoopFramesFixed'][()]
quiescentMoveFrames = d['quiescentMoveFrames'][:]
maxQuiescentMove = d['maxQuiescentNormMoveDist'][()]
trialEndFrame = d['trialEndFrame'][:end]
deltaWheel = d['deltaWheelPos'][:]                      # has wheel movement for every frame of session
trialMaskContrast = d['trialMaskContrast'][:end]

maskOnset = np.round(d['maskOnset'][()] * 1000/framerate).astype(int)
trialMaskOnset = np.round(d['trialMaskOnset'][:end] * 1000/framerate).astype(int)
maskLength = np.round(d['maskFrames'][()] * 1000/framerate).astype(int)
targetLength = np.round(d['targetFrames'][()] * 1000/framerate).astype(int)
maxResp = np.round(d['maxResponseWaitFrames'][()] * 1000/framerate).astype(int) 


for i, target in enumerate(trialTargetFrames):  # this is needed for older files nogos are randomly assigned a dir
    if target==0:
        trialRewardDirection[i] = 0

nogos = []   #not including maskOnly trials
for i, (rew, con) in enumerate(zip(trialRewardDirection, trialMaskContrast)):
    if rew==0 and con==0:
        nogos.append(i) 

nogoTurn, maskOnlyTurn, ndx = nogo_turn(d)
 
noMaskVal = maskOnset[-1] + round(np.mean(np.diff(maskOnset)))  # assigns noMask condition an evenly-spaced value from soas
maskOnset = np.append(maskOnset, noMaskVal)              # makes final value the no-mask condition
    
for i, (mask, trial) in enumerate(zip(trialMaskOnset, trialTargetFrames)):   # filters target-Only trials 
    if trial>0 and mask==0:
        trialMaskOnset[i]=noMaskVal       

# deltaWheel from start of stim to response (or no response) for each trial
# deltaWheel from start of closedLoop to response for nogos
# nogos are sliced from trialStart to resp, and also go-tone to end.  Predictive turning.  ask sam.
trialWheel = []  
nogoWheelFromCL = [] 
for i, (start, resp, mask) in enumerate(zip(trialStimStartFrame, trialResponseFrame, trialMaskContrast)):
    if trialRewardDirection[i]==0:
        if mask==0:  # nogo trials
            wheel = (deltaWheel[start+openLoopFrames:resp+5])   #from start of closedLoop
            nogoWheelFromCL.append(wheel)
            wheel2 = (deltaWheel[start:resp])
            trialWheel.append(wheel2)
        elif mask>0:   # maskOnly
            wheel = (deltaWheel[start:resp+1])
            trialWheel.append(wheel)
    else:
        wheel = (deltaWheel[start:resp])
        trialWheel.append(wheel)


#since deltawheel provides the difference in wheel mvmt from trial to trial
#taking the cumulative sum gives the actual wheel mvmt and plots as a smooth curve
cumWheel = []   
for mvmt in trialWheel:
    time = np.cumsum(mvmt)
    cumWheel.append(time)  # not using scipy.median.filter bc flattens final frames
    
#do not include nogo trials (==0); their wheel traces prior to gotone mess up rxn times)
# time from stimStart to moving the wheel
interpWheel = []
rxnTimes = []
ignoreTrials = []
for i, times in enumerate(cumWheel):
    if i in nogos:   # excluding nogos from rxnTime analysis
        rxnTimes.append(0)
        interpWheel.append(0)
        pass
    else:
        fp = times
        xp = np.arange(0, len(fp))*1/framerate
        x = np.arange(0, xp[-1], .001)
        interp = np.interp(x,xp,fp)
        interpWheel.append(interp)
        threshold = maxQuiescentMove*d['monSizePix'][0] 
        t = np.argmax(abs(interp[100::])>threshold) + 100  # starting at the guessing threshold
        if t==0:
            rxnTimes.append(0)   # no resp
        else:
            a = np.argmax(abs(interp[0:t])>5)
            if abs(t-a) < (10*1000/framerate):
                rxnTimes.append(a)
            else:
                b = np.argmax(abs(np.round(np.diff(interp[100::])))>0)
                rxnTimes.append(b+100)
    if 0 < a < 100:
        ignoreTrials.append(i)    # ask sam about ignoring trials, including nogos 
        rxnTimes.append(0)
               
# np.argmax(abs(cumWheel[i])>5)   old way 

# velocities  - inst=delta(x)/delta(t) - avg (slope of linear regression) 
#abs(cumWheel(end) - cumWheel(start)) / len(timeToOutcome)

timeToOutcome = []    # time to outcome is time from rxnTime (1st wheel mvmt) to respFrame
for i,j in zip(cumWheel, rxnTimes):    
    i = np.round(len(i)*1000/framerate)
    timeToOutcome.append(i-j)    # ends up just being the diff btwn trialLength and rxnTime


nogoCumWheelFromCL = []         # this is cum wheel mvmt from goTone to wheelMvmt (past threshold) 
for time in nogoWheelFromCL:    # for nogo trials
    time = np.cumsum(time)
    nogoCumWheelFromCL.append(time)

nogoRxnTimes = []               # num of frames from goTone to mvmt or reward
for times in nogoCumWheelFromCL:
    nogoRxnTimes.append(len(times)-4)
       
nogoTurn = nogo_turn(d)   # returns 3 arrays; [0] is nogoTurn dir, [1] is maskOnly, and 2
                            # is 2 lists of indices of those nogoMove trials
                            
nogoMove = np.zeros(len(trialResponse)).astype(int)
for i in range(len(trialResponse)):
    for (ind, turn) in zip(nogoTurn[2][0], nogoTurn[0]):
        if i==ind:
            nogoMove[i] = turn

data = list(zip(trialRewardDirection, trialResponse, trialStimStartFrame, trialResponseFrame))
index = range(len(trialResponse))

df = pd.DataFrame(data, index=index, columns=['rewDir', 'resp', 'stimStart', 'respFrame'])
df['trialLength'] = [np.round(len(t)*1000/framerate) for t in trialWheel]
df['reactionTime'] = rxnTimes
df['timeToOutcome'] = timeToOutcome
if len(maskOnset)>0:
    df['mask'] = trialMaskContrast
    df['soa'] = trialMaskOnset
df['nogoMove'] = nogoMove  # turning direction of nogo trial

for (ind, time) in zip(nogoTurn[2][0], nogoRxnTimes):
    df.loc[ind,'reactionTime'] = time


for i in ignoreTrials:
    df.loc[i,'ignoreTrial'] = True




## Time to move wheel from start of wheel mvmt - will be (-) in some trials 
    # only for trials with target

rxn = [i for e, i in enumerate(rxnTimes) if (0 < i < maxResp) & (e not in ignoreTrials)]
plt.figure()
sns.distplot(scipy.stats.zscore(rxn))
np.mean(rxnTimes)
times = [j for e, j in enumerate(timeToOutcome) if (0<j<maxResp) & (e not in ignoreTrials)]
sns.distplot(scipy.stats.zscore(times))


        
   # returns single plot of avg rxn times for each SOA (time from stim start to resp)
times = []
for onset in np.unique(trialMaskOnset):
    lst = []
    for i, (time, soa, resp,mask) in enumerate(zip(df['reactionTime'], df['soa'], df['resp'], df['mask'])):
        if soa==onset and resp!=0:
            #if mask==True: 
            if i not in ignoreTrials and time!=0:  # only masked trials and no obvious guessing trials included 
                lst.append(time)
    times.append(lst)

med = [np.median(x) for x in times]
means = [np.mean(x) for x in times]

fig, ax = plt.subplots()
ax.plot(np.unique(trialMaskOnset), med, label='Median', alpha=.4, lw=3)
ax.plot(np.unique(trialMaskOnset), means, label='Mean', alpha=.4, lw=3)
plt.plot()
ax.set(title='Reaction Time (from Stim start) by SOA:  ' + str(f.split('_')[-3:-1]))
ax.set_xticks(np.unique(trialMaskOnset))
ax.legend()


# then also plot the median no-mask trial response time
##  for the mask only, plot which side the mouse turns**
nogoTurn, maskOnlyTurn, inds = nogo_turn(d)  # has 2 arrays: 1st is nogos, 2nd maskOnly

Rtimes = []
Ltimes = []
maskOnlyTimes = []
for onset in np.unique(trialMaskOnset):
    Rlst = []
    Llst = []
    for i, (time, soa, resp, mask, direc) in enumerate(zip(
            df['reactionTime'], df['soa'], df['resp'], df['mask'], df['rewDir'])):
        if soa==onset and resp!=0:   # not no resp
            if i not in ignoreTrials:
                if time != 0:
                    if direc==1:        # soa=0 is targetOnly, R turning
                        Rlst.append(time)
                    elif direc==-1:   # soa=0 is targetOnly, L turning
                        Llst.append(time)
                    elif direc==0 and mask!=0:
                        maskOnly.append(time)
    Rtimes.append(Rlst)
    Ltimes.append(Llst)


Rmed = [np.median(x) for x in Rtimes]
Rmeans = [np.mean(x) for x in Rtimes]
Lmed = [np.median(x) for x in Ltimes]
Lmeans = [np.mean(x) for x in Ltimes]

max = np.max(np.mean(Rmed+Lmed))

for median, mean, title, time in zip([Rmed, Lmed], [Rmeans, Lmeans], ['Left', 'Right'], [Rtimes, Ltimes]):
    
    fig, ax = plt.subplots()
    ax.plot(np.unique(trialMaskOnset), median, 'o-', label='Median', alpha=.4, lw=3)
    ax.plot(np.unique(trialMaskOnset), mean, 'o-', label='Mean', alpha=.4, lw=3)
    ax.plot(0, np.mean(maskOnly), label='Mean MaskOnly', marker='o', c='b')
    ax.plot(0, np.median(maskOnly), label='Median MaskOnly', marker='o', c='g')
    ax.set(title='{}-turning Reaction Time From StimStart, by SOA'.format(title), xlabel='SOA', ylabel='Response Time (frames, 60/sec)')
    #ax.set_ylim([np.max()])
    ax.set_xticks(np.unique(trialMaskOnset))
    a = ax.get_xticks().tolist()
    a = [int(i) for i in a]     
    a[-1]='targetOnly' 
    a[0] = 'MaskOnly'
    ax.set_xticklabels(a)
    ax.legend()




