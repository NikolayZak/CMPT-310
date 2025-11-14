
import numpy as np
from torch.utils.data import Dataset, DataLoader
from datatransform import DataTransform, convertKeyFrame2KeyTowerFrame
import pandas as pd

dim = (118, 76)


class GameDataset(Dataset):
    def __init__(self, state_path, map_path, long_fmt=False):
        self.raw_map = np.loadtxt(map_path, delimiter=" ", dtype=int)
        if long_fmt:
            self.raw_state = pd.read_csv(state_path)
        else:
            self.raw_state = convertKeyFrame2KeyTowerFrame(pd.read_csv(state_path))
        self.data = DataTransform(self.raw_map, self.raw_state)
        self.map_data, self.money = self.data.loadMap("cache/map.npz")
        self.labels = self.data.loadLabels("cache/labels.npy")
    def __len__(self):
        return self.map_data.shape[0]
    def __getitem__(self, index):
        return (self.map_data[index].astype(np.float32), self.money[index]), self.labels[index,0]
