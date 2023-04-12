"""
Created on Tue Feb 25 12:17:00 2020

@author: sxm6202xx
"""
import os
from similarUI import similarUIUtility
from similarUI import FindIntersectingPercentage
import pickle
from  similarUI import  TextSearch
import sys
# divide the canvas into 4 by 6 zones
WidthZone = 4
HeightZone = 6

# Mapping class Name to Dictionay Key

dictMapper = {'avatar': 0, 'back': 1, 'camera': 2, 'cancel': 3, 'checkbox': 4, 'generalIcon': 5, 'dropDown': 6,
              'envelope': 7, 'forward': 8, 'house': 9, 'imageIcon': 10, 'leftarrow': 1, 'menu': 12, 'play': 13,
              'plus': 14, 'search': 15, 'settings': 16, 'share': 17, 'sliders': 18, 'square': 19, 'squiggle': 20,
              'star': 21, 'switch': 22, 'textButton': 23}
hierMapper = {'avatar': 24, 'back': 25, 'camera': 26, 'cancel': 27, 'checkbox': 28, 'generalIcon': 29, 'dropDown': 30,
              'envelope': 31, 'forward': 32, 'house': 33, 'imageIcon': 25, 'leftarrow': 35, 'menu': 36, 'play': 37,
              'plus': 38, 'search': 39, 'settings': 40, 'share': 41, 'sliders': 42, 'square': 43, 'squiggle': 44,
              'star': 45, 'switch': 46, 'textButton': 47}
noOfElement = 24


# Divide canvas into 4 by 4 grid and find position of element in the grid
def findPosition(x, y, width, height):
    # print(x,y,width, height)
    xGridSize = width / WidthZone
    yGridSize = height / HeightZone
    xGrid = int(x / xGridSize)
    yGrid = int(y / yGridSize)
    return xGrid + yGrid * WidthZone


def cordToInt(x, y):
    return x + y * WidthZone


# From the elementType and position generate object position weight. Current no use of parent hierarchy

def getPositionObj(elementType, parent, curPosAreas, recPosDict):
    elementKey = dictMapper[elementType]

    for curPos in range(24):
        if curPosAreas[curPos] != 0:
            if elementKey not in recPosDict:
                curElmPosObj = {}
                curElmPosObj[curPos] = (curPosAreas[curPos], 1)
                recPosDict[elementKey] = curElmPosObj
            else:
                if curPos not in recPosDict[elementKey]:
                    curElmPosObj = (curPosAreas[curPos], 1)
                    # curElmPosObj[curPos] = (curPosAreas[curPos],1)
                    recPosDict[elementKey][curPos] = curElmPosObj
                else:
                    curElmPosObj = recPosDict[elementKey][curPos]
                    newCurPosAreas = round(curElmPosObj[0] + curPosAreas[curPos], 3)
                    recPosDict[elementKey][curPos] = (newCurPosAreas, curElmPosObj[1] + 1)


def hierArchyToDictObjInternal(parent, child, rectPositionDict, width, height):
    elementType = child.getIconName()

    # if child.iconID !=-1:
    xCur = child.x + parent.x
    yCur = child.y + parent.y
    curPosAreas = FindIntersectingPercentage.findRectAreaPercent(xCur, yCur, child.width, child.height, width, height,
                                                                 WidthZone, HeightZone)

    getPositionObj(elementType, parent, curPosAreas, rectPositionDict)
    # if hierarchy matches then give weight 1

    for curChild in child.mChildren:
        hierArchyToDictObjInternal(child, curChild, rectPositionDict, width, height)
    return

# From hierarchy of Rectobj's create dictionay object for comparison.
def hierArchyToDictObj(rootObj, width, height):
    rectPositionDict = {}
    for curChild in rootObj.mChildren:
        hierArchyToDictObjInternal(rootObj, curChild, rectPositionDict, width, height)

    return rectPositionDict


# create hierarchy for finding text button
# then convert elements into array of element
def getRectObjsWithHier(jsonRootObjs, width, height):
    # print(jsonRootObjs)
    rawRects = similarUIUtility.jsonToRect(jsonRootObjs)

    rectObj = {}
    if (len(rawRects) != 0):
        rootObj = similarUIUtility.createHierachy(rawRects, width, height)

        rectObj = hierArchyToDictObj(rootObj, width, height)

    return rectObj


# For a position find the neighbors in the bigger grid. Like for 4 by 6, look for 2 by 3 grid.

def find2Grid(pos):
    if pos in [0,1,4,5]:
        return [0,1,4,5]
    elif pos in [2,3,6,7]:
        return [2,3,6,7]
    elif pos in [8,9,12,13]:
        return [8,9,12,13]
    elif pos in [10,11,14,15]:
        return [10,11,14,15]
    elif pos in [16,17,20,21]:
        return [16,17,20,21]
    else:
        return [18,19,22,23]

# For a position find the neighbors in 8 diection.


def find2GridNeighbor(pos):
    neighDict = {0:[0,1,4,5],1:[0,1,4,5,2,6],2:[1,2,3,5,6,7],3:[2,3,6,7],
                 4:[0,1,4,5,8,9],5:[0,1,2,4,5,6,8,9,10],6:[1,2,3,5,6,7,9,10,11],7:[2,3,6,7,10,11],
                 8:[4,5,8,9,12,13],9:[4,5,6,8,9,10,12,13,14],10:[5,6,7,9,10,11,13,14,15],11:[6,7,10,11,14,15],
                 12:[8,9,12,13,16,17],13:[8,9,10,12,13,14,16,17,18],14:[9,10,11,13,14,15,17,18,19],15:[10,11,14,15,18,19],
                  16:[12,13,16,17,20,21],17:[12,13,14,16,17,18,20,21,22],18:[13,14,15,17,18,19,21,22,23],19:[14,15,18,19,22,23],
                 20:[16,17,20,21],21:[16,17,18,20,21,22],22:[17,18,19,21,22,23],23:[18,19,22,23]}
    return neighDict[pos]

def common_member(a, b):
    a_set = set(a)
    b_set = set(b)
    if (a_set & b_set):
        return True
    else:
        return False


def findWeightWithArea(posObject, posRico):
    # Paremters are optimized in another project for sample data.
    parameters=[9,8,39,0.4,547]
    # Weight for match in whole UI
    firstPyramid=parameters[0]
    # Weight for match in same neighbor grid
    secondPyramid=parameters[1]
    # Weight for match in same grid

    thirdPyramid = parameters[2]
    ricoDictKyes = posRico.keys()
    weight=firstPyramid
    # Penalty if number of elements in RICO and current drawing differs for a certain element in a certain grid.
    elemDifferPenalty = parameters[3]
    # Penalty if weight of elements in RICO and current drawing differs for a certain element in a certain grid.
    # weight = element unit area / no of element
    singledifferWeight = parameters[4]

    for pos in posObject:
        if pos in ricoDictKyes:
            noOfElement = posObject[pos][1]
            drawingAreaPosWeight = posObject[pos][0] / noOfElement

            elementInRICO = posRico[pos][1]
            # weight = element unit area / no of element
            areaWeightInRICO = posRico[pos][0] / (100 * elementInRICO)

            noOfElement = posObject[pos][1]

            elementDifferWeight = 1
            # Find difference in element number
            elementDiffer = abs(noOfElement - elementInRICO)
            # Penalty if element number differ
            if elementDiffer != 0:
                elementDifferWeight = max(0,elementDifferWeight - elemDifferPenalty * elementDiffer)
            # Penalty if element weight differ
            areaWeightDiffer = 1-abs(areaWeightInRICO - drawingAreaPosWeight)
            # Scoring function
            weight = weight+thirdPyramid*(posObject[pos][0]/posObject[pos][1])*(posRico[pos][0]/posRico[pos][1]) + (noOfElement*elementDifferWeight*areaWeightDiffer * singledifferWeight)
            # Scoring function for neighbor match

        elif common_member(find2Grid(pos),ricoDictKyes):
            weight = weight + secondPyramid*(posObject[pos][0]/posObject[pos][1])
    return weight


def findWeightWithArea_Optimized(posObject, posRico):
    # Paremters are optimized in another project for sample data.
    # Weight for match in whole UI

    parameters =[1, 1, 11, 0.7, 3, 12, 8]

    firstPyramid=parameters[0]
    # Weight for match in same neighbor grid
    secondPyramid=parameters[1]
    # Weight for match in same grid

    thirdPyramid = parameters[2]
    ricoDictKyes = posRico.keys()
    weight=firstPyramid
    # Penalty if number of elements in RICO and current drawing differs for a certain element in a certain grid.
    elemDifferPenalty = parameters[3]
    # Penalty if weight of elements in RICO and current drawing differs for a certain element in a certain grid.
    # weight = element unit area / no of element
    areaDifferWeight = parameters[5]
    elementDifferWeight = parameters[4]
    skethc_contrib = parameters[6]
    # skethc_contrib2 = parameters[7]
    # rico_contrib = parameters[7]

    for pos in posObject:
        if pos in ricoDictKyes:

            drawingArea = posObject[pos][0]

            elementInRICO = posRico[pos][1]
            # weight = element unit area / no of element
            areaInRico = posRico[pos][0] / (100)

            noOfElementInSketch = posObject[pos][1]


            # Find difference in element number
            noElementDiffer = abs(noOfElementInSketch - elementInRICO)

            # Penalty if element number differ
            if noElementDiffer != 0:
                noElementDiffer = max(0,1 - noElementDiffer * elemDifferPenalty)

            # Penalty if element weight differ

            areaDiffer = 1-abs(areaInRico - drawingArea)

            # Scoring function
            weight = weight+thirdPyramid + skethc_contrib* posObject[pos][1] + noElementDiffer*elementDifferWeight + areaDiffer * areaDifferWeight

            # Scoring function for neighbor match

        elif common_member(find2Grid(pos),ricoDictKyes):
            weight = weight + secondPyramid
    return weight

def findAllUI(elementType, rectPosObj, similarUI, rico, idf):
    newSimilarUI={}
    max_score = 0
    if elementType != dictMapper['square']:
        # loop through individual UI element in drawing and calucate weight:
            ricoObjs = rico[elementType]
            for indvUI in ricoObjs:

                if str(indvUI) not in newSimilarUI:
                    newSimilarUI[str(indvUI)]=findWeightWithArea_Optimized(rectPosObj,rico[elementType][indvUI])*idf[elementType]
                else:
                     newSimilarUI[str(indvUI)] = newSimilarUI[str(indvUI)] +findWeightWithArea_Optimized(rectPosObj, rico[elementType][indvUI]) * idf[elementType]
                max_score = max(newSimilarUI[str(indvUI)], max_score)

    similarUI = {x: similarUI.get(x, 0) + newSimilarUI.get(x, 0)/max_score  for x in set(similarUI).union(newSimilarUI)}

    return similarUI


def findSimilarUI(jsonRectObjs, rico, canvasWidth, canvasHeight, idf, curText, previousTexts,searchCurText, compare=False, targetUI=None):
    # generate rect object from drawing
    rectObjs = getRectObjsWithHier(jsonRectObjs, canvasWidth, canvasHeight)
    # visual search
    similarUI = {}
    for elementType in rectObjs:
        similarUI = findAllUI(elementType, rectObjs[elementType], similarUI, rico, idf)

    # text search
    textSimilar = {}
    hasCurRes = False
    if searchCurText:
        hasCurRes, textSimilar = TextSearch.searchAllText(previousTexts, curText)

    else:
        if len(previousTexts)!=0:
            textSimilar = TextSearch.removeTextSearch(previousTexts)

    # merge text and visual search
    for key in textSimilar:
        if key in similarUI:
            similarUI[key] = similarUI[key] + textSimilar[key]
        else:
            similarUI[key] = textSimilar[key]

    # sort result for display
    resultUI = [k for k, v in sorted(similarUI.items(), key=lambda item: item[1], reverse=True)]
    return hasCurRes,resultUI








