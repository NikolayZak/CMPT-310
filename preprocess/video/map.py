from textextract import getTowerNameBlocking, TextProcessor
from feature import TowerLocationTracker, distance 

from difflib import get_close_matches
tower_types=("dart monkey", "boomerang monkey", "bomb shooter", "tack shooter",
            "ice monkey", "glue gunner", "desperado", "sniper monkey", "monkey sub",
            "monkey buccaneer", "monkey ace", "heli pilot", "mortar monkey", "dartling gunner",
            "wizard monkey", "super monkey", "ninja monkey", "alchemist", "druid", "mermonkey",
            "banana farm", "spike factory", "monkey village", "engineer monkey", "beast handler")

def getTowerType(name):
    name = get_close_matches(name, tower_types, n=1)
    if len(name) > 0:
        return tower_types.index(name[0]) + 1 
    return 0


class Tower:
    def __init__(self, tid, fid, coords, upgrades=(0,0,0), mode=0):
        self.tid = tid
        self.name = None
        self.frame = fid
        self.last_interacted = fid
        self.location = coords
        self.upgrades = upgrades
        self.mode = mode
    def setName(self, name):
        if not self.name is None:
            if self.name != name:
                print(f"Warning: {self.name} renamed to {name}")
        self.name = name
    def dump(self):
        return (self.tid, getTowerType(self.name), self.location[0], self.location[1], self.upgrades[0], self.upgrades[1], self.upgrades[2], self.mode)

class Map:
    def __init__(self):
        self.tracker = TowerLocationTracker()
        self.towers = []
        self.money = None
        self.lastSelectedTower = None
        self.textProc = TextProcessor()
    def getLastSelectedTower(self):
        if self.lastSelectedTower is None:
            return None
        return self.towers[self.lastSelectedTower]
    def analyzeFrame(self, fid, rawFrame, frame, blocking=False):
        self.tracker.processFrame(frame)
        towerLocation = self.tracker.getSelectedTower()
        if not towerLocation is None:
            tid = self.getTowerID(towerLocation)
            if tid is None:
                tid = len(self.towers)
                self.towers.append(Tower(tid,fid,towerLocation))
            self.lastSelectedTower = tid
            tower = self.towers[tid]
            tower.last_interacted = fid
            self.getTowerName(fid, tid, rawFrame, blocking)
        if self.tracker.isGameplay():
            return self.getMoney(fid, rawFrame)
    def getTowerID(self, coord):
        for tower in self.towers:
            if distance(coord, tower.location) < 100:
                return tower.tid
        return None
    def getTowerName(self, fid, tid, frame, blocking=False):
        if blocking:
            self.towers[tid].name = getTowerNameBlocking(frame)
        self.textProc.requestTowerName((fid,tid), frame)
    def getMoney(self, fid, frame, blocking=False):
        self.textProc.requestMoney(fid, frame)
    def gatherText(self):
        for entry in self.textProc.gatherTowerName():
            ids = entry[0]
            name = entry[1]
            for tower in self.towers:
                if tower.tid == ids[1]:
                    tower.setName(name)
        self.money = self.textProc.gatherMoney()
    def getTowerUpdates(self):
        return self.towers #TODO replace this with tower updates
