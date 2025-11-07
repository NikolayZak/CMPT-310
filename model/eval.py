from choicenet import makeChoiceClassifier
import torch
import sys
import numpy as np

model = makeChoiceClassifier()
model.load_state_dict(torch.load(sys.argv[1], weights_only=True))
model.eval()

# will need to load the data in later to test and see
# loading in the data that is an array form of the map
# test array for now
tester = torch.from_numpy(np.zeros((76*118*3,),dtype=np.float32))

# evaluation function
# currently it is log function, may adjust accordingly
# will return a number that corresponds to a choice
with torch.no_grad():
    log_probabilities = model(tester)

probabilities = torch.exp(log_probabilities)
print(probabilities)

output = np.argmax(probabilities)
print(output)
