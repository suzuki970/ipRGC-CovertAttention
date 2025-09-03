#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr  9 23:51:47 2025

@author: yutasuzuki
"""


import numpy as np
from psychopy import visual, core, event
from PyQt6.QtCore import QThread
from PIL import Image
import cv2
import json

import lib.config as config


# %%

def warp_image_from_json(img, json_path):
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    original = np.float32(data["original"])
    adjusted = np.float32(data["adjusted"])

    assert original.shape == adjusted.shape, "Point count mismatch"

    H, status = cv2.findHomography(original, adjusted, method=0)  # method=0: least squares
    warped = cv2.warpPerspective(img, H, (img.shape[1], img.shape[0]))

    warped_pil = Image.fromarray(cv2.cvtColor(warped, cv2.COLOR_BGR2RGB))
    return warped_pil


# %% --- Main loop ---

class StimulusThread(QThread):
    
    def __init__(self,gazeMode=True):
        super().__init__()
        
        self._running = True
        self.currentLight_ipRGC = True
        self.gazeMode = gazeMode
        self.textcount=0
        self.text = [
            "本研究では、特殊な光を用いてユーザに意識させることなく\n\n集中力向上や疲労感をやわらげる技術の探求を行っています。",
            "ipRGCという目の光受容体をうまく利用することで、\n\nユーザに気づかせることなく波長を制御できる\n\n「ステルス光」が設計できます。",
            "この光を浴びながら作業をすることで、タスクの効率化や",
            "眠気・疲労の軽減といった効果あることを発見しました。",
        ]
        
        if self.gazeMode:
            self.class_name = ["left","right"]
        else:
            self.class_name = ["ipRGC+","ipRGC-"]

        # % --------- Create windows ---------

        self.win_blue = visual.Window(
            size=config.screenSize[config.SCREEN_NUM_YELLOW],
            screen=config.SCREEN_NUM_YELLOW, 
            color=config.LUMINANCE_BACKGROUND,
            # units='pix', 
            units='norm', 
            fullscr=config.FULL_SCREEN
            )
        
        self.win_yellow = visual.Window(
            size=config.screenSize[config.SCREEN_NUM_BLUE], 
            screen=config.SCREEN_NUM_BLUE,
            color=config.LUMINANCE_BACKGROUND, 
            # units='pix', 
            units='norm', 
            fullscr=config.FULL_SCREEN
            )
        
        self.fps = self.win_blue.getActualFrameRate()
        
        if self.fps is not None:
            print(f"Estimated FPS: {self.fps:.2f}")
        else:
            self.fps=30
            print("FPS could not be determined reliably")

        
        # half_width_win_blue = self.win_blue.size[0]/2
        # half_height_win_blue = self.win_blue.size[1]/2
        
        # full_width_win_blue = self.win_blue.size[0]
        # full_height_win_blue = self.win_blue.size[1]

        # half_width_win_yellow = self.win_yellow.size[0]/2
        # half_height_win_yellow = self.win_yellow.size[1]/2
        
        # full_width_win_yellow = self.win_yellow.size[0]
        # full_height_win_yellow = self.win_yellow.size[1]


        self.rects = {
            
            #%%
            # 'left_blue': visual.Rect(self.win_blue, width=half_width_win_blue, height=full_height_win_blue, 
            #                      pos=(-half_width_win_blue / 2, 0), 
            #                      fillColor=config.colors["blue_left"], lineColor=None),
            
            # 'right_blue': visual.Rect(self.win_blue, width=half_width_win_blue, height=full_height_win_blue, 
            #                       pos=(half_width_win_blue / 2, 0), 
            #                       fillColor=config.colors["blue_right"], lineColor=None),
            
            # 'left_yellow': visual.Rect(self.win_yellow, width=half_width_win_yellow, height=full_height_win_yellow, 
            #                      pos=(-half_width_win_yellow / 2, 0), 
            #                      fillColor=config.colors["yellow_left"], lineColor=None),
            
            # 'right_yellow': visual.Rect(self.win_yellow, width=half_width_win_yellow, height=full_height_win_yellow, 
            #                       pos=(half_width_win_yellow / 2, 0), 
            #                       fillColor=config.colors["yellow_right"], lineColor=None),
            
            #%%
            # 'white_left_blue': visual.Rect(self.win_blue, 
            #                       width=half_width_win_blue, height=full_height_win_blue,
            #                       pos=(-half_width_win_blue / 2, 0),fillColor=config.colors["blue_ipRGC_white"], lineColor=None),
            # 'white_right_blue': visual.Rect(self.win_blue, 
            #                       width=half_width_win_blue, height=full_height_win_blue, 
            #                       pos=(half_width_win_blue / 2, 0),fillColor=config.colors["blue_control_white"], lineColor=None),
            
            # 'white_left_yellow': visual.Rect(self.win_yellow, 
            #                         width=half_width_win_yellow, height=full_height_win_yellow, 
            #                         pos=(-half_width_win_yellow / 2, 0),
            #                         fillColor=config.colors["yellow_ipRGC_white"], lineColor=None),
            
            # 'white_right_yellow': visual.Rect(self.win_yellow, 
            #                         width=half_width_win_yellow, height=full_height_win_yellow, 
            #                         pos=(half_width_win_yellow / 2, 0),
            #                         fillColor=config.colors["yellow_control_white"], lineColor=None),
            
            #%%
            'white_half_left_blue': visual.Rect(self.win_blue, 
                                                width=1, height=2*(2/3),
                                                pos=(-1/2, -1/3),
                                                fillColor=config.colors["blue_ipRGC_white"], lineColor=None),
            
            'white_half_right_blue': visual.Rect(self.win_blue, 
                                                 width=1, height=2*(2/3),
                                                 pos=(1/2, -1/3),
                                                 fillColor=config.colors["blue_control_white"], lineColor=None),
            
            'white_half_left_yellow': visual.Rect(self.win_yellow, 
                                                  width=1, height=2*(2/3),
                                                  pos=(-1/2, 1/3),
                                                  fillColor=config.colors["yellow_ipRGC_white"], lineColor=None),
            
            'white_half_right_yellow': visual.Rect(self.win_yellow, 
                                                width=1, height=2*(2/3),
                                                   pos=(1/2, 1/3),
                                                   fillColor=config.colors["yellow_control_white"], lineColor=None),
            
            #%%
            # 'ipRGC0': visual.Rect(self.win_blue, 
            #                       width=full_width_win_blue, height=full_height_win_blue, 
            #                       fillColor=config.colors["blue_ipRGC"], lineColor=None),
            # 'ipRGC1': visual.Rect(self.win_yellow, 
            #                       width=full_width_win_yellow, height=full_height_win_yellow, 
            #                       fillColor=config.colors["yellow_ipRGC"], lineColor=None),
            # 'control0': visual.Rect(self.win_blue, 
            #                         width=full_width_win_blue, height=full_height_win_blue, 
            #                         fillColor=config.colors["blue_control"], lineColor=None),
            # 'control1': visual.Rect(self.win_yellow, 
            #                         width=full_width_win_yellow, height=full_height_win_yellow, 
            #                         fillColor=config.colors["yellow_control"], lineColor=None),
            'line0': visual.Rect(self.win_blue, 
                                 width=config.LINE_WIDTH, height=2,
                                 pos=(0, 0), fillColor=config.LINE_COLOR, lineColor=None),
            'line1': visual.Rect(self.win_yellow,
                                 width=config.LINE_WIDTH, height=2,
                                 pos=(0, 0), fillColor=config.LINE_COLOR, lineColor=None),
            
            #%%
            # 'white_ipRGC0': visual.Rect(self.win_blue, 
            #                       width=full_width_win_blue, height=full_height_win_blue, 
            #                       fillColor=config.colors["blue_ipRGC_white"], lineColor=None),
            # 'white_ipRGC1': visual.Rect(self.win_yellow, 
            #                       width=full_width_win_yellow, height=full_height_win_yellow, 
            #                       fillColor=config.colors["yellow_ipRGC_white"], lineColor=None),
            # 'white_control0': visual.Rect(self.win_blue, 
            #                         width=full_width_win_blue, height=full_height_win_blue, 
            #                         fillColor=config.colors["blue_control_white"], lineColor=None),
            # 'white_control1': visual.Rect(self.win_yellow, 
            #                         width=full_width_win_yellow, height=full_height_win_yellow, 
            #                         fillColor=config.colors["yellow_control_white"], lineColor=None),
            
            #%%
            'white_half_ipRGC0': visual.Rect(self.win_blue, 
                                             width=2, height=2*(2/3), 
                                             pos=(0, -1/3),
                                             fillColor=config.colors["blue_ipRGC_white"], lineColor=None),
            'white_half_ipRGC1': visual.Rect(self.win_yellow, 
                                             width=2, height=2*(2/3), 
                                             pos=(0, 1/3),
                                             fillColor=config.colors["yellow_ipRGC_white"], lineColor=None),
            
            'white_half_control0': visual.Rect(self.win_blue, 
                                              width=2, height=2*(2/3), 
                                             pos=(0, -1/3),
                                               fillColor=config.colors["blue_control_white"], lineColor=None),
            'white_half_control1': visual.Rect(self.win_yellow, 
                                              width=2, height=2*(2/3), 
                                              pos=(0, 1/3),
                                              fillColor=config.colors["yellow_control_white"], lineColor=None),


        }


    #% --------------- Initial color assignment ---------------
    def run(self):
        
        self.show_instruction("左右の光を見比べてみましょう。")
        
        self.gazeMode = True
        self.draw_and_flip()
        # self.draw_image_with_rects()
        
        event.waitKeys(keyList=['down'])
        self.show_instruction("メガネをかけて、もう一度見比べてみましょう。")
        self.draw_and_flip()

        event.waitKeys(keyList=['down'])
        
        self.show_instruction("これらの2つの光に対する瞳孔径の変化を見てましょう。\n\nこれから表示される文章を読んでみてください。")
        self.gazeMode = False
        
        message="読み込み中・・・"
        text0 = visual.TextStim(self.win_blue, text=message,
                                font=config.FONT_INSTRUCTION,alignText='center',anchorHoriz='center',
                                color='white', 
                                pos=(0, -1/3),
                                height=config.FONTSIZE_MSG,
                                wrapWidth=1.8,
                                # wrapWidth=self.win_blue.size[0]*0.8
                                )
        
        text1 = visual.TextStim(self.win_yellow, text=message,
                                font=config.FONT_INSTRUCTION,alignText='center', anchorHoriz='center',
                                color='white', 
                                pos=(0, 1/3),
                                height=config.FONTSIZE_MSG,
                                wrapWidth=1.8,
                                # wrapWidth=self.win_yellow.size[0]*0.8
                                )
        
        for i in range(int(config.TIME_FADEIN * self.fps)):
            opacity = i / (config.TIME_FADEIN * self.fps)*2-1
            text0.contrast = opacity
            text1.contrast = opacity
            text0.draw()
            self.win_blue.flip()
            text1.draw()
            self.win_yellow.flip()
            core.wait(1.0 / self.fps)

        # self.draw_and_flip()
        
    def draw_striped_pattern(self, win, width, height, num_stripes=10, color1='white_left', color2='white_right', is_blue=True):
        stripe_width = width / num_stripes
        stripe_height = height / num_stripes
        
        for i in range(num_stripes):
            
            y_pos = height / 2 - stripe_height / 2 - i * stripe_height
     
            if i % 2 == 1:
                color_key = color1
            else:
                color_key = color2
                
            stripe = visual.Rect(
                 win=win,
                 width=width,
                 height=stripe_height,
                 pos=(0, y_pos),
                 fillColor=config.colors[color_key],
                 lineColor=None
            )
            stripe.draw()
            
    
    # %%
    def draw_image_with_rects(self):
    
        # img1 = cv2.imread("source/colored_whale_image1.png")
        # img2 = cv2.imread("source/colored_whale_image2.png")
        img1 = cv2.imread("source/pink_whale_image1.png")
        img2 = cv2.imread("source/pink_whale_image2.png")
        
        warped1 = warp_image_from_json(img1, "screen1_points.json")
        warped2 = warp_image_from_json(img2, "screen2_points.json")
        
        stim1 = visual.ImageStim(
            win=self.win_blue,
            image=warped1,
            size=self.win_blue.size
        )
        
        # plt.imshow(img1)
        # plt.imshow(warped)
        # plt.imshow(warped_pil)

        stim2 = visual.ImageStim(
            win=self.win_yellow,
            image=warped2,
            size=self.win_yellow.size
        )
        
        stim1.draw()
        stim2.draw()
        self.win_blue.flip()
        self.win_yellow.flip()
        # img_path_1 = "source/colored_whale_image1.png"
        # img_path_2 = "source/colored_whale_image2.png"
        
        # img_stim_0 = visual.ImageStim(win=self.win_blue, image=img_path_1, size=self.win_blue.size)
        # img_stim_1 = visual.ImageStim(win=self.win_yellow, image=img_path_2, size=self.win_yellow.size)
        
        # img_stim_0.draw()
        # self.win_blue.flip()
        
        # img_stim_1.draw()
        # self.win_yellow.flip()


    # %%

    def switch_screen(self,events):
        
        if 'left' in events or 'right' in events:
            
            if self.gazeMode:
                
                tmp_blue_left, tmp_yellow_left = config.colors["blue_left"], config.colors["yellow_left"]
                config.colors["blue_left"], config.colors["yellow_left"] = config.colors["blue_right"], config.colors["yellow_right"]
                config.colors["blue_right"], config.colors["yellow_right"] = tmp_blue_left, tmp_yellow_left

            self.draw_and_flip()

    def show_instruction(self, message):
        
        text0 = visual.TextStim(self.win_blue, 
                                text=message,
                                font=config.FONT_INSTRUCTION,
                                # alignText='center',
                                # anchorHoriz='center',
                                color='white', 
                                # height=0,
                                pos=(0, -1/3),
                                height=config.FONTSIZE_MSG,
                                wrapWidth=1.8,
                                
                                )
        
        text1 = visual.TextStim(self.win_yellow, text=message,
                                font=config.FONT_INSTRUCTION,
                                # alignText='center', anchorHoriz='center',
                                color='white', 
                                # height=0
                                pos=(0, 1/3),
                                height=config.FONTSIZE_MSG,
                                wrapWidth=1.8,
                                
                                )
        

        
        for i in range(int(config.TIME_FADEIN * self.fps)):
            opacity = i / (config.TIME_FADEIN * self.fps)*2-1
            text0.contrast = opacity
            text1.contrast = opacity
            text0.draw()
            self.win_blue.flip()
            text1.draw()
            self.win_yellow.flip()
            core.wait(1.0 / self.fps)
        
        event.waitKeys(keyList=['down'])

        for i in range(int(config.TIME_FADEOUT * self.fps)):
            opacity = 1 - (i / (config.TIME_FADEOUT * self.fps))*2-1
            text0.contrast = opacity
            text1.contrast = opacity
            text0.draw()
            self.win_blue.flip()
            text1.draw()
            self.win_yellow.flip()
            core.wait(1.0 / self.fps)
                 
    #% --------------- Helper function to create rectangles based on current color order ---------------

    def draw_and_flip(self):
    
        if self.gazeMode:
            
            # self.draw_striped_pattern(
            #     win=self.win_blue,
            #     width=self.win_blue.size[0],
            #     height=self.win_blue.size[1],
            #     num_stripes=6,
            #     color1="blue_ipRGC_white",
            #     color2="blue_control_white",
            #     is_blue=True
            # )
            
            # self.draw_striped_pattern(
            #     win=self.win_yellow,
            #     width=self.win_yellow.size[0],
            #     height=self.win_yellow.size[1],
            #     num_stripes=6,
            #     color1="yellow_ipRGC_white",
            #     color2="yellow_control_white",
            #     is_blue=False
            # )
            self.rects[config.white+'left_blue'].draw()
            self.rects[config.white+'right_blue'].draw()
            self.rects['line0'].draw()
            self.win_blue.flip()
        
            self.rects[config.white+'left_yellow'].draw()
            self.rects[config.white+'right_yellow'].draw()
            self.rects['line1'].draw()
            self.win_yellow.flip()

        else:
            

            if self.currentLight_ipRGC:
                
                text0 = visual.TextStim(self.win_blue, text=self.text[self.textcount],
                                        font=config.FONT_INSTRUCTION,
                                        # alignText='center',anchorHoriz='center',
                                        color=config.colors["blue_control_white"],
                                        pos=(0, -1/3),
                                        height=config.FONTSIZE_MSG,
                                        wrapWidth=1.8,
                                        
                                        )
                text1 = visual.TextStim(self.win_yellow, text=self.text[self.textcount],
                                        font=config.FONT_INSTRUCTION,
                                        # alignText='center', anchorHoriz='center',
                                        color=config.colors["yellow_control_white"], 
                                        pos=(0, 1/3),
                                        height=config.FONTSIZE_MSG,
                                        wrapWidth=1.8,
                                        
                                        # , wrapWidth=self.win_yellow.size[0]*0.8
                                        )
                
                self.rects[config.white+'ipRGC0'].draw()
                self.rects[config.white+'ipRGC1'].draw()
                self.currentLight_ipRGC = False
       
            else:
            
                text0 = visual.TextStim(self.win_blue, text=self.text[self.textcount],
                                        font=config.FONT_INSTRUCTION,
                                        # alignText='center',anchorHoriz='center',
                                        color=config.colors["blue_ipRGC_white"],
                                        height=config.FONTSIZE_MSG,
                                        pos=(0, -1/3),
                                        wrapWidth=1.8,
                                        
                                        # wrapWidth=self.win_blue.size[0]*0.8
                                        )
                text1 = visual.TextStim(self.win_yellow, text=self.text[self.textcount],
                                        font=config.FONT_INSTRUCTION,
                                        # alignText='center', anchorHoriz='center',
                                        color=config.colors["yellow_ipRGC_white"], 
                                        height=config.FONTSIZE_MSG,
                                        pos=(0, 1/3),
                                        wrapWidth=1.8,
                                        
                                        # wrapWidth=self.win_yellow.size[0]*0.8
                                        )
            
                self.rects[config.white+'control0'].draw()
                self.rects[config.white+'control1'].draw()
                self.currentLight_ipRGC = True

            text0.draw()
            text1.draw()
            self.win_blue.flip()
            self.win_yellow.flip()
            self.textcount+=1
            print(self.textcount)
        
    def fetch_light_status(self):
        return self.currentLight_ipRGC
    
    def stop(self):
        self._running = False
        self.win_blue.close()
        self.win_yellow.close()
        