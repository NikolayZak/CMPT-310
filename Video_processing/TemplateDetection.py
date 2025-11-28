import cv2
import numpy as np
import os
import sys

def is_permanent_duplicate(x, y, w, h, used_positions, tolerance=20):
    cx, cy = x + w/2, y + h/2
    for (ux, uy, uw, uh) in used_positions:
        ucx, ucy = ux + uw/2, uy + uh/2
        if abs(cx - ucx) < tolerance and abs(cy - ucy) < tolerance:
            return True
    return False


if len(sys.argv) < 4:
    print("Usage: python3 TemplateDetection.py <template_folder> <input_video> <output_text>")
    sys.exit(1)

template_folder = sys.argv[1]
video_path = sys.argv[2]
output_txt = sys.argv[3]


templates = []
template_names = []

# load templates
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

# open processed video
cap = cv2.VideoCapture(video_path)
if not cap.isOpened():
    print(f"Error: Could not open video {video_path}")
    sys.exit(1)

used_positions = []   # stores all past detections forever
threshold = 0.7
results = []
frame_idx = 0


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
            # overlatpping detections within this frame
            rects, _ = cv2.groupRectangles(rects, groupThreshold=1, eps=0.5)

            for (x, y, w, h) in rects:
                if is_permanent_duplicate(x, y, w, h, used_positions):
                    continue

                # append new detections
                used_positions.append((x, y, w, h))
                results.append(f"{frame_idx},{template_names[i]},{x},{y}\n")

cap.release()
cv2.destroyAllWindows()

# write to output
with open(output_txt, "w") as f:
    f.write("".join(results))
