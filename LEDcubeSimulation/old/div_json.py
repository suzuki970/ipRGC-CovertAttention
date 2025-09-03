# -*- coding: utf-8 -*-
"""
Created on Wed Mar  8 09:26:47 2023

@author: NTT
"""


from LightSource import LightSource
import numpy as np
import pandas as pd
import os
import json
from multiprocessing import Pool
from multiprocessing import Process, Queue
from tqdm import tqdm

fName = "data_LEDCube_20230309x28y26ipRGC88v10"
f = open(fName+".json")
dfAll = json.load(f)
f.close()

div=1000
for i in np.arange(len(dfAll["LEDs"])/div-1):
    tmp_dfAll = {}
    tmp_dfAll["cfg"] = dfAll["cfg"]
    for mmName in list(dfAll.keys()):
        if mmName != "cfg":
            tmp_dfAll[mmName] = dfAll[mmName][int(i*1000):int((i+1)*1000)]
    
    with open(os.path.join(fName+"_" + str(int(i))+".json"),"w") as f:
        json.dump(tmp_dfAll,f)

tmp_dfAll = {}
tmp_dfAll["cfg"] = dfAll["cfg"]
for mmName in list(dfAll.keys()):
    if mmName != "cfg":
        tmp_dfAll[mmName] = dfAll[mmName][int((i+1)*1000):]
    
with open(os.path.join(fName+"_" + str(int(i+1))+".json"),"w") as f:
    json.dump(tmp_dfAll,f)