from choicenet import makeChoiceClassifier:
import torch
from dataloader import GameDataset
import sys


model = makeChoiceClassifier()

# function for training loss, base to be modified later according to
# the needs of our system

loss_func = nn.NLLLoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

# number of runs through our training data
# commented out for now as there is no real use rn as no data
# to train and test on
epochs = 5
for epoch in range(epochs):
    # insert a for loop that goes through and calc loss pm decisions
        # Stuff below go into said forloop
    optimizer.zero_grad()

    output = model(tester)# note data, output, and results are placeholders
    loss = loss_function(output, results)

    loss.backward()
    optimizer.step()



torch.save(model.state_dict(), sys.argv[3])
