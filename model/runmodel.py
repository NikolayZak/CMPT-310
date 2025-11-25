import torch
import numpy as np
from choicenet import makeChoiceClassifier

def load_map(path):
    data = np.loadtxt(path, dtype=np.float32)   # (76,118) or (118,76)
    
    # If it's transposed (118x76), fix orientation
    if data.shape == (118, 76):
        data = data.T    # → (76,118)

    # Expand single channel → 3 channels
    data = np.stack([data, data, data], axis=0)   # (3,76,118)

    # Model expects (3,118,76)
    data = data.transpose(0, 2, 1)

    return torch.tensor(data).unsqueeze(0)  # (1,3,118,76)


# ==== LOAD MODEL ====
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = makeChoiceClassifier()
model.load_state_dict(torch.load("model.pth", map_location=device))
model.to(device)
model.eval()

# ==== LOAD YOUR MAP ====
field_tensor = load_map("binary_maps/meadows.txt").to(device)

# ==== MONEY ====
money_tensor = torch.tensor([[650]], dtype=torch.float32).to(device)

# ==== RUN ====
with torch.no_grad():
    act, tower, x_coord, y_coord = model(field_tensor, money_tensor)

print("Action:", torch.argmax(act, dim=1).item())
print("Tower:", torch.argmax(tower, dim=1).item())
print("X:", torch.argmax(x_coord, dim=1).item())
print("Y:", torch.argmax(y_coord, dim=1).item())