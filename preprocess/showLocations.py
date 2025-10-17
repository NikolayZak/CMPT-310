from video import *
from extractor import Extractor
from feature import TowerLocationTracker, distance 
from towertype import getTowerName

import numpy as np
import cv2 as cv

locations = {}
tracker = TowerLocationTracker()
lastSelectedTower = None
def replaceLater1(img, frame):
    global towerType
    global lastSelectedTower
    if not lastSelectedTower is None:
        towerType = getTowerName(img)
        frame = cv.putText(frame, towerType, (lastSelectedTower[0]+20, lastSelectedTower[1]+20,), cv.FONT_HERSHEY_SIMPLEX, 2,(0, 0, 0), 20)
        frame = cv.putText(frame, towerType, (lastSelectedTower[0]+20, lastSelectedTower[1]+20,), cv.FONT_HERSHEY_SIMPLEX, 2,(255, 255, 255), 10)
    return frame

def replaceLater(frame):
    global tracker
    global lastSelectedTower
    result = frame.copy()#np.zeros(frame.shape, np.uint8)
    towerLocation = tracker.getSelectedTower(frame)
    towerAdded = False
    for tower in locations:
        if towerLocation is None and not lastSelectedTower is None:
            if distance(lastSelectedTower, tower) < 200:
                result = cv.circle(result, tower, 50, (255, 255, 0), 10)
        else:
            if not towerLocation is None and distance(towerLocation, tower) < 200:
                result = cv.circle(result, tower, 50, (255, 255, 255), 10)
                lastSelectedTower = tower
                towerAdded = False
            else:
                result = cv.circle(result, tower, 50, (255, 0, 0), 10)
    if not towerLocation is None and not towerAdded:
        locations[towerLocation] = 1# replace
        lastSelectedTower = towerLocation
        result = cv.circle(result, towerLocation, 50, (255, 255, 255), 10)
    return result 

if not __name__ == "__main__":
    extract = Extractor("test/feature/out.mp4", user=replaceLater, user1=replaceLater1)
    #readVideo("test/download/meadow.mp4", extract.handleFrame, "0:58" , "1:01", extract.setInfo)
    #readVideo("test/download/meadow.mp4", extract.handleFrame, "0:58" , "4:47", extract.setInfo)
    readVideo("test/download/meadow.mp4", extract.handleFrame, "3:18" , "4:47", extract.setInfo)
    extract.close()
else:
    import sys
    if len(sys.argv) < 5:
        print("showLocations.py <input file> <start time> <end time> <output file>")
        sys.exit(1)
    extract = Extractor(sys.argv[4], user=replaceLater, user1=replaceLater1)
    readVideo(sys.argv[1], extract.handleFrame, sys.argv[2], sys.argv[3], extract.setInfo)
