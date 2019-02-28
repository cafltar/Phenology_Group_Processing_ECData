# -*- coding: utf-8 -*-
"""
Created on Fri Oct 26 09:30:07 2018

@author: Eric
"""

# -*- coding: utf-8 -*-
"""
Created on Thu Oct 25 14:51:25 2018

@author: Eric Russell
Dept. Civil and Environmental Engineering
Washington State University
eric.s.russell@wsu.edu

This script pulls out selected columns (Cols) from the NEON dataset into a pandas dataframe with predetermined column headers.
The index used is for the beginning time of the averaging period but could be changed as needed.
Data can be output or manipulated as needed once in the pandas dataframe for the users usage. 
The file names and variable names are free to be changed by the user as they see fit; this is my naming convention
This script pulls individual lists of data from the *.h5 files and not whole subsections of particular variables.
"""
import pandas as pd
import h5py
import glob
def ls_dataset(name,node):
    if isinstance(node, h5py.Dataset):
        print(node)
#list_dataset lists the names of datasets in an hdf5 file
def list_dataset(name,node):
    if isinstance(node, h5py.Dataset):
        print(name)

Cols = pd.read_csv(r'C:\*NEON_Data_IDs.csv',header=0)
fnames =glob.glob(r'C:\*.h5')
Final = []; Final = pd.DataFrame(Final, columns=[Cols['Var_Name']])
Final_m = []; Final_m = pd.DataFrame(Final)
for K in range(0,len(fnames)):
    f = h5py.File(fnames[K], 'r')
    for k in range(0,12):
        if k ==0:
            tme = serc_refl = pd.DataFrame(f[Cols['NEON'][k]][0:]['timeBgn'])
        serc_refl = pd.DataFrame(f[Cols['NEON'][k]][0:][Cols['Col_Num'][k]], columns =[Cols['Var_Name'][k]])
        Final_m[Cols['Var_Name'][k]] = serc_refl[Cols['Var_Name'][k]]
    tme = tme.astype(object)
    tme[0] = tme[0].str.decode("utf-8")
    Final_m.index = pd.to_datetime(tme[0])
    Final = pd.concat([Final,Final_m])
    Final_m = []; Final_m = pd.DataFrame(Final_m, columns=[Cols['Var_Name']])

Final.to_csv(r'C:\*\*.csv')