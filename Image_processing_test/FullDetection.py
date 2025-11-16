import os
import subprocess

# --- Paths ---
tower_templates = "../Images/TowerVectors"
number_templates = "../Images/NumbersVector"
map_image = "../Images/Maps/base_monkey_meadow.png"
input_video = "test_data.mp4"
intermediate_video = "preprocessed_video.mp4"
tower_output = "TowerOutput.txt"
money_output = "MoneyOutput.txt"
frame_frequency = 1

# --- Step 1: Run PreProcessing.py ---
print("Running PreProcessing...")
subprocess.run(["python3", "PreProcessing.py", map_image, input_video, str(frame_frequency)], check=True)
print(f"Matching templates to {intermediate_video}")

# --- Step 2: Run TemplateDetection.py for all templates in folder ---
print("Running template detections...")
subprocess.run([
    "python3", "TemplateDetection.py",
    tower_templates,           # <-- Pass folder instead of individual file
    intermediate_video,
    tower_output
], check=True)

# --- Step 3: Delete intermediate video ---
if os.path.exists(intermediate_video):
    os.remove(intermediate_video)
    print(f"Deleted {intermediate_video}")

print(f"Template Results saved in {tower_output}")

# --- Step 3: Run ExtractMoney.py
print("Extracting money...")
subprocess.run([
    "python3", "ExtractMoney.py",
    number_templates,
    input_video,
    str(frame_frequency),
    money_output
], check=True)