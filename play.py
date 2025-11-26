from model.choicenet import makeChoiceClassifier
import torch
import numpy as np
import sys
sys.path.append('BTDautogui')

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 3 and sys.argv[3] == "--stub":
        from BTDautogui.btdstub import getMoney, place_monkey, upgrade, noOp
    else:
        from BTDautogui.btdautogui import getMoney, place_monkey, upgrade, noOp

mapSize = (118, 76)
screenArea = (25,0,  1643, 1080)

def getCoord(x,y):
    x = x * ((screenArea[2]-screenArea[0]) / mapSize[0]) + screenArea[0]
    y = y * ((screenArea[3]-screenArea[1]) / mapSize[1]) + screenArea[1]
    return (x, y)

class Player:
    def __init__(self, model, map):
        self.map = np.zeros((mapSize[1], mapSize[0], 3), dtype=np.float32)
        self.map[:, :, 0] = map
        self.money = 0
        self.model = makeChoiceClassifier()
        self.model.load_state_dict(torch.load(model, weights_only=True, map_location=device))
    def place(self, action):
        place_monkey(action[0], getCoord(action[1], action[2]))
        self.map[action[2], action[1], 1] = action[0] + 1
    def applyAction(self, action):
        if action[0] == 1:
            self.place(action[1:])
        noOp()
    def evaluateMove(self):
        with torch.no_grad():
            output = self.model(torch.from_numpy(self.map), torch.tensor([self.money], dtype=torch.float32))
            _, act = torch.max(output[0], 1)
            _, tower = torch.max(output[1], 1)
            _, x = torch.max(output[2], 1)
            _, y = torch.max(output[3], 1)
        return [act.item(), tower.item(), x.item(), y.item()]
    def makeChoice(self):
        money = getMoney()
        if not money is None:
            self.money = money
        print(f"Money: {money}")
        action = self.evaluateMove()
        print(action)
        self.applyAction(action);

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "-h":
            print(f"{sys.argv[0]} [path to model] [path to map] <--stub>")
        model = sys.argv[1]
    else:
        model = "model_weights/model.pth"
    if len(sys.argv) > 2:
        map = sys.argv[2]
    else:
        map = "model/binary_maps/meadows.txt"
    import time

    map = np.loadtxt(map, delimiter=" ", dtype=int)
    player = Player(model, map)
    while True:
        time.sleep(0.25)
        player.makeChoice()
