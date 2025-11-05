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
# Load template image
# ----------------------------
template = cv2.imread(template_path, cv2.IMREAD_COLOR)
if template is None:
    print(f"Error: Could not read template image {template_path}")
    sys.exit(1)

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

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame_idx += 1

    res = cv2.matchTemplate(frame, template, cv2.TM_CCOEFF_NORMED)
    loc = np.where(res >= threshold)

    rects = []
    for pt in zip(*loc[::-1]):
        rects.append([pt[0], pt[1], w, h])

    if rects:
        rects, weights = cv2.groupRectangles(rects, groupThreshold=1, eps=0.5)

        for (x, y, w, h) in rects:
            if not is_duplicate(x, y, detected_objects, tolerance=40):
                detected_objects.append((x, y, w, h))
                line = f"Frame {frame_idx}: New object at (x={x}, y={y})"
                print(line)

                # Write each detection immediately
                with open(output_txt, "a") as f:
                    f.write(f"{frame_idx},{template_path[:-6]},{x},{y}\n")

cap.release()
cv2.destroyAllWindows()
print(f"Results appended to {output_txt}")