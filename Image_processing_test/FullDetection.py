import os
import sys
import subprocess


# Easy Run: python3 ./FullDetection.py test_data.mp4 monkey_meadow.png final_output.txt
# add a 5th argument to clear the results

# --- Paths ---
tower_templates = "../Images/TowerVectors"
number_templates = "../Images/NumbersVector"
menu_templates = "../Images/MenuTemplates"
maps = "../Images/Maps"

current_map = maps + sys.argv[2]
input_video = sys.argv[1]

intermediate_video = "preprocessed_video.mp4"

tower_output = "TowerOutput.txt"
money_output = "MoneyOutput.txt"
upgrade_output = "UpgradeOutput.txt"
final_output = sys.argv[3]

frame_frequency = 1


# ----------------------------
# Check arguments
# ----------------------------
if len(sys.argv) < 4:
    print("Usage: python3 FullDetection.py <video_data> <map_name> <output_file> <exists => delete_intermediate_files>")
    sys.exit(1)

# --- Step 0: Clear files if an argument is presented ---
if(len(sys.argv) > 4):
    # video
    if os.path.exists(intermediate_video):
        os.remove(intermediate_video)
    # towers
    if os.path.exists(tower_output):
        os.remove(tower_output)
    # money
    if os.path.exists(money_output):
        os.remove(money_output)
    # upgrades
    if os.path.exists(upgrade_output):
        os.remove(upgrade_output)
    # final
    if os.path.exists(final_output):
        os.remove(final_output)


# --- Step 1: Run PreProcessing.py ---
print("Running PreProcessing...")
if not os.path.exists(intermediate_video):
    subprocess.run(["python3", "PreProcessing.py", current_map, input_video, str(frame_frequency)], check=True)
print(f"Created: {intermediate_video}")

# --- Step 2: Run TemplateDetection.py for all templates in folder ---
print("Matching Templates...")
if not os.path.exists(tower_output):
    subprocess.run([
        "python3", "TemplateDetection.py",
        tower_templates,
        intermediate_video,
        tower_output
    ], check=True)
print(f"Template Results saved in {tower_output}")

# --- Step 3: Run ExtractMoney.py
print("Extracting money...")
if not os.path.exists(money_output):
    subprocess.run([
        "python3", "ExtractMoney.py",
        number_templates,
        input_video,
        str(frame_frequency),
        money_output
    ], check=True)
print(f"Money Results saved in {money_output}")

# --- Step 4: Run UpgradeDetection.py
print("Extracting Upgrades...")
if not os.path.exists(upgrade_output):
    subprocess.run([
        "python3", "UpgradeDetection.py",
        menu_templates,
        input_video,
        str(frame_frequency),
        upgrade_output
    ], check=True)
print(f"Upgrade Results saved in {upgrade_output}")

# --- Step 4: Run CombineData.py
print("Processing Data...")
if not os.path.exists(final_output):
    subprocess.run([
        "python3", "CombineData.py",
        money_output,
        tower_output,
        upgrade_output,
        final_output
    ], check=True)
print(f"Final Data Saved in: {final_output}")