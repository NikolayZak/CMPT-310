
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
        self.input = nn.Linear(76*118*3, 128)
        self.hidden = nn.Linear(128, 64)
        self.output = nn.Linear(64,4)
        
    def forward(self, x):
        # connect parts defined and return output
        x = x.view(-1, 76*118*3)
        x = F.relu(self.input(x))
        x = F.relu(self.hidden(x))
        x = F.log_softmax(self.output(x),dim=1)
        return x

