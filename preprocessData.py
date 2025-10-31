
import numpy as np
import pandas as pd
import sys

dim = (118, 76)
screen_area = (25,0,  1643, 1080)

tower_info = pd.read_csv(sys.argv[1])
"""
input data format:
    placed : the frame the tower was placed (a frame is 1/60 of a second)
    tower-id: unique id for the tower
    type:tower type
    x: x coords
    y: y coords
    upgrade-n: upgrade on the n upgrade path
    mode: misc ie boomerang monkey throw direction
"""




tower_info["x"] = (tower_info["x"] - screen_area[0]) // (screen_area[2]-screen_area[0] / dim[0])
tower_info["y"] = (tower_info["y"] - screen_area[1]) // (screen_area[3]-screen_area[1] / dim[1])

map_info = np.zeros(dim, np.uint8) #TODO load map

"""
cell format 6 bytes
 - byte 0 map tile (and indicate type) (leading 0 indicates map tile)
 - 1 byte (4 bits  1-4 - tower type

to add later
 - 1 byte upgrades
 - 1 byte tower mode
"""
map_dims = map_info.shape()

frame_count = np.max(tower_info['placed'])

output = np.memmap("data.npy", dtype=np.uint8, mode="w", shape=(frame_count, dim[0], dim[1], 2))


output[:, :, :, 0] = map_info
output[:, :, :, 1:2] = 0

def getUpgradeMode(up1, up2, up3, mode):
    out = 0
    if up1 > 0:
        out = out | 0xff

def applyTower(tower):
    output[tower['placed']:,tower['x'], tower['y'], 1] = tower['type']
    #output[tower['placed']:,tower['x'], tower['y'], 1] = tower['upgrade-1']

tower_info.apply(applyTower, axis=1)
output.flush()

choice = np.memmap("choice_labels.npy", dtype=np.uint8, mode="w", shape=(frame_count, 1))
choice[:] = 0

# place
idx = np.unique(tower_info["tower-id"])
choice[tower_info["placed"][idx]] = 1

# sell
rev = tower_info.iloc[::-1]
idx = np.unique(rev["tower-id"])
choice[rev["placed"][idx]+1] = 2


# TODO handle upgrading


choice.flush()
