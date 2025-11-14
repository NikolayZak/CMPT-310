from choicenet import makeChoiceClassifier
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from dataloader import GameDataset
from torch.utils.data import DataLoader, random_split
import sys


if len(sys.argv) < 3:
    # change these if not setting cli flags
    states = ""
    map = ""
else:
    states = sys.argv[1]
    map = sys.argv[2]

longFormat = False
if len(sys.argv) > 4:
    longFormat = True

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

print (device)

data = GameDataset(states, map, long_fmt=longFormat)

train_data, test_data = random_split(data, [0.8, 0.2])
train = DataLoader(train_data, batch_size=32, shuffle=True, num_workers=8)
test = DataLoader(test_data, batch_size=1, shuffle=False, num_workers=2)

print("loaded dataset")

model = makeChoiceClassifier()

model.to(device)

# function for training loss, base to be modified later according to
# the needs of our system

loss_func = nn.NLLLoss()
#optimizer = optim.Adam(model.parameters(), lr=0.001)
optimizer = optim.SGD(model.parameters(), lr=0.001, momentum=0.9)

# number of runs through our training data
# commented out for now as there is no real use rn as no data
# to train and test on
epochs = 20
run_loss = 0
for epoch in range(epochs):
    for i, data in enumerate(train):
        input, label = data[0], data[1].to(device)
        in_map, in_money = input[0].to(device), input[1].to(device)
        # insert a for loop that goes through and calc loss pm decisions
        # Stuff below go into said forloop
        optimizer.zero_grad()

        output = model(in_map, in_money)
        loss = loss_func(output, label)

        loss.backward()
        optimizer.step()

        run_loss += loss.item()
        if i % 100 == 99:
            print(f"[epoch: {epoch+1}, {i}] loss: {run_loss}")
            run_loss = 0
    total = 0
    correct = 0
    correct_types = {i:0 for i in range(4)}
    totals = {i:0 for i in range(4)}
    with torch.no_grad():
        for data in test:
            category = data[1].item()
            input, label = data[0], data[1].to(device)
            in_map, in_money = input[0].to(device), input[1].to(device)
            output = model(in_map, in_money)
            _, predicted = torch.max(output, 1)
            total += 1
            totals[category] += 1
            if predicted == label:
                correct += 1
                correct_types[category] += 1
    accuracy = {i:correct_types[i]/totals[i] for i in range(4) if totals[i] > 0}
    print(f"Epoch {epoch+1}/{epochs}, accuracy: {correct / total}")
    print(f"Category accuracy: {accuracy}")



torch.save(model.state_dict(), sys.argv[3])
