#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr  9 23:51:47 2025

@author: yutasuzuki
"""

import numpy as np
import time
import pandas as pd
import glob
import soundfile as sf
import sounddevice as sd
from PyQt6.QtCore import QThread

import lib.config as config
from lib.config import load_stimuli,make_condition_sequence

# %% --- Main loop ---
 
class StimulusThread(QThread):
    
    def __init__(self, win, bus, args):
        
        super().__init__()
        self.bus = bus
        self.args = args
        self.win=win
        self.sound = {}
        self.sound["stim_distractor"] = load_stimuli('./stim/distractor')
        self.sound["stim_target"] = load_stimuli('./stim/T1')
        self.sound["stim_probe"] = load_stimuli('./stim/T2')

        self.sound["silence"] = [
            np.zeros((int(config.TIME_ISI * config.AUDIO_SAMPLING_RATE),2)).astype('float32')
        ]

        self.t1_onset=0
        self.t2_onset=0
        self.esc_flg=False
        self.current_timestamp = 0
        self.events = []
        
        self.exp_start_time = time.perf_counter()

    def handle_new_sample(self, sample):
        self.latest_sample = sample
    
    def handle_key_event(self, keys):

        for key in keys:
            
            if (key["key"] == 'left') or (key["key"] == 'right'):
                
                print(f"[INFO] {key['key']} pressed ({round(key['RT'],4)}).")
                
                tmp = self.t1_onset if key['key'] == 'left' else self.t2_onset
                
                self.events.append({
                    'time':time.perf_counter()-self.exp_start_time,
                    # 'timestamp_eyetracker':self.eye_thread.getTime(),
                    'time_from_seq_onset':key['RT'],
                    'key':key['key'],
                    'RT':time.perf_counter()-tmp
                    })
                
            elif key['key'] == 'escape':
                self.esc_flg=True
        

    def save_files(self):
        
        self.bus.sendMessage.emit("END_EXPERIMENT")    
        
        df = pd.DataFrame(self.events)
    
        timestr = time.strftime("%Y%m%d_%H%M%S")
        filename = f"./results/{self.args.subject}/behavioral_data_{timestr}.parquet"
    
        df.to_parquet(filename, index=False)
        print(f"[INFO] Buffer saved to {filename}.")
        
    def play_if_trough(self,timestamp):
        self.trough_triggered = True
        self.current_timestamp = timestamp
        
    
    def run(self):
        
        array, bitrate = sf.read(sorted(glob.glob('./stim/distractor/*.wav'))[0])

        self.condition_frame = make_condition_sequence()

        self.bus.sendMessage.emit("START_EXPERIMENT")    
        self.count={
            "comparison":0,
            "reference":0,
            }
        
        with sd.OutputStream(samplerate=bitrate, channels=2, device=config.SOUND_DEVICE, dtype='float32') as stream:

            while self.count['comparison'] < len(self.condition_frame):
                
                seq = self.condition_frame['seq'][self.count['comparison']]
                start_time = time.perf_counter()

                print(f"[INFO] Start trial={self.count['comparison']+1}, Condition={seq}.")

                self.bus.sendMessage.emit("START_TRIAL 0")
                self.bus.sendMessage.emit(f"TRIAL {self.count['comparison']+1}")
                self.bus.sendMessage.emit(f"Condition {seq}")

                self.trough_triggered = False
                while not self.trough_triggered:

                    idx = int(np.random.randint(0, len(self.sound["stim_distractor"]), 1))
                    out = self.sound["stim_distractor"][idx]
                    stream.write(out)
                    stream.write(self.sound["silence"][0])
    
                    if self.esc_flg:
                        print("[INFO] ESC pressed. Stopping...")
                        break

                self.events.append({
                    'time': time.perf_counter() - self.exp_start_time,
                    'timestamp_eyetracker': self.current_timestamp,
                    'key': "T1T2 onset",
                })
        
                print(f"[T1T2 onset] Trough detected at {self.current_timestamp:.2f} sec")
                self.bus.sendMessage.emit("TROUGH_DETECTED")

                if self.esc_flg:
                    self.save_files()
                    break
            
                self.bus.sendMessage.emit("START_TRIAL 1")
                
                for iTone2 in range(config.NUM_SOUNDS):    
                    if seq == "T1_only":
                        if iTone2 == 0:
                            idx = self.condition_frame['t1_target'][self.count['comparison']]
                            out = self.sound["stim_target"][idx]
                            self.t1_onset = time.perf_counter()
                            self.bus.sendMessage.emit("ONSET_T1")

                        else:
                            idx = int(np.random.randint(0, len(self.sound["stim_distractor"]), 1))
                            out = self.sound["stim_distractor"][idx]

                    elif seq == "T2_only":
                        if iTone2 == 0:
                            out = self.sound["stim_probe"][0]
                            self.t2_onset = time.perf_counter()
                            self.bus.sendMessage.emit("ONSET_T2")

                        else:
                            idx = int(np.random.randint(0, len(self.sound["stim_distractor"]), 1))
                            out = self.sound["stim_distractor"][idx]

                    elif seq == "Both":                        
                        if iTone2 == 0:
                            idx = self.condition_frame['t1_target'][self.count['comparison']]
                            out = self.sound["stim_target"][idx]
                            self.t1_onset = time.perf_counter()
                            self.bus.sendMessage.emit("ONSET_T1")
    
                        elif iTone2 == self.condition_frame['t2_order'][self.count['comparison']]:
                            out = self.sound["stim_probe"][0]
                            self.t2_onset = time.perf_counter()
                            self.bus.sendMessage.emit("ONSET_T2")
    
                        else:
                            idx = int(np.random.randint(0, len(self.sound["stim_distractor"]), 1))
                            out = self.sound["stim_distractor"][idx]
           
                    stream.write(out)
                    stream.write(self.sound["silence"][0])
           
                for iTone in range(config.NUM_SOUNDS):
                    idx = int(np.random.randint(0, len(self.sound["stim_distractor"]), 1))
                    out = self.sound["stim_distractor"][idx]
                    stream.write(out)
                    stream.write(self.sound["silence"][0])
         
                if self.esc_flg:
                    self.save_files()
                    break
                    
                self.bus.sendMessage.emit("END_TRIAL")    

                print(f"[INFO] Lapsed time={round(time.perf_counter() - start_time,4)}.\n")
                self.count['comparison'] += 1

        self.save_files()

    
    def stop(self):
        self.esc_flg = True
        
        
        # if self.fps is not None:
        #     print(f"Estimated FPS: {self.fps:.2f}")
        # else:
        #     self.fps=30
        #     print("FPS could not be determined reliably")
    
    
        # self.key_monitor.stop()
        
            # if seq == 0:  # both absent
            #     for iTone in condition_frame['t0_no_tar_order'][count['comparison']]:
            #         out = self.sound["stim_distractor"][iTone]
            #         stream.write(out)
            #         stream.write(self.sound["silence"][0])
            #         self.monitorKeyInput()
            #         # print(f"{self.analysis_thread.getEventFlg()}")
                    
            # else:
            
                
            #     ##############################################################################
            #     # if iTone == condition_frame['t1_order'][count['comparison']]:
            #     #     idx = condition_frame['t1_target'][count['comparison']]
            #     #     out = self.sound["stim_target"][idx]
            #     #     # print('T1')
            #     #     self.t1_onset = time.perf_counter()

            #     # elif iTone == condition_frame['t1_order'][count['comparison']] + condition_frame['t2_order'][count['comparison']]:
            #     #     out = self.sound["stim_probe"][0]
            #     #     # print('Probe')
            #     #     self.t2_onset = time.perf_counter()
                
            #     # else:
            #     #     idx = int(np.random.randint(0,len(self.sound["stim_distractor"]), 1))
            #     #     out = self.sound["stim_distractor"][idx]
            
            
            # no target seq
            # for iTone in range(config.NUM_SOUNDS):
            #     idx = int(np.random.randint(0,len(self.sound["stim_distractor"]), 1))
            #     out = self.sound["stim_distractor"][idx]
            #     stream.write(out)
            #     stream.write(self.sound["silence"][0])
            #     self.monitorKeyInput()

            #     ##############################################################################
               
            # while True: # till pupil contriction/dilation event detects
            #     if self.analysis_thread.getEventFlg():
                    
            #         print("T1T2 onset")
                    
            #         self.events.append({
            #             'time':time.perf_counter()-self.exp_start_time,
            #             'timestamp_eyetracker':self.eye_thread.getTime(),
            #             'key':"T1T2 onset",
            #             })
                    
            #         for iTone2 in range(config.NUM_SOUNDS):
            #             if iTone2 == 0:
            #                 idx = condition_frame['t1_target'][count['comparison']]
            #                 out = self.sound["stim_target"][idx]
            #                 self.t1_onset = time.perf_counter()

            #             elif iTone2 == condition_frame['t2_order'][count['comparison']]:
            #                 out = self.sound["stim_probe"][0]
            #                 self.t2_onset = time.perf_counter()
                        
            #             else:
            #                 idx = int(np.random.randint(0,len(self.sound["stim_distractor"]), 1))
            #                 out = self.sound["stim_distractor"][idx]
                        
            #             stream.write(out)
            #             stream.write(self.sound["silence"][0])
            #             self.monitorKeyInput()
                  
            #         # no target seq
            #         for iTone in range(config.NUM_SOUNDS):
            #             idx = int(np.random.randint(0,len(self.sound["stim_distractor"]), 1))
            #             out = self.sound["stim_distractor"][idx]
            #             stream.write(out)
            #             stream.write(self.sound["silence"][0])
            #             self.monitorKeyInput()

            #         break
                        
            #     else:
            #         idx = int(np.random.randint(0,len(self.sound["stim_distractor"]), 1))
            #         out = self.sound["stim_distractor"][idx]

            #         stream.write(out)
            #         stream.write(self.sound["silence"][0])
            #         self.monitorKeyInput()
                    
                   
            # if self.esc_flg:
                
            #     print("[INFO] ESC pressed. Stopping...")
            #     self.save_files()
            #     break
            
            # print(f"[INFO] Lapsed time={round(time.perf_counter() - start_time,4)}.\n")
                     
            # count['comparison']+=1

        # self.win.close()

            
    # event.waitKeys(keyList=['down'])
    # self.show_instruction("メガネをかけて、もう一度見比べてみましょう。")
    # self.draw_and_flip()

    # event.waitKeys(keyList=['down'])
    
    # self.show_instruction("これらの2つの光に対する瞳孔径の変化を見てましょう。\n\nこれから表示される文章を読んでみてください。")
    # self.gazeMode = False
    
    # message="読み込み中・・・"
    # text0 = visual.TextStim(self.win_blue, text=message,
    #                         font=config.FONT_INSTRUCTION,alignText='center',anchorHoriz='center',
    #                         color='white', 
    #                         pos=(0, -1/3),
    #                         height=config.FONTSIZE_MSG,
    #                         wrapWidth=1.8,
    #                         # wrapWidth=self.win_blue.size[0]*0.8
    #                         )
    
    # text1 = visual.TextStim(self.win_yellow, text=message,
    #                         font=config.FONT_INSTRUCTION,alignText='center', anchorHoriz='center',
    #                         color='white', 
    #                         pos=(0, 1/3),
    #                         height=config.FONTSIZE_MSG,
    #                         wrapWidth=1.8,
    #                         # wrapWidth=self.win_yellow.size[0]*0.8
    #                         )
    
 