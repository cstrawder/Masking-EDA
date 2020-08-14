# -*- coding: utf-8 -*-
"""
Created on Tue Apr 21 16:08:34 2020

@author: chelsea.strawder

looking for Rabbit effect
will the response time be longer for a correct trial that follows an incorrect trial?

incorrect == turned the wrong way (not no resp)

possible combinations:
    correct --> incorrect
    correct --> correct
    incorrect --> incorrect
    incorrect --> correct * this is the one the theory is concerned with, 
                            but the others are interesting as well 


"""

from dataAnalysis import import_data, create_df, get_dates
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


d = import_data()
df = create_df(d)

trials = []
oppRabbit = []

for e, (prev, current) in enumerate(zip(df['resp'][:-1], df['resp'][1:])):
    if prev==-1 and current==1:
        if (df.loc[e, 'rewDir'] !=0) and (df.loc[e+1, 'rewDir'] !=0):
            trials.append((e, e+1))
    elif prev==1 and current==-1:
         if (df.loc[e, 'rewDir'] !=0) and (df.loc[e+1, 'rewDir'] !=0):
            oppRabbit.append((e, e+1))
        
        
prevIncorrect = [df.loc[time[0], 'outcomeTime'] for time in trials]
currentCorrect = [df.loc[time[1], 'outcomeTime'] for time in trials]

prevCorrect = [df.loc[time[0], 'outcomeTime'] for time in oppRabbit]
currIncorrect = [df.loc[time[1], 'outcomeTime'] for time in oppRabbit]
    
rabbitDf = pd.DataFrame()
rabbitDf['error'] = prevIncorrect
rabbitDf['correct'] = currentCorrect

plt.figure()
sns.barplot(data=rabbitDf)
plt.ylabel('Response Time')
plt.title('Response Time in Consecutive Trials')
plt.xlabel('Previous Trial | Next Trial')




oppDf = pd.DataFrame()
oppDf['correct'] = prevCorrect
oppDf['error'] = currIncorrect

plt.figure()
sns.barplot(data=oppDf)
plt.ylabel('Response Time')
plt.title('Response Times in Consecutive Trials')
plt.xlabel('Previous Trial | Next Trial')




prevCorr = []
prevIncorrect = []

for e, (prev, current) in enumerate(zip(df['resp'][:-1], df['resp'][1:])):
    if prev!=0 and current!=0:
        if prev==-1:
            if (df.loc[e, 'rewDir'] !=0) and (df.loc[e+1, 'rewDir'] !=0):
                prevIncorrect.append(df.loc[e+1, 'outcomeTime'])
        elif prev==1:
             if (df.loc[e, 'rewDir'] !=0) and (df.loc[e+1, 'rewDir'] !=0):
                prevCorr.append(df.loc[e+1, 'outcomeTime'])
            
        
rabbitt = pd.DataFrame()
rabbitt['prevIncorrect'] = prevIncorrect
rabbitt['prevCorrect'] = prevCorr



#### ------------

currentTrialPrevError = []  # inds of current trial
currentTrialPrevCorr = []

trialThatIsPrevError = []  # these are the inds of the prev trial to above trials
trialThatIsPrevCorr = []


# get indices of trials where prev trial was either corr/error 
# e is the ind of previous trial, e+1 is ind of current trial (That we want the time for)
for e, (prev, current) in enumerate(zip(df['resp'][:-1], df['resp'][1:])):
    
    if current==1:
        if (df.loc[e, 'rewDir'] !=0) and (df.loc[e+1, 'rewDir'] !=0):
            if (df.loc[e, 'ignoreTrial'] !=True) and (df.loc[e+1, 'ignoreTrial'] !=True):
                if prev==-1:
                    currentTrialPrevError.append(e+1)
                    trialThatIsPrevError.append(e)
                elif prev==1:
                        currentTrialPrevCorr.append(e+1)  # append the ind of the current trial
                        trialThatIsPrevCorr.append(e)

# use indices to get outcome times from df    
# these are the times for the previous trial
timePrevIncorrect = [df.loc[time, 'outcomeTime'] for time in trialThatIsPrevError]
timePrevCorrect = [df.loc[time, 'outcomeTime'] for time in trialThatIsPrevCorr]

#these are all correct, current trials; preceding trials differ (above)
timeCurrTrialWithPrevIncorrect = [df.loc[time, 'outcomeTime'] for time in currentTrialPrevError]
timeCurrTrialWithPrevCorrect = [df.loc[time, 'outcomeTime'] for time in currentTrialPrevCorr]


date = get_dates(df)


plt.figure()
sns.barplot(data=[timeCurrTrialWithPrevIncorrect, timeCurrTrialWithPrevCorrect])

plt.ylabel('Response Time of Next Trial (correct), (ms)')
plt.title('Response Time vs Previous Trial')
plt.suptitle(df.mouse + '  ' +  date)
plt.xlabel('Previous Trial Type')
plt.xticks(ticks=[0,1], labels=['incorrect', 'correct'])

#plt.figure()
#plt.hist(timePrevIncorrect)
#plt.title('Distribution of response times, previous trial incorrect')
#plt.xlabel('Response Time')
#plt.ylabel('Number of Trials')
#
#plt.figure()
#plt.hist(timePrevCorrect, color='g')
#plt.title('Distribution of response times, prev trial correct')
#plt.title('Distribution of response times, previous trial correct')
#plt.xlabel('Response Time')
#plt.ylabel('Number of Trials')

fig, ax = plt.subplots()
plt.scatter(timePrevIncorrect, timeCurrTrialWithPrevIncorrect, color='m', alpha=.5)
plt.title('Response Time of Current Trial vs Previous Incorrect Trial')
plt.suptitle(df.mouse + '  ' + df.date)
plt.xlabel('Response Time, Previous Trial Incorrect (ms))')
plt.ylabel('Response Time, Current Trial Correct (ms))')
ax.plot((100,800), (100,800), ls="--", color='k', alpha=.3)
ax.set_xlim(100,800)
ax.set_ylim(100,800)


fig, ax = plt.subplots()
plt.scatter(timePrevCorrect, timeCurrTrialWithPrevCorrect, color='c', alpha=.5)
plt.title('Response Time of Current Trial vs Previous Correct Trial')
plt.suptitle(df.mouse + '  ' + df.date)
plt.xlabel('Response Time, Previous Trial Correct (ms))')
plt.ylabel('Response Time, Current Trial Correct (ms))')
ax.plot((100,800),(100,800), ls="--", color='k', alpha=.3)
ax.set_xlim(100,800)
ax.set_ylim(100,800)



























