
import numpy as np
from torch.utils.data import Dataset, DataLoader
from datatransform import processAll, loadData, convertKeyFrame2KeyTowerFrame
import pandas as pd
import os

downsample = 0.2
dim = (118, 76)

class GameDataset(Dataset):
    def __init__(self, state_path, map_path, long_fmt=False):
        self.maps = {}
        for map in os.listdir(map_path):
            self.maps[os.path.basename(map)[:-4]] = os.path.join(map_path,map)
        self.file_offsets = [0]
        self.labels = []
        self.map_data = []
        self.money = []
        data_transform = []
        for map in os.listdir(state_path):
            map_path = os.path.join(state_path, map)
            for file in os.listdir(map_path):
                ext = os.path.basename(file).split('.')[-1]
                name = ".".join(os.path.basename(file).split('.')[:-1])
                path = os.path.join(map_path, file)
                data_transform.append((self.maps[map], path, name, ext == "csv"))
        files = processAll(data_transform)

        self.map_data = [loadData(data[0]) for data in files]
        self.money = [loadData(data[1]) for data in files]
        self.labels = [loadData(data[2]) for data in files]
        self.filter = []
        for i in range(len(self.labels)):
            threshold = downsample * np.sum([self.labels[i][0] == 0])/self.labels[i].shape[0]
            filter = np.random.uniform(size=len(self.labels[i])) < threshold
            print("threshold" ,float(threshold))
            filter[self.labels[i][:, 0] != 0] = True
            self.file_offsets.append(self.file_offsets[-1] + np.sum(filter))
            self.filter.append(filter)
        self.file_offsets = np.array(self.file_offsets[:-1])
        self.length = sum([np.sum(data) for data in self.filter])
    def __len__(self):
        return self.length  * 10
    def __getitem__(self, index):
        index = index % self.length
        map_index = np.argmin(index >= self.file_offsets) -1
        index = index - self.file_offsets[map_index]
        filter = self.filter[map_index]
        return (np.copy(self.map_data[map_index][filter][index].astype(np.float32)), np.copy(self.money[map_index][filter][index])), np.copy(self.labels[map_index][filter][index])
    def resetSeed(self):
        return np.random.seed(0)
