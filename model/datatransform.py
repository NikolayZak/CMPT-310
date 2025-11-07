import pandas as pd
import numpy as np
from functools import partial

def convertKeyFrame2KeyTowerFrame(path, out):
    data = pd.read_csv(path,sep='`', dtype=str,names=['data']) # do not seperate(need variable columns)
    data = data['data'].str.split(',', expand=True)
    rows = []
    for i in range((data.shape[1]-3)//6):
        rows.append(data[[0,1]+[i*6+j+2 for j in range(6)]].dropna().astype(int))
    return pd.DataFrame(data=np.concatenate(rows,axis=0), columns=["frame", "money", "type", "x", "y", "upgrade_1", "upgrade_2", "upgrade_3"])




inputDim = (118, 76)

# coordinate constants
screenRes=(1920, 1080)
fieldArea = (25,0,  1643, 1080)
scaleFactor=((fieldArea[2] - fieldArea[0])/inputDim[0],
        (fieldArea[3]-fieldArea[1]/inputDim[1]))
offsetFactor=(fieldArea[0], fieldArea[1])


def preprocessState(state):
    # scale coordinates
    state['x'] = (state['x'] - offsetFactor[0]) // scaleFactor[0]
    state['y'] = (state['y'] - offsetFactor[1]) // scaleFactor[1]
    return state

class DataTransform:
    def loadMap(self, path):
        self.mapOutput(path)
        return self.map_output
        # return np.load(path, mmap_mode="r")
    def loadLabels(self, path):
        self.labelOutput(path)
        return self.label_output
    def __init__(self, map_data, states):
        self.states = preprocessState(states)
        self.map_data = map_data
        self.frame_count = np.max(self.states['frame'])
    def mapOutput(self, path):
        self.map_output = np.memmap(path, dtype=np.uint8, mode="write", shape=(self.frame_count, inputDim[1], inputDim[0], 3))
        self.map_output[:, :, :, 0] = self.map_data
        self.map_output[:, :, :, 1:2] = 0
    def placeTowers(self):
        for row in self.states.itertuples():
            self.map_output[row['frame']:,row['x'], row['y'], 1] = row['type']+1
        self.map_output.flush()
    def labelOutput(self, path):
        self.label_output = np.memmap(path, dtype=np.uint8, mode="write", shape=(self.frame_count, 1))
        self.label_output[:] = 0

        idx = np.unique(self.states[["x","y","type"]], return_index=True, return_counts=False, axis=0)[1]
        frames = np.zeros((self.frame_count), dtype=bool)
        frames[idx] = True
        self.label_output[frames] = 1

        #rev = tower_info.iloc[::-1]
        #idx = np.unique(rev["tower-id"])
        #choice[rev["placed"][idx]+1] = 2
        
        self.label_output.flush()


    
