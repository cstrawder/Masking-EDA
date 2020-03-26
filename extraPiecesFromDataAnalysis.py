# -*- coding: utf-8 -*-
"""
Created on Thu Mar 26 15:09:56 2020

@author: chelsea.strawder
"""

from dataAnalysis import import_data, create_df


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