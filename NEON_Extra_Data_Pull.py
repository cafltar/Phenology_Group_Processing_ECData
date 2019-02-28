# -*- coding: utf-8 -*-
"""
Created on Thu Dec 13 15:08:15 2018

@author: Eric Russell
Dept. Civil and Environmental Engineering
Washington State University
eric.s.russell@wsu.edu


"""

import pandas as pd
import glob
import numpy as np

def indx_fill(df):   
    df.index = pd.to_datetime(df.index)
        # Sort index in case it came in out of order, a possibility depending on filenames and naming scheme
    df = df.sort_index()
        # Remove any duplicate times, can occur if files from mixed sources and have overlapping endpoints
    df = df[~df.index.duplicated(keep='first')]
        # Fill in missing times due to tower being down and pad dataframe to midnight of the first and last day
    idx = pd.date_range(df.index[0].floor('D'),df.index[len(df.index)-1].ceil('D'),freq = '30min')
    df = df.reindex(idx, fill_value=np.NaN)
    return df

def Fast_Read(filenames):
    if len(filenames) == 0:
        print('No Files in directory, check the path name.')
        return  # 'exit' function and return error
    else:
        #Initialize dataframe used within function
        Final = [];Final = pd.DataFrame(Final)
        for k in range (0,len(filenames)):
            #Read in data and concat to one dataframe; no processing until data all read in
            df = pd.read_csv(filenames[k],index_col = 'startDateTime',header= 0,low_memory=False)
            Final = pd.concat([Final,df])
        # Convert time index
        Out = indx_fill(Final)
    return Out # Return dataframe to main function.    

#%%
Cols = pd.read_csv(r'C:\*\NEON_Met_Data_Cols.csv',header=0)
fnames =glob.glob(r'C:\*\*.csv')
Precip = Fast_Read(fnames)
fnames = glob.glob(r'C:\*\*.csv')
par = Fast_Read(fnames)
fnames =glob.glob(r'C:\*\*.csv')
rad_net = Fast_Read(fnames)
fnames =glob.glob(r'C:\*\*.csv')
RH = Fast_Read(fnames)
data = []; data= pd.DataFrame(data, RH.index)
data = pd.concat([Precip,par,rad_net,RH],axis = 1, sort = True)

cls = data.columns 
s = cls.isin(Cols['Keep'])
data = data.drop(data[cls[~s]],axis = 1)


data.to_csv(r'C:\*\*.csv')