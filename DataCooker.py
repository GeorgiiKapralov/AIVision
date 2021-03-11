from pystray import Icon, MenuItem, Menu
from PIL import Image
import src.AIVisionView as AIVisionView
import src.Helper as helper
from src.Logger import logger
import keyboard
import numpy as np
import time

ViewFunctionArray = np.array([AIVisionView.SizeView, AIVisionView.RGBFilterView, AIVisionView.HSVFilterView, AIVisionView.CannyEdgeFilterView, AIVisionView.MatchTemplateView, AIVisionView.TextRecognitionView])
ThreadName = 'ViewThread'
ActiveView = -1

def Exit():
    logger.info('---------- Exit ----------')
    StopView()
    icon.visible = False
    icon.stop()
    
def StopView():
    logger.info('---------- Stop View ----------')
    helper.StopThread(ThreadName)
    # HACK : Make sure that everything destroyed in time
    time.sleep(0.2)
    global ActiveView
    ActiveView = -1
    
def StartView(viewIndex):
    StopView()
    helper.StartThread(ThreadName, ViewFunctionArray[viewIndex])
    # HACK : Make sure that everything constructed in time
    time.sleep(0.2)
    global ActiveView
    ActiveView = viewIndex
    
def StartViewTrayFunction(actionIndex):
    def inner(icon, item):
        StartView(actionIndex)
    return inner
    
def IsViewActiveTrayFunction(actionIndex):
    def inner(item):
        global ActiveView
        return ActiveView == actionIndex
    return inner
    
def SetKeyboardShortcutStateTrayFunction(v):
    def inner(icon, item):
        global IS_KEYBOARD_SHORTCUT_ENABLED
        helper.IS_KEYBOARD_SHORTCUT_ENABLED = v
        UpdateKeyboardShortcutEnabled()
    return inner

def GetSetKeyboardShortcutStateTrayFunction(v):
    def inner(item):
        return helper.IS_KEYBOARD_SHORTCUT_ENABLED == v
    return inner
    
def UpdateKeyboardShortcutEnabled():
    if helper.IS_KEYBOARD_SHORTCUT_ENABLED == True:
        logger.info('---------- Keyboard Shortcut: Enabled ----------')
        logger.info('Shortcuts:')
        logger.info('\'z\'    : SizeView')
        logger.info('\'x\'    : RGBFilter')
        logger.info('\'c\'    : HSVFilter')
        logger.info('\'v\'    : CannyEdgeFilter')
        logger.info('\'s\'    : Save to file')
        logger.info('\'q\'    : Exit')
        logger.info('\'/\'    : MatchTemplate')
        logger.info('\'.\'    : TextRecognition')
        logger.info('\'End\'  : StopView')

        keyboard.add_hotkey('z', lambda : StartView(0))
        keyboard.add_hotkey('x', lambda : StartView(1))
        keyboard.add_hotkey('c', lambda : StartView(2))
        keyboard.add_hotkey('v', lambda : StartView(3))
        keyboard.add_hotkey('/', lambda : StartView(4))
        keyboard.add_hotkey('.', lambda : StartView(5))
        keyboard.add_hotkey('q', Exit)
        keyboard.add_hotkey('end', StopView)
    else:
        logger.info('---------- Keyboard Shortcut: Disabled ----------')
        #HACK : Shortcuts cannot be cleaned in case if there is no shortcuts
        keyboard.add_hotkey('end', StopView)
        keyboard.clear_all_hotkeys()

def Tray():
    global icon, thread
    icon = None
    thread = None

    name = 'Wrapper'
    icon = Icon(name=name, title=name)
    logo = Image.open(helper.ResourcePath('src/logo.png'))
    icon.icon = logo

    icon.menu = Menu(
        MenuItem(
            'OpenCV',
            Menu(
               MenuItem(
                    'SizeView',
                    StartViewTrayFunction(0),
                    checked=IsViewActiveTrayFunction(0),
                    radio=True
                ),
               MenuItem(
                    'RGBFilter',
                    StartViewTrayFunction(1),
                    checked=IsViewActiveTrayFunction(1),
                    radio=True
                ),
               MenuItem(
                    'HSVFilter',
                    StartViewTrayFunction(2),
                    checked=IsViewActiveTrayFunction(2),
                    radio=True
                ),
                MenuItem(
                    'CannyEdgeFilter',
                    StartViewTrayFunction(3),
                    checked=IsViewActiveTrayFunction(3),
                    radio=True
                ),
                MenuItem(
                    'MatchTemplateView',
                    StartViewTrayFunction(4),
                    checked=IsViewActiveTrayFunction(4),
                    radio=True
                ),
                MenuItem(
                    'TextRecognition',
                    StartViewTrayFunction(5),
                    checked=IsViewActiveTrayFunction(5),
                    radio=True
                ),
            )
        ),
        MenuItem(
            'KeyboardShortcut',
            Menu(
                MenuItem(
                    'On',
                    SetKeyboardShortcutStateTrayFunction(True),
                    checked=GetSetKeyboardShortcutStateTrayFunction(True),
                    radio=True
                ),
                MenuItem(
                    'Off',
                    SetKeyboardShortcutStateTrayFunction(False),
                    checked=GetSetKeyboardShortcutStateTrayFunction(False),
                    radio=True
                ),
            )
        ),
        MenuItem('StopView', lambda : StopView()),
        MenuItem('Exit', lambda : Exit())
    )
    
    logger.info('---------- Welcome to Data Cooker ----------')
    UpdateKeyboardShortcutEnabled()

    icon.run()

if __name__ == '__main__':
    Tray()
