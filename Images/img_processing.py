import cv2
import os



# LEGACY FILE USED TO CREATE CROPPED TOWER VECTORS FROM BACKGROUND REMOVED IMAGES FROM "remove.bg"


# Folder containing PNG files
input_folder = "Monkeys_removed_background"
output_folder = "cropped_Monkeys"

# Create output folder if it doesn't exist
os.makedirs(output_folder, exist_ok=True)

# Process all PNG files in the folder
for filename in os.listdir(input_folder):
    if filename.endswith(".png"):
        # Remove watermark part from name
        name = filename.replace("-removebg-preview", "").replace(".png", "")
        input_path = os.path.join(input_folder, filename)
        output_path = os.path.join(output_folder, name + "_P.png")

        # Load image with alpha channel
        img = cv2.imread(input_path, cv2.IMREAD_UNCHANGED)
        if img is None:
            print(f"Failed to load {filename}")
            continue
        if img.shape[2] < 4:
            print(f"{filename} does not have alpha channel, skipping")
            continue

        # Separate alpha channel
        alpha = img[:, :, 3]

        # Find non-zero alpha pixels
        coords = cv2.findNonZero(alpha)
        if coords is None:
            print(f"No non-transparent pixels in {filename}, skipping")
            continue

        x, y, w, h = cv2.boundingRect(coords)

        # Crop the image to the bounding box
        cropped = img[y:y+h, x:x+w]

        # Save result
        cv2.imwrite(output_path, cropped)
        print(f"Cropped {filename} → {output_path}")

print("All images processed.")
