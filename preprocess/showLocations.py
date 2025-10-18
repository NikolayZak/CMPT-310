from video import createVideoReader, createVideoWriter
from extractor import VideoAnnotate
from feature import TowerLocationTracker, distance 
from textextract import getTowerName

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

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 5:
        print("showLocations.py <input file> <start time> <end time> <output file>")
        sys.exit(1)
    reader = createVideoReader(sys.argv[1])
    annotate = VideoAnnotate(sys.argv[4], user=replaceLater, user1=replaceLater1)
    res, fps = reader.getInfo()
    annotate.setInfo(res, fps)
    reader.process(annotate.handleFrame, start=sys.argv[2], end=sys.argv[3])
    annotate.close()
