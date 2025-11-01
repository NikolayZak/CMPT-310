import cv2
import numpy as np
import sys

if len(sys.argv) < 3:
    print("Usage: python script.py <map_image> <input_video>")
    sys.exit(1)

map_image = sys.argv[1]
input_video = sys.argv[2]

# Parameters
n = 1  # frames per second to process
croplen = (0, 0, 1650, 1080)
threshold = 0.15

# Load background reference
map_img = cv2.imread(map_image).astype(np.float32) / 255.0
x, y, w, h = croplen
map_img = map_img[y:y+h, x:x+w]

# Open input video
cap = cv2.VideoCapture(input_video)
fps = cap.get(cv2.CAP_PROP_FPS)
skip_frames = max(1, round(fps / n))

# Prepare output video
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter("output_video.mp4", fourcc, n, (w, h))

frame_idx = 0
while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame_idx += 1
    if frame_idx % skip_frames != 0:
        continue

    frame = frame.astype(np.float32) / 255.0
    tower = frame[y:y+h, x:x+w]

    # Subtraction and Gaussian blur
    subtracted = cv2.absdiff(tower, map_img)
    subtracted = cv2.GaussianBlur(subtracted, (0, 0), 7)

    # Threshold and convert to binary mask
    gray = cv2.cvtColor(subtracted, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, threshold, 1, cv2.THRESH_BINARY)

    # Remove small areas (bwareaopen equivalent)
    binary = (binary * 255).astype(np.uint8)
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for c in contours:
        if cv2.contourArea(c) < 200:
            cv2.drawContours(binary, [c], -1, 0, -1)

    # Morphological close (strel('disk', 20))
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (41, 41))
    binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)

    # Apply mask
    mask_3d = np.repeat((binary > 0)[:, :, np.newaxis], 3, axis=2).astype(np.float32)
    result = tower * mask_3d

    # Write frame to output video
    out.write((result * 255).astype(np.uint8))

# Cleanup
cap.release()
out.release()
