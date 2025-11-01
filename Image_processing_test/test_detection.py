import cv2
import numpy as np
import sys

# ----------------------------
# Check arguments
# ----------------------------
if len(sys.argv) < 3:
    print("Usage: python detect_template_video.py <template_image> <input_video> <output_video>")
    sys.exit(1)

template_path = sys.argv[1]
video_path = sys.argv[2]
output_path = sys.argv[3]  # new output video file

# ----------------------------
# Load template image
# ----------------------------
template = cv2.imread(template_path, cv2.IMREAD_COLOR)
if template is None:
    print(f"Error: Could not read template image {template_path}")
    sys.exit(1)
template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
w, h = template_gray.shape[::-1]

# ----------------------------
# Open input video
# ----------------------------
cap = cv2.VideoCapture(video_path)
if not cap.isOpened():
    print(f"Error: Could not open video {video_path}")
    sys.exit(1)

# Get video info
fps = cap.get(cv2.CAP_PROP_FPS)
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

# Prepare output video
fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # codec
out = cv2.VideoWriter(output_path, fourcc, fps, (frame_width, frame_height))

# ----------------------------
# Process each frame
# ----------------------------
frame_idx = 0
threshold = 0.35  # adjust similarity threshold here

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame_idx += 1
    frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Template Matching
    res = cv2.matchTemplate(frame_gray, template_gray, cv2.TM_CCOEFF_NORMED)
    loc = np.where(res >= threshold)

    # Draw rectangles if matches are found
    for pt in zip(*loc[::-1]):
        cv2.rectangle(frame, pt, (pt[0] + w, pt[1] + h), (0, 255, 0), 2)

    # Print if match detected
    if len(loc[0]) > 0:
        print(f"Match found in frame {frame_idx}")

    # Write frame to output video
    out.write(frame)

# ----------------------------
# Cleanup
# ----------------------------
cap.release()
out.release()
cv2.destroyAllWindows()
print(f"Output video saved to {output_path}")
