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
from datetime import datetime


d = dataAnalysis.import_data()

mouse_id=d['subjectName'][()]
date = d['startTime'][()].split('_')[0][-4:]
date = date[:2]+'-'+date[2:]

date = date if date[:2] in ['10','11','12'] else date[-4:]

fullDate = d['startTime'][()][:8]
titleDate = datetime.strptime(fullDate, '%Y%m%d').strftime('%A %B %d, %Y')
 

directory = r'\\allen\programs\braintv\workgroups\nc-ophys\corbettb\Masking\active_mice'
dataDir = os.path.join(os.path.join(directory, mouse_id), 'Plots/') 

c = canvas.Canvas(mouse_id + ' Daily Summary ' + date + '.pdf', pagesize=letter)

# insert "Daily Summary" at top bold, mouse id, and date 
c.setFont('Helvetica-Bold', 12)
c.drawString(2*inch, 10.5*inch, 'Daily Summary:   ')
c.setFont('Helvetica', 12)
c.drawString(3.3*inch, 10.5*inch, mouse_id + '                 ' + titleDate)


# insert daily wheel plot on left of canvas
reportlab.platypus.Image(dataDir + mouse_id + ' ' + date + '.png', 
                         width=6*inch, height=4.5*inch).drawOn(c, 0, 5.5*inch)

# no response wheel plot under daily wheel, same size

reportlab.platypus.Image(dataDir + '/Wheel Plots/No Resp Wheel/' + mouse_id + ' ' + date + ' no resp.png',
                         width=6*inch, height=4.5*inch).drawOn(c, 0, .2*inch)

# insert textbox with daily summary to right of plot - use textObject 
        # set text origin 6.25 from left, .9 from top (inches)
        # use textLines and moveCursor
textobject = c.beginText()
textobject.setTextOrigin(2*inch, 10.5*inch)
textobject.setFont('Helvetica', 12)
for stat in session_stats():
    pass
c.drawText(textobject)

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















