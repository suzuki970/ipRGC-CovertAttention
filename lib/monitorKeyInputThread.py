#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug  6 15:22:12 2025

@author: yutasuzuki
"""

# from PyQt6.QtCore import QObject, QThread, pyqtSignal, QMetaObject, Qt
# import time
# from psychopy import visual,core
# from psychopy import iohub

from PyQt6.QtCore import QTimer, pyqtSignal, QObject
from PyQt6.QtCore import QMetaObject, Qt
from psychopy.hardware import keyboard

class KeyMonitorThread(QObject):
    
    key_detected = pyqtSignal(list)

    def __init__(self, os_name, bus, window_ms=300):

        super().__init__(None)

        self.bus = bus

        self.timer = QTimer(self)
        self.timer.setTimerType(Qt.TimerType.PreciseTimer)
        self.timer.timeout.connect(self.poll_keys)
        self.timer.start()
        
        self.kb = keyboard.Keyboard()
        self.os_name=os_name
        
        self.buffer = []
        self.window_ms = window_ms

    def start(self):
        if not self._thread.isRunning():
            self._running = True
            self._thread.start()
            
    def poll_keys(self):
       
        keys = self.kb.getKeys(waitRelease=False)
        
        if keys:
            for key in keys:
                if self.os_name == "Darwin":
                    key_name = key.value[0]
                elif self.os_name == "Windows":
                    key_name = key.name

                # print(key)
                    
                self.bus.sendMessage.emit(f"KEY_INPUT {key_name}")

                self.key_detected.emit([{
                    'key':key_name,
                    'RT':key.t
                    }])
            
    def stop(self):
        QMetaObject.invokeMethod(
            self.timer, "stop", Qt.ConnectionType.QueuedConnection
            )
