import cv2
import numpy as np
import sys
import os

if len(sys.argv) < 5:
    print("Usage: python ExtractMoney.py <template_folder> <input_video> <frame_frequency> <output_text>")
    sys.exit(1)

template_folder = sys.argv[1]
input_video_path = sys.argv[2]
output_txt = sys.argv[4]

# Crop rectangle (x, y, w, h)
crop_rect = (360, 20, 195, 45)

stabilizer = []
fps_out = int(sys.argv[3])
frame_count = 0
threshold = 0.77
overlap_thresh = 0.5
digit_gap = 100

def nms_boxes(boxes, scores, overlapThresh):
    if len(boxes) == 0:
        return []

    boxes = np.array(boxes)
    scores = np.array(scores)

    x1 = boxes[:,0]
    y1 = boxes[:,1]
    x2 = boxes[:,0] + boxes[:,2]
    y2 = boxes[:,1] + boxes[:,3]

    area = (x2 - x1 + 1) * (y2 - y1 + 1)
    idxs = np.argsort(scores)
    pick = []

    while len(idxs) > 0:
        last = idxs[-1]
        pick.append(last)

        xx1 = np.maximum(x1[last], x1[idxs[:-1]])
        yy1 = np.maximum(y1[last], y1[idxs[:-1]])
        xx2 = np.minimum(x2[last], x2[idxs[:-1]])
        yy2 = np.minimum(y2[last], y2[idxs[:-1]])

        w = np.maximum(0, xx2 - xx1 + 1)
        h = np.maximum(0, yy2 - yy1 + 1)
        overlap = (w * h) / area[idxs[:-1]]

        idxs = np.delete(idxs, np.concatenate(([len(idxs)-1], np.where(overlap > overlapThresh)[0])))

    return pick

# Load templates
templates = {}
for d in range(10):
    path = os.path.join(template_folder, f"{d}_P.png")
    t = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    if t is None:
        print(f"Missing template: {path}")
        sys.exit(1)
    templates[d] = t

cap = cv2.VideoCapture(input_video_path)
video_fps = cap.get(cv2.CAP_PROP_FPS)
skip_frames = max(1, round(video_fps / fps_out))

if not cap.isOpened():
    print("Could not open video:", input_video_path)
    sys.exit(1)

frame_idx = 0
results = []
while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame_idx += 1
    if frame_idx % skip_frames != 0:
        continue

    # Crop
    x, y, w, h = crop_rect
    cropped = frame[y:y+h, x:x+w]
    gray = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)

    final_digits = []

    for digit, templ in templates.items():
        tH, tW = templ.shape[:2]
        res = cv2.matchTemplate(gray, templ, cv2.TM_CCOEFF_NORMED)

        ys, xs = np.where(res >= threshold)

        boxes = []
        scores = []

        for (x, y) in zip(xs, ys):
            boxes.append([x, y, tW, tH])
            scores.append(res[y, x])

        keep = nms_boxes(boxes, scores, overlap_thresh)

        for idx in keep:
            x, y, w, h = boxes[idx]
            final_digits.append((x, digit))

    # Sort digits left-to-right
    final_digits.sort(key=lambda x: x[0])

    # Check if there are any digits detected
    if final_digits:
        # Remove outlier digits on the left
        keep_index = 0
        for i in range(1, len(final_digits)):
            x_prev, _ = final_digits[i-1]
            x_curr, _ = final_digits[i]
            if x_curr - x_prev > digit_gap:
                keep_index = i

        final_digits = final_digits[keep_index:]

        # Build number string
        number_str = "".join(str(d) for _, d in final_digits)
    else:
        number_str = ""


    # Store valid numbers
    if number_str.isdigit():
        results.append(f"{frame_idx // skip_frames},{number_str}\n")

# Write all results at once

with open(output_txt, "w") as f:
    f.write("".join(results))
cap.release()
cv2.destroyAllWindows()