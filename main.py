#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr  1 17:46:47 2025

@author: yutasuzuki
"""

import sys
import os
import argparse
from PyQt6.QtWidgets import QApplication
from StimulusThread import StimulusThread
from psychopy import visual, core, event
import json
import lib.config as config
from PupilAnalysisThread import PupilAnalysisThread
from EyeTrackerThread import EyeTrackerThread,EyeTrackerThread_NEON

from lib.monitorKeyInputThread import KeyMonitorThread
from lib.MessageBus import MessageBus

# %%

def parse_args():

    parser = argparse.ArgumentParser()
    parser.add_argument("--demo", action="store_true", help="Run in demo mode (default: off)")
    parser.add_argument("--subject", "--sid", dest="subject", type=str)
    parser.add_argument("--gender", dest="gender", type=str)
    parser.add_argument("--age", dest="age", type=int)
    
    return parser.parse_args()

def draw_fixation(win):
    horiz = visual.Rect(win, width=20, height=3, fillColor=[0,0,0], lineColor=[0,0,0])
    vert = visual.Rect(win, width=3, height=20, fillColor=[0,0,0], lineColor=[0,0,0])
    horiz.draw()
    vert.draw()
    win.flip()

def main():
    
    app = QApplication(sys.argv)

    win = visual.Window(
        # size=config.screenSize[config.SCREEN_NUM],
        screen=config.SCREEN_NUM, 
        color=config.LUMINANCE_BACKGROUND,
        units='pix', 
        # units='norm', 
        fullscr=config.FULL_SCREEN
        )
    
    draw_fixation(win)
    # kb.clock.reset()

    args = parse_args()
    
    print(f"[INFO] Subject_id={args.subject}\nGender={args.gender}\nAge={args.age}")
    if not os.path.exists(f"results/{args.subject}"):
        os.mkdir(f"results/{args.subject}")
    tmp_cfg = {
        k: v for k, v in vars(config).items()
        if (k.isupper() or k in {"Lag", "TargetLocs", "keyList", "window_analysis"})
           and isinstance(v, (int, float, str, bool, list, dict))
    }
    tmp_cfg["Subject_id"]=args.subject
    tmp_cfg["Gender"]=args.gender
    tmp_cfg["Age"]=args.age

    with open(f"results/{args.subject}/config.json", "w") as f:
       json.dump(tmp_cfg, f, indent=2)

    sample_queue = []
    bus = MessageBus()

    if config.EYE_TRACKER=="Eyelink":
        eye_thread = EyeTrackerThread(win, sample_queue, bus, args)
    
    elif config.EYE_TRACKER=="Neon":
        eye_thread = EyeTrackerThread_NEON(win,sample_queue, bus, args)
    
    analysis_thread = PupilAnalysisThread(sample_queue, args)

    stim_thread = StimulusThread(win, bus, args)

    analysis_thread.trough_detected.connect(stim_thread.play_if_trough)

    key_thread = KeyMonitorThread(config.os_name,bus)
    key_thread.key_detected.connect(stim_thread.handle_key_event)

    def on_key(keys):
        for k in keys:
            if k["key"] == "escape":
                stim_thread.esc_flg = True
                app.quit() 
                
    stim_thread.finished.connect(app.quit)
    key_thread.key_detected.connect(on_key)

    eye_thread.start()
    analysis_thread.start()
    stim_thread.start()

    draw_fixation(win)
    
    try:
        sys.exit(app.exec())
        
    finally:
         if eye_thread.isRunning():
             eye_thread.stop()
         if analysis_thread.isRunning():
             analysis_thread.stop()
             
         win.close()
         os._exit(0)

# %%
    
if __name__ == "__main__":
    main()
