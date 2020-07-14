# -*- coding: utf-8 -*-
"""
Created on Mon Jul 13 14:54:31 2020

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
import matplotlib.pyplot as plt
import os
import reportlab
from reportlab.pdfgen import canvas
from reportlab.platypus import Image
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter


d = dataAnalysis.import_data()

mouse_id=d['subjectName'][()]
date = d['startTime'][()].split('_')[0][-4:]
date = date[:2]+'-'+date[2:]

date = date if date[:2] in ['10','11','12'] else date[-4:]

directory = r'\\allen\programs\braintv\workgroups\nc-ophys\corbettb\Masking\active_mice'
dataDir = os.path.join(os.path.join(directory, mouse_id), 'Plots/') 

c = canvas.Canvas(mouse_id + ' Daily Summary ' + date + '.pdf', pagesize=letter, bottomup=1)



# insert "Daily Summary" at top bold, mouse id, and date 
# insert daily wheel plot on left of canvas
reportlab.platypus.Image(dataDir + mouse_id + ' ' + date + '.png', width=6*inch, height=4.5*inch).drawOn(c, 0, 10*inch)

# insert textbox with daily summary to right of plot - use textObject 
        # set text origin 6.25 from left, .9 from top (inches)
# no response wheel under daily wheel, same size
# word "No Response" next to plot 
# break
c.showPage()


# insert catch trial wheel trace plot top left 
# insert textbox to right of plot with catch trial counts
# insert session plot - takes up entire bottom half, is already perfect size 
# break
c.showPage()

# insert frame dist plot in upper left 1/6 
# insert frame intervals plot in upper right 1/6 (same size)
# insert wheel pos dist plot underneath 
# break
c.showPage()


# insert qVio sum plot top left 2/3s
# insert textbox in top right 1/3 with Qvios and max
# insert qVio count below qVio sum, same size 
# save 

c.showPage()
c.save()















