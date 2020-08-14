# -*- coding: utf-8 -*-
"""
Created on Tue Jun  2 14:41:31 2020

@author: chelsea.strawder

Removed this from rxnTimes fxn in dataAnalysis bc wasn't helping.  
This (or something similar) might be useful in the future

"""

def wheel_trace_slice(dataframe, prestim=False):
    
    df = dataframe

    wheelDF = df[['trialStart','stimStart', 'respFrame', 'deltaWheel', 'trialFrameIntervals']].copy()
    wheelDF['wheelLen'] = list(map(len, wheelDF.loc[:,'deltaWheel']))   #len of deltaWheel trace
    
    
    
    wheelDF['stim'] = wheelDF['stimStart'] - wheelDF['trialStart']  #prestim
    wheelDF['resp'] = wheelDF['respFrame'] - wheelDF['trialStart']  #entire trial
    wheelDF['trialOnly'] = wheelDF['respFrame'] - wheelDF['stimStart'] #trialOnly
    
        # returns portion of wheel trace that is relevant only to target presentation (no prestim)
    if prestim==False:
        wheel = [wheel[start:stop] for (wheel, start, stop) in zip(
                wheelDF['deltaWheel'], wheelDF['stim'], wheelDF['trialOnly'])]
    else:  
        pass
#        # returns entire wheel trace from start of trial to end of trial ///not max possible trial length
##         wheel = [wheel[:stop] for (wheel, stop) in zip(
##                wheelDF['deltaWheel'], wheelDF['diff2'])]
#        THIS NEEDS MAJOR WORK
        
    #returns wheel slice from stim start to maxTrialLength
    wheel = [wheelTrace[stim:end] for (wheelTrace, stim, end) in 
             zip(wheelDF['deltaWheel'], wheelDF['stim'], wheelDF['wheelLen'] )]
        

    return (wheel, wheelDF['stim'])

