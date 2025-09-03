#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr  1 17:46:47 2025

@author: yutasuzuki
"""

import sys
from pyglet import canvas
display = canvas.Display()
    
import argparse
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QApplication
from PupilNeonGUI import PupilNeonGUI

# %%

def parse_args():

    parser = argparse.ArgumentParser(description="PupilNeon Live Visualizer")
    parser.add_argument("--demo", action="store_true", help="Run in demo mode (default: off)")
    parser.add_argument("--plotLength", type=int, default=10, help="Length of time window for plot (seconds)")
    parser.add_argument("--gaze", action="store_true")
    
    return parser.parse_args()

# def gradient_color(relative_pos):
#     # Clamp between -1 and 1
#     relative_pos = max(-1.0, min(1.0, relative_pos))
    
#     base = QColor(200, 200, 200)

#     if relative_pos < 0:
#         strength = abs(relative_pos)
#         r = base.red() * (1 - strength)
#         g = base.green() + (255 - base.green()) * strength
#         b = base.blue() + (255 - base.blue()) * strength
#     else:
#         strength = relative_pos
#         r = base.red() + (255 - base.red()) * strength
#         g = base.green() + (255 - base.green()) * strength
#         b = base.blue() * (1 - strength)

#     return QColor(int(r), int(g), int(b)).name()  # return hex string like '#AABBCC'
        
# def get_border_style(gaze_side,self.class_name):
#     color = COLOR_MAIN1 if gaze_side == self.class_name[0] else COLOR_MAIN2 # Cyan or Yellow
#     return f"""
#         QWidget {{
#             border: 4px solid {color};
#             border-radius: 10px;
#             margin: 5px;
#         }}
#     """
    
# %%

    
if __name__ == "__main__":
    
    args = parse_args()
    
    app = QApplication(sys.argv)
    
    window = PupilNeonGUI(demo=args.demo,plotLength=args.plotLength,gazeMode=args.gaze)
    window.show()
    
    sys.exit(app.exec())