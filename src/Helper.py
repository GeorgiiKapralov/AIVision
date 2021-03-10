from src.Logger import logger
from os.path import join, abspath
import os as os
from datetime import datetime
import time
import numpy as np
import threading
import kthread
import keyboard
import pydirectinput
import random

IS_KEYBOARD_SHORTCUT_ENABLED = True;

def ResourcePath(relative_path):
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = abspath(".")

    return join(base_path, relative_path)
    
def TimeStampStr():
    now = datetime.now()
    return now.strftime("%Yy%mm%dd%Hh%Mm%Ss")
    
def TimestampMillisec64():
    return int((datetime.utcnow() - datetime(1970, 1, 1)).total_seconds() * 1000) 
    
def GetFilesInFolder(path, endswith = ""):
    fileNameList = np.array([])
    for file in os.listdir(path):
        if file.endswith(endswith):
            fileNameList = np.append(fileNameList, file)
    return fileNameList
    
def StartThread(treadName, target):
    kthread.KThread(target = target, name = treadName).start()
    
def StopThread(treadName):
    for thread in threading.enumerate():
        if thread.getName() == treadName:
            thread.kill()
            
def IsThreadActive(treadName):
    for thread in threading.enumerate():
        if thread.getName() == treadName:
            return True;
    return False
    
def WaitForFunction(function, maxWaitTime = 10, sleepStep = 0.5):
    # Todo: We should use thread switch and timer instead of sleep here in future
    sleeped = 0
    while True:
        if function() == True:
            return True
        else:
            time.sleep(sleepStep)
            sleeped += sleepStep
            if sleeped > maxWaitTime:
                return False
    
class Executable:
    ThreadName = 'ExecutableThread'
    Path = ''
    
    def Run(self):
        if self.Path == '':
            logger.debug('Executable path is empty!')
        else:
            def inner():            
                os.system(self.Path)
            logger.debug('Starting executable: %s', str(self.Path))
            StartThread(self.ThreadName, inner)
        
    def Stop(self):
        logger.debug('Stop executable: %s', str(self.Path))
        StopThread(self.ThreadName)
    
    
class LogicTemplate:
    __Function = lambda : x
    DelayStart = True
    DelayTimer = 3
    
    def __ThreadFunciton(self):
        logger.info('---------- Logic started ----------')
        self.__Function()
        logger.info('---------- Logic finished ----------')
            
    def __StartLogicInternal(self):
        def StartingInner():
            logger.info('---------- Logic starting ----------')
            if self.DelayStart == True:
                logger.info('Delay Start. Timer: %d', self.DelayTimer)
                for it in range(self.DelayTimer):
                    logger.info('.')
                    time.sleep(1)
            StartThread("LogicThread", self.__ThreadFunciton)
        if not IsThreadActive("LogicStartingInnerThread") :
            StartThread("LogicStartingInnerThread", StartingInner)
    
    def __StopLogicInternal(self):
        logger.info('---------- Logic stopping ----------')
        StopThread("LogicStartingInnerThread")
        StopThread("LogicThread")
        
    def SetFunction(self, function):
        self.__Function = function
        
    def Run(self):
        global IS_KEYBOARD_SHORTCUT_ENABLED
        if IS_KEYBOARD_SHORTCUT_ENABLED == True:
            logger.info('\'Ctrl+PGUP\' : Start Logic')
            logger.info('\'Ctrl+PGDN\' : Stop Logic')
            logger.info('\'Ctrl+Esc\'  : Exit')
            
            keyboard.add_hotkey('ctrl+page up', self.__StartLogicInternal)
            keyboard.add_hotkey('ctrl+page down', self.__StopLogicInternal)
            keyboard.wait('ctrl+esc')
        else:
            __StartLogicInternal();
        
class InputHelper:
    AfterClickTime = 0.05
    IsRandomizes = False
    RandomizeTime = 0.05
    def __CalculateTime(self, additionalTime):
        time = 0
        if self.IsRandomizes == True:
            time += random.random() * self.RandomizeTime
        time += self.AfterClickTime + additionalTime
        logger.debug('Click delay: %s', str(time))
        return time
        
    def KeyPress(self, input, additionalTime = 0):
        pydirectinput.press(input)
        logger.debug('Pressed: %s', str(input))
        time.sleep(self.__CalculateTime(additionalTime))
        
    def KeyDown(self, input, additionalTime = 0):
        pydirectinput.keyDown(input)
        logger.debug('KeyDown: %s', str(input))
        time.sleep(self.__CalculateTime(additionalTime))
        
    def KeyUp(self, input, additionalTime = 0):
        pydirectinput.keyUp(input)
        logger.debug('KeyUp: %s', str(input))
        time.sleep(self.__CalculateTime(additionalTime))
        
    def MouseMove(self, x, y):
        pydirectinput.moveTo(x, y)
        logger.debug('Mouse Move To: %d %d', x, y)
        
    def MouseClick(self):
        pydirectinput.moveTo(x, y)
        logger.debug('Mouse Click')