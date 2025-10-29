
import numpy as np
from torch.utils.data import Dataset, DataLoader


dim = (118, 76)

class GameDataset(Dataset):
    def __init__(self, raw_map, labels):
        self.raw_map_data = np.load(raw_map, mmap_mode="r")
        self.labels = np.load(labels, mmap_mode="r")
    def __len__(self):
        return self.raw_map_data.shape[0]
    def __getitem__(self, index):
        return self.raw_map_data[index], self.labels[index]
