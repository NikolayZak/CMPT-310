
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F

import pandas as pd
import numpy as np

# will need to load the data in later to test and see
# loading in the data that is an array form of the map
# test array for now
# note to anyone touching this, must put array as such
# for testing, training, etc

# source of the base code we are using as a springboard
# https://www.youtube.com/watch?v=e5CDe00B3vE



# base system for our neural net, will need to make adjustments
class makeChoiceClassifier(nn.Module):
    def __init__(self, num_classes=4):
        # Where define all parts of model
        super().__init__()
        model_size = 2096
        self.input = nn.Linear(76*118*3, model_size)
        self.moneyA = nn.Linear(model_size, (model_size // 2))
        self.moneyB = nn.Linear(model_size, (model_size // 2))
        self.hidden = nn.Linear(model_size, (model_size // 2))
        self.act_out = nn.Linear((model_size // 2),4)
        self.tower_out = nn.Linear((model_size // 2), 25)
        self.x_out = nn.Linear((model_size // 2), 118)
        self.y_out = nn.Linear((model_size // 2), 76)
        
    def forward(self, field, money):
        # connect parts defined and return output
        # x = field.view(-1, 76*118*3)
        x = field.reshape(-1, 76*118*3)
        money = money.view(-1, 1)
        x = F.relu(self.input(x))
        x = F.relu(torch.add(self.moneyA(x), money*self.moneyB(x)))
        act = F.log_softmax(self.act_out(x),dim=1)
        tower = F.log_softmax(self.tower_out(x),dim=1)
        x_coord = F.log_softmax(self.x_out(x),dim=1)
        y_coord = F.log_softmax(self.y_out(x),dim=1)
        return act, tower, x_coord, y_coord

