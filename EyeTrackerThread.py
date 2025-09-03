#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 29 09:01:37 2025

@author: yutasuzuki
"""

from PyQt6.QtCore import QThread, pyqtSlot,Qt
from PyQt6.QtCore import QTimer, pyqtSignal, QObject

from queue import Queue
import pandas as pd
import time
from pupil_labs.realtime_api.simple import discover_one_device
import pylink
import subprocess
import shutil

from lib.EyeLinkCoreGraphicsPsychoPy import EyeLinkCoreGraphicsPsychoPy
import lib.config as config

# %% get data from eyelink

class EyeTrackerThread(QThread):

    def __init__(self, win, sample_queue: Queue, bus,args):
        super().__init__()
        
        self.args=args
        self.el_tracker = pylink.EyeLink()
        self.el_tracker.setOfflineMode()
        
        self.bus = bus
        self.bus.sendMessage.connect(self.sendMessage)

        # file_event_flags = 'LEFT,RIGHT,FIXATION,SACCADE,BLINK,MESSAGE,BUTTON,INPUT'
        # link_event_flags = 'LEFT,RIGHT,FIXATION,SACCADE,BLINK,BUTTON,FIXUPDATE,INPUT'

        # file_sample_flags = 'LEFT,RIGHT,GAZE,HREF,RAW,AREA,GAZERES,BUTTON,STATUS,INPUT'
        file_sample_flags = 'LEFT,RIGHT,GAZE,HREF,RAW,AREA'
        link_sample_flags = 'LEFT,RIGHT,GAZE,HREF,RAW,AREA'

        self.el_tracker.sendCommand("file_sample_data = %s" % file_sample_flags)
        self.el_tracker.sendCommand("link_sample_data = %s" % link_sample_flags)

        # Open an EDF data file on the Host PC
        self.el_tracker.openDataFile('test.edf')
        
        genv = EyeLinkCoreGraphicsPsychoPy(self.el_tracker, win,config.os_name)
        genv.setCalibrationColors((0,0,0), win.color)
        genv.setTargetType('circle')
        genv.setTargetSize(24)
        pylink.openGraphicsEx(genv)
        print("[INFO] Calling calibration...")
        self.el_tracker.doTrackerSetup()
        
        self.el_tracker.startRecording(1,1,1,1)

        self.running = True
        self.sample_queue = sample_queue
        self.start_time = time.perf_counter()
    
    def sendMessage(self,mes):
        if config.EYE_TRACKER=="Eyelink":
            self.el_tracker.sendMessage(mes)
        else:
            print("1111")

        
    def getTime(self):
        return self.sample_queue[-1]["timestamp_eyetracker"]
    
    def run(self):

        while self.running:
            
            sample = self.el_tracker.getNewestSample()
     
            if len(self.sample_queue)==0:
                init_timestamp = sample.getTime()
            
            if sample:
                # self.sample_queue.put((sample.getTime(),sample.getRightEye().getPupilSize()))
                self.sample_queue.append({
                        "timestamp": time.perf_counter()-self.start_time,
                        "timestamp_eyetracker": (sample.getTime()-init_timestamp)/1000,
                        "pupil_left":sample.getLeftEye().getPupilSize(), 
                        "pupil_right":sample.getRightEye().getPupilSize(),
                        })

    
            self.msleep(5)
    
    def stop(self):
        self.running = False
        timestr = time.strftime("%Y%m%d_%H%M%S")
        filename = f"./results/{self.args.subject}/pupil_data_Eyelink_{timestr}.parquet"
        
        print(f"[INFO] Buffer saved to {filename}.")

        df = pd.DataFrame(self.sample_queue)       
        df.to_parquet(filename, index=False)
        
        self.el_tracker.closeDataFile()
        
        edf_local_name = 'test.edf'
        filename = "test.edf"
        newfilename = f"./results/{self.args.subject}/{timestr}.edf"
        self.el_tracker.receiveDataFile(filename, edf_local_name)
        self.el_tracker.close()
        
        shutil.move(filename, newfilename)
        cmd = [r'C:\Program Files (x86)\SR Research\EyeLink\bin\edf2asc.exe', '-y', newfilename]
        subprocess.run(cmd)
        
# %% get data from NEON

class EyeTrackerThread_NEON(QThread):
    
    def __init__(self, win, sample_queue: Queue, bus):

        self.bus = bus
        self.bus.sendMessage.connect(self.sendMessage)

        self.el_tracker = discover_one_device()
        if self.el_tracker is None:
            print("No device found.")
        
        recording_id = self.el_tracker.recording_start()
        
        print(f"Phone IP address: {self.el_tracker.phone_ip}")
        print(f"Started recording with id {recording_id}")

        super().__init__()

        self.running = True
        self.sample_queue = sample_queue
        self.start_time = time.perf_counter()
        
    def sendMessage(self,mes):
        print(mes)

    def getTime(self):
        return self.sample_queue[-1]["timestamp_eyetracker"]

    def run(self):
    
        while self.running:
            
            latest_scene_sample, sample = self.el_tracker.receive_matched_scene_video_frame_and_gaze()
            
            if len(self.sample_queue)==0:
                init_timestamp=sample.timestamp_unix_seconds
                
            if sample:
                # print(round(sample.timestamp_unix_seconds-init_timestamp,4))
                # self.sample_queue.put((sample.timestamp_unix_seconds,sample.pupil_diameter_right))
                self.sample_queue.append({
                        "timestamp": time.perf_counter()-self.start_time,
                        "timestamp_eyetracker": sample.timestamp_unix_seconds-init_timestamp,
                        "pupil_left":sample.pupil_diameter_left, 
                        "pupil_right":sample.pupil_diameter_right,
                        })
            else:
                self.start_time = time.perf_counter()
                print("time reset")
                    
            # self.msleep(1)

  
    def stop(self):
        
        self.running = False
        self.el_tracker.recording_stop_and_save()

        timestr = time.strftime("%Y%m%d-%H%M%S")
        filename = f"./results/pupil_data_NEON_{timestr}.parquet"
        
        print(f"[INFO] Buffer saved to {filename}.")

        df = pd.DataFrame(self.sample_queue)
        
        df.to_parquet(filename, index=False)

    