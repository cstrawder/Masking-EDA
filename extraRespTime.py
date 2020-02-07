# -*- coding: utf-8 -*-
"""
Created on Thu Feb  6 16:22:20 2020

@author: svc_ccg

extra crap from responseTimesExp
Nice to expand the seaborn multi-histogram plots

"""

## the above plots, by side, don't include the mask-only trials whose rewDir==0
p = [3,10,13,17,42,54,63,64,73,83,87,111,123,140,144. 154,155,160,182,190,229,233,255,
     272,287,292,311,313,323,341,342,345,354,367,368,376,386,387,401,402,406,419,437,490,
     501,509,519,521,533,534,551,558,574,586,590,603,620,626]


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
     
        


for side in (Rtimes, Ltimes):
    fig, ax = plt.subplots(sharex='col', sharey='row')
    #ax.set_title('KDE for Response Times ' + '-'.join(f.split('_')[-3:-1])) 
    for i, s in enumerate(maskOnset):
        if i<4:
            plt.subplot(2,2,i+1)
            sns.distplot(side[i+1], color='r')
            #ax.text()
            plt.axvline(np.median(side[i+1]), ls='--', alpha=.3)
            plt.title('SOA {}'.format(s))  #, xlabel='Frames', ylabel='Dist')    
    plt.tight_layout()

  



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
grouped = df['reactionTime'].groupedby('stimStart')



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

rightArray = np.array(rightCorrect['reactionTime'])
leftArray = np.array(leftCorrect['reactionTime'])

rBins = freedmanDiaconis.freedman_diaconis(rightArray, returnas='bins')
lBins = freedmanDiaconis.freedman_diaconis(leftArray, returnas='bins')

totalTrials = df[df['resp']==1]
totalTrials = totalTrials[totalTrials['rewDir']!=0]
totalArray = np.array(totalTrials['reactionTime'])

 
rightArray = np.array(rightCorrect['newTimes'])
leftArray = np.array(leftCorrect['newTimes'])

rBins = freedmanDiaconis.freedman_diaconis(rightArray, returnas='bins')
lBins = freedmanDiaconis.freedman_diaconis(leftArray, returnas='bins')

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


