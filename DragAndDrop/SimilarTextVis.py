"""
Created on Tue Feb 25 12:17:00 2020

@author: sxm6202xx
"""
from  DragAndDrop import  TextSearch
from  DragAndDrop import  PositionHelper
from  DragAndDrop import  similarUIUtility
import os
import pickle

# find if element is a type of text
def isTextButton(elementType):
    if elementType in [19]:
        return True
    return False

# No score calculation for container. For text- only consider content
def avoidSimilarity(elementType):
    if elementType in [18,13]:
        return True
    return False

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

        elif PositionHelper.common_member(PositionHelper.find2Grid(pos),ricoDictKyes):
            weight = weight + secondPyramid
    return weight

def findAllUI(elementType, rectPosObj, similarUI, rico, idf):
    newSimilarUI={}
    max_score = 0
    ricoObjs = rico[elementType]
    for indvUI in ricoObjs:

        if str(indvUI) not in newSimilarUI:
            newSimilarUI[str(indvUI)]=findWeightWithArea_Optimized(rectPosObj,rico[elementType][indvUI])*idf[elementType]
        else:
            newSimilarUI[str(indvUI)] = newSimilarUI[str(indvUI)] + findWeightWithArea_Optimized(rectPosObj, rico[elementType][indvUI]) * idf[elementType]
        max_score = max(newSimilarUI[str(indvUI)], max_score)

    # Give less score for text button position and more on content
    if isTextButton(elementType):
        max_score = max_score/0.25

    similarUI = {x: similarUI.get(x, 0) + newSimilarUI.get(x, 0)/max_score  for x in set(similarUI).union(newSimilarUI)}

    return similarUI


def findSimilarUI(rectObjs, rico, idf, curText):
    # generate rect object from drawing
    # visual search
    similarUI = {}
    for elementType in rectObjs:
        # Avoid results for UI Type - Cotainer
        if not avoidSimilarity(elementType):
            similarUI = findAllUI(elementType, rectObjs[elementType], similarUI, rico, idf)

    # For check

    # justCheck = [k for k, v in sorted(similarUI.items(), key=lambda item: item[1], reverse=True)]
    # print("Only similarity top-score :{}",justCheck[0] )
    # print(similarUI[justCheck[0]])
    # text search
    textSimilar = {}
    hasCurRes = False
    if len(curText)>0:
        textSimilar = TextSearch.searchAllText(curText)


    # merge text and visual search
    for key in textSimilar:
        if key in similarUI:
            similarUI[key] = similarUI[key] + textSimilar[key]
        else:
            similarUI[key] = textSimilar[key]
    # print("After text similarity top-score :{}",justCheck[0] )
    # print(similarUI[justCheck[0]])

    resultUI = [k for k, v in sorted(similarUI.items(), key=lambda item: item[1], reverse=True)]

    # print(similarUI[resultUI[0]])
    # print("Combined top-score :{} - {}",resultUI[0],  )
    return hasCurRes,resultUI





