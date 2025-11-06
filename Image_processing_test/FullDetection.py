import os
import subprocess

# --- Paths ---
templates_dir = "../Images/TowerVectors"
map_image = "../Images/Maps/base_monkey_meadow.png"
input_video = "test_data.mp4"
intermediate_video = "preprocessed_video.mp4"
output_txt = "output.txt"

# --- Step 1: Run PreProcessing.py ---
print("Running PreProcessing...")
subprocess.run(["python3", "PreProcessing.py", map_image, input_video], check=True)
print(f"Matching templates to {intermediate_video}")

# --- Step 2: Run TemplateDetection.py for all templates in folder ---
print("Running template detections...")
subprocess.run([
    "python3", "TemplateDetection.py",
    templates_dir,           # <-- Pass folder instead of individual file
    intermediate_video,
    output_txt
], check=True)

# --- Step 3: Delete intermediate video ---
if os.path.exists(intermediate_video):
    os.remove(intermediate_video)
    print(f"Deleted {intermediate_video}")

print(f"✅ All done. Results saved in {output_txt}")
