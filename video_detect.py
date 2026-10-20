import cv2
from detector import detect

VIDEO_PATH = "demo.mp4"
OUTPUT_PATH = "outputs/demo_result.mp4"

cap = cv2.VideoCapture(VIDEO_PATH)
if not cap.isOpened():
    raise RuntimeError(f"Could not open {VIDEO_PATH}")

fps = cap.get(cv2.CAP_PROP_FPS) or 25
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

writer = cv2.VideoWriter(
    OUTPUT_PATH, cv2.VideoWriter_fourcc(*"mp4v"), fps, (width, height)
)

frame_number = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break

    detections = detect(frame)

    
    for d in detections:
        cv2.rectangle(frame, (d["x1"], d["y1"]), (d["x2"], d["y2"]), (0, 255, 0), 2)
        label = f'{d["name"]} {int(d["confidence"] * 100)}%'
        (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
        cv2.rectangle(frame, (d["x1"], d["y1"]), (d["x1"] + tw + 10, d["y1"] + th + 12), (0, 0, 0), -1)
        cv2.putText(frame, label, (d["x1"] + 5, d["y1"] + th + 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    # Print what was found, with the time in the video
    seconds = frame_number / fps
    for d in detections:
        print(f"{seconds:5.1f}s  {d}")

    writer.write(frame)
    cv2.imshow("Video detection (press Q to stop)", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

    frame_number += 1

cap.release()
writer.release()
cv2.destroyAllWindows()
print("Saved:", OUTPUT_PATH)