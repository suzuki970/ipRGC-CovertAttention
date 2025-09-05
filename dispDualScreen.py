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

SCREEN_NUM_YELLOW = 0
SCREEN_NUM_BLUE = 0


screenSize = []
for i, screen in enumerate(display.get_screens()):
    print(f"Screen {i}: {screen.width} x {screen.height}")
    screenSize.append([int(screen.width*1), int(screen.height*1)])
   
LINE_WIDTH = 100  # Width of the center black line in pixels
LINE_COLOR = [-1,-1,-1]

LINE_WIDTH = LINE_WIDTH/screenSize[SCREEN_NUM_BLUE][1]*2


FULL_SCREEN = True
FULL_SCREEN = False

LUMINANCE_BACKGROUND = [-1,-1,-1]

# %% --- Load RGB colors from .mat file ---

with open(glob.glob("data*.json")[0], "r") as f:
    res = json.load(f)

tmp_control = np.zeros(6).astype(int)
tmp_ipRGC = np.zeros(6).astype(int)
for led1,led2,coeff1,coeff2 in zip(res["LEDs"][0],res["LEDs"][-1],res["coeff"][0],res["coeff"][-1]):
    tmp_control[led1-1] = int(coeff1)
    tmp_ipRGC[led2-1] = int(coeff2)

# col_control = np.array(mat_data["light"][0][0][0])
# col_ipRGC = np.array(mat_data["light"][0][0][3])

numOfLight = 5

colors = {

    # 'blue_ipRGC': col_ipRGC[0,:3]/255*2-1,
    # 'blue_control': np.array([-0.60380645, -0.63533249, -0.48031925]),
    # 'yellow_ipRGC': col_ipRGC[0,3:]/255*2-1,
    # 'yellow_control': col_control[0,3:]/255*2-1,

    # 'blue_left': np.array([-0.60380645, -0.63533249, -0.48031925]),
    # 'blue_right': col_ipRGC[0,:3]/255*2-1,
    # 'yellow_left': col_control[0,3:]/255*2-1,
    # 'yellow_right': col_ipRGC[0,3:]/255*2-1,

    # 'blue_ipRGC_white': tmp_ipRGC[:3]/255*2-1,
    'blue_ipRGC_white':np.array([-1,-0.57260274,-1]),
    # 'blue_control_white': tmp_control[:3]/255*2-1,
    'blue_control_white':np.array([ 0.08568359,-0.16175128,-0.07657419]),
    # 'yellow_ipRGC_white': tmp_ipRGC[3:]/255*2-1,
    'yellow_ipRGC_white': np.array([-0.37046928, -1,0.59215686]),
    'yellow_control_white': tmp_control[3:]/255*2-1
}

# %% --- Screen configuration (adjust if needed) ---

# screen_size = [1920, 1080]
# half_width = screen_size[0] / 2
# full_height = screen_size[1]

# %% --- Create windows ---

win0 = visual.Window(size=screenSize[SCREEN_NUM_YELLOW],
                     screen=SCREEN_NUM_YELLOW, color=LUMINANCE_BACKGROUND,
                     # units='pix', 
                     units='norm', 
                     fullscr=FULL_SCREEN
                     )
win1 = visual.Window(size=screenSize[SCREEN_NUM_BLUE],
                     screen=SCREEN_NUM_BLUE, color=LUMINANCE_BACKGROUND,
                     # units='pix', 
                     units='norm', 
                     fullscr=FULL_SCREEN
                     )


# %% --- Helper function to create rectangles based on current color order ---

def draw_and_flip():
    rects = {
        
        # 'left0': visual.Rect(win0, 
        #                      width=half_width, height=full_height,
        #                      # pos=(-half_width/2, 0), 
        #                      # width=half_width, height=full_height*(2/3),
        #                      pos=(-half_width/2, -screen_size[1]*(1/3)),
        #                      fillColor=left_color0, lineColor=None),
        # 'right0': visual.Rect(win0, 
        #                       width=half_width, height=full_height,
        #                       pos=(half_width / 2, -screen_size[1]*(1/3)),
        #                       # width=half_width, height=full_height*(2/3),
        #                       # pos=(half_width/2, screen_size[0]*(2/6)),
        #                       fillColor=right_color0, lineColor=None),
        
        # 'left1': visual.Rect(win1, 
        #                      width=half_width, height=full_height,
        #                      pos=(-half_width / 2, screen_size[1]*(1/3)),
        #                      # width=half_width, height=full_height*(2/3),
        #                      # pos=(-half_width/2, -screen_size[0]*(2/6)),
        #                      fillColor=left_color1, lineColor=None),
        
        # 'right1': visual.Rect(win1, 
        #                       width=half_width, height=full_height,
        #                       pos=(half_width / 2, screen_size[1]*(1/3)),
        #                       # width=half_width, height=full_height*(2/3),
        #                       # pos=(-half_width/2, -screen_size[0]*(2/6)),
        #                       fillColor=right_color1, lineColor=None),
        
        
        'left0': visual.Rect(win0, 
                             width=1, height=2*(2/3),
                             pos=(-1/2, -1/3),
                             fillColor=left_color0, lineColor=None),
        
        'right0': visual.Rect(win0, 
                              width=1, height=2*(2/3),
                              pos=(1/2, -1/3),
                              fillColor=right_color0, lineColor=None),
        
        'left1': visual.Rect(win1, 
                             width=1, height=2*(2/3),
                             pos=(-1/2, 1/3),
                             fillColor=left_color1, lineColor=None),
        
        'right1': visual.Rect(win1, 
                              width=1, height=2*(2/3),
                              pos=(1/2, 1/3),
                              fillColor=right_color1, lineColor=None),
        
        'line0': visual.Rect(win0, 
                             width=LINE_WIDTH, height=2,
                             pos=(0, 0), fillColor=LINE_COLOR, lineColor=None),
        'line1': visual.Rect(win1,
                             width=LINE_WIDTH, height=2,
                             pos=(0, 0), fillColor=LINE_COLOR, lineColor=None)

    }

    # Draw in order: left, right, line
    rects['left0'].draw()
    rects['right0'].draw()
    rects['line0'].draw()
    win0.flip()

    rects['left1'].draw()
    rects['right1'].draw()
    rects['line1'].draw()
    win1.flip()
    
# %% --- Initial color assignment ---

# left_color0, right_color0 = colors['blue_left'], colors['blue_right']
# left_color1, right_color1 = colors['yellow_left'], colors['yellow_right']

# left_color0, right_color0 = colors['blue_control_white'],colors['blue_ipRGC_white']
# left_color1, right_color1 = colors['yellow_control_white'],colors['yellow_ipRGC_white']

left_color0, right_color0 = colors['blue_ipRGC_white'],colors['blue_control_white']
left_color1, right_color1 = colors['yellow_ipRGC_white'],colors['yellow_control_white']

  
ipRGCFlg = True

# %% --- Main loop ---

draw_and_flip()

while True:
    keys = event.waitKeys(keyList=['escape', 'left', 'right','p',
                                   'r', 't','q', 'w',
                                   'g', 'h','a', 's',
                                   'b', 'n','z', 'x'])

    if 'escape' in keys:
        break
    
    # elif 'left' in keys or 'right' in keys:
    #     if ipRGCFlg:
    #         left_color0 = np.array([-0.60380645, -0.63533249, -0.48031925])
    #         left_color1 = col_control[0,3:]/255*2-1,
    #         right_color0 = np.array([-0.60380645, -0.63533249, -0.48031925]),
    #         right_color1 = col_control[0,3:]/255*2-1
    #         ipRGCFlg = False
         
    #     else:
    #         left_color0 = col_ipRGC[0,:3]/255*2-1,
    #         left_color1 = col_ipRGC[0,3:]/255*2-1,
    #         right_color0 = col_ipRGC[0,:3]/255*2-1,
    #         right_color1 = col_ipRGC[0,3:]/255*2-1
    #         ipRGCFlg = True
            
        # left_color0, right_color0 = right_color0, left_color0
        # left_color1, right_color1 = right_color1, left_color1
        draw_and_flip()
        
    elif 'r' in keys:
        # Swap colors
        left_color0[0] = left_color0[0]+(1/(255*2+1))
        print(left_color0)
        draw_and_flip()
        
    elif 't' in keys:
        # Swap colors
        left_color0[0] = left_color0[0]-(1/(255*2+1))
        print(left_color0)
        draw_and_flip()
 
    elif 'g' in keys:
        # Swap colors
        left_color0[1] = left_color0[1]+(1/(255*2+1))
        print(left_color0)
        draw_and_flip()
 
    elif 'h' in keys:
        # Swap colors
        left_color0[1] = left_color0[1]-(1/(255*2+1))
        print(left_color0)
        draw_and_flip()
 
    elif 'b' in keys:
        # Swap colors
        left_color0[2] = left_color0[2]+(1/(255*2+1))
        print(left_color0)
        draw_and_flip()
 
    elif 'n' in keys:
        # Swap colors
        left_color0[2] = left_color0[2]-(1/(255*2+1))
        print(left_color0)
        draw_and_flip()
        
    elif 'q' in keys:
        # Swap colors
        left_color1[0] = left_color1[0]+(1/(255*2+1))
        print(left_color1)
        draw_and_flip()
 
    elif 'w' in keys:
        # Swap colors
        left_color1[0] = left_color1[0]-(1/(255*2+1))
        print(left_color1)
        draw_and_flip()
        
    elif 'a' in keys:
        # Swap colors
        left_color1[1] = left_color1[1]+(1/(255*2+1))
        print(left_color1)
        draw_and_flip()
 
    elif 's' in keys:
        # Swap colors
        left_color1[1] = left_color1[1]-(1/(255*2+1))
        print(left_color1)
        draw_and_flip()
 
    elif 'z' in keys:
        # Swap colors
        left_color1[2] = left_color1[2]+(1/(255*2+1))
        print(left_color1)
        draw_and_flip()
        
    elif 'x' in keys:
        # Swap colors
        left_color1[2] = left_color1[2]-(1/(255*2+1))
        print(left_color1)
        draw_and_flip()
        
    elif 'p' in keys: # Save left_color0 to a JSON file
        now = datetime.now().strftime("%Y%m%d_%H%M%S")
        save_filename = f"../source/calibrated/left_color0_{now}.json"
        with open(save_filename, 'w') as f:
            json.dump({"blue_ipRGC_white":left_color0.tolist(),
                       "blue_control_white":right_color0.tolist(),
                       "yellow_ipRGC_white":left_color1.tolist(),
                       "yellow_control_white":right_color1.tolist(),
                       }, f)
        print(f"left_color0 saved to {os.path.abspath(save_filename)}")


# %% --- Exit ---

win0.close()
win1.close()
core.quit()