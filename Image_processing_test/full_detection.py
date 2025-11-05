import os
import subprocess
import glob

# --- Paths ---
templates_dir = "../Images/Monkeys"
map_image = "base_monkey_meadow.png"
input_video = "test_data.mp4"
intermediate_video = "output_video.mp4"
output_txt = "output.txt"

# --- Step 1: Run opencv_test.py ---
print("Running opencv_test...")
subprocess.run(["python3", "opencv_test.py", map_image, input_video], check=True)

# --- Step 2: Process each template ---
print("Running template detections...")
templates = glob.glob(os.path.join(templates_dir, "*"))

for template_path in templates:
    print(f"Processing {template_path} ...")
    subprocess.run([
        "python3", "test_detection.py",
        template_path,
        intermediate_video,
        output_txt
    ], check=True)

# --- Step 3: Delete intermediate video ---
if os.path.exists(intermediate_video):
    os.remove(intermediate_video)
    print(f"Deleted {intermediate_video}")

print(f"✅ All done. Results saved in {output_txt}")
