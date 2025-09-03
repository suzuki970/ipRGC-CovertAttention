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
display = canvas.Display()

SCREEN_RANGE = 1
# SCREEN_RANGE = 0.5

# %% stimulus

white = "white_"
white = "white_half_"
# white = ""

FULL_SCREEN = True
FULL_SCREEN = False

SCREEN_NUM_YELLOW = 2
SCREEN_NUM_BLUE = 1
SCREEN_NUM_GUI = 0

SCREEN_NUM_YELLOW = 0
SCREEN_NUM_BLUE = 0

FONTSIZE_MSG = 120 #pix

LUMINANCE_BACKGROUND = [-1,-1,-1]

TIME_FADEIN = 0.5
TIME_FADEOUT = 0.5

FONT_GUI = "Orbitron"
# FONT_INSTRUCTION = "BIZ UDGothic"
# FONT_INSTRUCTION = "MPLUS1p"
# FONT_INSTRUCTION = "Noto Sans JP"
FONT_INSTRUCTION = "Rounded M+ 1c"
# FONT_LABEL = "Noto Sans JP"
# FONT_LABEL = "MPLUS1p"
FONT_LABEL = "Rounded M+ 1c"

mat_data = loadmat('source/light_20250121.mat')

with open(glob.glob("LEDcubeSimulation/data*.json")[0], "r") as f:
    res = json.load(f)

tmp_control = np.zeros(6).astype(int)
tmp_ipRGC = np.zeros(6).astype(int)
for led1,led2,coeff1,coeff2 in zip(res["LEDs"][0],res["LEDs"][-1],res["coeff"][0],res["coeff"][-1]):
    tmp_control[led1-1] = int(coeff1)
    tmp_ipRGC[led2-1] = int(coeff2)

col_control = np.array(mat_data["light"][0][0][0])
col_ipRGC = np.array(mat_data["light"][0][0][3])

numOfLight = 5

colors = {

    'blue_ipRGC': col_ipRGC[0,:3]/255*2-1,
    'blue_control': np.array([-0.60380645, -0.63533249, -0.48031925]),
    'yellow_ipRGC': col_ipRGC[0,3:]/255*2-1,
    'yellow_control': col_control[0,3:]/255*2-1,

    'blue_left': np.array([-0.60380645, -0.63533249, -0.48031925]),
    'blue_right': col_ipRGC[0,:3]/255*2-1,
    'yellow_left': col_control[0,3:]/255*2-1,
    'yellow_right': col_ipRGC[0,3:]/255*2-1,

    # 'blue_ipRGC_white': tmp_ipRGC[:3]/255*2-1,
    'blue_ipRGC_white':np.array([-1,-0.57260274,-1]),
    'blue_control_white': np.array([ 0.08568359, -0.16175128, -0.07657419]),
    # 'yellow_ipRGC_white': tmp_ipRGC[3:]/255*2-1,
    'yellow_ipRGC_white': np.array([-0.37046928, -1, 0.59215686]),
    'yellow_control_white': tmp_control[3:]/255*2-1
}

# --- Load most recent saved left_color0 ---
left_color0_files = glob.glob("source/calibrated/left_color0_*.json")
left_color0_files.sort()
with open(left_color0_files[-1], 'r') as f:
    tmp_colors = json.load(f)

for mmName in ['blue_ipRGC_white','blue_control_white','yellow_ipRGC_white','yellow_control_white']:
    colors[mmName] = np.array(tmp_colors[mmName])

print(f"Loaded left_color0 from {left_color0_files[-1]}")

LINE_WIDTH = 100  # Width of the center black line in pixels
LINE_COLOR = LUMINANCE_BACKGROUND

screenSize = []
for i, screen in enumerate(display.get_screens()):
    print(f"Screen {i}: {screen.width} x {screen.height}")
    screenSize.append([int(screen.width*SCREEN_RANGE), int(screen.height*SCREEN_RANGE)])
    
FONTSIZE_MSG = FONTSIZE_MSG/screenSize[SCREEN_NUM_BLUE][1]
LINE_WIDTH = LINE_WIDTH/screenSize[SCREEN_NUM_BLUE][1]*2

# %% GUI

FONTSIZE_LABELS = 40
FONTSIZE_LEGEND = 40
FONTSIZE_BUTTON = 50

COLOR_MAIN1 = "#66FFFF"
COLOR_MAIN2 = "#FFFF66"
COLOR_MAIN1 = "#33CCFF"
COLOR_MAIN2 = "#FFCC00"

