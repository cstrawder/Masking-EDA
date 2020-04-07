# -*- coding: utf-8 -*-
"""
Created on Thu Mar 26 15:09:56 2020

@author: chelsea.strawder
"""

from dataAnalysis import import_data, create_df
import scipy.stats as stats

dn = {}
for i, f in enumerate(files[-3:]):              #change index for desired files
    d = h5py.File(f) 
    dn['df_{}'.format(i)] = create_df(d)        #creates keys in dict dn with format df_#

dictget = lambda x, *k: [x[i] for i in k]
df1, df2, df3 = dictget(dn, 'df_0', 'df_1', 'df_2')    # assigns each dataframe to a new variable - essentially unpacks dict dn

dfall = pd.concat([df1,df2,df3], ignore_index=True)



def extract_vars(data):
    return {key: data[str(key)][()] for key in data.keys()}
    
def create_vars(dn):
    for key,val in dn.items():   #work in progress, if even possible
        globals()
        exec (key + '= val')

# IN PLOTTING BY PARAM
  
    
miss = missNonzero.pivot_table(values='trialLength', index=param, columns='rewDir', 
                        margins=True, dropna=True)
hit = corrNonzero.pivot_table(values='trialLength', index=param, columns='rewDir', 
                        margins=True, dropna=True)

print('hits avg t \n', hit)
print('\n' * 2)
print('misses avg t \n', miss)
  
# use the df to filter the trial by RewDir 
# maybe use multiindex?? 

y = corrNonzero.groupby(['rewDir', param])['trialLength'].describe()
print(y)
#y.to_excel("date_describe.xlsx")

#to reduce bulk below; something like this?
Rhit = corrNonzero[corrNonzero['rewDir']==1]
avgs = Rhit.groupby('soa')['trialLength'].mean()




    #hit.plot(title='hits')
    #miss.plot(title='misses')
    print('hits \n', hit)
    print('\n' * 2)
    print('misses \n', miss)


b = stats.f_oneway(df['trialLength'][df['soa'] == 17], 
             df['trialLength'][df['soa'] == 25],
             df['trialLength'][df['soa'] == 33],
             df['trialLength'][df['soa'] == 50],
             df['trialLength'][df['soa'] == 100])


b = stats.f_oneway(dfall['trialLength'][dfall['soa'] == 17], 
             dfall['trialLength'][dfall['soa'] == 25],
             dfall['trialLength'][dfall['soa'] == 33],
             dfall['trialLength'][dfall['soa'] == 50],
             dfall['trialLength'][dfall['soa'] == 100])


#When i do this 1-way ANOVA on the correct hits, pval isnt significant, but when I do on misses it is 
# only using actual masking SOAs

b = stats.f_oneway(nonzeroRxns['trialLength'][nonzeroRxns['soa'] == 17], 
             nonzeroRxns['trialLength'][nonzeroRxns['soa'] == 25],
             nonzeroRxns['trialLength'][nonzeroRxns['soa'] == 33],
             nonzeroRxns['trialLength'][nonzeroRxns['soa'] == 50],
             nonzeroRxns['trialLength'][nonzeroRxns['soa'] == 100])



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