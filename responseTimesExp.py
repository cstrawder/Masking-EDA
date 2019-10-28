# -*- coding: utf-8 -*-
"""
Created on Thu Aug 22 12:56:20 2019

@author: chelsea.strawder

Creats dataframe of response times per trial, by side, and plots distributions - 
including quiescent period violations 
(how quickly they turn after stim onset and/or goTone)

"""

import fileIO, h5py
import math
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import scipy.signal
import seaborn as sns 
from freedmanDiaconis import freedman_diaconis

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
trialMaskOnset = d['trialMaskOnset'][:end]
openLoop = d['openLoopFramesFixed'][()]
quiescentMoveFrames = d['quiescentMoveFrames'][:]
trialEndFrame = d['trialEndFrame'][:end]
deltaWheel = d['deltaWheelPos'][:]                      # has wheel movement for every frame of session
maxResp = d['maxResponseWaitFrames'][()]   
maskContrast = d['trialMaskContrast'][:end]==1


for i, trial in enumerate(trialTargetFrames):
    if trial==0:
        trialRewardDirection[i] = 0


# length of time from start of stim to response (or no response) for each trial
trialTimes = []   
for i, (start, resp) in enumerate(zip(trialStimStartFrame, trialResponseFrame)):
        respTime = (deltaWheel[start:resp])
        trialTimes.append(respTime)

#since deltawheel provides the difference in wheel mvmt from trial to trial
#taking the cumulative sum gives the actual wheel mvmt and plots as a smooth curve
cumRespTimes = []   
for i, time in enumerate(trialTimes):
    time = np.cumsum(time)
    cumRespTimes.append((time))

rxnTimes = []
for i, time2 in enumerate(cumRespTimes):
    time2 = time2[::-1]
    mask = (time2[:]<10)
    val = np.argmax(abs(time2)<10)
    t = len(time2) - val
    rxnTimes.append(t)
    
    
    np.argmax(abs(time2)>50)   #this is in pixels, calculated from Monitor norm and quiescent move threshold (.025)
    rxnTimes.append(val)
    
    #THEN trialresplength - rxnTimes

data = list(zip(trialRewardDirection, trialResponse, trialStimStartFrame, trialResponseFrame, maskContrast, trialMaskOnset))
index = range(len(trialResponse))

df = pd.DataFrame(data, index=index, columns=['rewDir', 'resp', 'stimStart', 'respFrame', 'mask', 'soa'])
df['trialLength'] = [len(t) for t in trialTimes]
df['reactionTime'] = rxnTimes

ignoreTrials = []
for i, t in enumerate(df['reactionTime']):     # 15 frames = 125 ms 
    if 0<t<10:
        ignoreTrials.append(i)
# return ignoreTrials and use in WheelPlot/behaviorAnalusis

plt.axvline(np.mean(df['reactionTime']), c='r', ls='--', alpha=.5)  #plots mena of rxn time - refine furhter by using by side and resp


# correct nogos have a rxn time of 0

for i, (time, mask, rew, resp, soa) in enumerate(zip(cumRespTimes, df['mask'], df['rewDir'], df['reactionTime'], df['soa'])):
    if mask==True and rew!=0:
       #if i in ignoreTrials[:]:
        plt.figure()
        plt.plot(time)
        plt.plot(0, len(time))
        plt.axvline(x=openLoop, ymin=0, ymax=1, c='k', ls='--', alpha=.5)
        plt.axvline(x=15, ymin=0, ymax=1, c='c', ls='--', alpha=.8)
        plt.title('-'.join(f.split('_')[-3:-1] + [str(i)] + [str(soa)]))
        

times = []
for onset in np.unique(trialMaskOnset):
    lst = []
    for time, soa, resp in zip(df['reactionTime'], df['soa'], df['resp']):
        if soa==onset and resp!=0:
            lst.append(time)
    times.append(lst)






rightCorrectWheelMvmt = []
for i, (time, resp, rew) in enumerate(zip(cumRespTimes, trialResponse, trialRewardDirection)):
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








    
df['cumRespTime'] = cumRespTimes

# here we calculate when the first wheel mvmt occured that passes the nogo threshold 
# which tells us when they reacted (i.e. first started moving to respond)

rxnTimes=[]         
for resp, time in zip(trialResponse, cumRespTimes):
    rxntime = []
    threshold=abs(2)
    for x in time:
        if abs(x)<threshold:
            rxntime.append(x)
    rxnTimes.append(rxntime)   




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

rightArray = np.array(rightCorrect['responseTime'])
leftArray = np.array(leftCorrect['responseTime'])

correctGo = df[(df['rewDir']!=0) & (df['resp']==1)]   # for correct go trials 
##########################################################

numGraphs = len(df.groupby('stimStart'))  
totalRows = math.ceil(numGraphs/10)
fig, axes = plt.subplots(nrows=totalRows, ncols=10, sharex=True, sharey=True)
axes_list = [item for sublist in axes for item in sublist]
grouped = df['cumRespTime'].groupedby('stimStart')



plt.tightlayout() 




for i, (time, resp) in enumerate(zip(cumRespTimes, df['resp'])):
    if i<20:
        plt.figure()
        plt.plot(time)
        plt.plot(0, len(time))
        plt.axvline(x=24, ymin=0, ymax=1, c='k', ls='--', alpha=.5)
        plt.title('-'.join(f.split('_')[-3:-1] + [str(i)]))
            
     
    

response = np.where()
   
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

 

'''want:
rew Dir so we know what trial type it was (L or R)
trial target frames so we know which trials were nogos
trialResponse so we know if they answered correctly 
stimstart so we know when the stim came on screen
trialResponseFrames so we know when they responded
deltaWheel bc we want to know WHEN they started moving the wheel and how quickly they moved it to center - tis is the response time
stimStart and Resp create a window within which deltawheal matters 

want to plot a distribution of both trial types and estimate parameters for each side 
for response time, it would be great to know time from moving wheel to hitting normRew

qperiod:
trialstartframes, openloop, quiescentframes (scalar), quiescent moveframes 
(frames in which movement ended/restarted q period) ** think about this one more
why do we want this plot?

nogos:
distance and direction turned for nogo, as well as responsetime'''

