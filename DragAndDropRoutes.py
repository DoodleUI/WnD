import os
from DragAndDrop import  similarUIUtility
import pickle
from DragAndDrop import  SimilarTextVis
from flask import Flask, render_template, request, Blueprint,send_from_directory,session,redirect,url_for,jsonify
from ast import  literal_eval
from flask_cors import cross_origin
import time


APP_ROOT = os.path.dirname(os.path.abspath(__file__))
RICO_PATH= os.path.join(APP_ROOT,"DragAndDrop","RICODAD.pkl")

# loads dictionary for prediction
pkl_file = open(RICO_PATH, 'rb')
ricoDict = pickle.load(pkl_file)
pkl_file.close()
idf = {0: 0.62, 1: 1.13, 2: 1.02, 3: 1.34, 4: 1.34, 5: 0.8, 6: 1.34, 7: 1.21, 8: 0.96, 9: 1.32, 10: 1.28, 11: 1.72,
       12: 1.7, 13: 0, 14: 1.27, 15: 1.57, 16: 1.7, 17: 1.74, 18: 0.06, 19: 0.23, 20: 0.15, 21: 1.67, 22: 2.38, 23: 1.8,
       24: 2.59, 25: 2.11, 26: 0.82, 27: 0.79, 28: 1.42, 29: 1.49, 30: 1.54, 31: 1.59, 32: 1.33, 33: 1.66, 34: 1.7,
       35: 1.51, 36: 1.84, 37: 1.75, 38: 1.93, 39: 1.97, 40: 1.7, 41: 2.08, 42: 2.14, 43: 1.8, 44: 1.94, 45: 1.76,
       46: 1.6, 47: 1.96, 48: 1.9, 49: 2.06, 50: 1.64, 51: 1.77, 52: 2.38}
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_FOLDER = os.path.join(APP_ROOT,'templates','draganddrop','build')
DragAndDropRoute = Blueprint('DragAndDropRoute', __name__, template_folder=TEMPLATE_FOLDER)
@DragAndDropRoute.route('/getTopPicks/', methods=['GET', 'POST'])
@cross_origin(origin='*',headers=['Content-Type','Authorization'])
def getTopPicks():
    responseJson = jsonify("Invalid Request")
    print(request)
    if 'elements' not in request.headers and 'canvasWidth' not in request.headers and 'canvasHeight' not in request.headers:
        return responseJson
    try:

        elementArr = literal_eval(request.headers['elements'])
        canvasWidth = int(request.headers['canvasWidth'])
        canvasHeight = int(request.headers['canvasHeight'])
        start1 = time.process_time()
        drawingPos, textObjs = similarUIUtility.elementArraytoRectPosText(elementArr,canvasWidth,canvasHeight)
        print(time.process_time() - start1)
        start = time.process_time()
        # your code here
        _,resultUI = SimilarTextVis.findSimilarUI(drawingPos,ricoDict,idf,textObjs)
        print(time.process_time() - start)

        responseJson = jsonify(resultUI)
    except:

        return responseJson
    return responseJson


@DragAndDropRoute.route('/DragnSearch/', methods=['GET', 'POST'])
@cross_origin(origin='*',headers=['Content-Type','Authorization'])
def serve():
    return render_template('index.html')

@DragAndDropRoute.route('/static/<folder>/<filename>')
def send_static(folder, filename):
    directory_path = os.path.join(TEMPLATE_FOLDER,'static',folder)
    return send_from_directory(directory_path, filename)


if __name__ == '__main__':
    # print("Damn it")
    # {19: {20: (0.733, 1), 21: (0.267, 1)}}
    canvasWidth = 500
    canvasHeight = 500
    curElement = [[56, 473, 90, 50, 19, 'Yes'], ]
    drawingPos, textObjs = similarUIUtility.elementArraytoRectPosText(curElement, canvasWidth, canvasHeight)
    _, resultUI = SimilarTextVis.findSimilarUI(drawingPos, ricoDict, idf, textObjs)
    print(resultUI[0:5])
