# -*- coding: utf-8 -*-
"""
Created on Tue Jun 30 10:59:57 2020

@author: chelsea.strawder
"""

import behaviorAnalysis
import performanceBySOA
from plottingTargetContrast import plot_contrast
from plotting_target_lengths import plot_flash
from SessionPerformance import plot_session
from responsePlotByParam import plot_by_param
import dataAnalysis
import qualityControl
from percentCorrect import session_stats
from catchTrials import catch_trials


# choose mouse file
d = dataAnalysis.import_data()

# plot session wheel trace - 1 plot, unless mask==True - 2 plots
##  if session is from 1/13 - 1/28, use framesToShowBeforeStart=30, else 60

behaviorAnalysis.makeWheelPlot(d, responseFilter=[-1,0,1], 
                               ignoreRepeats=True, framesToShowBeforeStart=60, 
                               mask=False, maskOnly=False, xlim=[0, .8])

# plot no response trials only (with repeats)
behaviorAnalysis.makeWheelPlot(d, responseFilter=[0], 
                               ignoreRepeats=False, framesToShowBeforeStart=60, 
                               mask=False, maskOnly=False,  xlim=[0, .8])

# plot activity over entire session, trial-by-trial - 1 plot
plot_session(d)


# plots catch trial wheel traces 
catch_trials(d, xlim=[0, .8])   

mouse_id=d['subjectName'][()]
date = d['startTime'][()].split('_')[0][-4:]
date = date[:2]+'-'+date[2:]
directory = r'\\allen\programs\braintv\workgroups\nc-ophys\corbettb\Masking\active_mice'
dataDir = os.path.join(os.path.join(directory, mouse_id), 'Plots') 
plt.savefig(dataDir+'/Wheel Plots/Catch/' + mouse_id + ' catch ' + date + '.png', dpi=300, bbox_inches='tight')


# prints out performance counts/% from session
session_stats(d)


# check for dropped frames
qualityControl.check_frame_intervals(d)


# check number of quiescent period violations - use 'sum' for cumsum OR 'count' for count per trial
qualityControl.check_qviolations(d, plot_type='sum')

qualityControl.check_qviolations(d, plot_type='count')

# check distribution of delta wheel position 
qualityControl.check_wheel(d)