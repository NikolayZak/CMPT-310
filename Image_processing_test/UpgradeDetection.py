import cv2
import numpy as np
import os
import sys


def is_predecessor(prev, curr):
    """
    True if curr is exactly prev + 1 in exactly one upgrade path.
    Format: (name, u1, u2, u3)
    """
    _, p1, p2, p3 = prev
    _, c1, c2, c3 = curr

    d1 = c1 - p1
    d2 = c2 - p2
    d3 = c3 - p3

    # Exactly one upgrade increased by +1
    return (
        ((d1 == 1) + (d2 == 1) + (d3 == 1)) == 1 and
        d1 >= 0 and d2 >= 0 and d3 >= 0
    )


# ----------------------------
# Check arguments
# ----------------------------
if len(sys.argv) < 5:
    print("Usage: python3 UpgradeDetection.py <menu_template_folder> <input_video> <frame_frequency> <output_text>")
    sys.exit(1)

menu_template_folder = sys.argv[1]
video_path = sys.argv[2]
fps_out = int(sys.argv[3])
output_txt = sys.argv[4]

sell_button = menu_template_folder + "/sell_button.png"
left_sell_button_location = [244, 872, 166, 73]
right_sell_button_location = [1464, 872, 166, 73]

name_folder = menu_template_folder + "/Towers"
left_name_location = [42, 60, 368, 35]
right_name_location = [1263, 60, 368, 35]

upgrade_template = menu_template_folder + "/upgrade_symbol.png"
left_upgrade_location = [42, 430, 28, 425]
right_upgrade_location = [1263, 430, 28, 425]


def is_template_present(image, template, region=None, threshold=0.8):
    """Check if template exists inside region of image."""
    if region:
        x, y, w, h = region
        search_img = image[y:y+h, x:x+w]
    else:
        search_img = image

    if len(search_img.shape) == 3:
        search_img = cv2.cvtColor(search_img, cv2.COLOR_BGR2GRAY)

    if len(template.shape) == 3:
        template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)

    result = cv2.matchTemplate(search_img, template, cv2.TM_CCOEFF_NORMED)
    max_val = cv2.minMaxLoc(result)[1]
    return max_val >= threshold


# -------------------------------------------------
# Extract upgrades (detecting 3 possible sections)
# -------------------------------------------------
def get_upgrades(frame_gray, region, upgrade_template, threshold=0.8):
    x, y, w, h = region
    crop = frame_gray[y:y+h, x:x+w]

    th, tw = upgrade_template.shape[:2]
    section_height = h // 3
    counts = []

    for sec in range(3):
        sy = sec * section_height
        section = crop[sy:sy + section_height, :].copy()

        count = 0

        while True:
            res = cv2.matchTemplate(section, upgrade_template, cv2.TM_CCOEFF_NORMED)
            max_val = cv2.minMaxLoc(res)[1]

            if max_val < threshold:
                break

            mx, my = cv2.minMaxLoc(res)[3]
            count += 1

            # erase matched area
            section[my:my + th, mx:mx + tw] = 0

        counts.append(count)

    return counts[0], counts[1], counts[2]


# ----------------------------
# Open input video
# ----------------------------
cap = cv2.VideoCapture(video_path)
video_fps = cap.get(cv2.CAP_PROP_FPS)
skip_frames = max(1, round(video_fps / fps_out))

if not cap.isOpened():
    print(f"Error: Could not open video {video_path}")
    sys.exit(1)


# ----------------------------
# Load all templates (names)
# ----------------------------
templates = []
template_names = []

for filename in os.listdir(name_folder):
    if filename.endswith("_menu.png"):
        path = os.path.join(name_folder, filename)
        img = cv2.imread(path, cv2.IMREAD_COLOR)
        if img is None:
            print(f"Failed to load {filename}, skipping.")
            continue

        template_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY).astype(np.float32)
        h, w = template_gray.shape
        templates.append((template_gray, w, h))
        template_names.append(filename.removesuffix("_menu.png"))

if not templates:
    print("No templates found. Exiting.")
    sys.exit(1)


sell_button_img = cv2.imread(sell_button)
upgrade_template_img = cv2.imread(upgrade_template, cv2.IMREAD_GRAYSCALE).astype(np.float32)

# ----------------------------
# Process video
# ----------------------------
frame_idx = 0
results = []

last_state = ("", 0, 0, 0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame_idx += 1
    if frame_idx % skip_frames != 0:
        continue

    frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY).astype(np.float32)

    # LEFT MENU
    if is_template_present(frame, sell_button_img, left_sell_button_location):
        for i, (template_gray, tw, th) in enumerate(templates):
            if is_template_present(frame_gray, template_gray, left_name_location):
                u1, u2, u3 = get_upgrades(frame_gray, left_upgrade_location, upgrade_template_img)

                current = (template_names[i], u1, u2, u3)

                # log only TRUE upgrades
                if is_predecessor(last_state, current):
                    results.append(f"{frame_idx // skip_frames},{current[0]},{u1},{u2},{u3}\n")

                last_state = current
                break

    # RIGHT MENU
    elif is_template_present(frame, sell_button_img, right_sell_button_location):
        for i, (template_gray, tw, th) in enumerate(templates):
            if is_template_present(frame_gray, template_gray, right_name_location):
                u1, u2, u3 = get_upgrades(frame_gray, right_upgrade_location, upgrade_template_img)

                current = (template_names[i], u1, u2, u3)

                # log only TRUE upgrades
                if is_predecessor(last_state, current):
                    results.append(f"{frame_idx // skip_frames},{current[0]},{u1},{u2},{u3}\n")

                last_state = current
                break

# Write all results at once
if results:
    with open(output_txt, "w") as f:
        f.write("".join(results))
cap.release()
