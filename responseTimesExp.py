# -*- coding: utf-8 -*-
"""
Created on Thu Aug 22 12:56:20 2019

@author: chelsea.strawder

Creats dataframe of response times per trial, by side, and plots distributions - 

(when they start turning in a trial,
how quickly they turn after stim onset and/or goTone,
how long it takes to reach an outcome,
and translating the velocity of their turns into choice confidence)

*add a plot of rxn times from MASK onset (not stimStart) to see if there is
dependence on mask presence

"""

import fileIO, h5py
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from scipy import signal, stats
import seaborn as sns 

from nogoData import nogo_turn


## SETUP  

matplotlib.rcParams['pdf.fonttype'] = 42

f = fileIO.getFile(rootDir=r'\\allen\programs\braintv\workgroups\nc-ophys\corbettb\Masking')
d = h5py.File(f)

fi = d['frameIntervals'][:]
framerate = int(np.round(1/np.median(fi)))

#in frames
trialResponse = d['trialResponse'][:]
end = len(trialResponse)
trialRewardDirection = d['trialRewardDir'][:end]
trialTargetFrames = d['trialTargetFrames'][:end]
trialStartFrame = d['trialStartFrame'][:]    
preStimFrames = d['preStimFramesFixed'][()]
preStimVar = d['preStimFramesVariableMean'][()]              
openLoopFrames = d['openLoopFramesFixed'][()]
openLoopVar = d['openLoopFramesVariableMean'][()]
openLoopMax = d['openLoopFramesMax'][()]
trialOpenLoopFrames = d['trialOpenLoopFrames'][:end]
maxQuiescentMove = d['maxQuiescentNormMoveDist'][()]
quiescentMoveFrames = d['quiescentMoveFrames'][:]
trialStimStartFrame = d['trialStimStartFrame'][:]
trialResponseFrame = d['trialResponseFrame'][:end] 
trialEndFrame = d['trialEndFrame'][:end]
deltaWheel = d['deltaWheelPos'][:]                      
trialMaskContrast = d['trialMaskContrast'][:end]
nogoWait = d['nogoWaitFrames'][()]

def convert_to_ms(value):
    return np.round(value * 1000/framerate).astype(int)

#in ms
maskOnset = convert_to_ms(d['maskOnset'][()])
trialMaskOnset = convert_to_ms(d['trialMaskOnset'][:end])
maskLength = convert_to_ms(d['maskFrames'][0])
targetLength = convert_to_ms(d['targetFrames'][0])
maxResp = convert_to_ms(d['maxResponseWaitFrames'][()])


for i, target in enumerate(trialTargetFrames):  # this is needed for older files where nogos are randomly assigned a dir
    if target==0:
        trialRewardDirection[i] = 0

nogos = [i for i, (rew, con) in enumerate(zip(trialRewardDirection, trialMaskContrast)) if rew==0 and con==0]

if np.any(trialMaskOnset)>0:
    noMaskVal = maskOnset[-1] + round(np.mean(np.diff(maskOnset)))  # creates an evenly-spaced value from soas for targetOnly condition 
    maskOnset = np.append(maskOnset, noMaskVal)                     # makes final value the targetOnly condition in maskOnset
    
    for i, (mask, trial) in enumerate(zip(trialMaskOnset, trialTargetFrames)):   # filters target-Only trials and applies value from above
        if trial>0 and mask==0:
            trialMaskOnset[i]=noMaskVal       

#gives all the wheel traces for each trial, each the same size
       
maxGo = d['maxResponseWaitFrames'][()]
trialWheel = []  
nogoWheel = []   #this 2nd list serves for separate analysis 

for i, (start, resp, mask) in enumerate(zip(trialStimStartFrame, trialResponseFrame, trialMaskContrast)):
    if trialRewardDirection[i]==0:
        if mask==0:                              # nogo trials
            wheel = (deltaWheel[start+trialOpenLoopFrames[i]:(start+trialOpenLoopFrames[i]+maxGo)])   
            trialWheel.append(wheel)
            wheel2 = (deltaWheel[start+trialOpenLoopFrames[i]:resp])  # wheel up until nogoMove, from go-tone
            nogoWheel.append(wheel2)
    else:                                       #target + maskOnly trials
        wheel = (deltaWheel[start:start+maxGo])
        trialWheel.append(wheel)

cumWheel = [np.cumsum(time) for time in trialWheel]  
nogoCumWheel = [np.cumsum(time) for time in nogoWheel]   # from goTone to mouse repsonse (past threshold) 


interpWheel = []
timeToMoveWheel = []    # time from stimStart to when they start moving the wheel
ignoreTrials = []

for i, (times, resp) in enumerate(zip(cumWheel, trialResponse)):
    fp = times    
    xp = np.arange(0, len(fp))*1/framerate
    x = np.arange(0, xp[-1], .001)    #wheel mvmt each ms 
    interp = np.interp(x,xp,fp)
    interpWheel.append(interp)
    qThreshold = maxQuiescentMove*d['monSizePix'][0]   #threshold to end nogo or q-period (unless we change nogo thresh...)
    rewThreshold = d['normRewardDistance'][()]*d['monSizePix'][0]
    rew = np.argmax(abs(interp)>rewThreshold)

    if 0<rew<150:           #if they move the wheel past the reward threshold before 150ms (pre-gotone)
        ignoreTrials.append(i)
        
    t = np.argmax(abs(interp)>qThreshold)
    print(t)
    if t <100:
        plt.figure()
        plt.plot(interp)
    if t <= 100:
        ignoreTrials.append(i)
        timeToMoveWheel.append(0)   # no resp, or moving before 100 ms
    else:
        t = np.argmax(abs(interp[100::])>qThreshold) + 100  #100 ms is limit of ignore trial
        a = np.argmax(abs(np.round(np.diff(interp[100::])))>0) + 100
        if 0 < a <= 100:
            ignoreTrials.append(i)    # ask sam about ignoring trials, including nogos 
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




  

velo = []           
for i, time in enumerate(interpWheel):   #time is array of wheel mvmt
    if type(time) is int:
        velo.append(0)          # no wheel mvmt is 0, an int
    else:
        q = int(timeToMoveWheel[i])   # rxn time of the trial, in ms, used as index of interpWheel
        v = abs(time[-1] - time[q]) / timeToOutcome[i]   # dist (in pix??) moved over time/time
        velo.append(v)
        # in pix/ms?  could convert to radians

nogoRespTimes = [convert_to_ms(len(times)) for times in nogoCumWheel]     # num of frames from goTone to mvmt or reward

       
nogoTurn, maskOnly, inds = nogo_turn(d)  # 1st 2 arrays are turned direction, 3rd is indices of 1st 2                       
                            
nogoMove = np.zeros(len(trialResponse)).astype(int)
for i in range(len(trialResponse)):
    for (ind, turn) in zip(inds[0], nogoTurn):
        if i==ind:
            nogoMove[i] = turn

data = list(zip(trialRewardDirection, trialResponse, trialStimStartFrame, trialResponseFrame))
index = range(len(trialResponse))

df = pd.DataFrame(data, index=index, columns=['rewDir', 'resp', 'stimStart', 'respFrame'])
df['trialLength'] = convert_to_ms((df['respFrame'] - df['stimStart']))
df['startMovingWheel'] = timeToMoveWheel
df['timeToOutcome'] = convert_to_ms((df['respFrame'] - df['reactionTime']))  ## this is wrong - resp - rxn
if len(maskOnset)>0:
    df['mask'] = trialMaskContrast
    df['soa'] = trialMaskOnset
df['nogoMove'] = nogoMove  # turning direction of nogo trial

#for (ind, time) in zip(nogoTurn[2][0], nogotimeToMoveWheel):    #adds rxnTimes to nogos; need to look at separately
#    df.loc[ind,'reactionTime'] = time


for i in ignoreTrials:
    df.loc[i,'ignoreTrial'] = True

s = df.soa
onsetIndex = s[(s!=128) & (s!=0)]   # indeices of trials that are masked (T and M)

##############################################################################################
##PLOTTING
    
## Time to move wheel from start of wheel mvmt - will be (-) in some trials 
    # only for trials with target

rxn = [i for e, i in enumerate(timeToMoveWheel) if (0 < i < maxResp) & (e not in ignoreTrials)]
plt.figure()
sns.distplot(scipy.stats.zscore(rxn))
np.mean(timeToMoveWheel)
times = [j for e, j in enumerate(timeToOutcome) if (0<j<maxResp) & (e not in ignoreTrials)]
sns.distplot(scipy.stats.zscore(times))


# plot average wheel velocity based on soa 
velocities=[]
for onset in np.unique(trialMaskOnset):
    vel = []
    for i, (v, soa, resp,mask) in enumerate(zip(velo, df['soa'], df['resp'], df['mask'])):
        if soa==onset and resp!=0:
            if v!=0:
                vel.append(v)
    velocities.append(vel)
   
err = [np.std(vel) for vel in velocities]

fig, ax = plt.subplots()
for i, (v,e) in enumerate(zip(velocities, err)):
    ax.errorbar(np.unique(trialMaskOnset)[i], np.mean(v), yerr=e, fmt='-o')
ax.set(title='Mean velocity (from start of wheel mvmt) by SOA:  ' + str(f.split('_')[-3:-1]))
ax.set_xticks(np.unique(trialMaskOnset))

# filter only trials where they responded, then only corr resps
# can be used with ['timeToOutcome'], ['trialLength'], ['reactionTime']
nonzeroRxns = df[(df['reactionTime']!=0) & (df['ignoreTrial']!=True)]
corrNonzero = nonzeroRxns[nonzeroRxns['resp']==1]

plt.figure()
sns.violinplot(x=nonzeroRxns['soa'], y=nonzeroRxns['reactionTime'])
plt.title('Dist of reaction times by SOA:  ' + str(f.split('_')[-3:-1]))

## not sure how to change axis labels- maybe bc seaborn?? Need to rethink
        
   # returns single plot of avg rxn times for hits each SOA (time from stim start to resp)
   # L and R turning combined
times = []
for onset in np.unique(trialMaskOnset):
    lst = []
    for i, (time, soa, resp,mask) in enumerate(zip(df['reactionTime'], df['soa'], df['resp'], df['mask'])):
        if soa==onset and resp==1:
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
ax.set(title='Median Reaction Time (from Stim start) by SOA:  ' + str(f.split('_')[-3:-1]))
ax.set_xticks(np.unique(trialMaskOnset))
a = ax.get_xticks().tolist()
a = [int(i) for i in a]     
a[-1]='targetOnly' 
#a[0] = 'MaskOnly'
ax.set_xticklabels(a)
ax.legend()



hits = [[],[]]  #R, L
misses = [[],[]]
maskOnlyTimes = [[],[]]  #R, L

for a, b in zip(inds[1], maskOnly):    # inds is index of maskOnly turning trials
    if b==1:
        maskOnlyTimes[0].append(timeToMoveWheel[a])  #maskonly turned R
    elif b==-1:
        maskOnlyTimes[1].append(timeToMoveWheel[a])  # maskOnly turned L

for onset in np.unique(trialMaskOnset):
    hitVal = [[],[]]
    missVal = [[],[]]
    for j, (time, soa, resp, mask, direc) in enumerate(zip(
            df['reactionTime'], df['soa'], df['resp'], df['mask'], df['rewDir'])):
        if soa==onset and resp!=0:   # not no resp
            if j not in ignoreTrials and time!=0:
                if direc==1:       # soa=0 is targetOnly, R turning
                    if resp==1:
                        hitVal[0].append(time)  #hit
                    else:
                        missVal[0].append(time)  #miss
                elif direc==-1:   # soa=0 is targetOnly, L turning
                    if resp==1:
                        hitVal[1].append(time)  #hit
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
ax.plot(0, np.median(maskOnlyTimes[0]), 'r>')
ax.plot(0, np.median(maskOnlyTimes[1]), 'b<')
ax.set(title='Median Reaction Time From StimStart, by SOA', xlabel='SOA', ylabel='Reaction Time (ms)')
plt.suptitle(str(f.split('_')[-3:-1]))
#ax.set_ylim([np.max()])
ax.set_xticks(np.unique(trialMaskOnset))
a = ax.get_xticks().tolist()
a = [int(i) for i in a]     
a[-1]='targetOnly' 
a[0] = 'MaskOnly'
ax.set_xticklabels(a)
ax.legend()