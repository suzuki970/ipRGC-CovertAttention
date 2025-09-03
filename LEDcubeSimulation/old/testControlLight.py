#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  9 17:27:15 2023

@author: yutasuzuki
"""

import json
import glob

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

fName = "data_LEDCube_20230313x28y26ipRGC88v2"

fileName = glob.glob(fName+"/*.json")
fileName.sort()

f = open(fileName[0])
df = json.load(f)
f.close()

resAll = {}
for mmName in list(df.keys()):
    resAll[mmName] = []
    
resAll["cfg"] = df["cfg"]

for fName in fileName:
    
    f = open(fName)
    df = json.load(f)
    f.close()

    for mmName in list(df.keys()):
        if mmName != "cfg":
            resAll[mmName] = resAll[mmName] + df[mmName]
        

#%%
plt.figure()
# plt.plot(np.array(resAll["corrected_Yxy"])[:,1],np.array(resAll["corrected_Yxy"])[:,2],'o')
plt.plot(np.array(resAll["corrected_Lab"])[:,1],np.array(resAll["corrected_Lab"])[:,2],'o')

fName = "data_LEDCube_20230309x28y26ipRGC133v10"

f = open(fName + ".json")
resAll_plus = json.load(f)
f.close()

plt.plot(np.array(resAll_plus["corrected_Lab"])[:,1],np.array(resAll_plus["corrected_Lab"])[:,2],'ro')

#%%
plt.figure()
for iCand in np.arange(len(resAll_plus["lambda"])):
    
    plt.subplot(2,2,iCand+1)
    plt.plot(resAll_plus["lambda"][iCand],np.array(resAll_plus["spectrum"][iCand]).sum(axis=0))
    plt.plot(resAll_plus["lambda"][iCand],np.array(resAll_plus["corrected_spectrum"][iCand]))
 
    
# plt.plot(np.array(resAll_plus["Lab"])[:,1],np.array(resAll_plus["Lab"])[:,2],'ro')
