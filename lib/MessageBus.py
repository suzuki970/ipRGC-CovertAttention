#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 12 21:48:17 2025

@author: yutasuzuki
"""

from PyQt6.QtCore import QObject, pyqtSignal

class MessageBus(QObject):
    sendMessage = pyqtSignal(str)