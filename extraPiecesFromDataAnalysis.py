# -*- coding: utf-8 -*-
"""
Created on Thu Mar 26 15:09:56 2020

@author: chelsea.strawder
"""

from dataAnalysis import import_data, create_df


def extract_vars(data):
    return {key: data[str(key)][()] for key in data.keys()}
    
def create_vars(dn):
    for key,val in dn.items():   #work in progress, if even possible
        globals()
        exec (key + '= val')


x = stats.f_oneway(dfall['trialLength'].groupby(df['soa']))


b = stats.f_oneway(dfall['trialLength'][dfall['soa'] == 17], 
             dfall['trialLength'][dfall['soa'] == 25],
             dfall['trialLength'][dfall['soa'] == 33],
             dfall['trialLength'][dfall['soa'] == 50],
             dfall['trialLength'][dfall['soa'] == 100])


#When i do this 1-way ANOVA on the correct hits, pval isnt significant, but when I do on misses it is 
# only using actual masking SOAs

b = stats.f_oneway(missNonzero['trialLength'][missNonzero['soa'] == 17], 
             missNonzero['trialLength'][missNonzero['soa'] == 25],
             missNonzero['trialLength'][missNonzero['soa'] == 33],
             missNonzero['trialLength'][missNonzero['soa'] == 50],
             missNonzero['trialLength'][missNonzero['soa'] == 100])



plt.figure()
for i,j,k,m in zip(nonzeroRxns.rewDir, nonzeroRxns.resp, nonzeroRxns.interpWheel, nonzeroRxns.soa):
    if i==1:
        if m==17:
            plt.plot(k, alpha=.2, color='m')
        elif m==33:
            plt.plot(k, alpha=.2, color='g')
        elif m==25:
            plt.plot(k, alpha=.2, color='k')
        elif m==50:
            plt.plot(k, alpha=.2, color='c')
        elif m==100:
            plt.plot(k, alpha=.2, color='b')
        
    elif i==1 and j==-1:
        plt.plot(k, alpha=.1, color='k')
        
        
        
plt.figure()
sns.violinplot(x=nonzeroRxns['soa'], y=nonzeroRxns['trialLength'])
plt.title('Dist of reaction times by SOA:  ' + str(f.split('_')[-3:-1]))

err = nonzeroRxns.groupby('soa')['trialLength'].std()