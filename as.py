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
    avgR = 0.0
    avgG = 0.0
    avgB = 0.0

    def __init__(self):
        area = 0
        innerPoints = []
        boundary = []
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

    def dist(self, img, x, y):
        return sqrt((self.avgR-img.getPixel(x,y).getRed())**2 + (self.avgG-img.getPixel(x,y).getGreen())**2 + (self.avgB-img.getPixel(x,y).getBlue())**2)

    def isInnerPoint(self, x, y):   # if (x, y) is a inner point
        p = (x,y)
        if p in self.innerPoints:
            return True
        return False

    def addBoundary(self, x, y):
        p = (x,y)
        if p not in self.boundary:
            self.boundary.append(p)

    def getInnerPoints(self):
        return self.innerPoints

    def getArea(self):
        return self.area


def joinCluster(c, img, x, y, th, is_chkd, q):
    if (not is_chkd[x][y]) and c.dist(img, x, y) < th:
        q.put((x, y))
    is_chkd[x][y] = True


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
            img = sourceImage # for short
            while not q.empty():
                (x, y) = q.get()
                c.addInnerPoint(img, x, y)
                if x > 0:
                    joinCluster(c, img, x-1, y, th, is_chkd, q)
                    if y > 0:
                        joinCluster(c, img, x-1, y-1, th, is_chkd, q)
                    if y < height-1:
                        joinCluster(c, img, x-1, y+1, th, is_chkd, q)
                if x < width-1:
                    joinCluster(c, img, x+1, y, th, is_chkd, q)
                    if y > 0:
                        joinCluster(c, img, x+1, y-1, th, is_chkd, q)
                    if y < height-1:
                        joinCluster(c, img, x+1, y+1, th, is_chkd, q)
                if y > 0:
                    joinCluster(c, img, x, y-1, th, is_chkd, q)
                if y < height-1:
                    joinCluster(c, img, x, y+1, th, is_chkd, q)
                
            if c.getArea() > 4:
                C.append(c)

    for clus in C:
        for x,y in clus.getInnerPoints():
            newImage.setPixel(x, y, Pixel(floor(clus.avgR), floor(clus.avgG), floor(clus.avgB)))
        print(clus.getArea())

    sourceImage.setPosition(0,0)
    sourceImage.draw(myImageWindow)
    newImage.setPosition(width,0)
    newImage.draw(myImageWindow)
    if ofile != '' : 
        newImage.save(ofile)
    myImageWindow.exitOnClick()


