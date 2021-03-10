from src.AIVision import AIVision
import src.Helper as helper
from src.Logger import logger
import cv2
import numpy as np

DisplayIndex = 0
ScreenStepsBox = np.array([20, 20, 200, 200])

LowHSV = np.array([0, 0, 0])
HighHSV = np.array([179, 255, 255])

LowBGR = np.array([0, 0, 0])
HighBGR = np.array([255, 255, 255])

CannyMinValue = 100
CannyMaxValue = 200
   
def WaitForKeyAndSaveFrame(_AIVision, logFunction = lambda : x):
    global IS_KEYBOARD_SHORTCUT_ENABLED
    global ScreenStepsBox
    
    if cv2.waitKey(33) & 0xFF == ord('s'):
        if helper.IS_KEYBOARD_SHORTCUT_ENABLED == True :
            _AIVision.SaveToFile()
            logger.info('ScreenStepsBox: %s', str(ScreenStepsBox))
            logFunction()

cropDrawing = False
cropStartPT = (-1, -1)
cropLastPT = (-1, -1)
            
def SizeView():
    _AIVision = AIVision()
    logger.info('---------- SizePreview Started ----------')
    logger.info('\'LMB\'  : Draw rectangle on window')
    logger.info('\'RMB\'  : Cut window with rectangel')
    displays = _AIVision.GetDisplays()
    logger.info('Displays:')
    it = 0
    for dispay in displays:
        logger.info('%d: %s', it, str(dispay))
        it += 1
    logger.info('Steps count: %d', _AIVision.GetScreenStepsCount())
    logger.info('Width Step: %d', _AIVision.GetWidthStep())
    logger.info('Height Step: %d', _AIVision.GetHeightStep())

    global ScreenStepsBox
    global DisplayIndex

    cv2.namedWindow('settings_Size')
    cv2.namedWindow('Size')

    cv2.createTrackbar('SizeWL','settings_Size',ScreenStepsBox[0],_AIVision.GetScreenStepsCount(),lambda x: x)
    cv2.createTrackbar('SizeWH','settings_Size',ScreenStepsBox[2],_AIVision.GetScreenStepsCount(),lambda x: x)

    cv2.createTrackbar('SizeHL','settings_Size',ScreenStepsBox[1],_AIVision.GetScreenStepsCount(),lambda x: x)
    cv2.createTrackbar('SizeHH','settings_Size',ScreenStepsBox[3],_AIVision.GetScreenStepsCount(),lambda x: x)
    
    cv2.createTrackbar('DisplayIndex','settings_Size',DisplayIndex,len(displays)-1 ,lambda x: x)
    
    def on_mouse(event, x, y, flags, param):
        global cropStartPT
        global cropLastPT
        global cropDrawing
        global ScreenStepsBox
        pt = _AIVision.ClampPointToStepsGrid(x, y)
        if event == cv2.EVENT_LBUTTONDOWN:
            cropDrawing = True
            cropStartPT = pt
            cropLastPT = pt
        elif event == cv2.EVENT_LBUTTONUP:
            cropDrawing = False
        elif event == cv2.EVENT_MOUSEMOVE:
            if cropDrawing == True:
                cropLastPT = pt
        elif event == cv2.EVENT_RBUTTONDOWN:
            if cropStartPT != (-1, -1) and cropLastPT != (-1, -1):
                ScreenStepsBox[2] = ScreenStepsBox[0] + cropLastPT[0] // _AIVision.GetWidthStep()
                ScreenStepsBox[0] = ScreenStepsBox[0] + cropStartPT[0] // _AIVision.GetWidthStep()
                ScreenStepsBox[3] = ScreenStepsBox[1] + cropLastPT[1] // _AIVision.GetHeightStep()
                ScreenStepsBox[1] = ScreenStepsBox[1] + cropStartPT[1] // _AIVision.GetHeightStep()
                cv2.setTrackbarPos('SizeWL', 'settings_Size', ScreenStepsBox[0])
                cv2.setTrackbarPos('SizeWH', 'settings_Size', ScreenStepsBox[2])
                cv2.setTrackbarPos('SizeHL', 'settings_Size', ScreenStepsBox[1])
                cv2.setTrackbarPos('SizeHH', 'settings_Size', ScreenStepsBox[3])
                cropDrawing = False
                cropStartPT = (-1, -1)
                cropLastPT = (-1, -1)
                logger.info('Screen cutted.')
                logger.info('ScreenStepsBox: %s', str(ScreenStepsBox))
        
    cv2.setMouseCallback("Size", on_mouse)
    
    while(True):
        ScreenStepsBox[0] = cv2.getTrackbarPos('SizeWL', 'settings_Size')
        ScreenStepsBox[2] = cv2.getTrackbarPos('SizeWH', 'settings_Size')
        ScreenStepsBox[1] = cv2.getTrackbarPos('SizeHL', 'settings_Size')
        ScreenStepsBox[3] = cv2.getTrackbarPos('SizeHH', 'settings_Size')
        DisplayIndex = cv2.getTrackbarPos('DisplayIndex', 'settings_Size')
        
        _AIVision.SetDisplayIndex(DisplayIndex)
        frame = _AIVision.CaptureFrame(ScreenStepsBox)
        
        cv2.rectangle(frame, cropStartPT, cropLastPT, (0, 255, 0), 2)
        cv2.imshow('Size', frame)
        
        def nothing():
            pass
        
        WaitForKeyAndSaveFrame(_AIVision, logFunction = nothing)
        
def RGBFilterView():
    _AIVision = AIVision()
    logger.info('---------- RGBFilterPreview Started ----------')
    
    global LowBGR
    global HighBGR

    cv2.namedWindow('RGBFilter')
    cv2.namedWindow('settings_RGB')

    # create trackbars for color change
    cv2.createTrackbar('lowR','settings_RGB',LowBGR[2],255,lambda x: x)
    cv2.createTrackbar('highR','settings_RGB',HighBGR[2],255,lambda x: x)

    cv2.createTrackbar('lowG','settings_RGB',LowBGR[1],255,lambda x: x)
    cv2.createTrackbar('highG','settings_RGB',HighBGR[1],255,lambda x: x)

    cv2.createTrackbar('lowB','settings_RGB',LowBGR[0],255,lambda x: x)
    cv2.createTrackbar('highB','settings_RGB',HighBGR[0],255,lambda x: x)

    while(True):
        # grab the frame
        _AIVision.CaptureFrame(ScreenStepsBox)

        # get trackbar positions
        LowBGR[2] = cv2.getTrackbarPos('lowR', 'settings_RGB')
        HighBGR[2] = cv2.getTrackbarPos('highR', 'settings_RGB')
        LowBGR[1] = cv2.getTrackbarPos('lowG', 'settings_RGB')
        HighBGR[1] = cv2.getTrackbarPos('highG', 'settings_RGB')
        LowBGR[0] = cv2.getTrackbarPos('lowB', 'settings_RGB')
        HighBGR[0] = cv2.getTrackbarPos('highB', 'settings_RGB')       

        frame = _AIVision.RGBFilter(LowBGR, HighBGR)

        # show thresholded output
        cv2.imshow('RGBFilter', frame) 

        def LoggingOnSave():
            logger.info('RGB Filter')
            logger.info('LowBGR: %s', str(LowBGR))
            logger.info('HighBGR: %s', str(HighBGR))
        WaitForKeyAndSaveFrame(_AIVision, logFunction = LoggingOnSave) 
  
def HSVFilterView():
    _AIVision = AIVision()
    logger.info('---------- HSVFilterPreview Started ----------')
    
    global LowHSV
    global HighHSV

    cv2.namedWindow('HSVFilter')
    cv2.namedWindow('settings_HSV')

    # create trackbars for color change
    # Max Hue value in HSV is 179
    cv2.createTrackbar('lowH','settings_HSV',LowHSV[0],179,lambda x: x)
    cv2.createTrackbar('highH','settings_HSV',HighHSV[0],179,lambda x: x)

    cv2.createTrackbar('lowS','settings_HSV',LowHSV[1],255,lambda x: x)
    cv2.createTrackbar('highS','settings_HSV',HighHSV[1],255,lambda x: x)

    cv2.createTrackbar('lowV','settings_HSV',LowHSV[2],255,lambda x: x)
    cv2.createTrackbar('highV','settings_HSV',HighHSV[2],255,lambda x: x)

    while(True):
        # grab the frame
        _AIVision.CaptureFrame(ScreenStepsBox)

        # get trackbar positions
        LowHSV[0] = cv2.getTrackbarPos('lowH', 'settings_HSV')
        HighHSV[0] = cv2.getTrackbarPos('highH', 'settings_HSV')
        LowHSV[1] = cv2.getTrackbarPos('lowS', 'settings_HSV')
        HighHSV[1] = cv2.getTrackbarPos('highS', 'settings_HSV')
        LowHSV[2] = cv2.getTrackbarPos('lowV', 'settings_HSV')
        HighHSV[2] = cv2.getTrackbarPos('highV', 'settings_HSV')       

        frame = _AIVision.HSVFilter(LowHSV, HighHSV)

        # show thresholded output
        cv2.imshow('HSVFilter', frame)   
        def LoggingOnSave():
            logger.info('HSV Filter')
            logger.info('LowHSV: %s', str(LowHSV))
            logger.info('HighHSV: %s', str(HighHSV))        
        WaitForKeyAndSaveFrame(_AIVision, logFunction = LoggingOnSave)
            

def CannyEdgeFilterView():
    _AIVision = AIVision()
    logger.info('---------- CannyFilterPreview Started ----------')
    
    global CannyMinValue
    global CannyMaxValue

    cv2.namedWindow('CannyFilter')
    cv2.namedWindow('settings_Canny')

    cv2.createTrackbar('minVal','settings_Canny',CannyMinValue,1000,lambda x: x)
    cv2.createTrackbar('maxVal','settings_Canny',CannyMaxValue,1000,lambda x: x)

    while(True):
        # grab the frame
        _AIVision.CaptureFrame(ScreenStepsBox)

        # get trackbar positions
        CannyMinValue = cv2.getTrackbarPos('minVal', 'settings_Canny')
        CannyMaxValue = cv2.getTrackbarPos('maxVal', 'settings_Canny') 
        
        frame = _AIVision.CannyEdgeFilter(CannyMinValue, CannyMaxValue)
        
        cv2.imshow('CannyFilter', frame)
          
        def LoggingOnSave():
            logger.info('Canny Edge Filter')
            logger.info('CannyMinValue: %d', CannyMinValue)
            logger.info('CannyMaxValue: %d', CannyMaxValue)
        WaitForKeyAndSaveFrame(_AIVision, logFunction = LoggingOnSave)
        
def MatchTemplateView():  
    _AIVision = AIVision()
    logger.info('---------- MatchTemplatePreview Started ----------')
    logger.info('\'s\'    : MatchTemplate stats')
    
    maxScore  = 0.9
    filter = 0
    isScaleMatch = 0
    minScale = 0.8
    maxScale = 1.4
    scaleSteps = 20
    filterName = "None"
    folderName = 'res/'
    files = helper.GetFilesInFolder(folderName, endswith='.png')
    sourceFileId = len(files) - 1
    sourceFile = 'res/NotepadTest.png'
    logger.info('Fond %d files in folder \'%s\'. File list:', len(files), folderName)
    it = 0
    for file in files:
        logger.info('%d : \'%s\'', it, file)
        it = it + 1
    
    cv2.namedWindow('MatchTemplatePreview')
    cv2.namedWindow('settings_MatchTemplate')
    settingsView = _AIVision.CreateUIImageWithText(np.array(["filter: " + filterName, "source: " + sourceFile]))
    cv2.imshow('settings_MatchTemplate', settingsView)
    cv2.waitKey(1)
    cv2.createTrackbar('maxScore','settings_MatchTemplate',int(maxScore * 100),100,lambda x: x)
    cv2.createTrackbar('filter','settings_MatchTemplate',filter,3,lambda x: x)
    cv2.createTrackbar('isScaleMatch','settings_MatchTemplate',isScaleMatch,1,lambda x: x)
    cv2.createTrackbar('minScale','settings_MatchTemplate',int(minScale*10),30,lambda x: x)
    cv2.createTrackbar('maxScale','settings_MatchTemplate',int(maxScale*10),30,lambda x: x)
    cv2.createTrackbar('scaleSteps','settings_MatchTemplate',scaleSteps,50,lambda x: x)
    cv2.createTrackbar('sourceFile','settings_MatchTemplate',sourceFileId,len(files)-1,lambda x: x)

    while(True):
        frame = _AIVision.CaptureFrame(ScreenStepsBox)
    
        maxScore = cv2.getTrackbarPos('maxScore', 'settings_MatchTemplate') / 100
        filter = cv2.getTrackbarPos('filter', 'settings_MatchTemplate')
        isScaleMatch = cv2.getTrackbarPos('isScaleMatch', 'settings_MatchTemplate')
        minScale = cv2.getTrackbarPos('minScale', 'settings_MatchTemplate') / 10
        maxScale = cv2.getTrackbarPos('maxScale', 'settings_MatchTemplate') / 10
        scaleSteps = cv2.getTrackbarPos('scaleSteps', 'settings_MatchTemplate')
        sourceFileId = cv2.getTrackbarPos('sourceFile', 'settings_MatchTemplate')
        sourceFile = folderName + files[sourceFileId]
        
        if filter == 1:
            _AIVision.RGBFilter(LowBGR, HighBGR)
            filterName = "RGB"
        elif filter == 2:
            _AIVision.HSVFilter(LowHSV, HighHSV)
            filterName = "HSV"
        elif filter == 3:
            filterName = "Canny"
            _AIVision.CannyEdgeFilter(CannyMinValue, CannyMaxValue) 
        else:
            filterName = "None"
        locations, templateWidth, templateHeight = _AIVision.MatchTemplate(sourceFile, maxScore, multiScale = isScaleMatch, scales = np.linspace(minScale, maxScale, scaleSteps), grayscale = True)
        # You can use  len(list(zip(*locations[::-1]))) > 0 instead of IsMatchTemplate. It used here just for Preview.
        isMatchTemplate = _AIVision.IsMatchTemplate(sourceFile, maxScore, multiScale = isScaleMatch)
        if isMatchTemplate == True :
            #matched
            cv2.putText(frame, 'Match', (10,40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        for pt in zip(*locations[::-1]):
            cv2.rectangle(frame, pt, (pt[0] + templateWidth, pt[1] + templateHeight), (0,0,255), 1)
        cv2.imshow('MatchTemplatePreview', frame)
        
        #UI text for settings
        settingsView = _AIVision.CreateUIImageWithText(np.array(["filter: " + filterName, "source: " + sourceFile]))
        cv2.imshow('settings_MatchTemplate', settingsView)
        
        global IS_KEYBOARD_SHORTCUT_ENABLED
    
        if cv2.waitKey(33) & 0xFF == ord('s'):
            if helper.IS_KEYBOARD_SHORTCUT_ENABLED == True :
                logger.info('=== MatchTemplate statistic ===')
                logger.info('isMatchTemplate: %d', isMatchTemplate)
                objectsFound = 0
                for pt in zip(*locations[::-1]):
                    objectsFound = objectsFound + 1
                    logger.info('Object pos: %s', str(pt))
                logger.info('foundObjects: %d', objectsFound)
                logger.info('filterName: %s', filterName)
                logger.info('sourceFile: %s', sourceFile)
                logger.info('maxScore: %s', maxScore)
                
def TextRecognitionView(): 
    _AIVision = AIVision()
    logger.info('---------- TextRecognitionView Started ----------')
    logger.info('\'s\'    : TextRecognitionView stats')
    
    global LowHSV
    global HighHSV
    
    while(True):
        # grab the frame
        frame = _AIVision.CaptureFrame(ScreenStepsBox)
        _AIVision.UpdateTextData()
        
        for i, el in enumerate(_AIVision.GetTextData().splitlines()):
            if i == 0:
                continue

            el = el.split()
            try:
                # Find words
                x, y, w, h = int(el[6]), int(el[7]), int(el[8]), int(el[9])
                cv2.rectangle(frame, (x, y), (w + x, h + y), (0, 0, 255), 1)
                cv2.putText(frame, el[11], (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 100, 100), 1)
            except IndexError:
                pass   
                
        cv2.imshow('CannyFilter', frame)
          
        def LoggingOnSave():
            logger.info('Text Recognition')
            text = _AIVision.GetText()
            logger.info('Text: %s', text)
            helloWordData = _AIVision.GetWordData('Hello');
            logger.info('Hello word data: %s', helloWordData)
        WaitForKeyAndSaveFrame(_AIVision, logFunction = LoggingOnSave)
    
    