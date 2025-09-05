#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 28 10:38:02 2025

@author: yutasuzuki
"""

from psychopy import visual, core, event
from scipy.io import loadmat
import numpy as np
import json
import glob
from datetime import datetime
import os

from pyglet import canvas
display = canvas.Display()

SCREEN_NUM_YELLOW = 2
SCREEN_NUM_BLUE = 1

screenSize = []
for i, screen in enumerate(display.get_screens()):
    print(f"Screen {i}: {screen.width} x {screen.height}")
    screenSize.append([int(screen.width*1), int(screen.height*1)])
   
LINE_WIDTH = 100  # Width of the center black line in pixels
LINE_COLOR = [-1,-1,-1]

LINE_WIDTH = LINE_WIDTH/screenSize[SCREEN_NUM_BLUE][1]*2

FULL_SCREEN = True
# FULL_SCREEN = False

LUMINANCE_BACKGROUND = [-1,-1,-1]

# %% --- Load RGB colors from .mat file ---

with open("LEDcubeSimulation/data_LEDCube_20240617x40y25ipRGC185v2.json", "r") as f:
    res = json.load(f)

# with open("LEDcubeSimulation/data_LEDCube_20240617x40y25ipRGC100v2.json", "r") as f:
#     res = json.load(f)

# %% --- Create windows ---

wins = {
        SCREEN_NUM_YELLOW:visual.Window(size=screenSize[SCREEN_NUM_YELLOW],
                     screen=SCREEN_NUM_YELLOW, color=LUMINANCE_BACKGROUND,
                     # units='pix', 
                     units='norm', 
                     fullscr=FULL_SCREEN
                     ),
        SCREEN_NUM_BLUE:visual.Window(size=screenSize[SCREEN_NUM_BLUE],
                     screen=SCREEN_NUM_BLUE, color=LUMINANCE_BACKGROUND,
                     # units='pix', 
                     units='norm', 
                     fullscr=FULL_SCREEN
                     )
}


# %%
def draw_and_flip(wins,light):
    
    for iProj in (SCREEN_NUM_YELLOW, SCREEN_NUM_BLUE):

        win = wins[iProj]

        w, h = screenSize[iProj]
        tmp = np.ones((h, w, 3))
        
        left_rgb  = np.array(light[iProj]) / 255
        right_rgb = np.array(light[iProj]) / 255
    
        mid = w // 2
        tmp[:,:mid,:] = left_rgb
        tmp[:,mid:,:] = right_rgb
    
        tmp_window = visual.ImageStim(
            win, 
            image=tmp, 
            units="pix", 
            size=(w, h), 
        )
        
        tmp_window.draw()
        win.flip()

    return tmp

# %% --- Initial color assignment ---

w,h = screenSize[0]

for numOfLight in np.arange(len(res["LEDs"])):
# for numOfLight in np.arange(7,8):

    tmp = np.zeros(6)
    
    # for i,led in enumerate(res["LEDs"][numOfLight]):
    #     tmp[led-1] = res["coeff"][numOfLight][i]
        
    # with open("source/right_20250905_152919_Light00.json", "r") as f:
    #     tmp = json.load(f)

    # with open(glob.glob(f"source/right_*_Light{numOfLight:02}.json")[-1], "r") as f:
    #     tmp = json.load(f)

    with open(glob.glob(f"source/right_20250905_150328_ipRGC.json")[-1], "r") as f:
        tmp = json.load(f)
        
    tmp_light={}
    # tmp_light[SCREEN_NUM_YELLOW]=tmp[:3]
    # tmp_light[SCREEN_NUM_BLUE]=tmp[3:]

    tmp_light[SCREEN_NUM_YELLOW] = np.array(tmp[str(SCREEN_NUM_YELLOW)])
    tmp_light[SCREEN_NUM_BLUE] = np.array(tmp[str(SCREEN_NUM_BLUE)])

    current_light = tmp_light
    draw_and_flip(wins,current_light)
    
    while True:
        
        keys = event.waitKeys(keyList=['escape', 'left', 'right','p',
                                       'r', 't','q', 'w',
                                       'g', 'h','a', 's',
                                       'b', 'n','z', 'x'])
        
        if 'left' in keys:
            print("Next light!")
            break
            
        elif 'r' in keys:
            current_light[SCREEN_NUM_YELLOW][0] = current_light[SCREEN_NUM_YELLOW][0]+1
            draw_and_flip(wins,current_light)
    
        elif 't' in keys:
            current_light[SCREEN_NUM_YELLOW][0] = current_light[SCREEN_NUM_YELLOW][0]-1
            draw_and_flip(wins,current_light)
    
        elif 'g' in keys:
            current_light[SCREEN_NUM_YELLOW][1] = current_light[SCREEN_NUM_YELLOW][1]+1
            draw_and_flip(wins,current_light)
     
        elif 'h' in keys:
            current_light[SCREEN_NUM_YELLOW][1] = current_light[SCREEN_NUM_YELLOW][1]-1
            draw_and_flip(wins,current_light)
     
        elif 'b' in keys:
            current_light[SCREEN_NUM_YELLOW][2] = current_light[SCREEN_NUM_YELLOW][2]+1
            draw_and_flip(wins,current_light)
     
        elif 'n' in keys:
            current_light[SCREEN_NUM_YELLOW][2] = current_light[SCREEN_NUM_YELLOW][2]-1
            draw_and_flip(wins,current_light)
            
        elif 'q' in keys:
            current_light[SCREEN_NUM_BLUE][0] = current_light[SCREEN_NUM_BLUE][0]+1
            draw_and_flip(wins,current_light)
     
        elif 'w' in keys:
            current_light[SCREEN_NUM_BLUE][0] = current_light[SCREEN_NUM_BLUE][0]-1
            draw_and_flip(wins,current_light)
            
        elif 'a' in keys:
            current_light[SCREEN_NUM_BLUE][1] = current_light[SCREEN_NUM_BLUE][1]+1
            draw_and_flip(wins,current_light)
     
        elif 's' in keys:
            current_light[SCREEN_NUM_BLUE][1] = current_light[SCREEN_NUM_BLUE][1]-1
            draw_and_flip(wins,current_light)
     
        elif 'z' in keys:
            current_light[SCREEN_NUM_BLUE][2] = current_light[SCREEN_NUM_BLUE][2]+1
            draw_and_flip(wins,current_light)
            
        elif 'x' in keys:
            current_light[SCREEN_NUM_BLUE][2] = current_light[SCREEN_NUM_BLUE][2]-1
            draw_and_flip(wins,current_light)
            
        elif 'p' in keys:
            now = datetime.now().strftime("%Y%m%d_%H%M%S")
            save_filename = f"./source/right_{now}_Light{numOfLight:02}.json"
            with open(save_filename, 'w') as f:
                json.dump(current_light, f, default=lambda x: x.tolist() if isinstance(x, np.ndarray) else x)
    
            print(f"left_color0 saved to {os.path.abspath(save_filename)}")
            break
    
        print(f"current light = {current_light}")
        print(f"Target xy = {res['Yxy'][numOfLight][1:]}")
    
    
    draw_and_flip(wins,current_light)


# %% --- Exit ---
for k in list(wins.keys()):
    wins[k].close()
    
core.quit()