#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 29 09:01:38 2025

@author: yutasuzuki
"""

from PyQt6.QtCore import QThread,pyqtSignal
from queue import Queue
import time
import numpy as np
import pandas as pd
from scipy.stats import norm

import lib.config as config
from pre_processing_cls import getPCPDevents
from zeroInterp import zeroInterp
from band_pass_filter import lowpass_filter_manual


def rejectOutliear(pupil_values):
    
    d = np.diff(pupil_values)
    q75, q25 = np.percentile(d, [75 ,25])
    IQR = q75 - q25

    lower = q25 - IQR*1.5
    upper = q75 + IQR*1.5
    d_witout_outliar = d[(d > lower) & (d < upper)]

    param = norm.fit(d_witout_outliar)
    
    (a,b) = norm.interval(0.99, loc=param[0], scale=param[1])
    
    ind = np.argwhere(abs(np.diff(pupil_values)) > b).reshape(-1)
    
    pupil_values[ind] = 0 

    return pupil_values

def detect_inflection_points(signal, dx=1.0):
    
    first_deriv = np.gradient(signal, dx)
    second_deriv = np.gradient(first_deriv, dx)

    extrema_sign_change = np.diff(np.sign(first_deriv))
    minima_candidates = np.where(extrema_sign_change > 0)[0] + 1

    # valleys = []
    # for idx in minima_candidates:
    #     if idx <= 1 or idx >= len(second_deriv) - 1:
    #         continue
    #     if second_deriv[idx - 1] < 0 and second_deriv[idx + 1] > 0:
    #         valleys.append(idx)

    return minima_candidates

# %% pupil anaylysis
class PupilAnalysisThread(QThread):

    trough_detected = pyqtSignal(float)
    
    def __init__(self, sample_queue: Queue,args):
        
        super().__init__()
        self.args=args
        self.sample_queue = sample_queue
        self.running = True
        self.buffer = []
        self.troughs_flg = False
        self.current_sample_num=0
        # self.start_time = time.perf_counter()
        self.result=[]
        self.analysis_st=False
        self.fs = 100
        
        if config.EYE_TRACKER=="Eyelink":
            self.padnum = 600
        elif config.EYE_TRACKER=="NEON":
            self.padnum = 60
            
            
    def getEventFlg(self):
        return self.troughs_flg
    
    def run(self):
        
        # self.start_time = time.perf_counter()
        
        while self.running:
            
            if len(self.sample_queue)==0:
                # self.start_time = time.perf_counter()
                # print("time reset")
                continue
            
            if len(self.sample_queue) == self.current_sample_num:
                continue
                        
            if len(self.sample_queue) < self.fs*3:
                # self.start_time = time.perf_counter()
                # print("time reset")
                continue

            self.current_sample_num = len(self.sample_queue)
            st = 0
            
            if self.sample_queue[-1]["timestamp_eyetracker"] < config.window_analysis:
                st = 0
                
            else:
                if not self.analysis_st:
                    self.analysis_st = True
                    print("[INFO] Analysis start!")
                    
                for st in np.arange(1,len(self.sample_queue)):
                    if self.sample_queue[-st]["timestamp_eyetracker"] < (self.sample_queue[-1]["timestamp_eyetracker"]-config.window_analysis):
                        self.fs = int(st/config.window_analysis)
                        # print(self.fs)
                        # print(f"{self.sample_queue[-st]['timestamp_eyetracker']}")
                        # print(f"{(self.sample_queue[-1]['timestamp_eyetracker']-config.window_analysis)}")
                        # print(f"st={st},{len(self.sample_queue)}")
                        break
                
            if not self.analysis_st:
                continue

            pupil_values=[]
            timestamp_eyetracker=[]
            for entry in self.sample_queue[-st:]:
                pupil_values.append(entry["pupil_right"])
                timestamp_eyetracker.append(entry["timestamp_eyetracker"])
            
            pupil_values = rejectOutliear(np.array(pupil_values))

            pupilData = zeroInterp(pupil_values.copy(),self.fs,(self.fs*0.04))
            # # pupilData = zeroInterp(pupil_values, 30,(30*0.04))
            pupilData = pupilData["pupilData"].reshape(-1)
                        
            y_lowpassed = lowpass_filter_manual(pupilData.copy(),0.2,self.fs,4,self.padnum)

            # sm = getPCPDevents(y_lowpassed,0.001)
            sm = getPCPDevents(y_lowpassed,0.01)
            sm = sm['troughs'][0]
            
            # sm = detect_inflection_points(y_lowpassed, dx=1/self.fs)

            # if len(sm["troughs"][0]) > 0:
            #     # print(f"{sm['troughs'][0][-1]},{len(pupilData)}")    
            #     if sm["troughs"][0][-1] > len(pupilData)-self.fs*1:
            #         self.troughs_flg = True
            #         print("[INFO] Trough detect!")
            #     else:
            #         self.troughs_flg = False
                    
            if len(sm) > 0:
                # print(f"{sm['troughs'][0][-1]},{len(pupilData)}")    
                if sm[-1] > len(pupilData)-self.fs*0.5:
                    self.troughs_flg = True
                    self.trough_detected.emit(timestamp_eyetracker[-1])
                    # print(f"[INFO] Trough detect! Time stamp={timestamp_eyetracker[-1]}")

                else:
                    self.troughs_flg = False
                    
            self.result.append({
                    "timestamp_eyetracker": timestamp_eyetracker,
                    "pupil_original": pupilData,
                    "pupil_lowpassed": y_lowpassed,
                    # "peaks": sm["peaks"],
                    "troughs": sm,
                    "event_flg": self.troughs_flg 
                    })
            #     # print(f"result={len(self.sample_queue)},pupilData={len(pupilData)}")
            #     # print(f"{self.sample_queue[st+i]}")
            #     # print(f"{st}")

            self.msleep(1)

    def stop(self):
        self.running = False
        
        df = pd.DataFrame(self.result)

        timestr = time.strftime("%Y%m%d_%H%M%S")
        filename = f"./results/{self.args.subject}/pupil_data_{timestr}.parquet"

        df.to_parquet(filename, index=False)
        print(f"[INFO] Buffer saved to {filename}.")
        
  