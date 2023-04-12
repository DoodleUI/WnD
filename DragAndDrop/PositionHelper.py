
from RectUtils.Rect import Rect


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

def findPosition(x, y, width, height,WidthZone,HeightZone):
    # print(x,y,width, height)
    xGridSize = width / WidthZone
    yGridSize = height / HeightZone
    xGrid = int(x / xGridSize)
    yGrid = int(y / yGridSize)
    return xGrid + yGrid * WidthZone


def cordToInt(x, y,WidthZone):
    return x + y * WidthZone

def findIntersectingArea(curRect, gridRects):
    dictAreas =[]
    for gRect in gridRects:
        (gRectbrX ,gRectbrY) = gRect.br()
        (curRectbrX ,curRectbrY) = curRect.br()
        xLeft =max(curRect.x ,gRect.x)
        yLeft =max(curRect.y ,gRect.y)
        xBR = min(gRectbrX ,curRectbrX)
        yBR = min(gRectbrY ,curRectbrY)
        if xLeft>=xBR or yLeft>=yBR:
            dictAreas.append(0)
        else:
            area = round((xBR -xLeft ) *(yBR -yLeft ) /curRect.area() ,3)
            dictAreas.append(area)

    return dictAreas


def findAllRects(width, height, widthZone, heightZone):

    dictRects =[]
    gridWidth = width /widthZone
    gridHeight = height /heightZone
    for i in range(heightZone):
        for j in range(widthZone):
            curRect = Rect( gridWidth *j ,gridHeight * i, gridWidth, gridHeight)
            dictRects.append(curRect)

    return dictRects


def findRectAreaPercent(x, y, width, height, canvasWidht, canvasHeight, widthZone, heightZone):
    # print(x,y,width, height, canvasWidht, canvasHeight, widthZone, heightZone)
    curRect = Rect(x, y, width, height)
    allRects = findAllRects(canvasWidht, canvasHeight, widthZone, heightZone)
    return findIntersectingArea(curRect, allRects)


if __name__ == "__main__":
    print("do nothing")    