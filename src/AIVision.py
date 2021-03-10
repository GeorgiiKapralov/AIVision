import cv2
import numpy as np
import d3dshot
import imutils
import src.Helper as helper
import src.Settings as settings
from src.Logger import logger
import time
import pytesseract

class AIVision:
    __CurrentFrame = None
    __RawFrame = None
    __D3DShot = None
    
    __ScreenWidth = 0
    __ScreenHeight = 0
    
    __ScreenStepsCount = 256
    __WidthStep = 0.0
    __HeightStep = 0.0
    
    __TextData = ""

    def __init__(self):
        self.__D3DShot = d3dshot.create(capture_output="numpy")
        self.__UpdateSizeSteps()
        
    def __del__(self):
        cv2.destroyAllWindows()
        del self.__D3DShot
        
    def __UpdateSizeSteps(self):
        self.__ScreenWidth, self.__ScreenHeight = self.__D3DShot.display.resolution
        self.__WidthStep = self.__ScreenWidth / self.__ScreenStepsCount
        self.__HeightStep = self.__ScreenHeight / self.__ScreenStepsCount
        
    def GetDisplays(self):
        return self.__D3DShot.displays
        
    def SetDisplayIndex(self, index):
        self.__D3DShot.display = self.__D3DShot.displays[index]
        self.__UpdateSizeSteps()
        
    def SetScreenStepsCount(self, screenStepsCount):
        self.__ScreenStepsCount = screenStepsCount
        self.__UpdateSizeSteps()
        
    def GetScreenStepsCount(self):
        return self.__ScreenStepsCount
        
    def GetWidthStep(self):
        return self.__WidthStep
        
    def GetHeightStep(self):
        return self.__HeightStep
        
    def ClampPointToStepsGrid(self, x, y):
        return int(x // self.__WidthStep * self.__WidthStep), int(y // self.__HeightStep * self.__HeightStep)
        
    def GetRawFrame(self):
        return self.__RawFrame
    
    def GetCurrentFrame(self):
        return self.__CurrentFrame
        
    def SetCurrentFrame(self, frame):
        self.__CurrentFrame = frame
        
    def SetResetCurrentFrameToRaw(self):
        self.__CurrentFrame = self.__RawFrame

    # ScreenStepsBox (left, top, right, bottom)
    def CaptureFrame(self, ScreenStepsBox=np.array([0,0,5000,5000])):
        if ScreenStepsBox[2] > self.__ScreenStepsCount:
            ScreenStepsBox[2] = self.__ScreenStepsCount
            
        if ScreenStepsBox[3] > self.__ScreenStepsCount:
            ScreenStepsBox[3] = self.__ScreenStepsCount
    
        if ScreenStepsBox[2] <= ScreenStepsBox[0]:
            ScreenStepsBox[0] = ScreenStepsBox[2] - 1
            
        if ScreenStepsBox[3] <= ScreenStepsBox[1]:
            ScreenStepsBox[1] = ScreenStepsBox[3] - 1
            
        region = (int(self.__WidthStep * ScreenStepsBox[0]), int(self.__HeightStep * ScreenStepsBox[1]), int(self.__WidthStep * ScreenStepsBox[2]), int(self.__HeightStep * ScreenStepsBox[3]))
        screen = self.__D3DShot.screenshot(region)

        screen = cv2.cvtColor(screen, cv2.COLOR_RGB2BGR)
        self.__CurrentFrame = screen
        self.__RawFrame = screen
        self.__TextData = ""
        return screen
        
    def SaveToFile(self, path = None):
        if path is None:
            path = 'res/' + helper.TimeStampStr() + '.png'
        logger.info('CurrenFrame saved to path: %s', path)
        cv2.imwrite(helper.ResourcePath(path), self.__CurrentFrame) 
            
    def CreateUIImageWithText(self, strings, width = 700):
        offsetLine = 10
        offsetLeft = 10
        textHeight = 25
        linesCount = len(strings)
        if linesCount == 0:
            return 0
        # + 40 is HACK. Doesn't work without it.
        HACK_HEIGHT = 20
        totalHeight = textHeight * linesCount + offsetLine * (linesCount + 1) + HACK_HEIGHT
        view = np.zeros((totalHeight, width), np.uint8)
        view.fill(180)
        currentOffset = offsetLine
        for str in strings:
            currentOffset = currentOffset + textHeight
            cv2.putText(view, str,(offsetLeft,currentOffset),cv2.FONT_HERSHEY_SIMPLEX, 1,(0),2)
            currentOffset = currentOffset + offsetLine
        return view
        
    def DebugShowCurrentFrame(self, seconds = 0.5):
        frameToDispaly = self.__CurrentFrame
        def inner():     
            cv2.imshow('DebugFrame', frameToDispaly)
            cv2.waitKey(int(seconds * 1000))
            cv2.destroyAllWindows()
            return                          
        helper.StartThread('DebugFrameThread', inner)       

    def RGBFilter(self, LowBGR, HighBGR):
        mask = cv2.inRange(self.__CurrentFrame, LowBGR, HighBGR)
        self.__CurrentFrame = cv2.bitwise_and(self.__CurrentFrame, self.__CurrentFrame, mask=mask)
        return self.__CurrentFrame
        
    def HSVFilter(self, LowHSV, HighHSV):
        hsv = cv2.cvtColor(self.__CurrentFrame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, LowHSV, HighHSV)
        self.__CurrentFrame = cv2.bitwise_and(self.__CurrentFrame, self.__CurrentFrame, mask=mask)
        return self.__CurrentFrame
        
    def CannyEdgeFilter(self, CannyMinValue, CannyMaxValue):
        self.__CurrentFrame = cv2.cvtColor(self.__CurrentFrame, cv2.COLOR_BGR2GRAY)
        self.__CurrentFrame = cv2.Canny(self.__CurrentFrame, CannyMinValue, CannyMaxValue)
        #Hack: We use RGB frames in common.
        self.__CurrentFrame = cv2.cvtColor(self.__CurrentFrame, cv2.COLOR_GRAY2RGB)
        return self.__CurrentFrame
        
    # could return multiple objects
    def MatchTemplate(self, sourceFile, maxScore = 0.8, multiScale = False, scales = [0.9,1,1.1], grayscale = False, addDebugInfo = False):
        templateWidth = 0
        templateHeight = 0
        loc = []
        readMethod = cv2.IMREAD_UNCHANGED
        frame = self.__CurrentFrame
        #if grayscale == True:
        #    readMethod = cv2.IMREAD_GRAYSCALE 
        template = cv2.imread(helper.ResourcePath(sourceFile), readMethod)
        if template is None:
            logger.error('File is not readed: %s', sourceFile)
            return loc, templateWidth, templateHeight
        if grayscale == True:
            template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
            frame = cv2.cvtColor(self.__CurrentFrame, cv2.COLOR_BGR2GRAY)
        if grayscale == True:
            templateWidth, templateHeight = template.shape[::-1]
        else:
            alpha, templateWidth, templateHeight = template.shape[::-1]
            
        res = None
        if multiScale == True:
            found = None
            res = np.zeros(shape=(frame.shape[0], frame.shape[1]))
            for scale in scales[::-1]:
                resized = imutils.resize(template, width = int(template.shape[1] * scale))
                ratio = template.shape[1] / float(resized.shape[1])
                
                # Make sure that template smaller than frame.
                if resized.shape[0] > frame.shape[0] or resized.shape[1] > frame.shape[1]:
                    break
                    
                resultPartial = cv2.matchTemplate(frame, resized, cv2.TM_CCOEFF_NORMED)
                (_, maxVal, _, maxLoc) = cv2.minMaxLoc(resultPartial)
                
                if found is None or maxVal > found[0]:
                    found = (maxVal, maxLoc, ratio)
                    
                bestLoc = np.where( resultPartial >= maxScore)
                for pt in zip(*bestLoc[::-1]):
                    res[pt[1], pt[0]] = resultPartial[pt[1], pt[0]]
                
                #res[maxLoc[1], maxLoc[0]] = maxVal
                    
            (maxVal, maxLoc, ratio) = found
            templateWidth = int(templateWidth / ratio)
            templateHeight = int(templateHeight / ratio)
        else:
            res = cv2.matchTemplate(frame, template, cv2.TM_CCOEFF_NORMED)
            
        loc = np.where( res >= maxScore)
        if addDebugInfo == True:
            isFirstMatch = True
            for pt in zip(*loc[::-1]):
                color = (0,0,255)
                if isFirstMatch == True:
                    isFirstMatch = False
                    color = (0,255,0)
                cv2.rectangle(self.__CurrentFrame, pt, (pt[0] + templateWidth, pt[1] + templateHeight), color, 1)
        return loc, templateWidth, templateHeight
        
    # return bool
    def IsMatchTemplate(self, sourceFile, maxScore = 0.8, multiScale = False, scales = [0.9,1,1.1], grayscale = False, addDebugInfo = False):
        locations, templateWidth, templateHeight = self.MatchTemplate(sourceFile, maxScore, multiScale, scales, grayscale, addDebugInfo)
        if len(list(zip(*locations[::-1]))) > 0:
            return True
        else:
            return False
            
    def GetText(self):
        pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_PATH
        config = r'--oem 3 --psm 6'
        return pytesseract.image_to_string(self.__CurrentFrame, config=config)
        
    def UpdateTextData(self):
        pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_PATH
        config = r'--oem 3 --psm 6'
        self.__TextData = pytesseract.image_to_data(self.__CurrentFrame, config=config)
        return self.__TextData
      
    def GetTextData(self):
        return self.__TextData
      
    def GetWordData(self, word):
        for i, el in enumerate(self.__TextData.splitlines()):
            if i == 0:
                continue

            el = el.split()
            try:
                if el[11] != word:
                    continue
                    
                x, y, w, h = int(el[6]), int(el[7]), int(el[8]), int(el[9])
                return x, y, w, h
                
            except IndexError:
                pass
        
        return 0, 0, 0, 0
        

