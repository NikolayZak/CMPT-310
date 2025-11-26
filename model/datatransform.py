import pandas as pd
import numpy as np
from functools import partial
import pickle
from multiprocessing.pool import ThreadPool
import os
import sys

def convertKeyFrame2KeyTowerFrame(path,name):
    print("converting "+path, file=sys.stderr)
    cachepath = f"cache/preprocess-{name}.csv"
    #if os.path.isfile(cachepath) and os.getenv("FORCE_PROCESS") is None:
    #    return pd.read_csv(cachepath)
    data = pd.read_csv(path,sep='`', dtype=str,names=['data'], skiprows=1) # do not seperate(need variable columns)
    data['data'] = data['data'].str.rstrip(',')
    data = data['data'].str.split(',', expand=True)
    rows = []
    for i in range((data.shape[1]-3)//6):
        rows.append(data[[0,1,0]+[i*6+j+2 for j in range(6)]].dropna().astype("Int64"))
    columns=["frame", "money", "tower-id", "type", "x", "y", "upgrade_1", "upgrade_2", "upgrade_3"]
    data = pd.concat((pd.DataFrame(data=np.concatenate(rows,axis=0), columns=columns),
            data[data[[2]].isna().any(axis=1)][list(range(9))].astype("Int64").rename(columns=lambda x: columns[x]))).sort_values(by=["frame"])
    data.to_csv(cachepath)
    return pd.read_csv(cachepath)



inputDim = (118, 76)

# coordinate constants
screenRes=(1920, 1080)
fieldArea = (25, 0,  1643, 1080)
scaleFactor=((fieldArea[2] - fieldArea[0])/inputDim[0],
        (fieldArea[3]-fieldArea[1])/inputDim[1])
offsetFactor=(fieldArea[0], fieldArea[1])


def preprocessState(state):
    # scale coordinates
    state['x'] = (state['x'] - offsetFactor[0]) // scaleFactor[0]
    state['y'] = (state['y'] - offsetFactor[1]) // scaleFactor[1]
    return state

def loadData(info):
    path, shape = info
    return np.memmap(path, dtype=np.uint8, mode="r", shape=shape)


class DataTransform:
    def procMap(self):
        path = f"cache/map-{self.name}.npz"
        if os.path.isfile(path) and self.can_skip:
            return path, self.mapShape
        print(f"creating {path}", file=sys.stderr)
        self.mapOutput(path)
        return path, self.map_output.shape
    def procMoney(self):
        path = f"cache/money-{self.name}.npy"
        if os.path.isfile(path) and self.can_skip:
            return path, self.moneyShape
        print(f"creating {path}", file=sys.stderr)
        self.moneyOutput(path)
        return path,self.money_output.shape
    def procLabels(self):
        path = f"cache/labels-{self.name}.npy"
        if os.path.isfile(path) and self.can_skip:
            return path, self.labelShape
        print(f"creating {path}", file=sys.stderr)
        self.labelOutput(path)
        return path,self.label_output.shape
    def preprocess(self):
        return self.procMap(), self.procMoney(), self.procLabels()
    def __init__(self, map_data, states, name):
        if not os.path.exists('cache'):
            os.mkdir('cache')
        self.name = name
        self.states = preprocessState(states)
        self.map_data = map_data
        self.frame_count = np.max(self.states['frame'])
        self.money = self.states['money']
        self.can_skip = os.getenv("FORCE_PROCESS") is None
        self.mapShape = (self.frame_count, inputDim[1], inputDim[0], 3)
        self.moneyShape = (self.frame_count, 1)
        self.labelShape = (self.frame_count, 5)
    def mapOutput(self, path):
        self.map_output = np.memmap(path, dtype=np.uint8, mode="write", shape=(self.frame_count, inputDim[1], inputDim[0], 3))
        self.map_output[:, :, :, 0] = self.map_data
        self.map_output[:, :, :, 1:2] = 0
        val,idx = np.unique(self.states[["x","y","type"]], return_index=True, return_counts=False, axis=0)
        idx = idx[np.isnan(val[:,0]) == False]
        for row in self.states.iloc[idx][["frame", "y", "x", "type"]].astype(int).itertuples():
            self.map_output[row[1]:,row[2], row[3], 1] = row[4]+1
        self.map_output.flush()
    def moneyOutput(self, path):
        self.money_output = np.memmap(path, dtype=int, mode="write", shape=(self.frame_count, 1))
        for row in self.states[["frame", "money"]].astype(int).itertuples():
            self.money_output[row[1]:] = row[2]
        self.money_output.flush()
    def labelOutput(self, path):
        self.label_output = np.memmap(path, dtype=np.uint8, mode="write", shape=(self.frame_count, 5))
        self.label_output[:] = 0

        val,idx = np.unique(self.states[["x","y","type"]], return_index=True, return_counts=False, axis=0)
        idx = idx[np.isnan(val[:,0]) == False]
        place = np.zeros((self.frame_count, 3), dtype=int)
        frames = self.states["frame"][idx]-1
        place[frames, 0] = self.states["type"][idx]
        place[frames, 1] = self.states["x"][idx]
        place[frames, 2] = self.states["y"][idx]
        self.label_output[frames,0] = 1
        self.label_output[:,1:4] = place

        
        self.label_output.flush()

def worker(args):
    import subprocess
    proc = subprocess.Popen([sys.executable, os.path.join(os.path.dirname(__file__), "datatransform.py")], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    stdout,_ = proc.communicate(input=pickle.dumps(args, protocol=pickle.HIGHEST_PROTOCOL))
    return pickle.loads(stdout)

def processAll(data):
    #pool = ThreadPool(os.cpu_count())
    pool = ThreadPool(3)
    return pool.map(worker, data)

if __name__ == "__main__":
    import sys
    map, state, name, long_fmt = pickle.loads(sys.stdin.buffer.read())
    print(f"loading {state}")
    if long_fmt:
        raw_state = pd.read_csv(state)
    else:
        raw_state = convertKeyFrame2KeyTowerFrame(state, name)
    map = np.loadtxt(map, delimiter=" ", dtype=int)
    transformer = DataTransform(map, raw_state, name)
    print(f"processing {name}", file=sys.stderr)
    out= transformer.preprocess()
    sys.stdout.buffer.write(pickle.dumps(out, protocol=pickle.HIGHEST_PROTOCOL))

