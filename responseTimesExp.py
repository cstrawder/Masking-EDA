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
from nogoTurn import nogo_turn

matplotlib.rcParams['pdf.fonttype'] = 42

f = fileIO.getFile(rootDir=r'\\allen\programs\braintv\workgroups\nc-ophys\corbettb\Masking')
d = h5py.File(f)

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
trialMaskOnset = d['trialMaskOnset'][:end]
trialMaskContrast = d['trialMaskContrast'][:end]
maskOnset = d['maskOnset'][()]
fi = d['frameIntervals'][:]
framerate = 1/np.median(fi)


for i, trial in enumerate(trialTargetFrames):  # this is needed for older files nogos are randomly assigned a dir
    if trial==0:
        trialRewardDirection[i] = 0

nogos = []
for i, (rew, mask) in enumerate(zip(trialRewardDirection, trialMaskContrast)):
    if rew==0 and mask==0:
        nogos.append(i) 
        

# deltaWheel from start of stim to response (or no response) for each trial
trialWheel = []  
nogoWheelFromCL = [] 
for i, (start, resp, mask) in enumerate(zip(trialStimStartFrame, trialResponseFrame, trialMaskContrast)):
    if trialRewardDirection[i]==0:
        wheel = (deltaWheel[start:resp+4])
        trialWheel.append(wheel)
        if mask==0:  # nogo trials
            wheel = (deltaWheel[start+openLoop:resp+4])   #from start of closedLoop
            nogoWheelFromCL.append(wheel)
            print(deltaWheel[resp+1]-deltaWheel[start+openLoop])
    else:
        wheel = (deltaWheel[start:resp])
        trialWheel.append(wheel)


#since deltawheel provides the difference in wheel mvmt from trial to trial
#taking the cumulative sum gives the actual wheel mvmt and plots as a smooth curve
cumWheel = []   
for mvmt in trialWheel:
    time = np.cumsum(mvmt)
    #smoothed = scipy.signal.medfilt(time, kernel_size=5)
    #cumRespTimes.append(smoothed)
    cumWheel.append(time)
    
    
# time from stimStart to moving the wheel
    # this is not right - we want to find the frame the wheel moves above 5 pix and then continues onto past 42
    # sam suggests linear interpolation on wheel trace
rxnTimes = []
ignoreTrials = []
for i, times in enumerate(cumWheel):
    x = lambda times: np.round(times)
    mvmt = x(times)
    threshold = maxQuiescentMove*d['monSizePix'][0]   #threshold for nogo qperiod/mvmt
    mask = (abs(mvmt[:])>threshold)  # before this was 5
    val = np.argmax(mask)    # the index of the frame right before the difference exceeds threshold (i.e. when they START moving)
    if 0 < val < 12:
        ignoreTrials.append(i)
        rxnTimes.append(0)
    else:
        rxnTimes.append(val)
    
 
    
timeToOutcome = []    # time to outcome is time from rxnTime (1st wheel mvmt) to respFrame
for i,j in zip(cumWheel, rxnTimes):    
    timeToOutcome.append(len(i)-j)    # ends up just being the diff btwn trialLength and rxnTime


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
df['trialLength'] = [len(t) for t in trialWheel]
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











plt.figure()
sns.distplot(scipy.stats.zscore(rxnTimes))



# correct nogos have a rxn time of 0

for i, (time, rew, resp) in enumerate(zip(cumWheel, df['rewDir'], df['reactionTime'])):
   # if mask==True and rew!=0:
   if i in ignoreTrials[:]:
   #if i<30 and rew==0:
   #if i in nogos:
   #if i <20:
        plt.figure()
        plt.plot(time, lw=2)
        plt.plot(0, len(time))
        plt.axvline(x=openLoop, ymin=0, ymax=1, c='k', ls='--', alpha=.5)
        plt.axvline(x=15, ymin=0, ymax=1, c='c', ls='--', alpha=.8)
        plt.title('-'.join(f.split('_')[-3:-1] + [str(i)]))
        

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
ax.plot(np.unique(trialMaskOnset), med, label='Median', alpha=.4)
ax.plot(np.unique(trialMaskOnset), means, label='Mean', alpha=.4)
ax.set(title='Response Time by SOA') 
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
        if soa==onset and resp!=0:
            #if i not in ignoreTrials:
            if direc==1:    
                Rlst.append(time)
            elif direc==-1:
                Llst.append(time)
        if direc==0 and mask==1:
            maskOnly.append(time)
        elif direc==0 and mask==0:
                    Mlst.append(time)
#        elif soa==0:
#                direc==0:
#                    maskOnly.append(time)
    Rtimes.append(Rlst)
    Ltimes.append(Llst)

    

Rmed = [np.median(x) for x in Rtimes]
Rmeans = [np.mean(x) for x in Rtimes]
Lmed = [np.median(x) for x in Ltimes]
Lmeans = [np.mean(x) for x in Ltimes]

for median, mean, title, time in zip([Rmed, Lmed], [Rmeans, Lmeans], ['Left', 'Right'], [Rtimes, Ltimes]):
    
    fig, ax = plt.subplots()
    ax.plot(np.unique(trialMaskOnset), median, label='Median', alpha=.4)
    ax.plot(np.unique(trialMaskOnset), mean, label='Mean', alpha=.4)
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


