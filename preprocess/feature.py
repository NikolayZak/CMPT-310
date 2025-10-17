import cv2 as cv
import numpy as np

def getOutline(img):
    img = img.astype(np.uint16)
    color = (img[:,:,0] + img[:,:,1]  + img[:,:,2]) >= 600
    return color.astype(np.uint8)*255

kernel = np.ones((3,3), np.uint8)
dist_kernel = np.ones((9,9), np.uint8)
def getObjects(img):
    gray = getOutline(img)
    mask = cv.distanceTransform(gray, cv.DIST_L2, 3)
    mask = cv.normalize(mask, mask, 0, 255, cv.NORM_MINMAX)
    _,mask = cv.threshold(mask, 50, 255, cv.THRESH_BINARY)
    mask = mask.astype(np.uint8)
    mask = cv.dilate(mask, dist_kernel, iterations=2)
    #mask = cv.dilate(mask, dist_kernel)
    mask = cv.bitwise_not(mask)
    gray = cv.bitwise_and(gray, mask)
    # replace threshold with morph open to remove popping
    #thresh = cv.morphologyEx(gray, cv.MORPH_OPEN, kernel)
    contours, heir = cv.findContours(gray, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
    return contours

def isFrameGameplay(frame):
    #pause menu + upgrade check
    cornerX = (0, int(frame.shape[0]*0.075))
    cornerY = (int(frame.shape[1]*0.9),frame.shape[1]-1)
    if np.any(frame[cornerX[0]:cornerX[1],cornerY[0]:cornerY[1],:]):
        return False
    # game tip check
    _,blue = cv.threshold(frame[:,:,0], 190, 255, 0)
    contours_blue, heir = cv.findContours(blue, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
    _,red = cv.threshold(frame[:,:,2], 190, 255, 0)
    contours_red, heir = cv.findContours(red, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
    info_box = []
    for contour in contours_blue:
        rect = cv.minAreaRect(contour)
        x,y = rect[0]
        w,h = rect[1]
        if w > 40 or h > 40:
            # this might be better off as a crop done before findContours
            if x < frame.shape[1]* 0.8 and x > frame.shape[1]*0.2:
                if y < frame.shape[0]* 0.8 and y > frame.shape[0]*0.25:
                    rect = cv.boundingRect(contour)
                    if rect[2] > rect[3] * 4/3:
                        info_box.append((contour, rect))
    for contour in contours_red:
        rect = cv.boundingRect(contour)
        for main in info_box:
            if rect[2] / main[1][2] > 2/3 - 0.05:
                if rect[2] / main[1][2] < 2/3 + 0.05:
                    if rect[3] *3  <  main[1][3] and rect[3] > main[1][3]*0.2:
                        if rect[0] > rect[2] / main[1][2] * (2/3 - 0.1):
                            if rect[1] < main[1][1]:
                                return False
    return True


def hasUpgradeMenu(frame):
    threshold = 0.8
    #right side upgrade menu
    cornerX = (int(frame.shape[1]*0.84375),int(frame.shape[1]*0.85625))
    cornerY = (int(frame.shape[0]*0.06), int(frame.shape[0]*0.87))
    check = frame[cornerY[0]:cornerY[1],cornerX[0]:cornerX[1],:]
    if np.count_nonzero(check)/np.prod(check.shape)>threshold:
        return 1
    #left side upgrade menu
    cornerX = (int(frame.shape[1]*0.015625),int(frame.shape[1]*0.02))
    cornerY = (int(frame.shape[0]*0.06), int(frame.shape[0]*0.87))
    check = frame[cornerY[0]:cornerY[1],cornerX[0]:cornerX[1],:]
    return -1*(np.count_nonzero(check)/np.prod(check.shape)>threshold)

def distance(point1, point2):
    return abs(point1[0] - point2[0]) + abs(point1[1] - point2[1])

class TowerLocationTracker:
    def __init__(self):
        self.baseTowerMask = None
    def createMasks(self, frame):
        if self.baseTowerMask is None:
            self.baseTowerMask = np.full(frame.shape[0:2], 255, np.uint8)
            self.baseTowerMask[:,int(frame.shape[1]*0.85625):frame.shape[1]-1] = 0
            self.baseTowerMask[int(frame.shape[0]*0.91825):frame.shape[0]-1,0:int(frame.shape[1]*0.071875)] = 0
            # for placement cancel button
            self.baseTowerMask[int(frame.shape[0]*0.075):int(frame.shape[0]*0.1425),int(frame.shape[1]*0.8125):frame.shape[1]-1] = 0
            self.leftTowerMask = np.full(frame.shape[0:2], 255, np.uint8)
            self.leftTowerMask[:,0:int(frame.shape[1]*0.3625)] = 0
            self.leftTowerMask[:,int(frame.shape[1]*0.85625):frame.shape[1]-1] = 0
            # for placement cancel button
            self.leftTowerMask[int(frame.shape[0]*0.075):int(frame.shape[0]*0.1425),int(frame.shape[1]*0.8125):frame.shape[1]-1] = 0
            self.rightTowerMask = np.full(frame.shape[0:2], 255, np.uint8)
            self.rightTowerMask[:,int(frame.shape[1]*0.5875):frame.shape[1]-1] = 0
            self.rightTowerMask[int(frame.shape[0]*0.91825):frame.shape[0]-1,0:int(frame.shape[1]*0.071875)] = 0
            
    def towerMask(self, frame):
        self.createMasks(frame)
        side = hasUpgradeMenu(frame)
        if side == 1:
            return self.rightTowerMask
        if side == -1:
            return self.leftTowerMask
        return self.baseTowerMask
    def getSelectedTower(self, frame):
        if not isFrameGameplay(frame):
            return None
        filtered_frame = cv.bitwise_and(frame,frame, mask=self.towerMask(frame))
        possibleLocations = [] # mean position, total position, total entries
        contours = getObjects(filtered_frame)
        for contour in contours:
            contour_rect = cv.minAreaRect(contour)
            w,h = contour_rect[1]
            if w > 60 and h > 60:
                rect = cv.boundingRect(contour)
                x = rect[0] + rect[2] / 2
                y = rect[1] + rect[3] / 2
                addLocation = True
                if len(possibleLocations) > 0:
                    for i in range(len(possibleLocations)):
                        if distance((x,y), possibleLocations[i][0]) < 200:
                            addLocation = False
                            totalPos = possibleLocations[i][1]
                            possibleLocations[i][1] = (x+totalPos[0], y+ totalPos[1])
                            totalPos = possibleLocations[i][1]
                            possibleLocations[i][2] += 1
                            totalCount = possibleLocations[i][2]
                            possibleLocations[i][0] = (totalPos[0] / totalCount, totalPos[1]/totalCount)
                if addLocation:
                    possibleLocations.append([(x,y),(x,y),1])
        towerPosition = None
        if len(possibleLocations) > 0:
            largestCount = 0
            for location in possibleLocations:
                if location[2] > largestCount:
                    largestCount = location[2]
                    towerPosition = (int(location[0][0]), int(location[0][1]))
        return towerPosition
    
