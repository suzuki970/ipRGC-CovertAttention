#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 25 18:47:43 2024

@author: yutasuzuki
"""


import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
import json
import datetime
import math
from scipy.stats import norm
from multiprocessing import Pool
from LightSource import LightSource,xyzTolab,labToxyz
import tqdm

cfg = {
    'numOfLEDs': [1,2,3,4,5,6],
    'winlambda' :[380,780],
    # 'Y'    :3,
    'Y'    :np.linspace(0.1,10,100, endpoint=True),
    'maxoutPw' : 255, # 100%
    'rod' : np.linspace(0,0.01,10, endpoint=True),
    'ipRGC' : np.linspace(0,1000,1000, endpoint=True),
    "visualization":False,
    "VISUAL_ANGLE":2,
    "projector":True,
    # "plus":True
    "plus":False
    }


cfg["outPw"] = 200
cfg["x"] = 0.3127
cfg["y"] = 0.3290

# cfg["Y"] = 5

# LEDCube = LightSource(cfg)
# res = LEDCube.seekCombinations()
# res = LEDCube.validation(res.copy(),"projector")

#%%

def run(x,y,Y):
    
    cfg["x"] = x
    cfg["y"] = y
    cfg["Y"] = Y
   
    LEDCube = LightSource(cfg)
    res = LEDCube.seekCombinations()
    f=[]
    
    if len(res["ipRGC"]) > 0:
        res = LEDCube.validation(res.copy(),"projector")
        
    # if len(res["ipRGC"]) > 0:
        # tmp = np.array(res["corrected_Yxy"])
        # tmp[:,1] = abs(tmp[:,1] - cfg["x"])
        # tmp[:,2] = abs(tmp[:,2] - cfg["y"])
        # tmp[:,0] = tmp[:,1]  + tmp[:,2]
        # candi = np.argmin(tmp[:,0])
    
        # tmp = []
        # for yxy in res["corrected_Yxy"]:
        #     tmp.append((cfg['x']-yxy[1])**2 + (cfg['y']-yxy[2])**2)
        # candi = np.argmin(tmp)

        # for mmName in list(res.keys()):
        #     res[mmName] = [res[mmName][candi]]
    
        f = pd.DataFrame(
            {"Y":Y, 
             "ratio":round(res["ipRGC"][-1] / res["ipRGC"][0],4),
             },index=[0])

    return f


#%%   
    
if __name__ == '__main__':
         
    LEDCube = LightSource(cfg)

    #%% seek combinations of LED
    nLength = 1
    
    theta_condi = np.arange(nLength,nLength*200,nLength)
    candidate = []
    
    for y in cfg["Y"]:
        candidate.append([cfg["x"], cfg["y"],y])
    
    candidate = tuple([tuple([e[0],e[1],e[2]]) for e in candidate])

    
    #%% seek combination
    with Pool(8) as p:
        res = p.starmap(run, candidate)
    
    res = pd.concat(res)
    
    # cfg["Y"] = res[res["ratio"]==res["ratio"].max()]["Y"].values[0]
    cfg["Y"] = 4.2

    LEDCube = LightSource(cfg)
    res = LEDCube.seekCombinations()
    
    res = LEDCube.validation(res.copy(),"projector")
    res = LEDCube.getMinMax(res,"corrected_ipRGC")

   
    #%% save data
    LEDCube.saveData(res)
