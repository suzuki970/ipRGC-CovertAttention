# -*- coding: utf-8 -*-
"""
Created on Wed Mar  8 13:31:21 2023

@author: NTT
"""

import json
import glob

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

fName = "data_LEDCube_20230315x33y33ipRGC8v2.json"
# fName = "data_LEDCube_20230314x28y26ipRGC8v2.json"

f = open(fName)
dfAll = json.load(f)
f.close()

fileName = glob.glob("tmp_test/*.csv")
fileName.sort()
# fileName = fileName[-3:]
# fileName = fileName[-4:]
# fileName = fileName[:3]

winWaveLen = [380,780]
dat = []
for f in fileName:
   
   csv_input = pd.read_csv(filepath_or_buffer = f, encoding="ms932", sep=",", header=None)
   dr1 = csv_input[0].values
   
   dat.append(csv_input[1].values[(dr1 >= winWaveLen[0]) & (dr1 <= winWaveLen[1])])

   dr1 = dr1[(dr1 >= winWaveLen[0]) & (dr1 <= winWaveLen[1])]
   
#%%

plt.figure()
# plt.plot(dr1,np.array(dat).sum(axis=0),label = "measured")
plt.plot(dr1,np.array(dat).T,label = "measured")
plt.plot(dr1,dfAll["corrected_spectrum"][0],label = "calculated")

plt.figure()
plt.plot(dr1,np.array(dat).mean(axis=0),label = "measured")

plt.plot(dr1,dfAll["corrected_spectrum"][0],label = "calculated")
plt.legend()

# figCount = 1
# for calculated,corrected in zip(dfAll["spectrum"],dfAll["corrected_spectrum"]):
     
#     # plt.subplot(5,2,figCount)
    
#     # plt.plot(dr1,measured,label = "measured")
#     plt.plot(dr1,np.array(calculated).sum(axis=0),label = "calculated")
#     plt.plot(dr1,corrected,label = "corrected")
    
#     # plt.legend(bbox_to_anchor=(1.02, 1), loc='upper left', borderaxespad=0)
#     # plt.ylim([0,0.01])
#     figCount += 1