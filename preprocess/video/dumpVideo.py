from map import Map
from video import createVideoReader
from background import Background

import pandas as pd

class DataExtractor:
    def __init__(self, video, start=None, end=None):
        self.map = Map()
        self.path = video
        self.start = start
        self.end = end
        self.frame_data = []
        self.tower_data = []
        self.fid = 0
    def dump(self, output_path):
        self.video = createVideoReader(self.path)
        resolution,fps = self.video.getInfo()
        self.background = Background(resolution)
        self.video.process(self.processFrame, start=self.start, end=self.end)
        output = self.extractData()
        output = pd.DataFrame(output, columns=["frame", "money", "tower-id", "type", "x", "y", "upgrade-1", "upgrade-2", "upgrade-3", "mode"])
        output.to_csv(output_path)
    def processFrame(self, frame):
        if not self.background.hasImg():
            self.background.setImg(frame)
        objects = self.background.rmBackground(frame)
        tower = self.map.analyzeFrame(self.fid, frame, objects)
        self.fid += 1
    def extractData(self):
        self.map.gatherText()
        frameUpdate = []
        towerStatus = self.map.getTowerUpdates()
        for frame in self.map.money:
            for tower in towerStatus:#TODO replace with numpy search
                if tower.frame >= frame[0]:
                    frameUpdate.append((frame[0], frame[1]) + tower.dump())
        return frameUpdate


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 5:
        print("showLocations.py <input file> <start time> <end time> <output file>")
        sys.exit(1)
    extract = DataExtractor(sys.argv[1], start=sys.argv[2], end=sys.argv[3])
    extract.dump(sys.argv[4])
