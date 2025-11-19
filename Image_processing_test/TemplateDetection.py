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
# Load all templates and convert to grayscale
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
        # Convert to grayscale for matching
        template_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY).astype(np.float32)
        h, w = template_gray.shape
        templates.append((template_gray, w, h))
        template_names.append(filename.removesuffix("_P.png"))

if not templates:
    print("No valid templates found.")
    sys.exit(1)

# ----------------------------
# Open input video
# ----------------------------
cap = cv2.VideoCapture(video_path)
if not cap.isOpened():
    print(f"Error: Could not open video {video_path}")
    sys.exit(1)

# ----------------------------
# Helper function to avoid duplicate detections
# ----------------------------
def is_duplicate(x, y, existing_boxes, tolerance=20):
    for (ex, ey, ew, eh) in existing_boxes:
        cx, cy = ex + ew / 2, ey + eh / 2
        if abs(x + ew/2 - cx) < tolerance and abs(y + eh/2 - cy) < tolerance:
            return True
    return False

# ----------------------------
# Process each frame
# ----------------------------
frame_idx = 0
threshold = 0.69
detected_objects = []
results = []

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame_idx += 1

    # Convert frame to grayscale
    frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY).astype(np.float32)

    # Match all templates on this frame
    for i, (template_gray, w, h) in enumerate(templates):
        res = cv2.matchTemplate(frame_gray, template_gray, cv2.TM_CCOEFF_NORMED)
        loc = np.where(res >= threshold)

        rects = [[pt[0], pt[1], w, h] for pt in zip(*loc[::-1])]

        if rects:
            rects, _ = cv2.groupRectangles(rects, groupThreshold=1, eps=0.5)
            for (x, y, w, h) in rects:
                if not is_duplicate(x, y, detected_objects, tolerance=20):
                    detected_objects.append((x, y, w, h))
                    results.append(f"{frame_idx},{template_names[i]},{x},{y}\n")

cap.release()
cv2.destroyAllWindows()

# Write all results at once
if results:
    with open(output_txt, "w") as f:
        f.write("".join(results))
