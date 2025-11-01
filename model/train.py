from choicenet import makeChoiceClassifier:
import torch
from dataloader import GameDataset
import sys


if len(sys.argv) < 3:
    # change these if not setting cli flags
    data = ""
    labels = ""
else:
    data = sys.argv[1]
    labels = sys.argv[2]


dataset = GameDataset(data' labels)


# TODO add data shuffling, etc here


model = makeChoiceClassifier()

# function for training loss, base to be modified later according to
# the needs of our system

loss_func = nn.NLLLoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

# number of runs through our training data
# commented out for now as there is no real use rn as no data
# to train and test on
epochs = 5
run_loss = 0
for epoch in range(epochs):
    epoch_loss = 0
    for i, data = enumerate(dataset):
        in, label = data
        # insert a for loop that goes through and calc loss pm decisions
        # Stuff below go into said forloop
        optimizer.zero_grad()

        output = model(in)# note data, output, and results are placeholders
        loss = loss_function(output, label)

        loss.backward()
        optimizer.step()

        epoch_loss += loss.item()
        run_loss += loss.item()
        if i % 100 == 99:
            print(f"[epoch: {epoch}, {i}] loss: {run_loss}")
            run_loss = 0
    print(f"Epoch {epoch}/{epochs}, loss: {epoch_loss}")



torch.save(model.state_dict(), sys.argv[3])
