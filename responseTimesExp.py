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
from freedmanDiaconis import freedman_diaconis
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
openLoop = d['openLoopFramesFixed'][()]
quiescentMoveFrames = d['quiescentMoveFrames'][:]
maxQuiescentMove = d['maxQuiescentNormMoveDist'][()]
trialEndFrame = d['trialEndFrame'][:end]
deltaWheel = d['deltaWheelPos'][:]                      # has wheel movement for every frame of session
maxResp = d['maxResponseWaitFrames'][()]   
trialMaskContrast = d['trialMaskContrast'][:end]

maskOnset = np.round(d['maskOnset'][()] * 1000/framerate).astype(int)
trialMaskOnset = np.round(d['trialMaskOnset'][:end] * 1000/framerate).astype(int)
maskLength = np.round(d['maskFrames'][()] * 1000/framerate).astype(int)
targetLength = np.round(d['targetFrames'][()] * 1000/framerate).astype(int)

for i, target in enumerate(trialTargetFrames):  # this is needed for older files nogos are randomly assigned a dir
    if target==0:
        trialRewardDirection[i] = 0

nogos = []   #not including maskOnly trials
for i, (rew, con) in enumerate(zip(trialRewardDirection, trialMaskContrast)):
    if rew==0 and con==0:
        nogos.append(i) 
        

# deltaWheel from start of stim to response (or no response) for each trial
# deltaWheel from start of closedLoop to response for nogos
trialWheel = []  
nogoWheelFromCL = [] 
for i, (start, resp, mask) in enumerate(zip(trialStimStartFrame, trialResponseFrame, trialMaskContrast)):
    if trialRewardDirection[i]==0:
        if mask==0:  # nogo trials
            wheel = (deltaWheel[start+openLoop:resp+5])   #from start of closedLoop
            nogoWheelFromCL.append(wheel)
            wheel2 = (deltaWheel[start:resp])
            trialWheel.append(wheel2)
            print(deltaWheel[resp+1]-deltaWheel[start+openLoop])
        elif mask>0:   # maskOnly
            wheel = (deltaWheel[start:resp])
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
    

#FIGURE OUT how to get the right times for all trial types - and have as one collection of times
'''
Possible cases:
    nogo no move 
    nogo resp (cross threshold)
    maskOnly no move
    maskOnly resp (cross threshold)
    go trial no resp = doesn't cross threshold (ends at end of maxResp)
    go trial no resp = crosses Q threshold but not trial threshold (normRewDist)
        will have 'rxnTime' but doesn't really mean anything
    go trial resp
    
Seems like we should only be looking at 'rxn' times for correct go trials and maskOnly?
SOA rxn time plot is all trial with mask, but not including no resp trials (or ignore trials?)
- what about maskOnly trials where they start moving before 100 ms?  Is that possible? physiologically
'''

#do not include nogo trials (no matter what, ==0; their wheel traces prior to gotone mess up rxn times)
# time from stimStart to moving the wheel

count = 0
rxnTimes = []
ignoreTrials = []
for i, times in enumerate(cumWheel):
    if i in nogos:
        rxnTimes.append(0)
    else:
        
        fp = times
        xp = np.arange(0, len(fp))*1/framerate
        x = np.arange(0, xp[-1], .001)
        interp = np.interp(x,xp,fp)
        threshold = maxQuiescentMove*d['monSizePix'][0] 
        val = np.argmax(abs(interp)>5)
        count+=1
#        t = np.argmax(abs(interp)>threshold)
#        a = np.argmax(abs(interp[0:t])>5)
#        if abs(t-a) < (10*1000/framerate):
#            rxnTimes.append(a)
#        else:
#            t = np.argmax(abs(interp[t::])>threshold)
#            rxnTimes.append(t)
        if 0 < val < 100:
            ignoreTrials.append(i)
            rxnTimes.append(0)
        else:
            rxnTimes.append(val)
        


# np.argmax(abs(cumWheel[i])>5)   old way 



n = start:threshold
np.where(n<5)[-1]
    




# velocities  - inst=delta(x)/delta(t) - avg (slope of linear regression) 




    
 
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
df['nogoMove'] = nogoMove

for (ind, time) in zip(nogoTurn[2][0], nogoRxnTimes):
    df.loc[ind,'reactionTime'] = time


for i in ignoreTrials:
    df.loc[i,'ignoreTrial'] = True




## Time to move wheel from start of wheel mvmt - will be (-) in some trials 
    # only for trials with target

rxn = [i for i in rxnTimes if 0 < i < maxResp]
plt.figure()
sns.distplot(scipy.stats.zscore(rxn))
np.mean(rxnTimes)
times = [j for j in timeToOutcome if 0<j<maxResp]
sns.distplot(scipy.stats.zscore(times))



# correct nogos have a rxn time of 0

for i, (time, rew, resp, soa) in enumerate(zip(cumWheel, df['rewDir'], df['reactionTime'], df['soa'])):
   #if mask==1 and rew!=0:
   #if i in ignoreTrials[:]:
   #if i<30 and rew==0:
   #if i in nogos:
   if i <371 and i>346:
        plt.figure()
        ax = plt.axes()
        plt.plot(time, lw=2)
        plt.axvline(x=openLoop, ymin=0, ymax=1, c='k', ls='--', alpha=.5)
        plt.axvline(x=15, ymin=0, ymax=1, c='c', ls='--', alpha=.8)
        #ax.set_xticklabels(xp)
        if trialMaskContrast[i]>0:
            plt.axvline(x=int(soa), ymin=0, ymax=1, c='m', ls='--', alpha=.7)
            plt.axvline(x=int(soa)+maskLength[0], ymin=0, ymax=1, c='m', ls='--', alpha=.7)

        plt.title('-'.join(f.split('_')[-3:-1] + [str(i)]))
     
        
        
# returns single plot of avg rxn times for each SOA (time from stim start to resp)
times = []
for onset in np.unique(trialMaskOnset):
    lst = []
    for i, (time, soa, resp,mask) in enumerate(zip(df['reactionTime'], df['soa'], df['resp'], df['mask'])):
        if soa==onset and resp!=0:
            if mask==True: #and i not in ignoreTrials:  # only masked trials and no obvious guessing trials included 
                lst.append(time)
    times.append(lst)

med = [np.median(x) for x in times]
means = [np.mean(x) for x in times]

fig, ax = plt.subplots()
ax.plot(np.unique(trialMaskOnset), med, label='Median', alpha=.4, lw=3)
ax.plot(np.unique(trialMaskOnset), means, label='Mean', alpha=.4, lw=3)
ax.set(title='Response Time by SOA:  ' + str(f.split('_')[-3:-1]))
ax.set_xticks(np.unique(trialMaskOnset))
ax.legend()


# then also plot the median no-mask trial response time
##  for the mask only, plot which side the mouse turns**

nogoTurn = nogo_turn(d)  # has 2 arrays: 1st is nogos, 2nd maskOnly

Rtimes = []
Ltimes = []
maskOnly=[]
for onset in np.unique(trialMaskOnset):
    Rlst = []
    Llst = []
    Mlst = []
    for i, (time, soa, resp, mask, direc) in enumerate(zip(
            df['reactionTime'], df['soa'], df['resp'], df['mask'], df['rewDir'])):
        if soa==onset and resp!=0:   # not no resp
            if i not in ignoreTrials:
                if direc==1:    
                    Rlst.append(time)
                elif direc==-1:
                    Llst.append(time)
                elif direc==0 and mask==0:
                    Mlst.append(time)
    Rtimes.append(Rlst)
    Ltimes.append(Llst)

    

Rmed = [np.median(x) for x in Rtimes]
Rmeans = [np.mean(x) for x in Rtimes]
Lmed = [np.median(x) for x in Ltimes]
Lmeans = [np.mean(x) for x in Ltimes]

for median, mean, title, time in zip([Rmed, Lmed], [Rmeans, Lmeans], ['Left', 'Right'], [Rtimes, Ltimes]):
    
    fig, ax = plt.subplots()
    ax.plot(np.unique(trialMaskOnset), median, label='Median', alpha=.4, lw=3)
    ax.plot(np.unique(trialMaskOnset), mean, label='Mean', alpha=.4, lw=3)
    ax.plot(0, np.mean(maskOnly), label='Mean MaskOnly', marker='o', c='b')
    ax.plot(0, np.median(maskOnly), label='Median MaskOnly', marker='o', c='g')
    ax.set(title='{}-turning Response Time by SOA'.format(title), xlabel='SOA', ylabel='Response Time (frames, 60/sec)')
    ax.set_xticks(np.unique(trialMaskOnset))
    ax.legend()

#alternatively:
fig, ax = plt.subplots() 
for median, title, time in zip([Rmed, Lmed], ['Left', 'Right'], [Rtimes, Ltimes]):
    ax.plot(np.unique(trialMaskOnset), median, label=title, alpha=.5)
    plt.title('Median Response Time by SOA'.format(title))
    ax.set_xticks(np.unique(trialMaskOnset))
    ax.legend()

## the above plots, by side, don't include the mask-only trials whose rewDir==0

for side in (Rtimes, Ltimes):
    fig, ax = plt.subplots(sharex='col', sharey='row')
    #ax.set_title('KDE for Response Times ' + '-'.join(f.split('_')[-3:-1])) 
    for i, s in enumerate(maskOnset):
        if i<4:
            plt.subplot(2,2,i+1)
            sns.distplot(side[i+1],  bins=(freedman_diaconis(side[i+1], returnas="bins")), color='r')
            #ax.text()
            plt.axvline(np.median(side[i+1]), ls='--', alpha=.3)
            plt.title('SOA {}'.format(s))  #, xlabel='Frames', ylabel='Dist')    
    plt.tight_layout()

  



times = []
for onset in np.unique(trialMaskOnset):
    lst = []
    for i, (time, soa, resp,mask) in enumerate(zip(df['timeToOutcome'], df['soa'], df['resp'], df['mask'])):
        if soa==onset and resp!=0:
            if mask==True and i not in ignoreTrials:  # only masked trials and no obvious guessing trials included 
                lst.append(time-soa)
    times.append(lst)

med = [np.median(x) for x in times]
means = [np.mean(x) for x in times]

















rightCorrectWheelMvmt = []
for i, (time, resp, rew) in enumerate(zip(cumWheel, trialResponse, trialRewardDirection)):
        for t in time:
            if (resp==1) and (rew==1):
                rightCorrectWheelMvmt.append((i, t))
            
df2 = pd.DataFrame(rightCorrectWheelMvmt, index=range(len(rightCorrectWheelMvmt)), columns=['trial', 'wheel mvmt'])
    
rightTrials = len(trialResponse[(trialResponse==1) & (trialRewardDirection==1)])
totalRows = math.ceil(rightTrials/10)
fig, axes = plt.subplots(nrows=totalRows, ncols=10, sharex=True, sharey=True)
axes_list = [item for sublist in axes for item in sublist]

for trial, wheelMvmt in df2.groupby('trial'):
    ax = axes_list.pop(0)
    wheelMvmt.plot(x=range(maxResp), y='wheel mvmt', label=trial, ax=ax)
    ax.set_title(trial)
    ax.tick_params(which='both',
                   bottom='off',
                   left='off', 
                   right='off',
                   top='off')
    
for ax in axes_list:
    ax.remove()
plt.tight_layout()






plt.hist(df['reactionTime'], bins=30)
plt.style.use('seaborn-darkgrid')

# create a loop that creates small multiples of wheel plots 
numGraphs = len(df.groupby('stimStart'))                  #choose stimStart bc it doesnt repeat, gives you all the trials 
#corrResps = len(trialResponse[trialResponse==1])          # for only plotting correct trials 
#incorrectResps = len(trialResponse[trialResponse==-1])    #for only plotting incorrect trials 
totalRows = math.ceil(numGraphs/10)

rightTrials = df[df['rewDir']==1]
rightCorrect = rightTrials[rightTrials['resp']==1]

leftTrials = df[df['rewDir']==-1]
leftCorrect = leftTrials[leftTrials['resp']==1]    #need to take delta wheel into account, to know when they started moving the wheel 

rightArray = np.array(rightCorrect['reactionTime'])
leftArray = np.array(leftCorrect['reactionTime'])

correctGo = df[(df['rewDir']!=0) & (df['resp']==1)]   # for correct go trials 
##########################################################

numGraphs = len(df.groupby('stimStart'))  
totalRows = math.ceil(numGraphs/10)
fig, axes = plt.subplots(nrows=totalRows, ncols=10, sharex=True, sharey=True)
axes_list = [item for sublist in axes for item in sublist]
grouped = df['cumRespTime'].groupedby('stimStart')



plt.tightlayout() 





    


   
response = np.where(respTime<respTime[0]-1)
respTime+=len(respTime[respTime>1])



df['trialLength'] = (trialResponseFrame-trialStimStartFrame)

df['respTime'] = [len(i) for i in responseTime[i>1] if len(i)>0]

newTimes=[] 
rxnTimes=[]         
for resp, time in zip(trialResponse, responseTime):
    newtime = []
    rxntime = []
    if resp==1:
        for x in time:
            if abs(x)>abs(3):
                newtime.append(x)
            else:
                rxntime.append(x)
                
    newTimes.append(newtime)
    rxnTimes.append(rxntime)
    
df['newTimes'] = [len(m) for m in newTimes]
df['reactionTime'] = [len(n) for n in rxnTimes]


           
#encoderAngle = d['rotaryEncoderRadians'][:]
reactionThresh = 0.1
reactionTime = np.full(trialResponse.size,np.nan)

for trial,(start,end) in enumerate(zip(trialStimStartFrame,trialEndFrame)):
    r = np.where(np.absolute(deltaWheel[start:end])>reactionThresh)[0]
    if any(r):
        reactionTime[trial] = r[0]/120


rightTrials = df[df['rewDir']==1]
rightCorrect = rightTrials[rightTrials['resp']==1]

leftTrials = df[df['rewDir']==-1]
leftCorrect = leftTrials[leftTrials['resp']==1]    #need to take delta wheel into account, to know when they started moving the wheel 

rightArray = np.array(rightCorrect['responseTime'])
leftArray = np.array(leftCorrect['responseTime'])

rBins = freedman_diaconis(rightArray, returnas='bins')
lBins = freedman_diaconis(leftArray, returnas='bins')

totalTrials = df[df['resp']==1]
totalTrials = totalTrials[totalTrials['rewDir']!=0]
totalArray = np.array(totalTrials['responseTime'])

 
rightArray = np.array(rightCorrect['newTimes'])
leftArray = np.array(leftCorrect['newTimes'])

rBins = freedman_diaconis(rightArray, returnas='bins')
lBins = freedman_diaconis(leftArray, returnas='bins')

totalTrials = df[df['resp']==1]
totalTrials = totalTrials[totalTrials['rewDir']!=0]
totalArray = np.array(totalTrials['newTimes'])


#fig, ax = plt.subplots()
#plt.hist(rightCorrect['responseTime'], bins=rBins, rwidth=4.1, color='r', alpha=.5)   # choose bin-width based on freedman-diaconis
#plt.hist(leftCorrect['responseTime'], bins=lBins, color='b', alpha=.5)
#plt.axvline(np.median(leftCorrect['responseTime']), c='b', ls='--')
#plt.axvline(np.mean(rightCorrect['responseTime']), c='r', ls='--')    # mean or median?

plt.figure()
sns.distplot(rightArray)
sns.distplot(leftArray)
plt.title('Distribution of response times by side:  ' + '-'.join(f.split('_')[-3:-1]))
plt.figure()
sns.distplot(totalArray, color='r')

# use gaussian KDE


