#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep  4 17:43:48 2025

@author: yutasuzuki
"""

import numpy as np
import os
import argparse
from psychopy import visual, core, event
import json
import pylink
import pandas as pd
import time
import shutil
import subprocess
from itertools import product

import lib.config as config
from lib.EyeLinkCoreGraphicsPsychoPy import EyeLinkCoreGraphicsPsychoPy

import pickle
import gzip

import matplotlib.pyplot as plt
import json
import numpy as np


NUM_TRIAL = 1

# %%
def analyzeData(df,args):

    file_name = "./LEDcubeSimulation/data_LEDCube_20250108x40y25ipRGC90v2.json"
    with open(file_name, "r") as f:
        data = json.load(f)
    
    sz = []
    for i in range(len(data["Yxy"])):
        count = len(df[(df["lightnum"] == i+1)&(df["response"] == 1)])
        sz.append(count)

    x = np.array(data["Yxy"])[:, 1]
    y = np.array(data["Yxy"])[:, 2]

    sizes = np.array(sz) / (NUM_TRIAL * 2) * 1000 + 30
    
    plt.figure(figsize=(8, 6))
    plt.scatter(x, y, s=sizes, alpha=0.5, edgecolors="w")
    
    I = np.argmax(sz)
    plt.scatter(x[I], y[I], s=sizes[I], color="red", edgecolors="k")
    plt.xlabel("x")
    plt.ylabel("y")
    plt.title(f"Selected light is {int(I+1)}")

    for i in range(len(data["Yxy"])):
        plt.text(x[i], y[i], str(i+1), fontsize=8, ha="center", va="center")
    
    plt.savefig(f"./results/{args.subject}/0_stimTest/res.png", dpi=300, bbox_inches="tight")

    plt.show()
    
    return int(I+1)


# %%

def make_condition_sequence():
    
    w,h = config.screenSize[1]

    condition_frame = pd.DataFrame(list(product(["ipRGC_1st","ipRGC_2nd"], range(1,14)))*NUM_TRIAL,columns=["order","lightNum"])
    condition_frame = condition_frame.sample(frac=1).reset_index(drop=True)
        
    return condition_frame

# %%
def parse_args():

    parser = argparse.ArgumentParser()
    parser.add_argument("--demo", action="store_true")
    parser.add_argument("--subject", "--sid", dest="subject", type=str)
    parser.add_argument("--gender", dest="gender", type=str)
    parser.add_argument("--age", dest="age", type=int)
    
    return parser.parse_args()

def draw_fixation(wins,params):
    
    for iProj in (config.SCREEN_NUM_YELLOW, config.SCREEN_NUM_BLUE):
            
        win = wins[iProj]
        w, h = config.screenSize[iProj]
        
        tmp_window = visual.ImageStim(
            win, 
            image=np.zeros((h, w, 3)), 
            units="pix", 
            size=(w, h), 
        )
        
        horiz = visual.Line(
            win,
            start=(-config.FIX_SIZE, 0),
            end=(config.FIX_SIZE, 0),
            lineColor='gray',
            lineWidth=config.FIX_LINE_WIDTH
        )
        
        vert = visual.Line(
            win,
            start=(0, -config.FIX_SIZE),
            end=(0, config.FIX_SIZE),
            lineColor='gray',
            lineWidth=config.FIX_LINE_WIDTH
        )
        
        tmp_window.draw()
        horiz.draw()
        vert.draw()

        win.flip()
        
    trialClock = core.Clock()
    trialClock.reset() 
    
    while True:
        # if 0.5 <= trialClock.getTime():
        if 0.01 <= trialClock.getTime():
            break

def draw_stim(wins,light):

    for iProj in (config.SCREEN_NUM_YELLOW, config.SCREEN_NUM_BLUE):
        
        win = wins[iProj]
        w, h = config.screenSize[iProj]
        
        tmp_window = visual.ImageStim(
            win, 
            image = light[iProj]/255, 
            units = "pix", 
            size = (w, h), 
        )
        tmp_window.draw()
        win.flip()
            
    trialClock = core.Clock()
    trialClock.reset() 
    while True:
        # if 1 <= trialClock.getTime():
        if 0.01 <= trialClock.getTime():
            break
  
def draw_text(wins,msg):
    
    for iProj in (config.SCREEN_NUM_YELLOW, config.SCREEN_NUM_BLUE):

        win = wins[iProj]
        w, h = config.screenSize[iProj]

        text = visual.TextStim(win, 
                               text=msg,
                               alignText='center',
                               anchorHoriz='center',
                               color='gray', 
                               pos=(0, -1/3),
                               )
        text.draw()
        win.flip()


# %%
def main():
    
    timestr = time.strftime("%Y%m%d_%H%M%S")
    
    args = parse_args()
    print(f"[INFO] Subject_id={args.subject}\nGender={args.gender}\nAge={args.age}")
    if not os.path.exists(f"results/{args.subject}"):
        os.mkdir(f"results/{args.subject}")
    
    tmp_cfg = {
        "Subject_id":args.subject,
        "Gender":args.gender,
        "Age":args.age
        }
    
    condition_frame = make_condition_sequence()

    # %% display setup
    
    wins = {
        config.SCREEN_NUM_YELLOW: 
            visual.Window(
            size=config.screenSize[config.SCREEN_NUM_YELLOW],
            fullscr=config.FULL_SCREEN, screen=config.SCREEN_NUM_YELLOW,
            units="pix",
            color=[-1, -1, -1]),
       config.SCREEN_NUM_BLUE: 
            visual.Window(
            size=config.screenSize[config.SCREEN_NUM_BLUE],
            fullscr=config.FULL_SCREEN, screen=config.SCREEN_NUM_BLUE,
            units="pix",
            color=[-1, -1, -1])
    }
    
    # %% main expriment

    with gzip.open('source/ishihara_20250121.pkl.gz', 'rb') as f:
        lightData = pickle.load(f)

    light_ipRGC={
        config.SCREEN_NUM_YELLOW:lightData["ipRGC"]["Light01"]["proj_YELLOW"],
        config.SCREEN_NUM_BLUE:lightData["ipRGC"]["Light01"]["proj_BLUE"]
        }
    
    # %% main experiment
    
    behavior_res=[]
    for iTrial in np.arange(len(condition_frame)):

        current_cond = condition_frame.iloc[iTrial,:].copy()
        
        print(f"[INFO] Trial:{iTrial}")
        print(f"[INFO] Order:{current_cond['order']}")
        print(f"[INFO] Light:{current_cond['lightNum']}")
        
        light_control = {
            config.SCREEN_NUM_YELLOW:lightData["control"][f"Light{current_cond['lightNum']:02}"]["proj_YELLOW"],
            config.SCREEN_NUM_BLUE:lightData["control"][f"Light{current_cond['lightNum']:02}"]["proj_BLUE"]
            }
        
        draw_fixation(wins,current_cond)

        if current_cond["order"] == 'ipRGC_1st':
            draw_stim(wins,light_ipRGC)
        else:
            draw_stim(wins,light_control)
            
        draw_fixation(wins,current_cond)

        if current_cond["order"] == 'ipRGC_1st':
            draw_stim(wins,light_control)
        else:
            draw_stim(wins,light_ipRGC)

        draw_fixation(wins,current_cond)
        
        draw_text(wins,"Did the perceived colors appear the same?\n[<-] No  [->] Yes?")

        rtClock = core.Clock()
        rtClock.reset() 
        
        keys = event.waitKeys(keyList=["left","right"], timeStamped=rtClock)
        response, rt = keys[0]

        print(f"Response={response}, RT={rt:.3f} sec")
        
        behavior_res.append(pd.DataFrame({
            "trial":iTrial,
            "lightnum":current_cond['lightNum'],
            "response":0 if response=="left" else 1,
            "RT":rt
            },index=[0]))
    
    # %% save data
    
    resultFolder = f"results/{args.subject}/0_stimTest/" 
    if not os.path.exists(resultFolder):
        os.makedirs(resultFolder,exist_ok=True)
    
    behavior_res = pd.concat(behavior_res).reset_index(drop=True)
    behavior_res.to_json(f"{resultFolder}behavioral_data_{timestr}.json")
   
    selectedLight = analyzeData(behavior_res,args)
   
    tmp_cfg["selectedLight"] = selectedLight
   
    with open(f"{resultFolder}/config_{timestr}.json", "w") as f:
       json.dump(tmp_cfg, f, indent=2)


    for k in list(wins.keys()):
        wins[k].close()
        
    os._exit(0)

# %%
    
if __name__ == "__main__":
    main()


# from scipy.io import loadmat
# import h5py

# with h5py.File('./0_stimTest/ishiharaLight20250121.mat', 'r') as f:
#     df={"control":{},"ipRGC":{}}
    
#     for light in np.arange(13)+1:
        
#         df["control"][f'Light{light:02}'] = {}
#         df["control"][f'Light{light:02}']['proj_YELLOW'] = np.transpose(f['ishiharaLight']['control'][f'iLight{light}']['proj0'][:], (1, 2, 0))
#         df["control"][f'Light{light:02}']['proj_BLUE'] = np.transpose(f['ishiharaLight']['control'][f'iLight{light}']['proj1'][:], (1, 2, 0))
        
#     df["ipRGC"][f'Light01'] = {}
#     df["ipRGC"][f'Light01']['proj_YELLOW'] = np.transpose(f['ishiharaLight']['ipRGC'][f'iLight1']['proj0'][:], (1, 2, 0))
#     df["ipRGC"][f'Light01']['proj_BLUE'] = np.transpose(f['ishiharaLight']['ipRGC'][f'iLight1']['proj1'][:], (1, 2, 0))
    
# with gzip.open('ishihara_20250121.pkl.gz', 'wb') as f:
#     pickle.dump(df, f, protocol=pickle.HIGHEST_PROTOCOL)
