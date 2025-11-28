import numpy as np
import pandas as pd
from PIL import Image, ImageFilter
import cv2

# we will be using this file with pipeline to get images from our image processing
# and read it into a numeric matrix to be read by the machine learning model

# map images are manually blocked out to train the data on
# first load in the image and set it as a numpy array
dataMap = Image.open('testMap3.png') # currently a temporary png to test pipeline
edgeMap = dataMap.filter(ImageFilter.FIND_EDGES)
dataMap = dataMap.filter(ImageFilter.SHARPEN) # processing image to read clearer
# dataMap.save("checkMap.png") #this was for testing
mapArray = np.array(dataMap)

# Get a blank matrix to use to convert the data into binary
# for path and empty space
mapSimple = np.empty([mapArray.shape[0],mapArray.shape[1]])

# create a function to input the rgb and return a color
def color(rgb,aimColor):
    aimColor = np.array(aimColor)
    return np.all(np.abs(rgb-aimColor)<10)

for i in range(mapArray.shape[0]): # for loop traverses through to convert map
    for j in range(mapArray.shape[1]):
        temp = mapArray[i][j]
        
        if (color(temp,[74,173,0])): # check green / empty space
            mapSimple[i][j] = 1 # this is empty space
            
        elif (color(temp,[112,205,255])): # check water 
            mapSimple[i][j] = 2 # this is empty water space
            
        elif (color(temp,[255,179,0])): # check if orange / tree
            mapSimple[i][j] = 3
            
        elif (color(temp,[255,26,0])): #areas in valide for placing
            mapSimple[i][j] = 4
            
        elif (color(temp,[91,91,91])):
            mapSimple[i][j] = 0 # check path 

# merging edge map with the full map to get rid of image edge issues
# we put the edge map into black and white, add a thick border to signify spacing
# and then run code on interpretting it
edgeMap = edgeMap.convert('L')
edgeMap = edgeMap.point(lambda x: 255 if x > 40 else 0)
edgeMap = edgeMap.convert('RGB')
edgeMap = edgeMap.filter(ImageFilter.MaxFilter(5))
mapSimple[np.sum(edgeMap,axis = 2) != 0] = -1
mapSimple = mapSimple.astype(int)

# now to resize the data into 14 * 14 pixel squares
mapFinal = np.zeros([76,118])


for i in range(mapFinal.shape[0]):
    for j in range(mapFinal.shape[1]):
        cut = mapSimple[i*7:(i+1)*7,j*7:(j+1)*7]
        if(np.all(cut == -1)): # getting rid of edge cases where it is all edges
            mapFinal[i][j] = 4
            continue
        values,counts = np.unique(cut[cut != -1],return_counts = True) #gives us count of all values
        index = np.argmax(counts)# get the index of the value with highest count      
        mapFinal[i][j] = values[index] #update new map value accordingly

np.savetxt('tester.txt',mapFinal,fmt = '%d')

