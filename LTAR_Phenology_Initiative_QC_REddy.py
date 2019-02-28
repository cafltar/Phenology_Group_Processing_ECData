# -*- coding: utf-8 -*-
"""
Created on Mon Oct  1 16:22:52 2018

@author: Eric Russell
Laboratory for Atmospheric Research
Dept. Civil and Environ. Engineering
Washington State University
eric.s.russell@wsu.edu

For use with the PhenoCam Initiative to prep data for the gap-filling into REddyProc 

"""
import pandas as pd
import glob
import os
import numpy as np
import datetime
import warnings
# Change this path to the directory where the LTAR_Flux_QC.py file is located
os.chdir(r'C:\*\LTAR_Phenology_Data_Processing')       
import LTAR_Flux_QC as LLT
import Reddy_Format as REF


files = glob.glob(r'C:\*\*.csv') #Directory or file name with file names here
# File with upper and lower limits for the flux values for each site based on visual inspection of each dataset
QC = pd.read_csv(r'C:\*\QC_Limits_List.csv',header = 0, index_col = 'Site')
for K in range (0,len(files)):
#Read in data and concat to one dataframe; no processing until data all read in - assumes data is from AmeriFlux or in the format that was defined by the group for data requests
    df = pd.read_csv(files[K],header= 0,sep=',',low_memory=False)
    dt = []
    nme = files[K][100:-4] # These values change with filepath; still need to de-hardcode this value
    Site = ''.join(filter(str.isalpha, files[K][108:111])) # These values change with filepath; still need to de-hardcode this value; grabs the 3-letter site abbreviation I use to ID site sets
    if '/' in str(df['TIMESTAMP_START'][0]):
        df.index = pd.to_datetime(df['TIMESTAMP_START'])
    else: # Convert timestamp to time-index for easier use
        for k in range (0,len(df)):
            Y =  str(int(df['TIMESTAMP_START'][k]))[0:4]
            M =  str(int(df['TIMESTAMP_START'][k]))[4:6]  
            D =  str(int(df['TIMESTAMP_START'][k]))[6:8]
            hh = str(int(df['TIMESTAMP_START'][k]))[8:10] 
            mm = str(int(df['TIMESTAMP_START'][k]))[10:12]
            dt.append(Y+'-'+M+'-'+D+' '+hh+':'+mm)
        dt = pd.DataFrame(dt);df.index = dt[0]
        df.index=pd.to_datetime(df.index) # Time-based index        
        df = df.astype(float)
    df = LLT.indx_fill(df,'30min') # Fill in and missing half-hours in the dataset to have a continuous data set from start time to end.
    df = df['2017-01-01':'2018-01-01'] # Limit data to just calendar year 2017
    #%%
#    Site = 'JOR' # If need to define specific site
    data_qc, data_flags = LLT.Grade_cs(df, QC, Site, site=True) #QC flux data
    sel = []
    #QA/QC and format the meteorology data needed for the gap-filling processing; see the processing notes for details on how this works
    if len(data_qc.filter(like='RH_').columns) >0:
        print('Multiple RH columns')
        for k in range (0,len(data_qc.filter(like='RH_').columns)):
            sel = data_qc.filter(like='RH_').columns
            data_qc[sel[k]][data_qc[sel[k]]>101] = np.NaN
            data_qc[sel[k]][data_qc[sel[k]]<0] = np.NaN
    if len(sel)>0:
        data_qc['RH'] = data_qc[sel].mean(axis=1)
        del sel
    if len(data_qc.filter(like='TA_').columns) >0:
        print('Multiple TA columns')
        sel = data_qc.filter(like='TA_').columns
        if len(sel)>0:
            data_qc['TA'] = data_qc[sel].mean(axis=1)
        del sel
    qn = (data_qc['TA']>150)&(data_qc['TA']<400) #Check to seee if temperature is in Kelvin or not
    data_qc['TA'][qn] = data_qc['TA'][qn] - 273.15 # Convert temperature to Celsius
    data_qc['TA'][data_qc['TA']<-500] = np.NaN
    if len(data_qc.filter(like='VPD').columns) == 0:
        Es = 0.61121*np.exp((18.678-(data_qc['TA']/234.5))*(data_qc['TA']/(257.14+data_qc['TA']))) # Calculates saturation vapor pressure for VPD calculation
        E = (data_qc['RH']/100) * Es
        data_qc['VPD'] = Es - E
        print('Calculated VPD')
    else: data_qc['VPD'] = data_qc[data_qc.filter(like='VPD').columns]; print('Renamed to VPD')
    if Site == 'CAF': #Specific unit conversion for the CAF sites for this work
        data_qc['VPD'] = data_qc['VPD']/1000
        data_qc['PA'] = data_qc['PA']/1000
        print('Convert CAF to kPa')
    data_qc['VPD'][data_qc['VPD']>35] = np.NaN
    if 'SW_IN' not in data_qc.columns:
        data_qc['SW_IN'] = data_qc['PPFD_IN']/2.1
        data_qc['SW_IN'][data_qc['SW_IN']< -100] = np.NaN
    s = data_qc.index[0]; ss = s
    s+= datetime.timedelta(days=5)
    with warnings.catch_warnings(): #Despike function for turbulent fluxes
        warnings.simplefilter("ignore", category=RuntimeWarning)
        FC = LLT.Despike_7(s,ss,data_qc['FC'].astype(float),'FC',5,3)
        LE = LLT.Despike_7(s,ss,data_qc['LE'].astype(float),'LE',5,3)
        H = LLT.Despike_7(s,ss,data_qc['H'].astype(float),'H',5,3)
        
    data_qc['LE'] = data_qc['LE'][LE['LE']] 
    data_qc['H'] = data_qc['H'][H['H']] 
    data_qc['FC'] = data_qc['FC'][FC['FC']] 
    FileName = 'C:\\*\\L2_QC_Gapped_'+nme+'.txt'
    REF.REddy_Format(data_qc, FileName,'Start_AF') # Function that formats the data into the format needed for REddyProc and outputs the data
    print('**********Completed '+FileName[72:]+'**********')
    df = [];data_qc = []
    
