
import numpy as np
from torch.utils.data import Dataset, DataLoader
from datatransform import processAll, loadData, convertKeyFrame2KeyTowerFrame
import pandas as pd
import os

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
        for file in os.listdir(state_path):
            file_name = os.path.basename(file).split('.')[:-1]
            name = "".join(file_name[:-1])
            map = file_name[-1]
            path = os.path.join(state_path, file)
            if long_fmt:
                raw_state = pd.read_csv(path)
            else:
                raw_state = convertKeyFrame2KeyTowerFrame(pd.read_csv(path))
            self.file_offsets.append(self.file_offsets[-1] + raw_state.shape[0])
            data_transform.append((self.maps[map], path, name, long_fmt))
        files = processAll(data_transform)
        self.map_data = [loadData(data[0]) for data in files]
        self.money = [loadData(data[1]) for data in files]
        self.labels = [loadData(data[2]) for data in files]
        self.file_offsets = np.array(self.file_offsets[:-1])
    def __len__(self):
        return sum([data.shape[0] for data in self.map_data])
    def __getitem__(self, index):
        map_index = np.argmax(index >= self.file_offsets)
        index = index - self.file_offsets[map_index]
        return (self.map_data[map_index][index].astype(np.float32), self.money[map_index][index]), self.labels[map_index][index,0]
