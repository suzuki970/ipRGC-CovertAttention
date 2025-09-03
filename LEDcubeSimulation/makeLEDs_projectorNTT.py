# -*- coding: utf-8 -*-
"""
Created on Mon Nov 14 15:46:34 2022

@author: NTT
"""


import numpy as np
import matplotlib.pyplot as plt
import json
import os
import pandas as pd
import matplotlib
import seaborn as sns        
from LightSource import LightSource,showSpectra
import glob
 
from scipy import interpolate
from pre_processing_cls import getNearestValue

matplotlib.rcParams['pdf.fonttype'] = 42
matplotlib.rcParams['ps.fonttype'] = 42

sns.set()
sns.set_style("whitegrid")
sns.set_palette("Set2")

#%%

cfg = {
    'numOfLEDs': [1,2,3,4,5,6],
    'winlambda' :[380,780],
    # 'Y'    :3,
    'Y'    :1.65,
    'maxoutPw' : 255,
    'rod' : np.linspace(0,0.001,10, endpoint=True),
    'ipRGC' : np.linspace(1,1000,2000, endpoint=True),
    "visualization":False,
    "VISUAL_ANGLE":2,
    "projector":True,
    "plus":True
    }

cfg["outPw"] = 120
cfg["x"] = 0.40053
cfg["y"] = 0.25057

# cfg["outPw"] = 130
# cfg["x"] = 0.30599
# cfg["y"] = 0.21216

# cfg["outPw"] = 120
# cfg["x"] = 0.2988
# cfg["y"] = 0.24595

# cfg["outPw"] = 130
# cfg["x"] = 0.29443
# cfg["y"] = 0.30977

# cfg["outPw"] = 130
# cfg["x"] = 0.28432
# cfg["y"] = 0.25577

# cfg["outPw"] = 130
# cfg["x"] = 0.26772
# cfg["y"] = 0.28168

LEDCube = LightSource(cfg)

res = LEDCube.seekCombinations()
res_val = LEDCube.validation(res.copy(),"projector")

res_val = LEDCube.getMinMax(res.copy(),"ipRGC")

# LEDCube.saveData(res_val)


#%%

# ind=np.array(np.linspace(0,len(res["coeff"]),6),dtype="int")

# res_selected=res.copy()

# for mm in list(res.keys()):
#     res_selected[mm] = [d for i,d in enumerate(res_selected[mm]) if i in ind]

# LEDCube.saveData(res_selected)

#%%

dr1 = np.arange(380,781)
cl_func = LEDCube.getXYZfunc()

tmp_dat = np.array(LEDCube.showProjectorSpectra(3))

import matplotlib.cm as cm

plt.figure()
for i in range(tmp_dat.shape[1]):
    plt.plot(dr1, tmp_dat[:,i], linestyle='solid' , color=cm.Blues(i/tmp_dat.shape[1]))
   
# plt.plot(dr1, tmp_dat[:,], linestyle='solid' , color=cm.Blues(i/tmp_dat.shape[1]))
# plt.plot(dr1, å, linestyle='solid' , color=cm.Blues(i/tmp_dat.shape[1]))
   
# plt.figure()
# for i in range(tmp_dat.shape[1]):
#     # plt.plot(i, np.sum(tmp_dat[:,i]*cl_func["Y"]), 'o', color=cm.Blues(i/tmp_dat.shape[1]))
#     plt.plot(i, np.max(tmp_dat[:,i]), 'o', color=cm.Blues(i/tmp_dat.shape[1]))


# res_val = LEDCube.validation(res,"projector")

# # res_val = LEDCube.optimizeLEDs(res,"projector")

# if cfg["visualization"]:
#     tmp=LEDCube.showMeasLightSummary("projector")

# tmp = []
# for yxy in res_val["corrected_Yxy"]:
#     tmp.append((cfg['x']-yxy[1])**2 + (cfg['y']-yxy[2])**2)

# for mm in list(res_val.keys()):
#     res[mm] = [d for i,d in enumerate(res_val[mm]) if i == np.argmin(tmp)]
        
# # LEDCube.saveData(res)

# targetNum=-1
# a=LEDCube.getLight(res_val["LEDs"][targetNum],res_val["corrected_coeff"][targetNum])

# plt.plot(res_val["corrected_spectrum"][targetNum])


#%%
# plt.figure()
# for xy in res_val["corrected_Yxy"]:
#     plt.plot(xy[1],xy[2],'o')

# plt.plot(cfg['x'],cfg['y'],'ro')

        
# tmp = []
# for yxy in res_val["corrected_Yxy"]:
#     tmp.append((cfg['x']-yxy[1])**2 + (cfg['y']-yxy[2])**2)
# candi = np.argmin(tmp)

# candi = [0, -1]

# for mmName in list(res_val.keys()):
#     res_val[mmName] = [res_val[mmName][candi]]

# res_val = LEDCube.getMinMax(res_val,"ipRGC")


# #%%
# ipRGC   = LEDCube.getipRGCfunc()
# rod   = LEDCube.getRodfunc()
# xyz   = LEDCube.getXYZfunc()


# # plt.plot(rod["lambda"],rod["rod"])
# # plt.plot(rod["lambda"],xyz["Y"])

# plt.figure(figsize=(8,3))

# for iCand in np.arange(len(res_val["lambda"])):
    
#     plt.subplot(1,3, 1)
#     plt.plot(res_val["lambda"][iCand],np.array(res_val["spectrum"][iCand]).sum(axis=0),label = str(iCand))
    
#     plt.subplot(1,3, 2)
#     plt.plot(res_val["lambda"][iCand],np.array(res_val["spectrum"][iCand]).sum(axis=0)*ipRGC["ipRGC"],label = str(iCand))
    
#     plt.subplot(1,3, 3)
#     plt.plot(res_val["lambda"][iCand],np.array(res_val["spectrum"][iCand]).sum(axis=0)*rod["rod"],label = str(iCand))
    
#     print(np.sum(np.array(res_val["spectrum"][iCand]).sum(axis=0)*rod["rod"].values))
#     # ,label="calcurated")
#     # plt.plot(res_val["lambda"][iCand],np.array(res_val["corrected_spectrum"][iCand]))
#     # ,label="corrected")
#     # plt.legend()
    
# # plt.xlabel("wavelength[nm]")
# # plt.ylabel("radiance[W・sr-1・m-2]")
# # plt.legend() 

# # plt.savefig("./candidate.pdf")

