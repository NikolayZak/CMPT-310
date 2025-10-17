import pytesseract

def getTowerNameImg(frame):
    startX = int(frame.shape[1] * 0.862)
    startY = int(frame.shape[0] * 0.080)
    width = int(frame.shape[1] * 0.120)
    height = int(frame.shape[0] * 0.051)
    return frame[startY:startY+height, startX:startX+width, :]

def getTowerName(frame):    
    return pytesseract.image_to_string(getTowerNameImg(frame)).strip().lower()

