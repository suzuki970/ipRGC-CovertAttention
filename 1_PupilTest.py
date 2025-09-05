#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep  4 23:00:02 2025

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
import glob
import lib.config as config
from lib.EyeLinkCoreGraphicsPsychoPy import EyeLinkCoreGraphicsPsychoPy

import pickle
import gzip

NUM_TRIAL = 4

# %%

def make_condition_sequence():
    
    condition_frame = pd.DataFrame(["ipRGC","control"]*NUM_TRIAL,columns=["light"])
    condition_frame = condition_frame.sample(frac=1).reset_index(drop=True)
        
    return condition_frame


# %% Eyelink setup

def setupEyelink(win):
    
    el_tracker = pylink.EyeLink()
    el_tracker.setOfflineMode()
    
    file_sample_flags = 'LEFT,RIGHT,GAZE,HREF,RAW,AREA'
    link_sample_flags = 'LEFT,RIGHT,GAZE,HREF,RAW,AREA'

    el_tracker.sendCommand("file_sample_data = %s" % file_sample_flags)
    el_tracker.sendCommand("link_sample_data = %s" % link_sample_flags)

    # Open an EDF data file on the Host PC
    el_tracker.openDataFile('test.edf')
    
    genv = EyeLinkCoreGraphicsPsychoPy(el_tracker, win, config.os_name)
    genv.setCalibrationColors((0,0,0), win.color)
    genv.setTargetType('circle')
    genv.setTargetSize(24)
    pylink.openGraphicsEx(genv)
    print("[INFO] Calling calibration...")
    el_tracker.doTrackerSetup()    
    el_tracker.startRecording(1,1,1,1)
    
    return el_tracker

def sendMessage(el_tracker,mes):
    el_tracker.sendMessage(mes)


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
        if 0.5 <= trialClock.getTime():
            break

def draw_stim(wins,light):

    for iProj in (config.SCREEN_NUM_YELLOW, config.SCREEN_NUM_BLUE):
        
        win = wins[iProj]
        w, h = config.screenSize[iProj]
        
        tmp = np.ones((h, w, 3))
        tmp[:,:,:] = np.array(light[iProj])/255
        
        tmp_window = visual.ImageStim(
            win, 
            image = tmp, 
            units = "pix", 
            size = (w, h), 
        )
        tmp_window.draw()
        win.flip()
            
    trialClock = core.Clock()
    trialClock.reset() 
    while True:
        if 1 <= trialClock.getTime():
            break
  
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
    
    # %% eye-tracker setup

    if not args.demo:
        el_tracker = setupEyelink(wins[config.SCREEN_NUM_BLUE])
    else:
        el_tracker = None

    if not args.demo:
        el_tracker.sendMessage("START_EXPERIMENT")

    # %% main expriment
    with open(glob.glob(f"results/{args.subject}/0_stimTest/config*.json")[0], "r") as f:
        params = json.load(f)
    
    
    config.lightData["control"] = config.lightData["control"][params["selectedLight"]]
    
    # %% main experiment
    
    for iTrial in np.arange(len(condition_frame)):

        current_cond = condition_frame.iloc[iTrial,:].copy()
        
        print(f"[INFO] Trial:{iTrial}")
        print(f"[INFO] Light:{current_cond['light']}")
        
        if not args.demo:
            el_tracker.sendMessage(f"START_TRIAL {iTrial}")
            el_tracker.sendMessage(f"Light {current_cond['light']}")
            el_tracker.sendMessage("onset_fixation")

        draw_fixation(wins,current_cond)

        if not args.demo:
            el_tracker.sendMessage("onset_stimlus")
        
        draw_stim(wins,config.lightData[current_cond["light"]])
        
    
    # %% save data
    
    resultFolder = f"results/{args.subject}/1_PupilTest/" 

    if not os.path.exists(resultFolder):
        os.makedirs(resultFolder,exist_ok=True)
    
    with open(f"{resultFolder}/config_{timestr}.json", "w") as f:
       json.dump(tmp_cfg, f, indent=2)

    if not args.demo:
        el_tracker.sendMessage("END_EXPERIMENT")
            
        el_tracker.closeDataFile()
        
        edf_local_name = 'test.edf'
        filename = "test.edf"

        newfilename = f"{resultFolder}{timestr}.edf"
        el_tracker.receiveDataFile(filename, edf_local_name)
        el_tracker.close()
        
        shutil.move(filename, newfilename)
        cmd = [r'C:\Program Files (x86)\SR Research\EyeLink\bin\edf2asc.exe', '-y', newfilename]
        subprocess.run(cmd)
    

    for k in list(wins.keys()):
        wins[k].close()
        
    os._exit(0)

# %%
    
if __name__ == "__main__":
    main()
