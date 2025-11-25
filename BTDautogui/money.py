import pytesseract
import numpy as np


def cropMoney(frame):
    startX = int(frame.shape[1] * 0.18)
    startY = int(frame.shape[0] * 0)
    width = int(frame.shape[1] * 0.164)
    height = int(frame.shape[0] * 0.06)
    return frame[startY:startY+height, startX:startX+width, :]


def getMoney(img):
    img[:,:,0] = 255*((img[:,:,0] > 235) & (img[:,:,0] > 235) & (img[:,:,0] > 235))
    img[:,:,1] = img[:,:,0]
    img[:,:,2] = img[:,:,0]
    amnt = pytesseract.image_to_string(img).strip().lower()
    amnt = amnt.replace("o", "0").replace("l","1").replace("!", "1").replace("z", "2").replace("s","5").replace("g","6")[1:]
    amnt = "".join(c for c in amnt if c.isdigit())
    if amnt == "":
        print("Unable to read money")
        return None
    return int(amnt)
