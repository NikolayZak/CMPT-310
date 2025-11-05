import cv2
import numpy as np
import sys

# ----------------------------
# Check arguments
# ----------------------------
if len(sys.argv) < 4:
    print("Usage: python detect_template_video.py <template_image> <input_video> <output_text>")
    sys.exit(1)

template_path = sys.argv[1]
video_path = sys.argv[2]
output_txt = sys.argv[3]

# ----------------------------
# Load template image and convert to gray
# ----------------------------
template = cv2.imread(template_path, cv2.IMREAD_COLOR)
if template is None:
    print(f"Error: Could not read template image {template_path}")
    sys.exit(1)

template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
template_gray = template_gray.astype(np.float32)
h, w = template_gray.shape

# ----------------------------
# Open input video
# ----------------------------
cap = cv2.VideoCapture(video_path)
if not cap.isOpened():
    print(f"Error: Could not open video {video_path}")
    sys.exit(1)

# ----------------------------
# Helper function
# ----------------------------
def is_duplicate(x, y, existing_boxes, tolerance=30):
    """Check if (x, y) is within 'tolerance' pixels of any existing box center."""
    for (ex, ey, ew, eh) in existing_boxes:
        cx, cy = ex + ew / 2, ey + eh / 2
        if abs(x + w/2 - cx) < tolerance and abs(y + h/2 - cy) < tolerance:
            return True
    return False

# ----------------------------
# Process each frame
# ----------------------------
frame_idx = 0
threshold = 0.7
detected_objects = []
results = []

# Optional: skip frames to reduce processing
fps_skip = 1  # process every 2nd frame (adjust for speed)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame_idx += 1
    if frame_idx % fps_skip != 0:
        continue

    frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    frame_gray = frame_gray.astype(np.float32)

    # Template Matching
    res = cv2.matchTemplate(frame_gray, template_gray, cv2.TM_CCOEFF_NORMED)
    loc = np.where(res >= threshold)

    rects = [[pt[0], pt[1], w, h] for pt in zip(*loc[::-1])]

    if rects:
        rects, _ = cv2.groupRectangles(rects, groupThreshold=1, eps=0.5)

        for (x, y, w, h) in rects:
            if not is_duplicate(x, y, detected_objects, tolerance=40):
                detected_objects.append((x, y, w, h))
                results.append(f"{frame_idx},{template_path.removesuffix('_P.png').removeprefix('../Images/TowerVectors/')},{x},{y}")
                print(f"Frame {frame_idx}: New object at (x={x}, y={y})")

cap.release()
cv2.destroyAllWindows()

# Write all results at once
if results != []:
    with open(output_txt, "a") as f:
        f.write("\n".join(results) + "\n")

print(f"Results appended to {output_txt}")
