#!/usr/bin/python3

import queue
import cImage
from cImage import Pixel
from math import log
from math import sqrt
from math import floor

class Cluster:
    area = 0
    innerPoints = []
    boundary = []
    path = []
    avgR = 0.0
    avgG = 0.0
    avgB = 0.0

    def __init__(self):
        area = 0
        innerPoints = []
        boundary = []
        path = []
        avgR = 0.0
        avgG = 0.0
        avgB = 0.0
        
    def addInnerPoint(self, img, x, y):
        p = (x,y)
        if self.area == 0:
            self.avgR = img.getPixel(x,y).getRed()
            self.avgG = img.getPixel(x,y).getGreen()
            self.avgB = img.getPixel(x,y).getBlue()
            self.innerPoints.append(p)
            self.area += 1
        else:
            if p not in self.innerPoints:
                self.avgR = (self.avgR*self.area + img.getPixel(x,y).getRed())/(self.area+1)
                self.avgG = (self.avgG*self.area + img.getPixel(x,y).getGreen())/(self.area+1)
                self.avgB = (self.avgB*self.area + img.getPixel(x,y).getBlue())/(self.area+1)
                self.innerPoints.append(p)
                self.area += 1

    def addPath(self, x, y):
        p = (x, y)
        self.path.append(p)
    
    def dist(self, p, x, y):
        return sqrt((self.avgR-p.getRed())**2 + (self.avgG-p.getGreen())**2 + (self.avgB-p.getBlue())**2)

    def isInnerPoint(self, x, y):   # if (x, y) is a inner point
        p = (x,y)
        if p in self.innerPoints:
            return True
        return False

    def addBoundary(self, x, y):
        p = (x,y)
        if p not in self.boundary:
            self.boundary.append(p)

    def isBoundary(self, x, y):
        p = (x, y)
        if p in self.boundary:
            return True
        return False

    def getInnerPoints(self):
        return self.innerPoints

    def getBoundary(self):
        return self.boundary

    def getArea(self):
        return self.area


def joinCluster(c, p, x, y, th, is_chkd, q):
    if is_chkd[x][y]:
        return
    if c.dist(p, x, y) < th:
        q.put((x, y))
    else:
        c.addBoundary(x,y)
    is_chkd[x][y] = True


'''
Return leftmost point in lp.
lp is not null.
'''
def leftMost(lp):
    mini = lp[0][0]
    r = lp[0]
    for p in lp:
        if p[0]<mini:
            mini = p[0]
            r = p
    return r

'''
The main function.
'''
def main( ifile = 'test.jpg',
                # file to open
                ofile = '', \
                # file to save
                th = 20, \
                # deviation threshold
				) :
    try:
        sourceImage = cImage.FileImage(ifile)
    except:
        print('Failed to open the given source file, which may not exist!')
        return
    width = sourceImage.getWidth()
    height = sourceImage.getHeight()
    is_chkd = [[False for x in range(height)] for y in range(width)]

    myImageWindow = cImage.ImageWin('Main',2*width,height)
    newImage = cImage.EmptyImage(width,height)
    # background -> white
    for i in range(width):
        for j in range(height):
            newImage.setPixel(i,j,Pixel(255,255,255))

    C = [] # list of clusters
    for i in range(width):
        for j in range(height):
            # check if (i,j) is already checked
            if is_chkd[i][j]:
                continue
            # now (i,j) is new
            c = Cluster()
            q = queue.Queue()
            q.put((i, j))
            is_chkd[i][j] = True
            while not q.empty():
                (x, y) = q.get()
                c.addInnerPoint(sourceImage, x, y)
                if x > 0:
                    joinCluster(c, sourceImage.getPixel(x-1,y), x-1, y, th, is_chkd, q)
                else:
                    c.addBoundary(x,y)
##                    if y > 0:
##                        joinCluster(c, sourceImage.getPixel(x-1,y-1), x-1, y-1, th, is_chkd, q)
##                    if y < height-1:
##                        joinCluster(c, sourceImage.getPixel(x-1,y+1), x-1, y+1, th, is_chkd, q)
                if x < width-1:
                    joinCluster(c, sourceImage.getPixel(x+1,y), x+1, y, th, is_chkd, q)
                else:
                    c.addBoundary(x,y)
##                    if y > 0:
##                        joinCluster(c, sourceImage.getPixel(x+1,y-1), x+1, y-1, th, is_chkd, q)
##                    if y < height-1:
##                        joinCluster(c, sourceImage.getPixel(x+1,y+1), x+1, y+1, th, is_chkd, q)
                if y > 0:
                    joinCluster(c, sourceImage.getPixel(x,y-1), x, y-1, th, is_chkd, q)
                else:
                    c.addBoundary(x,y)
                if y < height-1:
                    joinCluster(c, sourceImage.getPixel(x,y+1), x, y+1, th, is_chkd, q)
                else:
                    c.addBoundary(x,y)
                
            if c.getArea() > 100:
                C.append(c)

    untraced = [[True for x in range(height)] for y in range(width)]
    for c in C:
        B = c.getBoundary()
        lmp = leftMost(B)
        c.addPath(lmp[0], lmp[1])
        lastP = None
        curX = lmp[0]
        curY = lmp[1]
        while True:
            if (curX, curY-1) != lastP and (curX, curY-1) != lmp and c.isBoundary(curX, curY-1) and untraced[curX][curY-1]:
                c.addPath(curX, curY-1)
                lastP = (curX, curY)
                untraced[curX][curY] = False
                curY -= 1
                continue
            if (curX+1, curY-1) != lastP and (curX+1, curY-1) != lmp and c.isBoundary(curX+1, curY-1) and untraced[curX+1][curY-1]:
                c.addPath(curX+1, curY-1)
                lastP = (curX, curY)
                untraced[curX][curY] = False
                curX += 1
                curY -= 1
                continue
            if (curX+1, curY) != lastP and (curX+1, curY) != lmp and c.isBoundary(curX+1, curY) and untraced[curX+1][curY]:
                c.addPath(curX+1, curY)
                lastP = (curX, curY)
                untraced[curX][curY] = False
                curX += 1
                continue
            if (curX+1, curY+1) != lastP and (curX+1, curY+1) != lmp and c.isBoundary(curX+1, curY+1) and untraced[curX+1][curY+1]:
                c.addPath(curX+1, curY+1)
                lastP = (curX, curY)
                untraced[curX][curY] = False
                curX += 1
                curY += 1
                continue
            if (curX, curY+1) != lastP and (curX, curY+1) != lmp and c.isBoundary(curX, curY+1) and untraced[curX][curY+1]:
                c.addPath(curX, curY+1)
                lastP = (curX, curY)
                untraced[curX][curY] = False
                curY += 1
                continue
            if (curX-1, curY+1) != lastP and (curX-1, curY+1) != lmp and c.isBoundary(curX-1, curY+1) and untraced[curX-1][curY+1]:
                c.addPath(curX-1, curY+1)
                lastP = (curX, curY)
                untraced[curX][curY] = False
                curX -= 1
                curY += 1
                continue
            if (curX-1, curY) != lastP and (curX-1, curY) != lmp and c.isBoundary(curX-1, curY) and untraced[curX-1][curY]:
                c.addPath(curX-1, curY)
                lastP = (curX, curY)
                untraced[curX][curY] = False
                curX -= 1
                continue
            if (curX-1, curY-1) != lastP and (curX-1, curY-1) != lmp and c.isBoundary(curX-1, curY-1) and untraced[curX-1][curY-1]:
                c.addPath(curX-1, curY-1)
                lastP = (curX, curY)
                untraced[curX][curY] = False
                curX -= 1
                curY -= 1
                continue
            break

    f = open('test_output.svg', 'w')
    S = '<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 '+str(width)+' '+str(height)+'\" enable-background=\"new 0 0 '+str(width)+' '+str(height)+'\">'
    for c in C:
        S = S+'<path d=\"M'
        for i in range(len(c.path)):
            S = S+str(c.path[i][0])+' '+str(c.path[i][1])
            if i < len(c.path)-1:
                S = S+'L'
            else:
                S = S+'Z\"'
        S = S+' fill=\"rgb('+str(floor(c.avgR))+','+str(floor(c.avgG))+','+str(floor(c.avgB))+')\"/>'
    S = S+'</svg>'
    f.write(S)
    f.close()

    sourceImage.setPosition(0,0)
    sourceImage.draw(myImageWindow)
    newImage.setPosition(width,0)
    newImage.draw(myImageWindow)
    if ofile != '' : 
        newImage.save(ofile)
    myImageWindow.exitOnClick()


