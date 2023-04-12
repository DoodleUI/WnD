from flask import Flask, render_template, request, Blueprint,send_from_directory,session,redirect,url_for,jsonify
import os
from random import randint
import binascii
import time
from similarUI import  SimilarTextVis
from helpers import StrokeParse
import pickle
from mlModule.FastPredict import FastPredict
import pickle
from mlModule.Predict23LSTM import Predictor23LSTM
from RectUtils.RectObj import RectObj
from mlModule import GetPrediction
from  similarUI import TextSearch

# set all folders for model
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
output_directory = os.path.join(APP_ROOT,'Trained_Model')
export_dir = os.path.join(APP_ROOT,'Trained_Model','tb')
RICO_PATH= os.path.join(APP_ROOT, 'similarUI',"RICO23BOWCount.pkl")

# loads dictionary for prediction
pkl_file = open(RICO_PATH, 'rb')
RICO = pickle.load(pkl_file)
pkl_file.close()

# set blueprint for the route
TextSearchRoutes = Blueprint('TextSearchRoutes', __name__, template_folder='templates')


RICO2 = {18: 1.3078818029580455, 17: 1.139763200847382, 7: 1.6042572583253525, 23: 0.20480255166735367, 13: 1.2705841196816363, 21: 1.2151277497211468, 14: 1.109574534964655, 4: 1.27350305661627, 1: 0.5610761239057094, 8: 1.2898451990888444, 3: 1.1001165287284727, 19: 0.2384449560029641, 22: 1.3393355557525861, 0: 0.9671365739392712, 2: 1.6390691490153984, 15: 0.8551847317189294, 6: 2.3419400282173046, 20: 0.026601131356820077, 9: 1.2291284704809808, 12: 0.6849345254248218, 16: 1.076536962335742, 10: 0.10631666807601393, 5: 0.254524251188198, 11: 0}
# loads model for prediction
PREDICTOR = Predictor23LSTM(export_dir,output_directory)
FASTPREDICT = FastPredict(PREDICTOR.classifier,PREDICTOR.example_input_fn)

# Create Json dict from rect to pass it to canvas to sketch.
def rectObjtoJson(rectObj):
    dictObj = {'x':str(rectObj.x), 'y':str(rectObj.y),'width':str(rectObj.width),'height':str(rectObj.height),'iconID':str(rectObj.iconID),'elementId':str(rectObj.elementId)}
    return dictObj

# Generate token to record the drawing of current session
def generateToken(tokenSize):
    byteToken = os.urandom(tokenSize)
    hexToken = binascii.hexlify(byteToken)
    return hexToken.decode("utf-8")

# Set all the session to deafault. This page is for comparison (A UI at left). Let cosider all item with this page as- "Compare"
@TextSearchRoutes.route('/VisTxCompare/')
def VisTxCompare():
    if 'username' not in session:
        session['username'] = generateToken(16)
    session['ELEMENTID'] =  0
    session['RectObjs'] = []
    session['SimilarStrokes']=[]
    session['strtTime'] = -1
    session['endTime'] = -1
    session['canvasStrokes'] =  []
    session['retrievedImage'] =  []
    session['searchTexts'] = []

    return render_template('TextVisualSearchCompare.html')




# Fetch prediction during drawing
@TextSearchRoutes.route('/MidPredictVisTx/', methods=['GET','POST'])
def MidPredictVisTx():
    if request.method == 'POST':
        canvas_strokes = request.form['save_data']
#        start = timeit.default_timer()
        if(session['strtTime']==-1):
            session['strtTime'] = round(time.monotonic()*1000)
            # session['dispTime'] = round(time.monotonic() * 1000)
        compressStroke,rect = StrokeParse.compressDataForFullUI(canvas_strokes)

        if len(compressStroke)==0:
            result = "Unchanged"
        else:
            result =GetPrediction.getFasterTop3Predict(compressStroke, PREDICTOR, FASTPREDICT )


        response = jsonify(predictedResult =result)
        return response

# A single canvas with for search. Let cosider all item with this page as- "Similar"
@TextSearchRoutes.route('/WnD/')
def WnD():
    session['ELEMENTID'] = 0
    session['RectObjs'] = []
    session['searchTexts'] = []
    session['strtTime'] = -1
    return render_template('TextVisualSearch.html')



# A single canvas with for search. Let cosider all item with this page as- "Similar"
@TextSearchRoutes.route('/VisTextTest/')
def VisTextTest():
    session['ELEMENTID'] = 0
    session['RectObjs'] = []
    session['searchTexts'] = []
    session['strtTime'] = -1
    return render_template('TextVisualSegmenter.html')


# When a text is removed from the search stack
@TextSearchRoutes.route('/RemoveText/', methods=['GET','POST'])
def RemoveText():
    if request.method == 'POST':
        search_text = request.form['save_data']

        prevSearchTexts = session['searchTexts']
        prevSearchTexts.remove(search_text)
        session['searchTexts'] = prevSearchTexts
        jsonRectObjs = session['RectObjs']

        canvasWidth = int(session['canvas_width'])
        canvasHeight = int(session['canvas_height'])
        hasRes, similarUI = SimilarTextVis.findSimilarUI(jsonRectObjs, RICO, canvasWidth, canvasHeight, RICO2,
                                                         "", session['searchTexts'],False)

        errorMsg=""
        response = jsonify(similarUI =similarUI,error= errorMsg)
        return response



# process search text, valiadte to show error message and fetch result

@TextSearchRoutes.route('/SearchWithText/', methods=['GET','POST'])
def SearchWithText():
    if request.method == 'POST':
        search_text = request.form['save_data']
        errorMsg = ""
        similarUI=[]
        prevSearchTexts = session['searchTexts']
        if(TextSearch.isInValid(search_text)):
            errorMsg="Invalid Text"
        else:
            jsonRectObjs = session['RectObjs']

            canvasWidth = int(session['canvas_width'])
            canvasHeight = int(session['canvas_height'])
            hasRes, similarUI = SimilarTextVis.findSimilarUI(jsonRectObjs, RICO, canvasWidth, canvasHeight, RICO2,search_text,prevSearchTexts,True )
            if hasRes:
                # For compare appending in the Similarity Measure
                prevSearchTexts.append(search_text)
                session['searchTexts'] = prevSearchTexts
            else:
                errorMsg ="No such UI"
        response = jsonify(similarUI =similarUI,error= errorMsg)
        return response

# Similar and compare functions are different. Have to track drawings in the session for prediction.
# When a text is removed from the search stack


# Remove last drawing from session for Similar and update search result.
@TextSearchRoutes.route('/RemoveLastIconForVsTx/', methods=['GET', 'POST'])
def RemoveLastIconForVsTx():
    elementID = session['ELEMENTID']
    rectObjs = session['RectObjs']
    for item in rectObjs:
        if (item['elementId'] == str(elementID - 1)):
            rectObjs.remove(item)
            break
    #    print(rectObjs)
    session['RectObjs'] = rectObjs
    session['ELEMENTID'] = elementID - 1
    # if len(rectObjs) == 0:
    #     response = jsonify(similarUI=[])
    #     return response

    # print(len(rectObjs))
    canvasWidth = int(session['canvas_width'])
    canvasHeight = int(session['canvas_height'])

    _,similarUIArray = SimilarTextVis.findSimilarUI(rectObjs, RICO, canvasWidth, canvasHeight, RICO2,"",session['searchTexts'],False )

    response = jsonify(similarUI=similarUIArray)
    return response

# Get last drawing from Canvas for Similar and update search result.

@TextSearchRoutes.route('/DrawSaveWithVsTx/', methods=['GET', 'POST'])
def DrawSaveWithVsTx():
    elementID = session['ELEMENTID']
    if request.method == 'POST':
        canvas_strokes = request.form['save_data']

        compressStroke, rect = StrokeParse.compressDataForFullUI(canvas_strokes)
        if len(compressStroke) == 0:
            responseResult = "Unchanged"
        else:
            result = GetPrediction.getFasterTop3Predict(compressStroke, PREDICTOR, FASTPREDICT)
            resultID = int(result[session['CurrentClassLabel']][1])

            rectObj = RectObj(rect, resultID, elementID)
            jsonRectObj = rectObjtoJson(rectObj)

            jsonRectObjs = session['RectObjs']

            jsonRectObjs.append(jsonRectObj)
            session['RectObjs'] = jsonRectObjs

            canvasWidth = int(session['canvas_width'])
            canvasHeight = int(session['canvas_height'])
            # tic = time.clock()

            _,similarUIArray = SimilarTextVis.findSimilarUI(jsonRectObjs, RICO, canvasWidth, canvasHeight, RICO2,"",session['searchTexts'],False)
            session['retrievedImage'] = similarUIArray[0:10]
            session['ELEMENTID'] = elementID + 1
            responseResult = "Updated"

        response = jsonify(predictedResult=responseResult, similarUI=similarUIArray)
        return response

# Get last drawing from Canvas for Compare, update search result and also put drawings in the session.

# Remove last drawing from session for Compare and update search result. As all json object of drawings are stored in the session, we need to change the json object.
@TextSearchRoutes.route('/DrawSaveForVsTxCompare/', methods=['GET', 'POST'])
def DrawSaveForVsTxCompare():
    elementID = session['ELEMENTID']
    if request.method == 'POST':
        canvas_strokes = request.form['save_data']
        similarUIArray=[]
        compressStroke, rect = StrokeParse.compressDataForFullUI(canvas_strokes)
        if len(compressStroke) == 0:
            responseResult = "Unchanged"
        else:
            result = GetPrediction.getFasterTop3Predict(compressStroke, PREDICTOR, FASTPREDICT)
            resultID = int(result[session['CurrentClassLabel']][1])
            rectObj = RectObj(rect, resultID, elementID)

            jsonRectObj = rectObjtoJson(rectObj)

            #   Maintaining Session for Tracking Elements
            jsonRectObjs = session['RectObjs']
            jsonRectObjs.append(jsonRectObj)
            session['RectObjs'] = jsonRectObjs

            #   Maintaining Session for Tracking Elements
            currentStrokes = session['SimilarStrokes']
            currentStrokes.append(compressStroke)
            session['SimilarStrokes'] = currentStrokes

            canvasWidth = int(session['canvas_width'])
            canvasHeight = int(session['canvas_height'])

            curTs = round(time.monotonic() * 1000) - session['strtTime']

            _,similarUIArray = SimilarTextVis.findSimilarUIForCompare(jsonRectObjs, currentStrokes, RICO, canvasWidth,
                                                                  canvasHeight, RICO2, session['taskID'],
                                                                  session['UIISimilarImage'], curTs,"",session['searchTexts'],False)
            session['retrievedImage'] = similarUIArray[0:10]
            # similarUIArray = SimilarTFIDFWithFiltering.findSimilarGridLoadedRICO(jsonRectObjs,RICO,RICO1,RICO2,canvasWidth,canvasHeight)
            responseResult = "Updated"
        session['endTime'] = round(time.monotonic()*1000)
        session['ELEMENTID'] = elementID + 1

        response = jsonify(predictedResult=responseResult, similarUI=similarUIArray)
        return response


