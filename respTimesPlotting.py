# -*- coding: utf-8 -*-
"""
Created on Thu Feb  6 17:28:53 2020

@author: svc_ccg
"""

plt.figure()
for onset in np.unique(trialMaskOnset):
    for i, (v, soa, resp,mask) in enumerate(zip(velo, df['soa'], df['resp'], df['mask'])):
        if soa==onset and resp!=0:
            plt.scatter(soa, v) 


   # returns single plot of avg rxn times for each SOA (time from stim start to resp)
Rtimes = [[],[]]   # hit, miss
Ltimes = [[],[]]
for onset in np.unique(trialMaskOnset):
    Clst = []
    Ilst = []
    for i, (time, soa, resp,mask) in enumerate(zip(df['reactionTime'], df['soa'], df['resp'], df['mask'])):
        if soa==onset and resp!=0:
            if i not in ignoreTrials and time!=0:  # only masked trials and no obvious guessing trials included 
                if resp==1:
                    Clst.append(time)
                elif resp==-1:
                    Ilst.append(time)
    for l in (Rtimes, Ltimes):
        l[1].append(Ilst)
        l[0].append(Clst)

RhitMed = [np.median(x) for x in Rtimes[0]]
RmissMed = [np.median(x) for x in Rtimes[0]]
LhitMed = [np.median(x) for x in Rtimes[0]]
LmissMed = [np.median(x) for x in Rtimes[0]]

#means = [np.mean(x) for x in times]

fig, ax = plt.subplots()
ax.plot(np.unique(trialMaskOnset), corrMed, label='Median, hit trials', alpha=.4, lw=3)
ax.plot(np.unique(trialMaskOnset), incorrMed, label='Median, miss trials', alpha=.4, lw=3)
plt.plot()
ax.set(title='Reaction Time (from Stim start) by SOA:  ' + str(f.split('_')[-3:-1]))
ax.set_xticks(np.unique(trialMaskOnset))
ax.legend()


nogoTurn, maskOnly, inds = nogo_turn(d)  # has 2 arrays: 1st is nogos, 2nd maskOnly

hits = [[],[]]  #R, L
misses = [[],[]]
maskOnlyTimes = [[],[]]  #R, L

for a, b in zip(inds[1], maskOnly):    # inds is index of maskOnly turning trials
    if b==1:
        maskOnlyTimes[0].append(rxnTimes[a])  #maskonly turned R
    elif b==-1:
        maskOnlyTimes[1].append(rxnTimes[a])  # maskOnly turned L

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

#Lmeans = [np.mean(x) for x in Ltimes]
#Rmeans = [np.mean(x) for x in Rtimes]
#max = np.max(np.mean(Rmed+Lmed))
fig, ax = plt.subplots()
#for right, left, title, time in zip([Rmed, RmissMed], [Lmed, LmissMed], ['Left', 'Right'], [Rtimes, Ltimes]):

ax.plot(np.unique(trialMaskOnset[:-2]), Rmed, 'ro-', label='Rhit',  alpha=.6, lw=3)
ax.plot(np.unique(trialMaskOnset[:-2]), RmissMed, 'ro-', label='R miss', ls='--', alpha=.3, lw=2)
ax.plot(np.unique(trialMaskOnset[:-2]), Lmed, 'bo-', label='L hit', alpha=.6, lw=3)
ax.plot(np.unique(trialMaskOnset[:-2]), LmissMed, 'bo-', label='L miss', ls='--', alpha=.3, lw=2)
ax.plot(0, np.median(maskOnly), marker='o', c='k')
ax.set(title='{}-turning Reaction Time From StimStart, by SOA'.format(title), xlabel='SOA', ylabel='Response Time (frames, 60/sec)')
#ax.set_ylim([np.max()])
ax.set_xticks(np.unique(trialMaskOnset))
a = ax.get_xticks().tolist()
a = [int(i) for i in a]     
a[-1]='targetOnly' 
a[0] = 'MaskOnly'
ax.set_xticklabels(a)
ax.legend()