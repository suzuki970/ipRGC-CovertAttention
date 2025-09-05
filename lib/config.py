#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 14 08:16:44 2025

@author: yutasuzuki
"""

import numpy as np
from scipy.io import loadmat
import json
import glob
from pyglet import canvas
from itertools import product
import pandas as pd
from pixel_size import pixel_size
display = canvas.Display()

SCREEN_RANGE = 1
# SCREEN_RANGE = 0.5

# %% stimulus

# white = "white_"
# white = "white_half_"
# white = ""

FULL_SCREEN = True
# FULL_SCREEN = False

# SCREEN_NUM_YELLOW = 2
# SCREEN_NUM_BLUE = 1
# SCREEN_NUM_GUI = 0

SCREEN_NUM_YELLOW = 1
SCREEN_NUM_BLUE = 2

FONTSIZE_MSG = 120 #pix

LUMINANCE_BACKGROUND = [-1,-1,-1]

TIME_ARROW = 2

# 505x290mm with a resolution of 1920x1080px 
DOT_PITCH = np.mean([505/1920,290/1080])
VISUAL_DISTANCE=60

GABOR_SIZE = round(pixel_size(DOT_PITCH, 4, VISUAL_DISTANCE))
# GABOR_LOCS = round(pixel_size(DOT_PITCH, 11.9898, VISUAL_DISTANCE))

WIDTH_LINE = round(pixel_size(DOT_PITCH, 2.428, VISUAL_DISTANCE))
ARROW_SISE = round(WIDTH_LINE*0.5)

FIX_SIZE = round(pixel_size(DOT_PITCH, 0.3, VISUAL_DISTANCE))
FIX_LINE_WIDTH = round(pixel_size(DOT_PITCH, 0.03, VISUAL_DISTANCE))

lightData = {
    "ipRGC":{
        SCREEN_NUM_YELLOW:np.array([29,0,72]),
        SCREEN_NUM_BLUE:np.array([91,38,0]),
        },
    "control":{}
    #     SCREEN_NUM_YELLOW:np.array([31,23,0]),
    #     SCREEN_NUM_BLUE:np.array([72,0,64]),
    #     }
}

# from scipy.io import loadmat
# mat_data = loadmat('source/light_20250121.mat')["light"][0][0][0]

# with open(f"source/light_20250121.json", "w") as f:
#    json.dump(mat_data.tolist(), f)

with open("source/light_20250121.json", "r") as f:
    tmp_lightData = json.load(f)
    

for i in np.arange(len(tmp_lightData)):
    lightData["control"][i]={
        SCREEN_NUM_BLUE:tmp_lightData[i][:3],
        SCREEN_NUM_YELLOW:tmp_lightData[i][3:],
    }

# with open(glob.glob("LEDcubeSimulation/data*.json")[0], "r") as f:
#     res = json.load(f)

# with open(glob.glob("LEDcubeSimulation/data*.json")[0], "r") as f:
#     res = json.load(f)

# tmp_control = np.zeros(6).astype(int)
# tmp_ipRGC = np.zeros(6).astype(int)
# for led1,led2,coeff1,coeff2 in zip(res["LEDs"][0],res["LEDs"][-1],res["coeff"][0],res["coeff"][-1]):
#     tmp_control[led1-1] = int(coeff1)
#     tmp_ipRGC[led2-1] = int(coeff2)

# col_control = np.array(mat_data["light"][0][0][0])
# col_ipRGC = np.array(mat_data["light"][0][0][3])

# numOfLight = 5

# colors = {

#     'blue_ipRGC': col_ipRGC[0,:3]/255*2-1,
#     'blue_control': np.array([-0.60380645, -0.63533249, -0.48031925]),
#     'yellow_ipRGC': col_ipRGC[0,3:]/255*2-1,
#     'yellow_control': col_control[0,3:]/255*2-1,

#     'blue_left': np.array([-0.60380645, -0.63533249, -0.48031925]),
#     'blue_right': col_ipRGC[0,:3]/255*2-1,
#     'yellow_left': col_control[0,3:]/255*2-1,
#     'yellow_right': col_ipRGC[0,3:]/255*2-1,

#     # 'blue_ipRGC_white': tmp_ipRGC[:3]/255*2-1,
#     'blue_ipRGC_white':np.array([-1,-0.57260274,-1]),
#     'blue_control_white': np.array([ 0.08568359, -0.16175128, -0.07657419]),
#     # 'yellow_ipRGC_white': tmp_ipRGC[3:]/255*2-1,
#     'yellow_ipRGC_white': np.array([-0.37046928, -1, 0.59215686]),
#     'yellow_control_white': tmp_control[3:]/255*2-1
# }

# --- Load most recent saved left_color0 ---
# left_color0_files = glob.glob("source/calibrated/left_color0_*.json")
# left_color0_files.sort()
# with open(left_color0_files[-1], 'r') as f:
#     tmp_colors = json.load(f)

# for mmName in ['blue_ipRGC_white','blue_control_white','yellow_ipRGC_white','yellow_control_white']:
#     colors[mmName] = np.array(tmp_colors[mmName])

# print(f"Loaded left_color0 from {left_color0_files[-1]}")

# LINE_WIDTH = 100  # Width of the center black line in pixels
# LINE_COLOR = LUMINANCE_BACKGROUND

screenSize = []
for i, screen in enumerate(display.get_screens()):
    print(f"Screen {i}: {screen.width} x {screen.height}")
    screenSize.append([int(screen.width*SCREEN_RANGE), int(screen.height*SCREEN_RANGE)])
    

# FONTSIZE_MSG = FONTSIZE_MSG/screenSize[SCREEN_NUM_BLUE][1]
# LINE_WIDTH = LINE_WIDTH/screenSize[SCREEN_NUM_BLUE][1]*2

# %%

# NUM_TRIAL = 10
TASK_JITTER=[10,15]

NUM_GABOR = [3,8]


# %% GUI

# FONTSIZE_LABELS = 40
# FONTSIZE_LEGEND = 40
# FONTSIZE_BUTTON = 50

# COLOR_MAIN1 = "#66FFFF"
# COLOR_MAIN2 = "#FFFF66"
# COLOR_MAIN1 = "#33CCFF"
# COLOR_MAIN2 = "#FFCC00"

