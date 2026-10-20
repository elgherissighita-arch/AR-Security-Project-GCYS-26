import os
import glob
from ultralytics import YOLO

USEFUL_CLASSES = {
    "laptop", "cell phone", "keyboard", "mouse", "tv",
    "bottle", "cup", "book", "backpack", "person",
}
MIN_CONFIDENCE = 0.25

model = YOLO("yolov8n.pt")

os.makedirs("outputs", exist_ok=True)

image_paths = glob.glob("images/*.jpg") + glob.glob("images/*.jpeg") + glob.glob("images/*.png")

if not image_paths:
    print("No images found in the images/ folder.")

for path in image_paths:
    print("\n=== Image:", path, "===")

    results = model(path, conf=MIN_CONFIDENCE, verbose=False)
    result = results[0]

    for box in result.boxes:
        class_id = int(box.cls[0])
        name = model.names[class_id]
        confidence = float(box.conf[0])
        x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())

        kept = "KEEP" if name in USEFUL_CLASSES else "ignore"
        print(f"{name:12s} conf={confidence:.2f} box=({x1},{y1},{x2},{y2}) [{kept}]")

    output_path = os.path.join("outputs", os.path.basename(path))
    result.save(filename=output_path)
    print("Saved:", output_path)