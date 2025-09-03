#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 15 16:38:13 2025

@author: yutasuzuki
"""

from PIL import Image
import numpy as np
import os
from scipy.io import loadmat
import json
import glob

mat_data = loadmat('light_20250121.mat')

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


# Define the 4 RGB color arrays
colors = [
    # np.array([0, 51, 0]),  # dark green
    # np.array([138.42465773, 106.8767118, 117.73679078]),  # muted pinkish
    # np.array([88, 1, 203]),  # deep violet
    # np.array([0, 24, 0])  # very dark green
   col_ipRGC[0,:3],
   (np.array([-0.60380645, -0.63533249, -0.48031925])+1)*255/2,
   # col_ipRGC[0,3:],
   # col_control[0,3:],
]

# Load the original black and white image
original_path = "source/img1.png"
img = Image.open(original_path).convert("L")

# Convert to binary (black and white)
bw_img = img.point(lambda x: 255 if x > 128 else 0, mode='1')

# Map white and black to given RGB values
white_color = colors[0]
black_color = colors[1]

# white_color = colors[2]
# black_color = colors[3]


# Convert to numpy array
bw_array = np.array(bw_img)
color_img = np.zeros((bw_array.shape[0], bw_array.shape[1], 3), dtype=np.uint8)

# Assign colors
color_img[bw_array == True] = white_color
color_img[bw_array == False] = black_color

# Save result
colored_img = Image.fromarray(color_img, 'RGB')
colored_path = "source/pink_whale_image1.png"
colored_img.save(colored_path)

colored_path
