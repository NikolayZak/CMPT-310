import cv2
import numpy as np
import sys

if len(sys.argv) < 3:
    print("Usage: python3 PreProcessing.py <map_image> <input_video>")
    sys.exit(1)

map_image_path = sys.argv[1]
input_video_path = sys.argv[2]
output_video_path = "preprocessed_video.mp4"

# ----------------------------
# Parameters
# ----------------------------
fps_out = 1  # frames per second to process
crop_rect = (0, 0, 1650, 1080)  # x, y, w, h
threshold = 0.2  # pixel difference threshold
min_area = 50  # ignore tiny regions (optional)
blur_ksize = (3, 3)  # Gaussian blur kernel
morph_kernel_size = 9  # Morphological closing kernel size

# ----------------------------
# Load reference map image
# ----------------------------
map_img = cv2.imread(map_image_path).astype(np.float32) / 255.0
x, y, w, h = crop_rect
map_img = map_img[y:y+h, x:x+w]

# ----------------------------
# Open input video
# ----------------------------
cap = cv2.VideoCapture(input_video_path)
if not cap.isOpened():
    print(f"Error: Could not open video {input_video_path}")
    sys.exit(1)

video_fps = cap.get(cv2.CAP_PROP_FPS)
skip_frames = max(1, round(video_fps / fps_out))

# Prepare output video
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter(output_video_path, fourcc, fps_out, (w, h))

# ----------------------------
# Morphological kernel
# ----------------------------
kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (morph_kernel_size, morph_kernel_size))

# ----------------------------
# Process frames
# ----------------------------
frame_idx = 0
while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame_idx += 1
    if frame_idx % skip_frames != 0:
        continue

    # Convert to float32
    frame = frame.astype(np.float32) / 255.0
    tower = frame[y:y+h, x:x+w]

    # Subtract static background
    subtracted = cv2.absdiff(tower, map_img)
    subtracted = cv2.GaussianBlur(subtracted, blur_ksize, 0)

    # Convert to grayscale and threshold
    gray = cv2.cvtColor(subtracted, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, threshold, 1, cv2.THRESH_BINARY)

    # Morphological closing to fill holes
    binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)

    # Remove small areas
    binary = (binary * 255).astype(np.uint8)
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    mask_clean = np.zeros_like(binary)
    for c in contours:
        if cv2.contourArea(c) >= min_area:
            cv2.drawContours(mask_clean, [c], -1, 255, -1)

    # Apply mask
    mask_3d = np.repeat((mask_clean > 0)[:, :, np.newaxis], 3, axis=2).astype(np.float32)
    result = tower * mask_3d

    # Write to output video
    out.write((result * 255).astype(np.uint8))

# Cleanup
cap.release()
out.release()
cv2.destroyAllWindows()
print(f"Preprocessed video saved to {output_video_path}")
