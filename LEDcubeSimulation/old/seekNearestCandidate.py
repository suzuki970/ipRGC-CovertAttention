#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov  1 10:43:09 2022

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
    # 'Y'    :1.65,
    'Y'    :1.2,
    'maxoutPw' : 255, # 100%
    'rod' : np.linspace(0,0.01,10, endpoint=True),
    # 'ipRGC' : np.linspace(0,1000,1000, endpoint=True),
    'ipRGC' : np.linspace(1,1000,2000, endpoint=True),
    "visualization":False,
    "VISUAL_ANGLE":2,
    "projector":True,
    # "plus":True
    "plus":False
    }

# cfg["outPw"] = 200
# cfg["x"] = 0.40053
# cfg["y"] = 0.25057

cfg["outPw"] = 120
cfg["outPw"] = 100
cfg["x"] = 0.40053
cfg["y"] = 0.25057


# if cfg["plus"]:
#     cfg["ipRGC"] = np.arange(373,374,1)
#     # cfg["ipRGC"] = np.arange(123,124,1)
# else:
# cfg["ipRGC"] = np.arange(169,170,1)
cfg["ipRGC"] = np.arange(109,110,1)
#     # cfg["ipRGC"] = np.arange(71,72,1)


#%%

def run(x,y):
    
    cfg["x"] = x
    cfg["y"] = y
   
    LEDCube = LightSource(cfg)
    res = LEDCube.seekCombinations()
    
    if len(res["ipRGC"]) > 0:
        res = LEDCube.validation(res.copy(),"projector")
        
    if len(res["ipRGC"]) > 0:
        # tmp = np.array(res["corrected_Yxy"])
        # tmp[:,1] = abs(tmp[:,1] - cfg["x"])
        # tmp[:,2] = abs(tmp[:,2] - cfg["y"])
        # tmp[:,0] = tmp[:,1]  + tmp[:,2]
        # candi = np.argmin(tmp[:,0])
    
        tmp = []
        for yxy in res["corrected_Yxy"]:
            tmp.append((cfg['x']-yxy[1])**2 + (cfg['y']-yxy[2])**2)
        candi = np.argmin(tmp)

        for mmName in list(res.keys()):
            res[mmName] = [res[mmName][candi]]
    
    return res


#%%   
    
if __name__ == '__main__':
         
    LEDCube = LightSource(cfg)
    res = LEDCube.seekCombinations()
    
    if len(res["ipRGC"]) > 0:
        res = LEDCube.validation(res.copy(),"projector")
    #     # res = LEDCube.rejectOutlier(res.copy())
    #     if not cfg["plus"]:
            
    #         tmp = []
    #         for yxy in res["corrected_Yxy"]:
    #             tmp.append((cfg['x']-yxy[1])**2 + (cfg['y']-yxy[2])**2)
    #         candi = np.argmin(tmp)

    #         for mmName in list(res.keys()):
    #             res[mmName] = [res[mmName][candi]]
            
    base_lab = np.array(xyzTolab(res["XYZ"][:1])).reshape(-1)
    
    
    #%% seek combinations of LED
    nLength = 2
    
    theta_condi = np.arange(nLength,nLength*200,nLength)
    
    lab = [[0,0]]
    dist = [0]
    # for i,r in enumerate(np.arange(0.1, 3, 0.1)):
    # for i,r in enumerate(np.arange(0.1, 3, 0.5)):
    # for i,r in enumerate(np.arange(0.1, 3, 0.4)):
    # for i,r in enumerate(np.linspace(0.1, 3, 2)):
    for i,r in enumerate(np.linspace(1, 3, 2)):
    
        for theta in np.arange(0,2*np.pi,np.pi/theta_condi[i]):
            tmp_x = np.round(r*math.sin(theta),3)
            tmp_y = np.round(r*math.cos(theta),3)
    
            lab.append([tmp_x,tmp_y])
            
            dist.append(i+1)
     
    plt.plot(np.array(lab)[:,0],np.array(lab)[:,1],'o')
    
    candidate = []
    for shift_ab in lab:
        # biased_lab = [[base_lab[0], base_lab[1]+shift_ab[0]-1, base_lab[2]+shift_ab[1]-1]]
        biased_lab = [[base_lab[0], base_lab[1]+shift_ab[0], base_lab[2]+shift_ab[1]]]
        
        t = labToxyz(biased_lab)[0]
        tmp_yxy = np.round([t[1],(t[0]/sum(t)),(t[1]/sum(t))],5)
        candidate.append(tmp_yxy.tolist())
    
    # plt.plot(np.array(candidate)[:,1],np.array(candidate)[:,2],'o')
    
    candidate = tuple([tuple([e[1],e[2]]) for e in candidate])

    
    #%% seek combination
    if not cfg["plus"]:
        with Pool(8) as p:
            res = p.starmap(run, candidate)
        
        reject = []
        resAll = {}
        for mmName in list(res[0].keys()):
            resAll[mmName] = []
            
            for i,r in enumerate(res):
                
                if( mmName == list(res[0].keys())[0]) and (len(r["LEDs"])==0):
                    reject.append(i)
                    
                if len(r[mmName]) > 0:
                    resAll[mmName].append(r[mmName][0])
                    
        dist = [d for i,d in enumerate(dist) if not i in reject]
            
    else:
        resAll = res.copy()
        
    #%% show L-M contrast
    
    # resAll["L-M contrast"]=[]
    # resAll["S-(L+M) contrast"]=[]
    # resAll["dist"] = dist
    
    # for i,lms in enumerate(resAll["corrected_LMS"]):
    # # for i,lms in enumerate(resAll["LMS"]):
    #     resAll["L-M contrast"].append(np.round(lms[0]-lms[1],5))
    #     resAll["S-(L+M) contrast"].append(np.round(lms[2]-(lms[1]+lms[0]),5))
    
    # plt.figure()    
    # for (ml,lm_s) in zip(resAll["L-M contrast"],resAll["S-(L+M) contrast"]):
    #     plt.plot(ml,lm_s,'o')
    # plt.plot(resAll["L-M contrast"][0],resAll["S-(L+M) contrast"][0],'ro',markersize=10)
        
    # plt.xlabel("L-M contrast(green-red)")
    # plt.ylabel("S-(L+M) contrast(yellow-blue)")
    
    #%% show xy
    
    # import colour
    # from colour.plotting.diagrams import plot_chromaticity_diagram_CIE1931
    
    # plt.figure()
    # plot_chromaticity_diagram_CIE1931(bounding_box=(-0.1, 0.9, -0.1, 0.9), standalone=False)
   
    xy = np.array(resAll["Yxy"])
    plt.plot(xy[:,1],xy[:,2],'bo',label = "candidate")
    
    for i in np.arange(len(xy)):
        plt.text(xy[i,1],xy[i,2], str(i+1))
        
    plt.plot(cfg['x'],cfg['y'],'ro',markersize=10,label = "target")
    plt.xlabel("x")
    plt.ylabel("y")

    plt.xlim(0.38, 0.42)
    plt.ylim(0.24, 0.26)
    plt.legend()

    plt.savefig("./light_xy.pdf")
 
    plt.figure()  
    for s in resAll["spectrum"]:
        plt.plot(np.array(s).sum(axis=0))
    
    # plt.plot(cfg['x'],cfg['y'],'ro')

    #%% show xy
    base_lab = np.array(xyzTolab(resAll["XYZ"]))
        
    resAll["Lab"] = base_lab.tolist()
    
    # resAll["corrected_Lab"] = np.array(xyzTolab(resAll["corrected_XYZ"])).tolist()
    
    resAll["cfg"] = cfg
    
    for mm in list(resAll["cfg"].keys()):
        if not isinstance(resAll["cfg"][mm],list):
            if not isinstance(resAll["cfg"][mm], int):
                if not isinstance(resAll["cfg"][mm], float):
                    if not isinstance(resAll["cfg"][mm], bool):
                        resAll["cfg"][mm] = resAll["cfg"][mm].tolist()
       
    if cfg["plus"]:
        # tmp = []
        # for yxy in resAll["corrected_Yxy"]:
        #     tmp.append((cfg['x']-yxy[1])**2 + (cfg['y']-yxy[2])**2)
        # candi = np.argmin(tmp)
        candi = 0
        for mmName in list(resAll.keys()):
            if mmName != "cfg":
                resAll[mmName] = [resAll[mmName][candi]]

    #%% save data
    LEDCube.saveData(resAll)
