# -*- coding: utf-8 -*-
"""
Created on Mon Nov 12 14:48:20 2018

@author: Eric Russel
LAR
CEE
WSU
Formats output from the gap-filling code into 30-minute and daily values of the ecosystem exchange and meteorology values
Does not include any wind data or meteorology data that is not used within the gap-filling code (Tair, RH, Rg [SW_IN], H, LE, and Fc)
Initially developed for use with the Phenology Iniative
"""

# -*- coding: utf-8 -*-
"""T
Created on Thu Oct 11 15:26:43 2018

@author: Eric
"""

import pandas as pd
import numpy as np
import glob
import calendar

def JulianDate_to_MMDDYYY(y,jd):
    month = 1
    while jd - calendar.monthrange(y,month)[1] > 0 and month <= 12:
        jd = jd - calendar.monthrange(y,month)[1]
        month = month + 1
    return month,jd,y
Path = 'C:\\*\\Final_Data\\'
files = glob.glob('C:\\*\\Gap-Filled\\*.csv')
for K in range(0, len(files)):
    OutName_Daily = Path+files[K][67:-4]+'_Summary_Prelim_Daily.csv'
    OutName_30Mins = Path+files[K][67:-4]+'_Summary_Prelim_30Mins.csv'
    datae = pd.read_csv(files[K],header=0)
    Y = datae['Year']
    D = datae['DoY']
    H = datae['Hour']
    half = H % 1
    idx = []
    for i in range(0,len(Y)):
        month, jd, y = JulianDate_to_MMDDYYY(Y[i],D[i])
        if half[i] == 0:
            M = '00'
        else: M = '30'
        dt = str(y)+'-'+str(month)+'-'+str(jd)+' '+str(int(H[i]))+':'+str(M)
        idx.append(dt)
    
    datae.index = idx
    datae.index = pd.to_datetime(datae.index)

    datae = datae['2017-01-01':'2018-01-01']

# Columns reduction and renaming here; try to match previous column names

    cols = pd.read_csv('C:\\Users\\Eric\\Desktop\\LTAR\\Updated_Fluxes\\L3_GapFilled\\Rename_Template.csv',header=0)
    cls = datae.columns # Keeping data as an unchanged variable from this point forward in case want to do more with it; can be changed
# Using data that came from EddyPro so selected the Epro column to check column names against.
    s = cls.isin(cols['REDDY'])

    data_out = datae.drop(datae[cls[~s]],axis = 1)
    cls = data_out.columns  #Grab column headers from AF_Out after dropping unneeded columns
# Change column header names and keep only columns that match
    for k in range (0,len(cols)):
        if cols['REDDY'][k] in cls:
            qn = cols['REDDY'][k] == cls
            data_out = data_out.rename(columns={cls[qn][0]:cols['Final'][k]})

    L_v = (2501000 - 2370*(data_out['Tair_Gapfilled_L3']))   
    Con = (1/L_v)*(30*60)
    data_out['ET_Gapfilled_L3'] = data_out['LE_Gapfilled_L3']*Con
    data_out['ET_Gapfilled_SD'] = data_out['LE_Gapfilled_SD']*Con
    Data_30 = data_out
    units = cols['Units_30'] 
# Adjust header to have both units and column names; more housekeeping
    array_30 = [np.array(cols['Final'][0:40]),np.array(units[0:40])]                                 

    CE_S = data_out.resample('D').sum()
    CE_M = data_out.resample('D').mean()
    CE_Max = data_out.resample('D').max()
    CE_Min = data_out.resample('D').min()
#%%
    Full = []; Full = pd.DataFrame(Full)
    Full = CE_M.join(CE_S,rsuffix='_Sum').join(CE_Max,rsuffix='_Max').join(CE_Min,rsuffix='_Min')
    Full['Fc_Gapfilled_L3_Sum_Carbon'] =Full['Fc_Gapfilled_L3_Sum']*12*10**(-6)*60*30 
    Full['GPP_L3_Sum_Carbon'] =Full['GPP_L3_Sum']*12*10**(-6)*60*30
    Full['Reco_L3_Sum_Carbon'] =Full['Reco_L3_Sum']*12*10**(-6)*60*30
# Drop unwanted columns
    cls = Full.columns 
    s = cls.isin(cols['Keepers'])
    data_out = Full.drop(Full[cls[~s]],axis = 1)
    units = cols['Units']

# Adjust header to have both units and column names
#    arrays = [np.array(cols['Keepers']),np.array(units)]                                 
#    data_out.columns = arrays
    data_out.to_csv(OutName_Daily)
#    Data_30.columns = array_30
    Data_30.to_csv(OutName_30Mins)
    print(OutName_Daily)