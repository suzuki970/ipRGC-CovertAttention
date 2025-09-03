# -*- coding: utf-8 -*-
"""
Created on Mon Oct  3 17:45:31 2022

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


f = open("df_x31y32v2.json")
# f = open("./df_x31y32v2.json")
# f = open("./df_x32y26v10.json")
dfAll = pd.read_json(f)
f.close()

dfAll = dfAll[dfAll["Y"]==3]
dfAll = dfAll[dfAll["x"]>0.3]
dfAll = dfAll[dfAll["x"]<0.4]
dfAll = dfAll[dfAll["y"]>0.25]
dfAll = dfAll[dfAll["ipRGC"]>1.]

# df_s = dfAll.sort_values('ipRGC', ascending=False)

cfg = {
    'numOfLEDs': [1,2,3,4,5,6,7,8,9,10,11,12],
    'winlambda' :[380,780],
    # 'outPw'    : int(df_s["outPW"][selectedNum:selectedNum+1].values),
    # 'x'    : float(df_s["x"][selectedNum:selectedNum+1].values),
    # 'y'    : float(df_s["y"][selectedNum:selectedNum+1].values),
    'maxoutPw' : 1000, # 100%
    'rod' : np.linspace(0,0.01,10, endpoint=True),
    # 'ipRGC' : np.arange(0,0.5,0.02),
    "ipRGC" : np.arange(0,1000,10),
    "visualization":True,
    "VISUAL_ANGLE":10
    }

# cfg['x']=0.32
# cfg['y']=0.26
# cfg['outPw']=440
    
    
#%%
def run():

    LEDCube = LightSource(cfg)
               
    #%% seek combinations of LED
    res = LEDCube.seekCombinations()
    
    #%% validation
    res_val = LEDCube.validation(res.copy())
    
    #%% reject outlier
    res_val = LEDCube.rejectOutlier(res_val.copy())
    
    # plt.plot(np.array(res["spectrum"][-1]).sum(axis=0))
    # plt.plot(np.array(res["spectrum"][-1])[0])
    
    #%% reject outlier by optimzed data
    # res_opt = LEDCube.rejectOutlier(res_opt.copy(),"optimized_Yxy")
   
    #%% reject outlier
    # resMin = LEDCube.getMinMax(res_opt.copy(),"corrected_ipRGC")
    
    resMin = LEDCube.getMinMax(res_val.copy(),"corrected_ipRGC")
    
    #%% optimazation
    res_opt = LEDCube.optimzeLEDs(resMin.copy())


    # plt.plot(np.array(res_opt["spectrum"][0]).sum(axis=0))
    # plt.plot(np.array(res_opt["optimized_spectrum"][0]))
    
    # filePath = "/Users/yutasuzuki/GoogleDrive/PupilAnalysisToolbox/python/preprocessing/lib/LEDdata/"
    # LEDs = []
    # for iLED in np.arange(1,max(cfg['numOfLEDs'])+1):
    #     LEDs.append(pickle.load(open(filePath + "LED/LED"+str(iLED)+".pkl", 'rb')))
    
    # waveL = np.arange(res["lambda"][0][0],res["lambda"][0][-1]+1)
    
    # tmp = []
    # for iCoeff,iLED,iSpectrum in tqdm(zip(res['coeff'],res['LEDs'],res["spectrum"])):
    #     print(iCoeff)
    #     # yy = interpolate.PchipInterpolator(res["lambda"][0], np.array(iSpectrum).sum(axis=0))
     
    #     result = minimize(f_optLEDs, np.array(iCoeff), 
    #                       method="Nelder-Mead", 
    #                       bounds=((0, 1000),(0, 1000),(0, 1000),(0, 1000)),
    #                       args=(iLED,waveL,np.array(iSpectrum).max(axis=1),LEDs)
    #                       )
        
    #     t = np.round(result.x)
    #     tmp.append(t.tolist())
    
    # nunTargetLight = 2
    # tmp_spectra = {}
    # for mmName in list(res_opt.keys()):
    #     tmp_spectra[mmName] = res_opt[mmName][nunTargetLight]

    # tmp = []
    # for iLEDs,pw in zip(tmp_spectra["LEDs"],tmp_spectra["optimized_coeff"]):
    #      tmp.append(LEDCube.showLEDSpectra(iLEDs,pw/10))

    # y = np.array(tmp).mean(axis=0)
    # plt.plot(tmp_spectra["lambda"],y,label="opt")
    
    # y = np.array(tmp_spectra["spectrum"]).mean(axis=0)
    # plt.plot(tmp_spectra["lambda"],y,label="opt")

    LEDCube.saveData(res_opt)
   
    return resMin


if __name__ == '__main__':
               
    res_val = run()
    # with Pool(4) as p:
    #     df = p.map(run, np.round(np.arange(0.2,0.4,0.01),4))

    # for i,t in enumerate(res_val['optimized_XYZ']):
    #     res_val['optimized_XYZ'][i] = t.tolist()