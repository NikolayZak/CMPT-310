import cv2
import numpy as np
import os
import sys

# ----------------------------
# Check arguments
# ----------------------------
if len(sys.argv) < 4:
    print("Usage: python3 TemplateDetection.py <template_folder> <input_video> <output_text>")
    sys.exit(1)

template_folder = sys.argv[1]
video_path = sys.argv[2]
output_txt = sys.argv[3]

# ----------------------------
# Load templates
# ----------------------------
templates = []
template_names = []

for filename in os.listdir(template_folder):
    if filename.endswith("_P.png"):
        path = os.path.join(template_folder, filename)
        img = cv2.imread(path, cv2.IMREAD_COLOR)
        if img is None:
            print(f"Failed to load {filename}, skipping.")
            continue

        template_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY).astype(np.float32)
        h, w = template_gray.shape

        templates.append((template_gray, w, h))
        template_names.append(filename.removesuffix("_P.png"))

if not templates:
    print("No valid templates found.")
    sys.exit(1)

# ----------------------------
# Open video
# ----------------------------
cap = cv2.VideoCapture(video_path)
if not cap.isOpened():
    print(f"Error: Could not open video {video_path}")
    sys.exit(1)

# ----------------------------
# Permanent duplicate check
# ----------------------------
def is_permanent_duplicate(x, y, w, h, used_positions, tolerance=20):
    """
    A detection is forbidden forever if it occurs too close
    to any previously accepted detection.
    """
    cx, cy = x + w/2, y + h/2
    for (ux, uy, uw, uh) in used_positions:
        ucx, ucy = ux + uw/2, uy + uh/2
        if abs(cx - ucx) < tolerance and abs(cy - ucy) < tolerance:
            return True
    return False

used_positions = []   # stores all past detections forever
threshold = 0.7
results = []
frame_idx = 0

# ----------------------------
# Process video
# ----------------------------
while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame_idx += 1

    frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY).astype(np.float32)

    for i, (template_gray, w, h) in enumerate(templates):
        res = cv2.matchTemplate(frame_gray, template_gray, cv2.TM_CCOEFF_NORMED)
        loc = np.where(res >= threshold)

        rects = [[pt[0], pt[1], w, h] for pt in zip(*loc[::-1])]

        if rects:
            # group overlapping hits within this frame
            rects, _ = cv2.groupRectangles(rects, groupThreshold=1, eps=0.5)

            for (x, y, w, h) in rects:
                # PERMANENT blocking
                if is_permanent_duplicate(x, y, w, h, used_positions):
                    continue

                # accept new detection forever
                used_positions.append((x, y, w, h))
                results.append(f"{frame_idx},{template_names[i]},{x},{y}\n")

cap.release()
cv2.destroyAllWindows()

# ----------------------------
# Save results
# ----------------------------
with open(output_txt, "w") as f:
    f.write("".join(results))
