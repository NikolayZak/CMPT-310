from textextract import getTowerNameBlocking, TextProcessor
from feature import TowerLocationTracker, distance 

def TowerTypeID(name):
    return 0


class Tower:
    def __init__(self, tid, fid, coords, upgrades=(0,0,0), mode=0):
        self.tid = tid
        self.name = None
        self.placed = fid
        self.last_interacted = fid
        self.location = coords
        self.upgrades = upgrades
        self.mode = mode
    def setName(self, name):
        self.name = name
    def dump(self):
        pass


class Map:
    def __init__(self):
        self.tracker = TowerLocationTracker()
        self.towers = []
        self.lastSelectedTower = None
        self.textProc = TextProcessor()
    def getLastSelectedTower(self):
        if self.lastSelectedTower is None:
            return None
        return self.towers[self.lastSelectedTower]
    def analyzeFrame(self, fid, rawFrame, frame, blocking=False):
        towerLocation = self.tracker.getSelectedTower(frame)
        if not towerLocation is None:
            tid = self.getTowerID(towerLocation)
            if tid is None:
                tid = len(self.towers)
                self.towers.append(Tower(tid,fid,towerLocation))
            self.lastSelectedTower = tid
            tower = self.towers[tid]
            tower.last_interacted = fid
            self.getTowerName(fid, tid, rawFrame, blocking)
    def getTowerID(self, coord):
        for tower in self.towers:
            if distance(coord, tower.location) < 100:
                return tower.tid
        return None
    def getTowerName(self, fid, tid, frame, blocking=False):
        if blocking:
            self.towers[tid].name = getTowerNameBlocking(frame)
        self.textProc.requestTowerName((fid,tid), frame)
    def gatherText(self):
        return self.textProc.gatherTowerName()
