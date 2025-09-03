#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 28 14:02:32 2021

@author: yutasuzuki
"""

from LightSource import LightSource
import numpy as np
import pandas as pd
from multiprocessing import Pool
from tqdm import tqdm
from LightSource import xyzTolab,labToxyz
import math
import matplotlib.pyplot as plt


# cfg = {
#     'numOfLEDs': [1,2,3,4,5,6],
#     'winlambda' :[380,780],
#     'maxoutPw' : 255, # 100%
#     'rod' : np.linspace(0,0.01,10, endpoint=True),
#     "ipRGC" : np.arange(0,1000,10),
#     "visualization":False,
#     "VISUAL_ANGLE":10,
#     "Y":np.arange(2,7,1),
#     "projector":True
#     }

cfg = {
    # 'numOfLEDs': [1,2,3,4,5,6],
    'numOfLEDs': [1,2,3,4,5,6],
    'winlambda' :[380,780],
    'Y'    :np.arange(2,6,1),
    'maxoutPw' : 255, # 100%
    'rod' : np.linspace(0,0.01,10, endpoint=True),
    'ipRGC' : np.linspace(100,1000,2000, endpoint=True),
    "visualization":False,
    "VISUAL_ANGLE":2,
    "projector":True,
    "plus":False
    }


#%%

def run(Y,x,y):
    
    info = f'#{x:>2} '
    
    df = pd.DataFrame()
    for outPW in tqdm(np.arange(100,150,10), desc=info, position=1):
    # for outPW in tqdm(np.arange(180,190,10), desc=info, position=1):
      
        # print("######################")
        # print("x="+str(x)+",y="+str(y)+",outPw=" + str(outPW))
        cfg['x'] = x
        cfg['y'] = y
        cfg['Y'] = Y
        cfg['outPw'] = outPW
            
        LEDCube = LightSource(cfg)
      
        #%% get spectra of the LEDs embeded in LEDCube
        # dat_LED_spectrum = LEDCube.getLEDspectra()
        # sns.lineplot(x = "lambda", y = "ipRGC", data=ipRGC)
        
        #%% get XYZ values of the LEDs
        # dat_LED_XYZ = LEDCube.getXYZvalues(Y_d65,cl_func,dat_LED_spectrum,ipRGC,rod)
        
        #%% seek combinations of LED
        res_val = LEDCube.seekCombinations()
        
        # plt.plot(spectra["optimized_spectrum"][0]*rod["rod"])
        # plt.plot(spectra["optimized_spectrum"][1]*rod["rod"])
        # plt.plot(spectra["optimized_spectrum"][2]*rod["rod"])
        
        # sum(spectra["optimized_spectrum"][0]*rod["rod"])
        # sum(spectra["optimized_spectrum"][1]*rod["rod"])
        # sum(spectra["optimized_spectrum"][2]*rod["rod"])
       
        # sum(spectra["corrected_spectrum"][0]*rod["rod"])
        # sum(spectra["corrected_spectrum"][1]*rod["rod"])
        # sum(spectra["corrected_spectrum"][2]*rod["rod"])
        
        # sum(spectra["optimized_spectrum"][0]*ipRGC["ipRGC"])
        # sum(spectra["optimized_spectrum"][1]*ipRGC["ipRGC"])
        # sum(spectra["optimized_spectrum"][2]*ipRGC["ipRGC"])
        
        # res = LEDCube.seekCombinations5LEDs(dat_LED_XYZ,dat_LED_spectrum,cl_func,ipRGC,rod)
        
        # res_val = LEDCube.validation(res.copy())
        
        #%%
        # rejectNum = []
        # for iCond,(leds, coeff) in enumerate(zip(res_val["LEDs"],res_val["corrected_coeff"])):
        #     for i,led in enumerate(leds):
        #         if led != 3:
        #             if coeff[i] > 960:
        #                 rejectNum.append(iCond) 
        #                 continue

        # for mm in res_val.keys():
        #     res_val[mm] = [d for i,d in enumerate(res_val[mm]) if not i in rejectNum]
        
        #%%    
        # if len(res_val["ipRGC"]) > 1:
        #     tmp = []
        #     tmp_coeff = []
        #     for led,coeff in zip(res_val["LEDs"],res_val["corrected_coeff"]):
        #         ind = np.argwhere(np.array(led) == 3).reshape(-1)
        #         if len(ind) > 0:
        #             tmp.append(coeff[int(ind)])
        #             tmp_coeff.append([coeff[2],coeff[3]])
        #         else:
        #             tmp.append(0)
        #             tmp_coeff.append(0)

            #%% reject if coeff is impossible (>1000)
            # res_val = LEDCube.rejectOutlier(res_val)
        
        if len(res_val["ipRGC"]) > 1:
        
            #%% save data
            if cfg["visualization"]:
                LEDCube.saveData(res_val)
            
            f = pd.DataFrame(
                np.array([outPW, 
                          # round(res_val["corrected_ipRGC"][-1] / res_val["corrected_ipRGC"][0],4),
                          round(res_val["ipRGC"][-1] / res_val["ipRGC"][0],4),
                          x,
                          y,
                          # max(tmp),
                          # max(tmp_coeff[np.argmax(np.array(tmp))]),
                          Y]).reshape(1, 5),
                columns=["outPW","ipRGC","x","y",'Y'])
   
            df = pd.concat([df,f])
              
    return df

if __name__ == '__main__':
           
    x0=0.3127
    y0=0.3290

    Y = 1
    
    S = Y/y0
    X = S*x0
    Z = S-X-Y
    
    xyz = [[X,Y,Z]]
    
    wp_d65 = [[0.9504, 1.0000, 1.0888]]
    
    base_lab = np.array(xyzTolab(xyz)).reshape(-1)
    
    nLength = 2
   
    # wid = 0.5 
    wid = 6
    
    theta_condi = np.arange(nLength,1000,nLength)
    
    # lab = [[0,0]]
    # for i,r in enumerate(np.linspace(2, 20, 8)):
        
    # theta_condi = [4,6,8,12,16]
    xy=[[0,0]]
    for i,r in enumerate(np.arange(wid,150,wid)):
        # for theta in np.arange(0,2*np.pi,np.pi/8):
        for theta in np.arange(0,2*np.pi,np.pi/theta_condi[i]):
            tmp_x = np.round(r*math.sin(theta),3)
            tmp_y = np.round(r*math.cos(theta),3)
    
            xy.append([tmp_x,tmp_y])
   
    candidate = []
    for Y in cfg['Y']:
        for shift_ab in xy:
    
            biased_lab = [[base_lab[0], base_lab[1]+shift_ab[0], base_lab[2]+shift_ab[1]]]
            
            t = labToxyz(biased_lab)[0]
            tmp_yxy = np.round([Y,(t[0]/sum(t)),(t[1]/sum(t))],5)
            candidate.append(tmp_yxy.tolist())

    candidate = tuple([tuple([e[0],e[1],e[2]]) for e in candidate])
        
    from colour.plotting.diagrams import plot_chromaticity_diagram_CIE1931
    
    plt.figure()
    plot_chromaticity_diagram_CIE1931(bounding_box=(-0.1, 0.9, -0.1, 0.9), standalone=False)
  
    # plt.figure()
    plt.plot(np.array(candidate)[:,1],np.array(candidate)[:,2],'o')
 
    
    with Pool(8) as p:
        df = p.starmap(run, candidate)

    dfAll = pd.DataFrame()
    for tmp_df in df:
        dfAll = pd.concat([dfAll,tmp_df])
    
    dfAll = dfAll.reset_index()
    dfAll.to_json("./df_x"+ str(int(x0*100)) + "y" + str(int(y0*100)) + "v" + str(int(cfg["VISUAL_ANGLE"])) + ".json")
  