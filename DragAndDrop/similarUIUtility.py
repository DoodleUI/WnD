# -*- coding: utf-8 -*-
"""
Created on Sun Nov  3 01:16:09 2019

@author: sxm6202xx
"""
from DragAndDrop import  PositionHelper
from DragAndDrop.Mapper import  element_mapper
WidthZoneElement = 4
HeightZoneElement= 6
WidthZoneText = 2
HeightZoneText= 2

def posToTextZone(pos):
    if(pos==0):
        return "tl"
    elif(pos==1):
        return "tr"
    elif(pos==2):
        return "bl"
    else:
        return "br"


def extractText(element, textArr, canvasWidth, canvasHeight ):
    elementType= element[4]
    elementText = element[5]
    if element_mapper['Text']==elementType or element_mapper['Text Button']==elementType:
        if elementText!="":
            xCur = element[0]
            yCur = element[1]
            curPos = PositionHelper.findPosition(xCur, yCur, canvasWidth, canvasHeight,WidthZoneText,HeightZoneText)
            textZone = posToTextZone(curPos)
            zonedText = textZone + ":" + elementText
            textArr.append(zonedText)


def getPositionObj(elementKey, curPosAreas, recPosDict):
    for curPos in range(24):
        if curPosAreas[curPos] != 0:
            if elementKey not in recPosDict:
                curElmPosObj = {}
                curElmPosObj[curPos] = (curPosAreas[curPos], 1)
                recPosDict[elementKey] = curElmPosObj
            else:
                if curPos not in recPosDict[elementKey]:
                    curElmPosObj = (curPosAreas[curPos], 1)
                    recPosDict[elementKey][curPos] = curElmPosObj
                else:
                    curElmPosObj = recPosDict[elementKey][curPos]
                    newCurPosAreas = round(curElmPosObj[0] + curPosAreas[curPos], 3)
                    recPosDict[elementKey][curPos] = (newCurPosAreas, curElmPosObj[1] + 1)


def elementArraytoRectPosText(elementArr, canvasWidth, canvasHeight):
    rectPositionDict = {}
    textArr = []
    for element in elementArr:
        xCur = element[0]
        yCur = element[1]
        width = element[2]
        height = element[3]
        elementType= element[4]
        curPosAreas = PositionHelper.findRectAreaPercent(xCur, yCur, width, height, canvasWidth, canvasHeight,
                                                                 WidthZoneElement, HeightZoneElement)
        extractText(element,textArr,canvasWidth,canvasHeight)
        getPositionObj(elementType, curPosAreas, rectPositionDict)

    return rectPositionDict, textArr


