# -*- coding: utf-8 -*-
"""
Created on Tue Feb 26 15:41:00 2019

@author: Eric
"""



import numpy as np   
import os
from dateutil.parser import parse
import pandas as pd
import datetime
import warnings
os.chdir(r'C:\Users\Eric\Documents\GitHub\Flux_Processing_Code')       
import LTAR_QAQC_Online as LLT
import AF_Rename as AF

info_file = r'C:\Users\Eric\Desktop\PyScripts\Flux_Processing_Code\\Inputs_Driver.csv'
Data = pd.read_csv(r'C:\Users\Eric\Desktop\LTAR\LTAR_National_Projects\PhenologyInitiative\EC Data\Processed\LTAR_EC_UMRB_morrissouth_20170609_20181001.csv',header = 1, skiprows=[2], index_col = 'TimeStamp')
Data.index = pd.to_datetime(Data.index)
print('******Formatting for AmeriFlux******')
AF_File='C:\\Users\\Eric\\Desktop\\UMRB_morrissouth_LTAR_Pheno_'
AF_Cols='C:\\Users\\Eric\\Desktop\\PyScripts\\Flux_Processing_Code\\AF_EP_EF_Column_Renames.csv'

Data = LLT.indx_fill(Data, '30min')

AF.AmeriFlux_Rename(Data, AF_File, 'EPro', AF_Cols)
