# -*- coding: utf-8 -*-
"""
Created on Mon Aug 12 12:36:41 2019

@author: svc_ccg
"""
"""
Script that plots the performance of individual mice over time.  
For the position task, Produces 2 separate plots:  1 includes percent correct by side and no-gos.  
The other has no response trials and the direction turned for no-go trials.

For the orientation task, returns a single plot with all information (no no-go trials)

"""


import h5py
import fileIO
import numpy as np
from performanceData import performance_data

f = fileIO.getFile(rootDir=r'\\allen\programs\braintv\workgroups\nc-ophys\corbettb\Masking')
d = h5py.File(f)

performance_data(mouse='460312', ignoreRepeats=True)
