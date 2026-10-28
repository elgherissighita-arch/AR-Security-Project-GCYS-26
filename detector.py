from ultralytics import YOLO

# Classes we keep (edit this list if needed)
USEFUL_CLASSES = {
    "laptop", "cell phone", "keyboard", "tv",
    "bottle", "cup", "book", "backpack", "person",
}

MIN_CONFIDENCE = 0.5

# The model is loaded once, when the file is imported
model = YOLO("yolov8n.pt")


def detect(image):
    """
    image: a file path (str) or an OpenCV frame (numpy array).
    Returns a list of detections in the common format:
    {"name": str, "confidence": float (0 to 1),
     "x1": int, "y1": int, "x2": int, "y2": int}
    (x1, y1) = top-left corner, (x2, y2) = bottom-right corner, in pixels.
    """
    results = model(image, conf=MIN_CONFIDENCE, verbose=False)
    detections = []

    for box in results[0].boxes:
        name = model.names[int(box.cls[0])]

        if name not in USEFUL_CLASSES:
            continue

        x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())

        detections.append({
            "name": name,
            "confidence": round(float(box.conf[0]), 2),
            "x1": x1,
            "y1": y1,
            "x2": x2,
            "y2": y2,
        })

    return detections