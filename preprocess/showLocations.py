from video import createVideoReader, createVideoWriter
from extractor import VideoAnnotate
from map import Map

import numpy as np
import cv2 as cv

map = Map()


def render(fid, img, frame):
    output = frame.copy()#np.zeros(frame.shape, np.uint8)
    map.analyzeFrame(fid, img, frame, blocking = True)
    tower = map.getLastSelectedTower()
    tid = None
    if not tower is None:
        tid = tower.tid
    for twr in map.towers:
        if twr.tid != tid:
            output = cv.circle(output, twr.location, 50, (255, 0, 0), 10)
    if not tower is None:
        position = tower.location
        if tower.last_interacted == fid:
            # currently selected
            output = cv.circle(output, position, 50, (255, 255, 255), 10)
        else:
            # last selected
            output = cv.circle(output, position, 50, (255, 255, 0), 10)
        # text render
        output = cv.putText(output, tower.name, (position[0]+20, position[1]+20), cv.FONT_HERSHEY_SIMPLEX, 2,(0, 0, 0), 20)
        output = cv.putText(output, tower.name, (position[0]+20, position[1]+20), cv.FONT_HERSHEY_SIMPLEX, 2,(255, 255, 255), 10)
    return output

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
