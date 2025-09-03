#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr  9 23:51:48 2025

@author: yutasuzuki
"""

import numpy as np
import cv2
import time
import glob
import math
import pandas as pd

from pupil_labs.realtime_api.simple import discover_one_device

from PyQt6.QtCore import QTimer,Qt
from PyQt6.QtGui import QColor,QFont

from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QHBoxLayout
from PyQt6.QtWidgets import QSpacerItem, QSizePolicy, QLabel

from pyqtgraph import ImageView
import pyqtgraph as pg
from scipy.stats import norm

from StimulusThread import StimulusThread

import lib.config as config
from lib.zeroInterp import zeroInterp


# %%

# def smooth(y, window_size):
#     if len(y) < window_size:
#         return np.array(y)
#     weights = np.ones(window_size) / window_size
#     return np.convolve(y, weights, mode="valid")

def style_button( button, color=config.COLOR_MAIN1):
    button.setStyleSheet(f"""
        QPushButton {{
            background-color: {color};
            color: black;
            border: none;
            border-radius: 15px;
            padding: 10px 20px;
        }}
        QPushButton:hover {{
            background-color: #00CCCC;
        }}
    """)

def capture_gui(widget, save_path, frame_num):
    pixmap = widget.grab()
    filename = f"{save_path}frame_{frame_num:04d}.png"
    pixmap.save(filename)
    
# def load_latest_data(filename):

#     with open(filename, "rb") as f:
#         data = pickle.load(f)
        
#     return pd.DataFrame(data)

# %%


class PupilNeonGUI(QMainWindow):
    def __init__(self, demo=True, plotLength=10,gazeMode=True):
        
        super().__init__()

        self.demo = demo
        self.plotLength = plotLength
        self.gazeMode = gazeMode
        
        if self.gazeMode:
            self.class_name = ["left","right"]
        else:
            self.class_name = ["ipRGC+","ipRGC-"]

        self.data = pd.DataFrame()
        self.fs = 10
        self.window_size = int(0.1*int(self.fs))
        
        self.max_data_points = self.plotLength * self.fs
        self.is_running = False
        self.replay = False
        self.start = False
        self.fin = False
        self.showEye = "left"
        
        self.last_index = -1
        self.frame_count = 0
        self.save_dir = "./capture/"

        if not self.demo:
            self.connect_neon()
 
        filenames = glob.glob("results/*")
        
        filenames.sort()
        if len(filenames)>0:
            self.df = pd.read_parquet(filenames[-1])
            
        self.init_ui()
        
        self.timer = QTimer()
        self.timer.setInterval(int(1/self.fs*1000)) 
        self.timer.timeout.connect(self.fetch_pupil_data)
        self.timer.start()



    def connect_neon(self):
    
        self.device = discover_one_device()
        if self.device is None:
            print("No device found.")
            
        print(f"Phone IP address: {self.device.phone_ip}")
  
    def init_ui(self):
        
        self.setWindowTitle("Pupil Neon Live Visualization")
        # Get screen size
        screens = QApplication.screens()
        print(f"Screen number:{screens}")
        # screen = QApplication.primaryScreen()
        screen = screens[config.SCREEN_NUM_GUI]
        
        screen_geometry = screen.availableGeometry()
        
        screen_width = screen_geometry.width()
        screen_height = screen_geometry.height()
        
        # Set window size to 80% of the screen size
        window_width = int(screen_width * config.SCREEN_RANGE)
        window_height = int(screen_height * config.SCREEN_RANGE)
        
        # Center the window on the screen
        x = int((screen_width - window_width) / 2)
        y = int((screen_height - window_height) / 2)
        
        # Set geometry
        self.setGeometry(x, y, window_width, window_height)
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        self.central_widget.setStyleSheet("""
        QWidget {
                background-color: #000000;
            }
        """)


        # %%

        main_layout = QVBoxLayout()
        self.central_widget.setLayout(main_layout)
        
        top_layout = QHBoxLayout()
        middle_layout = QHBoxLayout()
        button_layout = QHBoxLayout()

        bar_layout = QHBoxLayout()
        image_layout = QHBoxLayout()

        main_layout.addLayout(top_layout, stretch=4)

        spacer_w = QSpacerItem(100, 0, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)
        spacer_h = QSpacerItem(0, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
    
        main_layout.addItem(spacer_h)

        middle_layout.addItem(spacer_w)
        middle_layout.addLayout(bar_layout, stretch=1)
        middle_layout.addItem(spacer_w)
        middle_layout.addLayout(image_layout, stretch=2)

        main_layout.addLayout(middle_layout, stretch=2)    

        main_layout.addItem(spacer_h)
        main_layout.addLayout(button_layout)


        # %%

        # Graph area
        self.graph_widget = pg.PlotWidget()
        self.graph_widget.setBackground("black")
        self.graph_widget.setYRange(2, 6)
        self.graph_widget.setXRange(0, self.plotLength)

        # self.graph_widget.setLabel("left", "Pupil Size (mm)", **label_style)
        label_style = {"color": "white", "font-size": f"{config.FONTSIZE_LABELS}pt", "font-family": config.FONT_LABEL}
        
        self.graph_widget.setLabel("left", "瞳孔径 (mm)", **label_style)
        # self.graph_widget.setLabel("left",f'<font face="{config.FONT_LABEL}">瞳孔径 (mm)</font>')
        left_label = f'<span style="font-family: {config.FONT_LABEL}; font-size: {config.FONTSIZE_LABELS}pt; color: white;">瞳孔径 (mm)</span>'
        

        self.graph_widget.setLabel("bottom", "時間 (s)", **label_style)
        # self.graph_widget.setLabel("bottom", "Time", **label_style)
        
        
        self.graph_widget.getAxis("left").setPen(pg.mkPen(color='white', width=2))
        self.graph_widget.getAxis("left").setTextPen(pg.mkPen(color='white'))
        self.graph_widget.getAxis("left").setTickFont(QFont(config.FONT_GUI, config.FONTSIZE_LABELS))
        # self.graph_widget.getAxis("left").setLabel(QFont(config.FONT_GUI, config.FONTSIZE_LABELS))

        self.graph_widget.getAxis("bottom").setPen(pg.mkPen(color='white', width=2))
        self.graph_widget.getAxis("bottom").setTextPen(pg.mkPen(color='white'))
        self.graph_widget.getAxis("bottom").setTickFont(QFont(config.FONT_GUI, config.FONTSIZE_LABELS))

        # Create curves with dummy data
        self.glow = {
            "state1":self.graph_widget.plot([0], [0], pen=pg.mkPen(QColor(config.COLOR_MAIN1).lighter(190), width=12)),
            "state2":self.graph_widget.plot([0], [0], pen=pg.mkPen(QColor(config.COLOR_MAIN2).lighter(190), width=12)),
            }
        
        self.curve = {
            "state1":self.graph_widget.plot([0], [0], pen=pg.mkPen(QColor(config.COLOR_MAIN1), width=10)),
            "state2":self.graph_widget.plot([0], [0], pen=pg.mkPen(QColor(config.COLOR_MAIN2), width=10)),
            }
        
        # self.legend = pg.LegendItem((100, 60))
        self.legend = pg.LegendItem((100, 20))

        self.legend.setParentItem(self.graph_widget.getPlotItem())
        
        # Create custom font labels using HTML
        left_label = f"<span style=\"font-family:'{config.FONT_GUI}'; font-size:{config.FONTSIZE_LEGEND}pt; color:white; \">{self.class_name[0]}</span>"
        right_label = f"<span style=\"font-family:'{config.FONT_GUI}'; font-size:{config.FONTSIZE_LEGEND}pt; color:white; \">{self.class_name[1]}</span>"

        # Add to legend
        self.legend.addItem(self.curve["state1"], left_label)
        self.legend.addItem(self.curve["state2"], right_label)
            
        self.legend.anchor((1, 0), (1, 0))  # top-right

        # top_layout.addWidget(self.graph_widget)
        top_layout.addWidget(self.graph_widget)

        # %% bar

        self.bar_widget = pg.PlotWidget()

        self.bar_left = pg.BarGraphItem(x=[0.3], height=[0], width=0.2, brush=config.COLOR_MAIN1)
        self.bar_right = pg.BarGraphItem(x=[0.6], height=[0], width=0.2, brush=config.COLOR_MAIN2)

        self.bar_widget.addItem(self.bar_left)
        self.bar_widget.addItem(self.bar_right)

        self.bar_widget.setYRange(0, 6)
        self.bar_widget.setXRange(0.1, 0.8)
        # self.bar_widget.setLabel("bottom", "Avg Pupil Size (mm)", **label_style)
        # self.bar_widget.setLabel("left", "Ave pupil size (mm)", **label_style)
        self.bar_widget.setLabel("left", "平均瞳孔径 (mm)", **label_style)
        self.bar_widget.setLabel("bottom", " ", **label_style)
        
        self.bar_widget.getAxis("left").setPen(pg.mkPen(color='white', width=2))
        self.bar_widget.getAxis("left").setTextPen(pg.mkPen(color='white'))
        self.bar_widget.getAxis("left").setTickFont(QFont(config.FONT_GUI, config.FONTSIZE_LABELS))

        self.bar_widget.getAxis("bottom").setTicks([[(0.3, self.class_name[0]), (0.6, self.class_name[1])]])
        self.bar_widget.getAxis("bottom").setPen(pg.mkPen(color='white', width=2))
        self.bar_widget.getAxis("bottom").setTextPen(pg.mkPen(color='white'))
        self.bar_widget.getAxis("bottom").setTickFont(QFont(config.FONT_LABEL, config.FONTSIZE_LABELS))

        bar_layout.addWidget(self.bar_widget, stretch=1)
        
        # %% Image display area (right side)

        self.scene_image_view = ImageView()
        self.scene_image_view.ui.histogram.hide()
        self.scene_image_view.ui.roiBtn.hide()
        self.scene_image_view.ui.menuBtn.hide()
        # image_layout.addWidget(self.scene_image_view, stretch=1)
        self.eye_image_view = ImageView()
        self.eye_image_view.ui.histogram.hide()
        self.eye_image_view.ui.roiBtn.hide()
        self.eye_image_view.ui.menuBtn.hide()
        
        self.eye_label = QLabel(f"Eye camera: {self.showEye.capitalize()} eye")
        # self.eye_label.setStyleSheet(f"color: white; font-size: {config.FONTSIZE_LABELS}pt,font-family: {config.FONT_LABEL};")
        self.eye_label.setFont(QFont(config.FONT_GUI, config.FONTSIZE_LABELS))
        self.eye_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        for view in [self.scene_image_view, self.eye_image_view]:
            view.ui.histogram.hide()
            view.ui.roiBtn.hide()
            view.ui.menuBtn.hide()
            view.setStyleSheet(f"""
                QWidget {{
                    border: 2px solid {config.COLOR_MAIN1};
                    border-radius: 10px;
                    margin: 5px;
                }}
            """)
            # image_layout.addWidget(view)
            
        scene_layout = QVBoxLayout()
        scene_label = QLabel("Scene video")
        scene_label.setFont(QFont(config.FONT_GUI, config.FONTSIZE_LABELS))
        scene_label.setStyleSheet(f"color: white; font-size: {config.FONTSIZE_LABELS}pt,font-family: {config.FONT_LABEL};")
        scene_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        scene_layout.addWidget(scene_label)
        scene_layout.addWidget(self.scene_image_view)
        image_layout.addLayout(scene_layout, stretch=1)

        eye_layout = QVBoxLayout()
        eye_layout.addWidget(self.eye_label)
        eye_layout.addWidget(self.eye_image_view)
        
        image_layout.addLayout(eye_layout, stretch=1)

        # image_layout.addWidget(eye_layout, stretch=1)
        # image_layout.addWidget(self.eye_image_view, stretch=1)
        
    
        # image_layout.addWidget(image_layout, stretch=2)
        middle_layout.addLayout(image_layout, stretch=1)

        # %% button layout

        self.start_button = QPushButton("Start")
        self.start_button.setFont(QFont(config.FONT_GUI, config.FONTSIZE_BUTTON))
        self.start_button.clicked.connect(self.start_measurement)
        style_button(self.start_button, "#5DBA6F")
        button_layout.addWidget(self.start_button)

        self.calibration_button = QPushButton("Replay")
        self.calibration_button.setFont(QFont(config.FONT_GUI, config.FONTSIZE_BUTTON))
        self.calibration_button.clicked.connect(self.replay_pupil_data)
        style_button(self.calibration_button, "#E0B84D")
        button_layout.addWidget(self.calibration_button)

        self.stop_button = QPushButton("Stop")
        self.stop_button.setFont(QFont(config.FONT_GUI, config.FONTSIZE_BUTTON))
        self.stop_button.clicked.connect(self.stop_measurement)
        style_button(self.stop_button, "#D96A5A")
        button_layout.addWidget(self.stop_button)

        self.quit_button = QPushButton("Quit")
        self.quit_button.setFont(QFont(config.FONT_GUI, config.FONTSIZE_BUTTON))
        self.quit_button.clicked.connect(self.quit_application)
        style_button(self.quit_button, "#C0C0C0")
        button_layout.addWidget(self.quit_button)
    
        
    def run_calibration(self):
        
        calibration = self.device.get_calibration()

        print("Scene camera matrix:")
        print(calibration["scene_camera_matrix"][0])
        print("\nScene distortion coefficients:")
        print(calibration["scene_distortion_coefficients"][0])
        
        print("\nRight camera matrix:")
        print(calibration["right_camera_matrix"][0])
        print("\nRight distortion coefficients:")
        print(calibration["right_distortion_coefficients"][0])
        
        print("\nLeft camera matrix:")
        print(calibration["left_camera_matrix"][0])
        print("\nLeft distortion coefficients:")
        print(calibration["left_distortion_coefficients"][0])
        
    def start_measurement(self):
        
        if not self.is_running:
            
            self.stim_thread = StimulusThread(gazeMode = self.gazeMode)
            self.stim_thread.run()

            self.is_running = True
            self.start = False
            self.replay = False
            self.fin = False
            self.last_index = -1

            if not self.demo:
                recording_id = self.device.recording_start()
                print(f"Started recording with id {recording_id}")
            else:
                print("Started demo mode.")
            
            self.data = pd.DataFrame()
            self.activateWindow()
            
    def stop_measurement(self):
        
        if self.is_running:
            if not self.demo:
                # if self.gazeMode:
                    # save_file_name = "results/gaze/pupil_data_%Y%m%d_%H%M%S.parquet"
                # else:
                save_file_name = "results/pupil_data_%Y%m%d_%H%M%S.parquet"
    
                filename = time.strftime(save_file_name)
                # self.data = pd.concat(self.data)
                self.data.to_parquet(filename)
                print(f"Data is saved as {filename}")
    
            if not self.demo:
                self.device.recording_stop_and_save()
        
        self.is_running = False
        self.start = False
        self.replay = False
    
    
    def replay_pupil_data(self):
        
        if self.is_running:
            self.stop_measurement()
        
        self.is_running = False
        self.start = False
        self.replay=True

        filenames = glob.glob("results/*")
        
        filenames.sort()
        if len(filenames)>0:
            print(f"load {filenames[-1]}")
            self.df = pd.read_parquet(filenames[-1])
    
        self.data = pd.DataFrame()
        
        
    def fetch_pupil_data(self):

        if self.replay:
            
            if not self.start:
                self.start_time = time.time()
                self.start = True

            self.data = self.df[self.df["timestamp"]<=(time.time()- self.start_time)]
            self.data = [self.data.iloc[[i]] for i in range(len(self.data))]

            if len(self.data)>0:
    
                self.latest_scene_sample = None
                self.latest_eyevideo_sample = None
    
                self.update_plot()
                
            # capture_gui(self, self.save_dir, self.frame_count)
            # self.frame_count += 1
        if not self.is_running:
            return
        
        if not self.demo:
            
            self.latest_scene_sample, latest_gaze_sample = self.device.receive_matched_scene_video_frame_and_gaze()
            self.latest_eyevideo_sample = self.device.receive_eyes_video_frame()

            if not self.start:
                self.start_time = time.time()    
                self.start = True
                
                if self.stim_thread.fetch_light_status():
                    self.gaze_side = self.class_name[0]
                else:
                    self.gaze_side = self.class_name[1]
                    
            else:
                if self.stim_thread.fetch_light_status():
                    self.gaze_side = self.class_name[1]
                else:
                    self.gaze_side = self.class_name[0]

            
            elapsed = time.time() - self.start_time
            current_index = int(elapsed // 10) % 2
        
            gaze_pos = [latest_gaze_sample.x, latest_gaze_sample.y]
            
            self.latest_scene_sample = cv2.cvtColor(self.latest_scene_sample.bgr_pixels, cv2.COLOR_BGR2RGB)
            self.latest_eyevideo_sample = cv2.cvtColor(self.latest_eyevideo_sample.bgr_pixels, cv2.COLOR_BGR2RGB)
            
            self.latest_scene_sample = cv2.rotate(self.latest_scene_sample, cv2.ROTATE_90_CLOCKWISE)
            self.latest_eyevideo_sample = cv2.rotate(self.latest_eyevideo_sample, cv2.ROTATE_90_CLOCKWISE)

            self.latest_scene_sample = cv2.flip(self.latest_scene_sample, 1)
            self.latest_eyevideo_sample = cv2.flip(self.latest_eyevideo_sample, 1)

            # === Gaze overlay ===
            h, w, _ = self.latest_scene_sample.shape
            x = int(gaze_pos[1])
            y = int(gaze_pos[0])

            if self.gazeMode:
                self.gaze_side = "left" if (w-y) > (y/2) else "right"

            self.data = pd.concat([self.data,
                                   pd.DataFrame({
                                       "timestamp": time.time() - self.start_time,
                                       "pupil_left":latest_gaze_sample.pupil_diameter_left, 
                                       "pupil_right":latest_gaze_sample.pupil_diameter_right, 
                                       "left_x":-1, "right_x":-1, "state1_y":-1, "state2_y":-1, 
                                       "gaze_side":self.gaze_side, 
                                       "gaze_x":latest_gaze_sample.x, 
                                       "gaze_y":latest_gaze_sample.y,
                                       # "scene_sample":self.latest_scene_sample,
                                       # "eyevideo_sample":self.latest_eyevideo_sample,
                                       },index=[0])])

            cv2.circle(self.latest_scene_sample, (x, y), 15, (255, 0, 0), -1)
      
        else:
            if not self.start:
                self.start_time = time.time()
                self.start = True

            elapsed = time.time() - self.start_time
            current_index = int(elapsed // 10) % 2

            self.data = self.df[self.df["timestamp"]<=(time.time()- self.start_time)]
            self.data = [self.data.iloc[[i]] for i in range(len(self.data))]

            if len(self.data)>0:
    
                self.latest_scene_sample = None
                self.latest_eyevideo_sample = None
    
                self.update_plot()

        self.update_plot()
               
        if current_index != self.last_index:                        
            self.last_index = current_index
            self.stim_thread.draw_and_flip()

        if time.time() - self.start_time > 40:
            
            self.fin = True
            self.stop_measurement()

            self.preprocessing()
            self.update_timecourse()

            time.sleep(0.2)
            self.stim_thread.show_instruction("デモは終了です\n\n瞳孔径の変化をご覧ください")
            self.activateWindow()

            # self.replay_pupil_data()

    def preprocessing(self):
        
        recent_data =  self.data.copy()
        self.data[["left_x","right_x","state1_y","state2_y"]] = np.nan

        self.data.loc[self.data["gaze_side"]==self.class_name[0],"left_x"] = self.data[self.data["gaze_side"]==self.class_name[0]]["timestamp"]
        self.data.loc[self.data["gaze_side"]==self.class_name[1],"right_x"] = self.data[self.data["gaze_side"]==self.class_name[1]]["timestamp"]
        
        tmp_pupil = recent_data['pupil_'+self.showEye].values.copy()
        
        d = np.diff(tmp_pupil)
    
        q75, q25 = np.percentile(d, [75 ,25])
        IQR = q75 - q25

        lower = q25 - IQR*6
        upper = q75 + IQR*6

        d_witout_outliar = d[(d > lower) & (d < upper)]
    
        param = norm.fit(d_witout_outliar)
        
        (a,b) = norm.interval(0.99, loc=param[0], scale=param[1])

        ind = np.argwhere(abs(np.diff(tmp_pupil)) > b).reshape(-1)
        tmp_pupil[ind] = 0  

        recent_data['pupil_interp_'+self.showEye] = zeroInterp(tmp_pupil.copy(),10,1)["pupilData"].reshape(-1)            
        recent_data['pupil_mvAve_'+self.showEye] = recent_data['pupil_interp_'+self.showEye].rolling(window=1,center=True).mean()

        self.data.loc[self.data["gaze_side"]==self.class_name[0],"state1_y"] = recent_data[recent_data["gaze_side"]==self.class_name[0]]["pupil_mvAve_"+self.showEye]
        self.data.loc[self.data["gaze_side"]==self.class_name[1],"state2_y"] = recent_data[recent_data["gaze_side"]==self.class_name[1]]["pupil_mvAve_"+self.showEye]

    def update_timecourse(self):
      
        self.glow["state1"].setData(self.data["left_x"], self.data["state1_y"])
        self.curve["state1"].setData(self.data["left_x"], self.data["state1_y"])
        
        self.glow["state2"].setData(self.data["right_x"], self.data["state2_y"])
        self.curve["state2"].setData(self.data["right_x"], self.data["state2_y"])

        if self.fin:
            self.graph_widget.setXRange(0, self.data["timestamp"].values[-1])
            
        elif self.data["timestamp"].values[-1] < self.plotLength:
            self.graph_widget.setXRange(0, self.plotLength)
        else:
            # self.graph_widget.setXRange(0, timestamps[-1])
            self.graph_widget.setXRange(self.data["timestamp"].values[-1]-self.plotLength, self.data["timestamp"].values[-1])

        ymin = np.nanmin(np.r_[self.data["state1_y"],self.data["state2_y"]])
        ymax = np.nanmax(np.r_[self.data["state1_y"],self.data["state2_y"]])
        
        if not np.isnan(ymin):
            ymin = math.floor((ymin - 0.1) * 5) / 5
            ymax = math.ceil((ymax + 0.1) * 5) / 5
                    
            # self.graph_widget.setYRange(ymin, ymax)
            self.graph_widget.setYRange(2, 8)


    def update_bar(self):
        
        if "state1_y" in self.data and len(self.data["state1_y"].dropna()) > 0:
            avg_left = np.nanmean(self.data["state1_y"])
        else:
            avg_left = np.nan
    
        if "state2_y" in self.data and len(self.data["state2_y"].dropna()) > 0:
            avg_right = np.nanmean(self.data["state2_y"])
        else:
            avg_right = np.nan
            
        self.bar_left.setOpts(height=avg_left)
        self.bar_right.setOpts(height=avg_right)
        
        ymin = np.nanmin([avg_left, avg_right])-0.05
        ymax = np.nanmax([avg_left, avg_right])+0.05
        
        if not np.isnan(ymin):
            self.bar_widget.setYRange(ymin, ymax)
            
    def update_plot(self):
                
        if len(self.data) == 0:
            print("No data!")
            return
        
        self.preprocessing()
        self.update_timecourse()
        self.update_bar()
        
        # %% eye and scene plot
        
        if self.latest_scene_sample is not None:
            self.scene_image_view.setImage(self.latest_scene_sample / 255, autoLevels=False)
        if self.latest_eyevideo_sample is not None:
            self.eye_image_view.setImage(self.latest_eyevideo_sample / 255, autoLevels=False)

    def quit_application(self):
        print("Quitting application...")
        
        if hasattr(self, "timer") and self.timer.isActive():
            self.timer.stop()

        if self.is_running and not self.demo:
            print("Stopping recording...")
            self.device.recording_stop_and_save()
        
        if hasattr(self, 'device'):
            self.device.close()
            
        if hasattr(self, 'stim_thread'):
            self.stim_thread.stop()

        QApplication.instance().quit()
        
        
    def keyPressEvent(self, event):
        
        if event.key() == Qt.Key.Key_Left or event.key() == Qt.Key.Key_Right:
            self.showEye = "left" if self.showEye == "right" else "right"
            self.eye_label.setText(f"Eye camera: {self.showEye.capitalize()} eye")
            
            self.update_plot()
            
        elif event.key() == Qt.Key.Key_Escape:
            self.stim_thread.switch_screen("Esc")
            
        elif event.key() == Qt.Key.Key_Up:

            self.start_measurement()
            time.sleep(1)
                
        # elif event.key() == Qt.Key.Key_Down:

        #     self.stop_measurement()
        #     time.sleep(1)
                    