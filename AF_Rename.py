# -*- coding: utf-8 -*-
"""
Created on Tue Jan 29 10:30:38 2019

@author: Eric
"""

import pandas as pd
import numpy as np
import datetime
# Change this path to the directory where the LTAR_Flux_QC.py file is located
def AmeriFlux_Rename(data, outfile, Format, AF):
    AF = pd.read_csv(AF,header = 0) # File path for where the column names sit
    AM = data; cls = AM.columns # Keeping data as an unchanged variable from this point forward in case want to do more with it; can be changed
    # Using data that came from EddyPro so selected the Epro column to check column names against.
    Format = Format.upper() # Which format the initial column headers are in; 'Epro' or 'Eflux' are only accepted; must be in single quotes
    s = cls.isin(AF[Format])
    # Drop columns not in the AmeriFlux data list
    AF_Out = AM.drop(AM[cls[~s]],axis = 1)
    cls = AF_Out.columns  #Grab column headers from AF_Out after dropping unneeded columns    
# Change column header names and keep only columns that match
    for k in range (2,len(AF)):
        if AF[Format][k] in cls:
            qn = AF[Format][k] == cls
            AF_Out = AF_Out.rename(columns={cls[qn][0]:AF['AmeriFlux'][k]})
            print('Converting ',AF[Format][k],' to ',AF['AmeriFlux'][k])
# In case SW_IN not a part of the initial data set; this conversion can work
    if 'SW_IN' not in AF_Out.columns:
        AF_Out['SW_IN'] = AF_Out['PPFD_IN'].astype(float)/2.1
        AF_Out['SW_IN'][AF_Out['SW_IN']< -100] = np.NaN
#Shift time to match AmeriFlux format; can change this depending on how averaging time is assigned
    AF_Out['TIMESTAMP_END'] = AF_Out.index.shift(0, '30T')
    AF_Out['TIMESTAMP_START'] = AF_Out.index.shift(-1, '30T')    
    AF_Out['TIMESTAMP_START']= AF_Out.TIMESTAMP_START.map(lambda x: datetime.datetime.strftime(x, '%Y%m%d%H%M'))
    AF_Out['TIMESTAMP_END']= AF_Out.TIMESTAMP_END.map(lambda x: datetime.datetime.strftime(x, '%Y%m%d%H%M'))
# Format columns into a same order as in the input *.csv file because housekeeping is always good
    acl = AF['AmeriFlux']
    tt = acl[acl.isin(AF_Out.columns)]
    AF_Out_QC=AF_Out[tt]   
    
    AF_Out_QC['TAU'] = AF_Out_QC['TAU']*-1
    # use regex for better than hardcoding?
    AF_Out_QC['FC_SSITC_TEST'][(AF_Out_QC['FC_SSITC_TEST'] <= 3) & (AF_Out_QC['FC_SSITC_TEST'] >= 0)] = 0
    AF_Out_QC['FC_SSITC_TEST'][(AF_Out_QC['FC_SSITC_TEST'] >= 4) & (AF_Out_QC['FC_SSITC_TEST'] <7)] = 1
    AF_Out_QC['FC_SSITC_TEST'][AF_Out_QC['FC_SSITC_TEST'] >= 7] = 2
    
    AF_Out_QC['H_SSITC_TEST'][(AF_Out_QC['H_SSITC_TEST'] <= 3) & (AF_Out_QC['H_SSITC_TEST'] >= 0)] = 0
    AF_Out_QC['H_SSITC_TEST'][(AF_Out_QC['H_SSITC_TEST'] >= 4) & (AF_Out_QC['H_SSITC_TEST'] <7)] = 1
    AF_Out_QC['H_SSITC_TEST'][AF_Out_QC['H_SSITC_TEST'] >= 7] = 2
    
    AF_Out_QC['LE_SSITC_TEST'][(AF_Out_QC['LE_SSITC_TEST'] <= 3) & (AF_Out_QC['LE_SSITC_TEST'] >= 0)] = 0
    AF_Out_QC['LE_SSITC_TEST'][(AF_Out_QC['LE_SSITC_TEST'] >= 4) & (AF_Out_QC['LE_SSITC_TEST'] <7)] = 1
    AF_Out_QC['LE_SSITC_TEST'][AF_Out_QC['LE_SSITC_TEST'] >= 7] = 2
    
    AF_Out_QC['TAU_SSITC_TEST'][(AF_Out_QC['TAU_SSITC_TEST'] <= 3) & (AF_Out_QC['TAU_SSITC_TEST'] >= 0)] = 0
    AF_Out_QC['TAU_SSITC_TEST'][(AF_Out_QC['TAU_SSITC_TEST'] >= 4) & (AF_Out_QC['TAU_SSITC_TEST'] <7)] = 1
    AF_Out_QC['TAU_SSITC_TEST'][AF_Out_QC['TAU_SSITC_TEST'] >= 7] = 2
    
    AF_Out_QC = AF_Out_QC.fillna(-9999)
    zz = AF_Out_QC == 'NAN'
    AF_Out_QC[zz] = np.nan
    AF_Out_QC = AF_Out_QC.fillna(-9999)
# Ameriflux uses -9999 to represent missing data so convert NaN to -9999
    AF_Out_QC['TAU_SSITC_TEST'] = AF_Out_QC['TAU_SSITC_TEST'].astype(int)
    AF_Out_QC['LE_SSITC_TEST'] = AF_Out_QC['LE_SSITC_TEST'].astype(int)
    AF_Out_QC['H_SSITC_TEST'] = AF_Out_QC['H_SSITC_TEST'].astype(int)
    AF_Out_QC['FC_SSITC_TEST'] = AF_Out_QC['FC_SSITC_TEST'].astype(int)
#%%
# Change output directory to whatever it needs to be
    cols = AF_Out_QC.columns.tolist()
    cols.insert(0,cols.pop(cols.index('TIMESTAMP_START')))
    cols.insert(1,cols.pop(cols.index('TIMESTAMP_END')))
    AF_Out_QC = AF_Out_QC.reindex(columns = cols) 
    outfile = outfile+str(AF_Out['TIMESTAMP_START'][0])+'_'+str(AF_Out['TIMESTAMP_END'][-1])+'.csv'
    AF_Out_QC.to_csv(outfile, index = False)
