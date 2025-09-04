#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr  1 17:46:47 2025

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

NUM_TRIAL=10

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

def make_condition_sequence():
    
    w,h = config.screenSize[1]

    condition_frame = pd.DataFrame(list(product(["Left","Right"], ["ipRGC+|ipRGC-","ipRGC-|ipRGC+"]))*NUM_TRIAL,columns=["cue","window"])
    condition_frame = condition_frame.sample(frac=1).reset_index(drop=True)

    low, high = config.TASK_JITTER
    condition_frame['jitter'] = list(np.random.uniform(low, high + 1, size=(len(condition_frame), 1)).reshape(-1))
    
    
    condition_frame['num_gabor'] = list(np.random.randint(config.NUM_GABOR[0], config.NUM_GABOR[1] + 1, size=(len(condition_frame), 1)).reshape(-1))

    condition_frame['gabor_timing'] = None
    condition_frame['gabor_locs_w'] = None
    condition_frame['gabor_locs_h'] = None
    condition_frame['num_task'] = -1

    for iTrial in np.arange(len(condition_frame)):
        condition_frame.at[iTrial,"gabor_timing"]=sorted(list(np.round(np.random.uniform(2, condition_frame.iloc[iTrial,:]["jitter"] - 1, 
                                                                              size=(condition_frame.iloc[iTrial,:]["num_gabor"], 1)),3).reshape(-1)))
        
        
        numOfTask=0
        values = []
        while len(values) < condition_frame.iloc[iTrial,:]["num_gabor"]:
            x = np.random.randint(config.GABOR_SIZE, w-config.GABOR_SIZE)
            if not (w/2-config.WIDTH_LINE-config.GABOR_SIZE <= x <= w/2+config.WIDTH_LINE+config.GABOR_SIZE):
                values.append(x)
                if (condition_frame.iloc[iTrial,:]["cue"] == "Left") and (x<w/2):
                    numOfTask+=1
                    
                if (condition_frame.iloc[iTrial,:]["cue"] == "Right") and (x>w/2):
                    numOfTask+=1                    

        condition_frame.at[iTrial,"num_task"] = numOfTask
        condition_frame.at[iTrial,"gabor_locs_w"] = values
        condition_frame.at[iTrial,"gabor_locs_h"] = list(np.random.randint(config.GABOR_SIZE, h-config.GABOR_SIZE, 
                                                                      size=(condition_frame.iloc[iTrial,:]["num_gabor"], 1)).reshape(-1))
        
    return condition_frame

# %%

def parse_args():

    parser = argparse.ArgumentParser()
    parser.add_argument("--demo", action="store_true")
    parser.add_argument("--subject", "--sid", dest="subject", type=str)
    parser.add_argument("--gender", dest="gender", type=str)
    parser.add_argument("--age", dest="age", type=int)
    
    return parser.parse_args()

def gabor_cosine_rgba(size_px, wavelength, sigma, contrast=0.2,
                      phase=0.0, angle_deg=0.0):
    
    """
    size_px : int
        Size of the patch (pixels, square).
    wavelength : float
        Wavelength (λ) of the cosine grating in pixels.
    sigma : float
        Standard deviation of the Gaussian envelope (pixels).
    contrast : float, optional
        Contrast scaling factor (0..1). Default is 0.2.
    phase : float, optional
        Phase offset of the grating (radians). Default is 0.0.
    """

    coords = np.arange(-size_px/2+1, size_px/2+1)
    X, Y = np.meshgrid(coords, coords)

    th = np.deg2rad(angle_deg).astype(np.float32)
    U = X * np.cos(th) + Y * np.sin(th)

    cosine = (np.cos(2*np.pi*U / wavelength + phase) + 1.0) * 0.5

    gaussian = np.exp(-(X**2 + Y**2) / (2*sigma**2))
    gabor = contrast * cosine * gaussian

    return 1-gabor

def draw_background(win,params,iProj):
    
    w, h = config.screenSize[iProj]
    tmp = np.ones((h, w, 3))
    
    if params["window"] == "ipRGC+|ipRGC-":
        left_rgb  = config.lightData["ipRGC"][iProj]   / 255.0
        right_rgb = config.lightData["control"][iProj] / 255.0
    else:
        left_rgb  = config.lightData["control"][iProj] / 255.0
        right_rgb = config.lightData["ipRGC"][iProj]   / 255.0

    mid = w // 2
    tmp[:,:mid,:] = left_rgb
    tmp[:,mid:,:] = right_rgb
        
    tmp = np.concatenate([tmp,np.ones((h, w, 1))],axis=2)
    
    tmp[:, mid-config.WIDTH_LINE:mid+config.WIDTH_LINE, :] = 0

    return tmp

def draw_fixation(wins,params):
  
    
    for iProj in (config.SCREEN_NUM_YELLOW, config.SCREEN_NUM_BLUE):
        
        win = wins[iProj]
        w, h = config.screenSize[iProj]

        tmp_screen = draw_background(win,params,iProj)

        tmp_window = visual.ImageStim(
            win, 
            image=tmp_screen, 
            units="pix", 
            size=(w, h), 
        )
        
        horiz = visual.Line(
            win,
            start=(-config.FIX_SIZE, 0),
            end=(config.FIX_SIZE, 0),
            lineColor='white',
            lineWidth=config.FIX_LINE_WIDTH
        )
        
        vert = visual.Line(
            win,
            start=(0, -config.FIX_SIZE),
            end=(0, config.FIX_SIZE),
            lineColor='white',
            lineWidth=config.FIX_LINE_WIDTH
        )
        
        horiz.draw()
        vert.draw()
        tmp_window.draw()

        win.flip()

def draw_arrow(wins,params):
    
    for iProj in (config.SCREEN_NUM_YELLOW, config.SCREEN_NUM_BLUE):
        
        win = wins[iProj]
        w, h = config.screenSize[iProj]

        tmp_screen = draw_background(win,params,iProj)

        tmp_window = visual.ImageStim(
            win, 
            image=tmp_screen, 
            units="pix", 
            size=(w, h), 
        )
        
        shaft = visual.Line(
            win,
            start=(-config.ARROW_SISE, 0),
            end=(config.ARROW_SISE, 0),
            lineColor="gray",
            lineWidth=4
        )
        
        if params["cue"]=="Left":
            sLine = -config.ARROW_SISE
        else:
            sLine = config.ARROW_SISE
            
        head_up = visual.Line(
            win,
            start=(sLine, 0),
            end=(0, config.ARROW_SISE*(2/3)),
            lineColor="gray",
            lineWidth=3
        )
        
        head_down = visual.Line(
            win,
            start=(sLine, 0),
            end=(0, -config.ARROW_SISE*(2/3)),
            lineColor="gray",
            lineWidth=3
        )
            
        shaft.draw()
        head_up.draw()
        head_down.draw()

        tmp_window.draw()
        win.flip()


def draw_gabor(wins,tmp_gabor,params):

    gabor_size_half = int(config.GABOR_SIZE/2)

    for iProj in (config.SCREEN_NUM_YELLOW, config.SCREEN_NUM_BLUE):
        
        win = wins[iProj]
        w, h = config.screenSize[iProj]

        tmp_screen = draw_background(win,params,iProj)

        tmp_screen[(params["gabor_locs_h"]-gabor_size_half):(params["gabor_locs_h"]+gabor_size_half),
            (params["gabor_locs_w"]-gabor_size_half):(params["gabor_locs_w"]+gabor_size_half),3] = tmp_gabor
        
        tmp_window = visual.ImageStim(
            win, 
            image=tmp_screen, 
            units="pix", 
            size=(w, h), 
        )
        
        horiz = visual.Line(
            win,
            start=(-config.FIX_SIZE, 0),
            end=(config.FIX_SIZE, 0),
            lineColor='white',
            lineWidth=config.FIX_LINE_WIDTH
        )
        
        vert = visual.Line(
            win,
            start=(0, -config.FIX_SIZE),
            end=(0, config.FIX_SIZE),
            lineColor='white',
            lineWidth=config.FIX_LINE_WIDTH
        )
        
        horiz.draw()
        vert.draw()
        tmp_window.draw()

        win.flip()

def draw_text(wins,msg,params):
    
    for iProj in (config.SCREEN_NUM_YELLOW, config.SCREEN_NUM_BLUE):

        win = wins[iProj]
        w, h = config.screenSize[iProj]

        tmp_screen = draw_background(win,params,iProj)

        tmp_window = visual.ImageStim(
            win, 
            image=tmp_screen, 
            units="pix", 
            size=(w, h), 
        )

        text = visual.TextStim(win, 
                               text=msg,
                               alignText='center',
                               anchorHoriz='center',
                               color='gray', 
                               pos=(0, -1/3),
                               )
        tmp_window.draw()
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

    tmp_gabor = gabor_cosine_rgba(
            size_px=config.GABOR_SIZE,
            wavelength=20,
            sigma=config.GABOR_SIZE/8,
            contrast=0.8,
            angle_deg=0
            )
    
    # %% eye-tracker setup

    if not args.demo:
        el_tracker = setupEyelink(wins[config.SCREEN_NUM_BLUE])
    else:
        el_tracker = None

    if not args.demo:
        el_tracker.sendMessage("START_EXPERIMENT")
    
    # %% main expriment

    behavior_res=[]
    for iTrial in np.arange(len(condition_frame)):
        
        current_cond = condition_frame.iloc[iTrial,:].copy()
        
        print(f"[INFO] Trial:{iTrial}")
        print(f"[INFO] Cue:{current_cond['cue']}")
        print(f"[INFO] Window:{current_cond['window']}")
        
        if not args.demo:
            el_tracker.sendMessage(f"START_TRIAL {iTrial}")
            el_tracker.sendMessage(f"TRIAL {iTrial+1}")
            el_tracker.sendMessage(f"Cue {current_cond['cue']}")
            el_tracker.sendMessage(f"Window {current_cond['window']}")
            el_tracker.sendMessage("onset_arrow")

        draw_arrow(wins,current_cond)
        trialClock = core.Clock()
        while True:
            if config.TIME_ARROW <= trialClock.getTime():
                break
    
        if not args.demo:
            el_tracker.sendMessage("onset_fixation")
            
        draw_fixation(wins,current_cond)
        
        trialClock = core.Clock()
        trialClock.reset() 
        task_count = 0
        while True:
            if task_count < current_cond["num_gabor"]:
                if (current_cond["gabor_timing"][task_count] <= trialClock.getTime()):
                    
                    print("[INFO] Gabor presented!")
                    
                    current_cond["gabor_locs_w"] = current_cond["gabor_locs_w"][task_count]
                    current_cond["gabor_locs_h"] = current_cond["gabor_locs_h"][task_count]
                    
                    if not args.demo:
                        el_tracker.sendMessage("onset_gabor")

                    draw_gabor(wins,
                               tmp_gabor,
                               current_cond)
                    
                    current_cond = condition_frame.iloc[iTrial,:]
                    
                    task_count+=1
                
            if current_cond["jitter"] <= trialClock.getTime():
                break
        
        if not args.demo:
            el_tracker.sendMessage("onset_msg")

        draw_text(wins,"How many target did you see?",current_cond)
        rtClock = core.Clock()
        rtClock.reset() 
        
        keys = event.waitKeys(keyList=["0","1","2","3","4","5","6","7","8","9"], timeStamped=rtClock)
        response, rt = keys[0]
        print(f"Response={response}, RT={rt:.3f} sec")
        
        behavior_res.append(pd.DataFrame({
            "trial":iTrial,
            "response":response,
            "RT":rt
            },index=[0]))
        
        if not args.demo:
            el_tracker.sendMessage(f"RESPONSE {response}")
            el_tracker.sendMessage("END_TRIAL")
    
    # %% save data
    
    resultFolder = f"results/{args.subject}/2_attention_main/" 

    if not os.path.exists(resultFolder):
        os.makedirs(resultFolder,exist_ok=True)
        
    if not args.demo:
        el_tracker.sendMessage("END_EXPERIMENT")
            
        el_tracker.closeDataFile()
        
        edf_local_name = 'test.edf'
        filename = "test.edf"

        newfilename = f"{resultFolder}/{timestr}.edf"
        el_tracker.receiveDataFile(filename, edf_local_name)
        el_tracker.close()
        
        shutil.move(filename, newfilename)
        cmd = [r'C:\Program Files (x86)\SR Research\EyeLink\bin\edf2asc.exe', '-y', newfilename]
        subprocess.run(cmd)
    
    filename = f"{resultFolder}behavioral_data_{timestr}.json"
    behavior_res=pd.concat(behavior_res)
    behavior_res.to_json(filename, index=False)
   
    with open(f"{resultFolder}/config_{timestr}.json", "w") as f:
       json.dump(tmp_cfg, f, indent=2)

    for k in list(wins.keys()):
        wins[k].close()
        
    os._exit(0)

# %%
    
if __name__ == "__main__":
    main()
