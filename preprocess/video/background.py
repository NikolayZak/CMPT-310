import numpy as np
import cv2 as cv

color1 = [63, 175, 132]
back1 = [56, 207, 160]
color2 = [158, 164, 157]
back2 = [177, 193, 192]

def extractColor(color1, color2, back1, back2):
    def extractComp(a1, a2, b1, b2):
        return (b1*(a2-b2) - b2*(a1-b1))/(a2+b1-a1-b2)
    def getAlpha(comp, a, b):
        return (a-b)/(comp-b)
    color = [0,0,0]
    alphas =[0,0,0]
    for i in range(3):
        comp = extractComp(color1[i], color2[i], back1[i], back2[i])
        color[i] = round(comp)
        alpha = getAlpha(comp, color1[i], back1[i])
        alphas[i] = alpha
    alpha = sum(alphas)/3
    # get tint foreground
    color = [c*alpha for c in color]
    return (color, alpha)

select_tint = extractColor(color1, color2, back1, back2)

def tintImg(img, tintColor, tintAlpha):
    img = img.astype(float)
    img = (1.0-tintAlpha) * img
    img = np.add(tintColor, img)
    return img.astype(np.uint8)


morph_kernel = np.ones((7,7), np.uint8)

def createMask(image, background):
    mask = cv.cvtColor(cv.absdiff(image, background), cv.COLOR_BGR2GRAY)
    return cv.morphologyEx(mask, cv.MORPH_OPEN, morph_kernel)

def applyMask(image, mask, tol):
    mask = mask[:,:,] >= tol
    return cv.bitwise_or(image,image,mask=mask.astype(np.uint8)*255)

def mergeMask(masks, tol):
    final_mask = masks[0]
    for mask in masks[1:]:
        final_mask = applyMask(final_mask, mask, tol)
    return final_mask

class Background:
    def __init__(self, resolution):
        self.select_color = np.full((int(resolution[1]), int(resolution[0]), 3), select_tint[0], float)
        self.img = []
    def hasImg(self):
        return len(self.img) > 0
    def setImg(self, img):
        self.img = [img]
        self.img.append(tintImg(img, self.select_color, select_tint[1]))
    def rmBackground(self, image, tol = 5):
        masks = [createMask(image, back) for back in self.img]
        mask = mergeMask(masks, tol)
        return applyMask(image, mask, tol)

