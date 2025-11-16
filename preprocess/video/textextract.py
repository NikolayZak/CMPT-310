import pytesseract
import numpy as np

def cropTowerName(frame):
    startX = int(frame.shape[1] * 0.862)
    startY = int(frame.shape[0] * 0.080)
    width = int(frame.shape[1] * 0.120)
    height = int(frame.shape[0] * 0.051)
    return frame[startY:startY+height, startX:startX+width, :]

def cropMoney(frame):
    startX = int(frame.shape[1] * 0.18)
    startY = int(frame.shape[0] * 0)
    width = int(frame.shape[1] * 0.164)
    height = int(frame.shape[0] * 0.06)
    return frame[startY:startY+height, startX:startX+width, :]

def getTowerNameBlocking(frame):
    return pytesseract.image_to_string(cropTowerName(frame)).strip().lower()

from multiprocessing import Pool

#import cv2 as cv
def processTowerName(pid, img):
    name = pytesseract.image_to_string(img).strip().lower()
    return (pid, name)

def processMoney(pid, img):
    img[:,:,0] = 255*((img[:,:,0] > 235) & (img[:,:,0] > 235) & (img[:,:,0] > 235))
    img[:,:,1] = img[:,:,0]
    img[:,:,2] = img[:,:,0]
    amnt = pytesseract.image_to_string(img).strip().lower()
    amnt = amnt.replace("o", "0").replace("l","1").replace("!", "1").replace("z", "2").replace("s","5").replace("g","6")[1:]
    amnt = "".join(c for c in amnt if c.isdigit())
    if amnt == "":
        print("Unable to read money")
        return (int(pid), 0)
    return (int(pid), int(amnt))

class TextProcessor:
    def __init__(self):
        self.pool = Pool()
        self.queuedTowerName = []
        self.towerName = []
        self.queuedMoney = []
        self.money = []
    def requestTowerName(self, fid, img):
        img = cropTowerName(img)
        self.queuedTowerName.append(self.pool.apply_async(processTowerName, (fid, img)))
        if len(self.queuedTowerName) % 2000 == 0:
            self.towerName += [task.get() for task in self.queuedTowerName]
            self.queuedTowerName = []
    def requestMoney(self, fid, img):
        img = cropMoney(img)
        #cv.imwrite("test.png",img)
        self.queuedMoney.append(self.pool.apply_async(processMoney, (fid, img)))
        if len(self.queuedMoney) % 2000 == 0:
            self.money += [task.get() for task in self.queuedMoney]
            self.queuedMoney = []
    def gatherTowerName(self):
        return self.towerName + [task.get() for task in self.queuedTowerName]
    def gatherMoney(self):
        return np.array(self.money+[task.get() for task in self.queuedMoney], dtype=np.dtype("int,int"))
