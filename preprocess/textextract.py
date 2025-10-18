import pytesseract

def getTowerNameImg(frame):
    startX = int(frame.shape[1] * 0.862)
    startY = int(frame.shape[0] * 0.080)
    width = int(frame.shape[1] * 0.120)
    height = int(frame.shape[0] * 0.051)
    return frame[startY:startY+height, startX:startX+width, :]

def getTowerName(frame):
    return pytesseract.image_to_string(getTowerNameImg(frame)).strip().lower()

from multiprocessing import Pool

def processTowerName(frame, img):
    return (frame, pytesseract.image_to_string(img).strip().lower())

class TextProcessor:
    def __init__(self):
        self.pool = Pool()
        self.queuedTowerName = []
    def requestTowerName(self, frame, img):
        self.queuedTowerName.append(self.pool.apply_async(processTowerName, (frame, img)))
    def gatherTowerName(self):
        return [task.get() for task in self.queuedTower]

